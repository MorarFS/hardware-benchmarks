"""Frozen source workload on MLX; separate quantization/cache/timing configuration."""
import argparse,importlib.util,json,sys,threading,time
from pathlib import Path
import mlx.core as mx
from mlx_lm import load,stream_generate
from mlx_lm.sample_utils import make_sampler
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import runner as frozen
from mac_runtime import gpu_lock
loader=importlib.util.spec_from_file_location('bench',ROOT/'scripts/run-mac-benchmark.py');bench=importlib.util.module_from_spec(loader);loader.loader.exec_module(bench)
def main():
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,default=ROOT/'work/mlx-qwen8');p.add_argument('--output',type=Path,default=ROOT/'local-results/m4-mlx-history');a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);suite=frozen.load_suite(ROOT/'experiments/history-v2');before=bench.snapshot();stop=threading.Event();abort=[];samples=[]
 receipt={'backend':'MLX','model_revision':'545dc4251c05440727734bcd94334791f6ab0192','model_repository':'mlx-community/Qwen3-8B-4bit','fixture_hashes':suite['freeze']['files'],'context_preflight_limit':32768,'max_output_tokens':2048,'seed':42,'temperature':0,'thinking':False,'cache':'Fresh default MLX cache per request, no prefix reuse, no KV quantization or sliding window requested','downloads':'Continue by user instruction','comparison_limit':'Different 4-bit group64 artifact and BF16 model dtype from FP16-KV Q4_K_M llama.cpp configuration; not backend-only comparison.'}
 (a.output/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
 def monitor():
  import os
  while not stop.is_set():
   row={'time':time.time(),**bench.snapshot(os.getpid())};samples.append(row)
   if row['swap_used_bytes']-before['swap_used_bytes']>1024**3:abort.append('Swap growth above1GiB')
   if not row['ac_connected']:abort.append('AC disconnected')
   stop.wait(2)
 thread=threading.Thread(target=monitor,daemon=True);thread.start();records={}
 try:
  mx.random.seed(42);model,tok=load(str(a.model));receipt['model_dtype']=str(model.layers[0].self_attn.q_proj.scales.dtype)
  (a.output/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
  def request(name,prompt,inputs):
   if any(x.startswith('gold/') for x in inputs):raise RuntimeError('Gold forbidden')
   messages=[{'role':'system','content':suite['prompts']['system']},{'role':'user','content':prompt}]
   tokens=tok.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False)
   if len(tokens)+2048+256>32768:raise RuntimeError('Full prompt exceeds limit')
   payload={'messages':messages,'max_tokens':2048,'enable_thinking':False,'temperature':0,'seed':42};(a.output/(name+'-request.json')).write_text(json.dumps(payload,indent=2)+'\n')
   start=time.perf_counter();first=None;last=None;output='';ids=[];response=None
   with (a.output/(name+'-stream.jsonl')).open('w') as log:
    for response in stream_generate(model,tok,tokens,max_tokens=2048,sampler=make_sampler(temp=0)):
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
  request('merged-summary-synthesis',suite['prompts']['synthesis'].format(source=merged),['prompts.json'])
  request(*control)
  held=[r for n,r in records.items() if not n.startswith('development-')];n=sum(r['visible_tokens_retokenized'] for r in held);phase=sum(r['visible_phase_seconds'] for r in held);wall=sum(r['wall_seconds'] for r in held)
  (a.output/'complete.json').write_text(json.dumps({'heldout_requests':len(held),'visible_tokens':n,'visible_phase_tokens_per_second':n/phase,'visible_tokens_per_wall_second':n/wall,'wall_seconds':wall,'quality':'Unadjudicated; execution is not an accuracy score'},indent=2)+'\n')
 finally:
  stop.set();thread.join();(a.output/'memory.json').write_text(json.dumps(samples,indent=2)+'\n')
if __name__=='__main__':
 with gpu_lock(ROOT):main()
