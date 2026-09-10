"""Separate context diagnostics; never replaces the frozen source battery."""
import argparse,importlib.util,json,os,sys,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from mac_runtime import gpu_lock
from flash_next_compat import configure_sawfwair_norms
spec=importlib.util.spec_from_file_location('bench',ROOT/'scripts/run-mac-benchmark.py');bench=importlib.util.module_from_spec(spec);spec.loader.exec_module(bench)
def main():
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 import mlx.core as mx
 from mlx_vlm import load,stream_generate
 def write(name,data):(a.output/name).write_text(json.dumps(data,indent=2)+'\n')
 before=bench.snapshot();stop=threading.Event();samples=[]
 def monitor():
  while not stop.is_set():
   r={'time':time.time(),**bench.snapshot(os.getpid())};samples.append(r)
   if r['swap_used_bytes']-before['swap_used_bytes']>1024**3 or r['process_rss_bytes']>55*1024**3 or not r['ac_connected']:
    write('abort.json',r);os._exit(2)
   stop.wait(2)
 thread=threading.Thread(target=monitor,daemon=True);thread.start()
 try:
  compatibility=configure_sawfwair_norms(a.model);mx.random.seed(42);model,processor=load(str(a.model),lazy=False,strict=True);tok=processor.tokenizer
  write('protocol.json',{'purpose':'Context diagnostics after a failed full-source synthesis; does not replace or rescore frozen outputs','temperature':0,'seed':42,'MTP':False,'enable_thinking':False,'max_tokens':256,'prefill_step_size':256,'runtime_compatibility':compatibility})
  source='\n\n'.join((ROOT/'experiments/history-v2/inputs'/f'H{i}.txt').read_text() for i in range(1,5))
  prompt='Using only these four excerpts, give three concise answers with PDF page citations: (1) Who led the Visigoths toward the Danube? (2) Who intervened in the gladiatorial games in AD404? (3) Who reunited the Ottoman realm after its civil wars?\n\n'+source+'\n\nGive the three requested names and citations now.'
  requests=[('all-source-retrieval',prompt,{'names':['Fritigern','Telemachus','Mohammed or Mahomet']})]
  filler='The archive contains ordinary notes about weather, gardens, roads, buildings, and weekly schedules. These notes do not contain any registration codes. '
  filler_ids=tok.encode(filler,add_special_tokens=False)
  for size in [4096,16000]:
   segment=tok.decode((filler_ids*(size//len(filler_ids)+2))[:size//2-100])
   prompt='Find the three registration codes in the document. Return only a JSON object with BEGIN, MIDDLE, and END.\n\nBEGIN registration code: opal-5731\n'+segment+'\nMIDDLE registration code: cobalt-8426\n'+segment+'\nEND registration code: cedar-1964\n\nReturn all three registration codes now.'
   requests.append((f'synthetic-{size}',prompt,{'BEGIN':'opal-5731','MIDDLE':'cobalt-8426','END':'cedar-1964'}))
  records=[]
  for name,prompt,expected in requests:
   rendered=tok.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True,enable_thinking=False);n=len(tok.encode(rendered,add_special_tokens=False));assert 0<n<32768-512
   write(name+'-request.json',{'prompt':prompt,'rendered_prompt':rendered,'expected':expected,'input_tokens':n})
   start=time.perf_counter();text='';response=None
   with (a.output/(name+'-stream.jsonl')).open('w') as log:
    for response in stream_generate(model,processor,rendered,max_tokens=256,temperature=0,seed=42,enable_thinking=False,prefill_step_size=256):
     elapsed=time.perf_counter()-start
     if elapsed>900:raise RuntimeError('Diagnostic timeout')
     text+=response.text;log.write(json.dumps({'elapsed_seconds':elapsed,'text':response.text,'token':response.token})+'\n');log.flush()
   record={'name':name,'output':text,'input_tokens':n,'reported_prompt_tokens':response.prompt_tokens,'generation_tokens':response.generation_tokens,'generation_tps':response.generation_tps,'prompt_tps':response.prompt_tps,'peak_memory_GB':response.peak_memory,'finish_reason':response.finish_reason,'wall_seconds':time.perf_counter()-start}
   write(name+'.json',record);records.append(record);print(name,n,text,flush=True)
  write('complete.json',{'requests':records})
 finally:
  stop.set();thread.join();write('memory.json',samples)
if __name__=='__main__':
 with gpu_lock(ROOT):main()
