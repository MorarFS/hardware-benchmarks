"""Measured target-only MLX Flash-Next smoke/warm runs with disk-backed full PLE."""
import argparse,dataclasses,importlib.util,json,os,sys,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from mac_runtime import gpu_lock
from flash_next_compat import configure_sawfwair_norms
spec=importlib.util.spec_from_file_location('bench',ROOT/'scripts/run-mac-benchmark.py');bench=importlib.util.module_from_spec(spec);spec.loader.exec_module(bench)
def main():
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 import mlx.core as mx
 from mlx.utils import tree_flatten
 from mlx_vlm import load,stream_generate
 from mlx_vlm.models.qwen4_exp.ple_storage import QuantizedMMapNGramEmbedding
 before=bench.snapshot();stop=threading.Event();samples=[];abort=[]
 def write(name,value):(a.output/name).write_text(json.dumps(value,indent=2)+'\n')
 def monitor():
  while not stop.is_set():
   row={'time':time.time(),**bench.snapshot(os.getpid())};samples.append(row)
   with (a.output/'memory.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
   if row['swap_used_bytes']-before['swap_used_bytes']>1024**3:abort.append('Swap growth above 1 GiB')
   if row['process_rss_bytes']>55*1024**3:abort.append('Process RSS above 55 GiB')
   if not row['ac_connected']:abort.append('AC disconnected')
   if abort:
    write('abort.json',{'reason':abort,'last_sample':row});os._exit(2)
   stop.wait(2)
 thread=threading.Thread(target=monitor,daemon=True);thread.start()
 try:
  write('protocol.json',{'repository':'Sawfwair/Qwen3.8-Flash-Next-MLX-Mixed-2bit','revision':'a6e3d7a43efb8803cd6b847299a54084dc4e8ef4','runtime_commit':'8f5dc3ddddbb8d7dd2b88ac51015def6f81fed21','device':mx.device_info(),'MTP':False,'thinking':False,'temperature':0,'seed':42,'max_tokens':256,'prefill_step_size':256,'cache':'Fresh native cache per request; no prefix reuse or KV quantization','PLE':'Complete Q4/g32 original tensor ranges mapped read-only, no persistent row cache','PLE_stats_note':'Logical quantized row bytes and lookup elapsed time; not measured physical SSD throughput or filesystem cache misses','downloads':'Never paused','memory_limits':'No limit above device recommendation. Upstream generation temporarily wires up to recommended working set.'})
  write('runtime-compatibility.json',configure_sawfwair_norms(a.model))
  mx.random.seed(42);start=time.perf_counter();model,processor=load(str(a.model),lazy=False,strict=True);mx.synchronize()
  parameter_bytes=sum(v.nbytes for _,v in tree_flatten(model.parameters()))
  # PLE store is intentionally not an nn.Module; inspect the architecture field.
  stores=[layer.ple.ple_embedding.ngram_embedding for layer in model.language_model.model.layers if hasattr(layer,'ple') and layer.ple is not None]
  assert len(stores)==1 and isinstance(stores[0],QuantizedMMapNGramEmbedding)
  write('load.json',{'seconds':time.perf_counter()-start,'parameter_bytes':parameter_bytes,'active_memory_bytes':mx.get_active_memory(),'peak_memory_bytes':mx.get_peak_memory(),'ple_rows':stores[0].row_count,'note':'Filesystem cache is uncontrolled; do not call this a cold load.'})
  tok=processor.tokenizer if hasattr(processor,'tokenizer') else processor
  prompts=[('coherence','Answer these three items briefly: What is 6 times 7? What is the capital of France? Explain in three sentences why a large language model can fit in memory yet generate slowly.')]+[(('warmup' if i==0 else 'warm-'+str(i)),'Explain in plain English how unified memory affects local language-model inference. Discuss weights, KV cache, and why a model can fit yet be slow. Use about 180 words.') for i in range(4)]
  records=[]
  for name,prompt in prompts:
   messages=[{'role':'user','content':prompt}];rendered=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
   assert tok.encode(rendered,add_special_tokens=False),'Tokenizer produced empty input'
   write(name+'-request.json',{'messages':messages,'rendered_prompt':rendered,'prompt_tokens':len(tok.encode(rendered,add_special_tokens=False)),'enable_thinking':False,'max_tokens':256})
   start=time.perf_counter();first=None;last=None;text='';response=None
   with (a.output/(name+'-stream.jsonl')).open('w') as f:
    for response in stream_generate(model,processor,rendered,max_tokens=256,temperature=0,seed=42,enable_thinking=False,prefill_step_size=256):
     elapsed=time.perf_counter()-start
     if elapsed>600:raise RuntimeError('Smoke request exceeded 600 seconds')
     text+=response.text
     if response.text:first=elapsed if first is None else first;last=elapsed
     f.write(json.dumps({'elapsed_seconds':elapsed,'text':response.text,'token':response.token})+'\n');f.flush()
   record={'name':name,'text':text,'wall_seconds':time.perf_counter()-start,'first_content_seconds':first,'last_content_seconds':last,'prompt_tokens':response.prompt_tokens,'generation_tokens':response.generation_tokens,'prompt_tps':response.prompt_tps,'generation_tps':response.generation_tps,'peak_memory_gb':response.peak_memory,'finish_reason':response.finish_reason,'visible_tokens':len(tok.encode(text,add_special_tokens=False)),'PLE_stats':dataclasses.asdict(stores[0].stats)}
   write(name+'.json',record);records.append(record);print(name,record['generation_tps'],text[:200],flush=True)
  write('complete.json',{'requests':records,'quality':'Unreviewed; execution alone does not establish coherence or source accuracy.'})
 except BaseException as e:
  write('failure.json',{'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()});raise
 finally:
  stop.set();thread.join();write('memory-summary.json',{'before':before,'after':bench.snapshot(),'peak_process_rss_bytes':max((x['process_rss_bytes'] for x in samples),default=0),'peak_swap_used_bytes':max((x['swap_used_bytes'] for x in samples),default=0)})
if __name__=='__main__':
 with gpu_lock(ROOT):main()
