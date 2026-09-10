"""Frozen source workload on target-only Flash-Next MLX with full disk-backed PLE."""
import argparse,importlib.util,json,sys,threading,time
from pathlib import Path
import mlx.core as mx
from mlx_vlm import load,stream_generate

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import runner as frozen
from mac_runtime import gpu_lock
from flash_next_compat import configure_sawfwair_norms
loader=importlib.util.spec_from_file_location('bench',ROOT/'scripts/run-mac-benchmark.py');bench=importlib.util.module_from_spec(loader);loader.loader.exec_module(bench)
def main():
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);suite=frozen.load_suite(ROOT/'experiments/history-v2');before=bench.snapshot();stop=threading.Event();abort=[];samples=[]
 receipt={'backend':'MLX-VLM','runtime_commit':'8f5dc3ddddbb8d7dd2b88ac51015def6f81fed21','MTP':False,'prefill_step_size':256,'PLE':'Complete source Q4/g32 table, read-only disk-backed ranges, no persistent row cache','model_revision':'a6e3d7a43efb8803cd6b847299a54084dc4e8ef4','model_repository':'Sawfwair/Qwen3.8-Flash-Next-MLX-Mixed-2bit','fixture_hashes':suite['freeze']['files'],'context_preflight_limit':32768,'max_output_tokens':2048,'seed':42,'temperature':0,'thinking':False,'cache':'Fresh default MLX cache per request, no prefix reuse, no KV quantization or sliding window requested','downloads':'Continue by user instruction','comparison_limit':'Full model mixed Q2/g128 experts and Q4 core/PLE, BF16 protected tensors; full Q4 PLE read from SSD. Target-only, no MTP. Separate MLX artifact and native cache from GGUF comparisons.'}
 (a.output/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
 def monitor():
  import os
  while not stop.is_set():
   row={'time':time.time(),**bench.snapshot(os.getpid())};samples.append(row)
   if row['swap_used_bytes']-before['swap_used_bytes']>1024**3:abort.append('Swap growth above 1 GiB')
   if row['process_rss_bytes']>55*1024**3:abort.append('Process RSS above 55 GiB')
   if not row['ac_connected']:abort.append('AC disconnected')
   if abort:
    (a.output/'abort.json').write_text(json.dumps({'reason':abort,'last_sample':row},indent=2));os._exit(2)
   stop.wait(2)
 thread=threading.Thread(target=monitor,daemon=True);thread.start();records={}
 try:
  receipt['runtime_compatibility']=configure_sawfwair_norms(a.model)
  mx.random.seed(42);load_start=time.perf_counter();model,processor=load(str(a.model),lazy=False,strict=True);mx.synchronize();receipt['load_seconds']=time.perf_counter()-load_start;tok=processor.tokenizer if hasattr(processor,'tokenizer') else processor;receipt['model_dtype']='BF16 protected matrices and mixed affine quantized matrices'
  (a.output/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
  def request(name,prompt,inputs):
   if any(x.startswith('gold/') for x in inputs):raise RuntimeError('Gold forbidden')
   messages=[{'role':'system','content':suite['prompts']['system']},{'role':'user','content':prompt}]
   rendered=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
   tokens=tok.encode(rendered,add_special_tokens=False)
   if not tokens:raise RuntimeError('Tokenizer produced empty input')
   if len(tokens)+2048+256>32768:raise RuntimeError('Full prompt exceeds limit')
   payload={'messages':messages,'max_tokens':2048,'enable_thinking':False,'temperature':0,'seed':42};(a.output/(name+'-request.json')).write_text(json.dumps(payload,indent=2)+'\n')
   start=time.perf_counter();first=None;last=None;output='';ids=[];response=None
   with (a.output/(name+'-stream.jsonl')).open('w') as log:
    for response in stream_generate(model,processor,rendered,max_tokens=2048,temperature=0,seed=42,enable_thinking=False,prefill_step_size=256):
     elapsed=time.perf_counter()-start
     if abort:raise RuntimeError(abort[0])
     if elapsed>900:raise RuntimeError('request timeout')
     output+=response.text;ids.append(response.token)
     if response.text:
      first=elapsed if first is None else first;last=elapsed
     log.write(json.dumps({'elapsed_seconds':elapsed,'text':response.text,'token':response.token})+'\n')
   wall=time.perf_counter()-start
   visible=tok.encode(output,add_special_tokens=False);span=last-first if first is not None and last>first else None
   record={'name':name,'output':output,'source_files':inputs,'prompt_tokens':len(tokens),'generation_tokens':response.generation_tokens,'prompt_tps':response.prompt_tps,'generation_tps':response.generation_tps,'peak_memory_gb':response.peak_memory,'first_content_seconds':first,'last_content_seconds':last,'visible_phase_seconds':span,'visible_tokens_retokenized':len(visible),'wall_seconds':wall,'finish_reason':response.finish_reason,'status':'capped' if response.finish_reason=='length' else 'ok'}
   records[name]=record;(a.output/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n');(a.output/(name+'.md')).write_text(output+'\n');print(name,record['generation_tps'],wall,flush=True)
  stages,control=frozen.source_stages(suite)
  for name,prompt,inputs in stages:request(name,prompt,inputs)
  merged='\n\n'.join(h['id']+'\n'+records[h['id']+'-summary']['output'] for h in suite['questions'])
  if all(records[h['id']+'-summary']['status']=='ok' for h in suite['questions']):
   request('merged-summary-synthesis',suite['prompts']['synthesis'].format(source=merged),['prompts.json'])
  else:(a.output/'merged-summary-synthesis.json').write_text(json.dumps({'status':'blocked_by_parent','reason':'At least one direct summary capped; synthesis not submitted'},indent=2)+'\n')
  request(*control)
  held=[r for n,r in records.items() if not n.startswith('development-')];n=sum(r['visible_tokens_retokenized'] for r in held);phase=sum(r['visible_phase_seconds'] for r in held);wall=sum(r['wall_seconds'] for r in held)
  (a.output/'complete.json').write_text(json.dumps({'heldout_requests':len(held),'visible_tokens':n,'visible_phase_tokens_per_second':n/phase,'visible_tokens_per_wall_second':n/wall,'wall_seconds':wall,'quality':'Unadjudicated; execution is not an accuracy score'},indent=2)+'\n')
 finally:
  stop.set();thread.join();(a.output/'memory.json').write_text(json.dumps(samples,indent=2)+'\n')
if __name__=='__main__':
 with gpu_lock(ROOT):main()
