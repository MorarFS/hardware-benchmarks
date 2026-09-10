#!/usr/bin/env python3
"""Separate single-request context/logging diagnostic; never replaces the battery."""
import csv,datetime,hashlib,json,re,socket,subprocess,sys,threading,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/history_v2'));sys.path.insert(0,str(ROOT/'scripts'))
import run_mac as history
from mac_runtime import gpu_lock,model_specs,storage_relative
SOURCE=ROOT/'results/2026-09-10/m4-max/history/qwen3-8b'
def main():
 spec=model_specs(ROOT)['qwen3-8b'];model=ROOT/'work'/storage_relative(spec)
 assert history.bench.sha256(model)==spec['sha256']
 out=ROOT/'local-results'/('m4-context-diagnostic-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir(parents=True)
 payload=json.loads((SOURCE/'H1-summary-request.json').read_text())
 source_command=json.loads((SOURCE/'server-command.json').read_text())
 results=[]
 for index,(context,verbose) in enumerate([(32768,True),(8192,True),(32768,False),(8192,False),(32768,True)],1):
  folder=out/f"{index}-ctx{context}-{'verbose' if verbose else 'quiet'}"
  folder.mkdir()
  with socket.socket() as available:available.bind(('127.0.0.1',0));port=available.getsockname()[1]
  command=list(source_command);command[0]=str(ROOT/'work/llama-metal/llama-b10852/llama-server')
  for flag,value in [('-m',str(model)),('-c',str(context)),('--port',str(port))]:command[command.index(flag)+1]=value
  if not verbose:command.remove('-v')
  (folder/'command.json').write_text(json.dumps([Path(v).name if v.startswith(str(ROOT)) else v for v in command],indent=2)+'\n')
  (folder/'request.json').write_text(json.dumps(payload,indent=2)+'\n')
  before=history.bench.snapshot();assert before['ac_connected'];started=time.monotonic();samples=[];record={};worker=None
  with (folder/'runtime.log').open('w') as log:
   process=subprocess.Popen(command,stdout=log,stderr=log,stdin=subprocess.DEVNULL)
   try:
    while process.poll() is None:
     sample=dict(elapsed_seconds=time.monotonic()-started,**history.bench.snapshot(process.pid));samples.append(sample)
     if sample['swap_used_bytes']-before['swap_used_bytes']>1024**3:raise RuntimeError('Swap guard')
     if not sample['ac_connected']:raise RuntimeError('AC disconnected')
     if time.monotonic()-started>240:raise RuntimeError('Diagnostic trial timeout')
     if worker is None:
      try:
       with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1) as reply:ready=json.load(reply).get('status')=='ok'
      except (OSError,TimeoutError):ready=False
      if ready:
       base=f'http://127.0.0.1:{port}'
       rendered=history.post(base,'/apply-template',{'messages':payload['messages'],'chat_template_kwargs':{'enable_thinking':False}})['prompt']
       tokens=history.post(base,'/tokenize',{'content':rendered,'add_special':True})['tokens']
       assert len(tokens)+payload['max_tokens']+256<=context
       record.update(prompt_tokens_preflight=len(tokens),server_ready_seconds=time.monotonic()-started)
       worker=threading.Thread(target=history.stream,args=(base,payload,folder,'H1-summary',record),daemon=True);worker.start()
     elif not worker.is_alive():break
     time.sleep(1)
    if worker:worker.join(timeout=1)
   finally:
    if process.poll() is None:
     process.terminate()
     try:process.wait(timeout=15)
     except subprocess.TimeoutExpired:process.kill();process.wait()
  raw=(folder/'runtime.log').read_text(errors='replace');off=re.findall(r'offloaded\s+(\d+)/(\d+)\s+layers to GPU',raw)
  full_offload=bool(off) and all(a==b and int(a)>0 for a,b in off)
  if verbose:assert full_offload
  if off:assert full_offload
  assert record.get('status')=='ok' and not record['reasoning_output'].strip(),record
  assert record['usage']['prompt_tokens']==record['prompt_tokens_preflight']
  assert (record['usage']['prompt_tokens_details'].get('cached_tokens',0))==0
  events=[json.loads(line) for line in (folder/'H1-summary-stream.jsonl').read_text().splitlines()]
  assert ''.join(c.get('delta',{}).get('content') or '' for e in events for c in e['event'].get('choices',[]))==record['output']
  assert any(e['event'].get('system_fingerprint')=='b10852-050dde50c' for e in events)
  record.update(index=index,context=context,verbose_logging=verbose,model_sha256=spec['sha256'],output_sha256=hashlib.sha256(record['output'].encode()).hexdigest(),peak_rss_bytes=max(s['process_rss_bytes'] for s in samples),peak_swap_bytes=max(s['swap_used_bytes'] for s in samples),runtime_log_bytes=(folder/'runtime.log').stat().st_size,full_gpu_offload=True if full_offload else None,placement_note='Verified from runtime' if full_offload else 'All layers requested with fit off; quiet runtime omits independent placement receipt. Diagnostic only.',request_sha256=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest())
  (folder/'result.json').write_text(json.dumps(record,indent=2)+'\n');(folder/'output.md').write_text(record['output']+'\n')
  with (folder/'memory.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=samples[0]);w.writeheader();w.writerows(samples)
  (folder/'offload.txt').write_text('\n'.join(line for line in raw.splitlines() if re.search(r'offloaded |buffer size|recommendedMaxWorkingSetSize|n_ctx\s+=|memory breakdown',line))+'\n')
  results.append(record);(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
  print(index,context,verbose,record['timings'],flush=True)
 receipt={'model':spec,'request':'Exact previously validated H1-summary payload, no gold sent','request_source':'results/2026-09-10/m4-max/history/qwen3-8b/H1-summary-request.json','sequence':[(r['context'],r['verbose_logging']) for r in results],'purpose':'Explore allocated context and verbose-logging effects on one fixed source prompt after the earlier battery. Five sequential fresh-server observations with no prompt cache hits, not repeated full batteries or an isolated thermal test. All original measurements remain unchanged.','downloads_continued':True}
 (out/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':
 with gpu_lock(ROOT):main()
