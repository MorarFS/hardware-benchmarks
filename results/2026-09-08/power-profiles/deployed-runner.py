"""Finite supported power-profile comparison; standalone pinned Vulkan, installed files only."""
from pathlib import Path
import json,time,subprocess,os,hashlib,fcntl,urllib.request,urllib.error,threading,traceback,signal,importlib.util
R=Path(__file__).resolve().parent
O=R/'power-profile-comparison'; O.mkdir(exist_ok=True)
B=R/'upstream-b10852/vulkan/llama-b10852'
s=importlib.util.spec_from_file_location('f',R/'followup_controller.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
MODELS=[('qwen8','Qwen/Qwen3-8B-GGUF/Qwen3-8B-Q4_K_M.gguf','d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785'),('gemma26','unsloth/gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-Q4_K_M.gguf','f2c28b3dc4776931ac6f879e11f203dec637ea0f14267a86ec8f6165f63f293f')]
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def state(x,**kw):
 d=dict(state=x,time=f.b.now(),**kw);save(O/'status.json',d);print(json.dumps(d),flush=True)
def run(a,**kw):return subprocess.run(a,capture_output=True,text=True,timeout=60,**kw)
def power():
 d={'time':f.b.now(),'monotonic':time.monotonic()}
 for p in Path('/sys/class/hwmon').glob('hwmon*'):
  try:name=(p/'name').read_text().strip()
  except OSError:continue
  for q in p.iterdir():
   if q.name.startswith(('temp','power','energy','freq')) and q.name.endswith(('_input','_average','_label','_cap')):
    try:d[name+'/'+q.name]=q.read_text().strip()
    except OSError:pass
 for p in [Path('/sys/devices/system/cpu/cpu0/cpufreq')/n for n in ['scaling_governor','energy_performance_preference','scaling_min_freq','scaling_max_freq']]:
  try:d[p.name]=p.read_text().strip()
  except OSError:pass
 return d
class Power:
 def __init__(self,p):self.p=p;self.stop=threading.Event()
 def __enter__(self):
  def collect():
   with self.p.open('w') as z:
    while not self.stop.is_set():
     z.write(json.dumps(power())+'\n');z.flush();self.stop.wait(1)
  self.t=threading.Thread(target=collect);self.t.start();return self
 def __exit__(self,*args):self.stop.set();self.t.join()
def post(path,payload):
 req=urllib.request.Request('http://127.0.0.1:1236'+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as z:return json.load(z)
def terminate(proc):
 if proc and proc.poll() is None:
  os.killpg(proc.pid,signal.SIGTERM)
  try:proc.wait(timeout=15)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
def rocm_idle():
 key=(R/'integration/<PRIVATE_API_KEY_FILE>').read_text().strip()
 for _ in range(12):
  try:
   req=urllib.request.Request('http://127.0.0.1:1235/slots',headers={'Authorization':'Bearer '+key})
   with urllib.request.urlopen(req,timeout=3) as z:slots=json.load(z)
   if not any(x.get('is_processing') for x in slots):return
  except urllib.error.URLError:pass
  time.sleep(5)
 raise RuntimeError('Optional serving route not verified idle; no interruption')
def synthetic(folder,model,depth):
 args=[str(B/'llama-bench'),'-m',str(model),'-dev','Vulkan0','-sm','none','-ngl','99','-fa','on','-b','512','-ub','512','-t','10','-ctk','f16','-ctv','f16','-p','512' if depth==0 else '0','-n','256','-d',str(depth),'-r','5','-o','json','--progress','-v']
 stem=folder/f'depth{depth}';save(stem.with_suffix('.command.json'),args);t=time.perf_counter();proc=None
 try:
  with stem.with_suffix('.json').open('w') as out,stem.with_suffix('.log').open('w') as err,Power(folder/f'depth{depth}-power.jsonl'),f.b.Monitor(folder/f'depth{depth}-memory.jsonl') as mon:
   proc=subprocess.Popen(args,stdout=out,stderr=err,env={**os.environ,'LD_LIBRARY_PATH':str(B)},start_new_session=True)
   code=proc.wait(timeout=900)
  save(stem.with_suffix('.execution.json'),dict(returncode=code,wall_seconds=time.perf_counter()-t,peak_memory=mon.peaks()))
  if code:raise RuntimeError('Synthetic process failed')
  data=json.loads(stem.with_suffix('.json').read_text())
  assert all(x['backends']=='Vulkan' and x['n_gpu_layers']==99 and len(x['samples_ts'])==5 for x in data)
 finally:terminate(proc)
def prose(folder,model):
 args=[str(B/'llama-server'),'-m',str(model),'-dev','Vulkan0','-sm','none','-ngl','99','-fa','on','-b','512','-ub','512','-t','10','-ctk','f16','-ctv','f16','-c','8192','-np','1','--host','127.0.0.1','--port','1236','--reasoning','off','--no-webui']
 save(folder/'prose-server-command.json',args)
 proc=None;t=time.perf_counter()
 with (folder/'prose-server.log').open('w') as log:
  try:
   proc=subprocess.Popen(args,stdout=log,stderr=log,env={**os.environ,'LD_LIBRARY_PATH':str(B)},start_new_session=True)
   for _ in range(180):
    if proc.poll() is not None:raise RuntimeError('Prose server exited')
    try:
     with urllib.request.urlopen('http://127.0.0.1:1236/health',timeout=2) as z:
      if z.status==200:break
    except urllib.error.URLError:pass
    time.sleep(1)
   else:raise TimeoutError('Prose server load exceeded 180 seconds')
   save(folder/'prose-load.json',dict(wall_to_ready_seconds=time.perf_counter()-t,profile=run(['powerprofilesctl','get']).stdout.strip()))
   source=(R/'accuracy-v2-suite/inputs/H1.txt').read_text()
   prompt='Write a connected summary of 180–220 words using only the following passage. Cover its beginning, middle, and ending. Preserve qualifications. Attribute the author’s evaluations. Cite physical PDF pages. Write readable prose without em dashes.\n\nSOURCE:\n'+source
   for trial in [1,2]:
    payload=dict(messages=[{'role':'user','content':prompt}],stream=True,stream_options={'include_usage':True},max_tokens=1024,temperature=0.0,top_k=20,top_p=1.0,min_p=0.0,repeat_penalty=1.0,seed=42,cache_prompt=False)
    save(folder/f'prose-{trial}-request.json',payload);tt=time.perf_counter();first=None;content='';reason='';final=None;finish=None
    req=urllib.request.Request('http://127.0.0.1:1236/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with Power(folder/f'prose-{trial}-power.jsonl'),f.b.Monitor(folder/f'prose-{trial}-memory.jsonl') as mon,urllib.request.urlopen(req,timeout=180) as z,(folder/f'prose-{trial}-stream.jsonl').open('w') as out:
     for line in z:
      if time.perf_counter()-tt>240:raise TimeoutError('Bounded prose request exceeded 240 seconds')
      if not line.startswith(b'data:'):continue
      if line[5:].strip()==b'[DONE]':break
      e=json.loads(line[5:]);elapsed=time.perf_counter()-tt;out.write(json.dumps(dict(elapsed_seconds=elapsed,event=e))+'\n');out.flush()
      final=e
      for c in e.get('choices',[]):
       delta=c.get('delta',{});chunk=delta.get('content') or '';reason+=delta.get('reasoning_content') or ''
       if chunk and first is None:first=elapsed
       content+=chunk
       if c.get('finish_reason'):finish=c['finish_reason']
    wall=time.perf_counter()-tt;tokens=len(post('/tokenize',dict(content=content,add_special=False))['tokens'])
    row=dict(trial=trial,wall_seconds=wall,first_visible_seconds=first,visible_tokens=tokens,visible_phase_tps=tokens/(wall-first) if first else None,visible_total_wall_tps=tokens/wall,finish_reason=finish,output_limit_reached=finish=='length',reasoning_text=reason,output=content,last_event=final,peak_memory=mon.peaks(),quality='Pending readable/source check; not a new accuracy benchmark')
    save(folder/f'prose-{trial}.json',row);(folder/f'prose-{trial}.md').write_text(content+'\n')
  finally:terminate(proc)
def main():
 if (O/'complete.json').exists():state('already_terminal');return
 errors=[];prior=run(['powerprofilesctl','get']).stdout.strip()
 assert prior in ['balanced','performance','power-saver']
 save(O/'protocol.json',dict(started=f.b.now(),original_profile=prior,available_profiles=run(['powerprofilesctl','list']).stdout,models=MODELS,synthetic='Pinned b10852/050dde50c Vulkan, pp512, tg256 depths0/2048, five reps, default warmup, F16 cache, batch512, threads10, full GPU, speculation off',prose='Two H1 summaries per model/profile, own pinned server, context8192 parallel1 reasoningoff seed42 greedy, cache_prompt false, max1024',order='qwen8 balanced, qwen8 performance, gemma26 balanced, gemma26 performance; fixed order, no randomized thermal crossover',cache='No OS cache flush. Synthetic warmup default. Prose first and second separately retained.',power_note='Sysfs sensors overlap on this APU; no additive CPU/GPU or UMA memory totals. No wall meter.',restore='Original supported profile and previously idle serving models; no system-driver/BIOS changes'))
 with (R/'benchmark.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  assert not f.active('evo-accuracy-v2.service') and (R/'accuracy-v2-results/complete.json').exists()
  assert not f.active('evo-vulkan-model-matrix.service')
  idle=f.snapshot();assert all(x.get('status')=='idle' and not x.get('queued',0) for x in idle)
  assert all(x.get('identifier')=='gemma-4-e4b-uncensored-hauhaucs-aggressive' or x.get('identifier','').startswith('evo-') for x in idle),'Unrelated idle model; no interruption'
  rocm_active=f.active('evo-rocm-server.service');paused=False
  try:
   if rocm_active:rocm_idle();subprocess.run(['systemctl','--user','stop','evo-rocm-server.service'],check=True);paused=True
   f.b.unload_ours(dict(models=[{'identifier':x['identifier']} for x in idle]))
   for name,relative,expected in MODELS:
    model=Path.home()/'.lmstudio/models'/relative
    with model.open('rb') as z:sha=hashlib.file_digest(z,'sha256').hexdigest()
    assert sha==expected
    for profile in ['balanced','performance']:
     folder=O/name/profile;folder.mkdir(parents=True,exist_ok=True)
     try:
      state('setting_profile',model=name,profile=profile)
      rr=run(['powerprofilesctl','set',profile]);save(folder/'profile-set.json',dict(returncode=rr.returncode,stdout=rr.stdout,stderr=rr.stderr))
      if rr.returncode:raise RuntimeError('Supported profile could not be selected')
      actual=run(['powerprofilesctl','get']).stdout.strip();assert actual==profile
      save(folder/'configuration.json',dict(model_file=model.name,model_sha256=sha,bytes=model.stat().st_size,profile=actual,before=power()))
      for depth in [0,2048]:
       state('synthetic',model=name,profile=profile,depth=depth);synthetic(folder,model,depth)
      state('prose',model=name,profile=profile);prose(folder,model)
      save(folder/'complete.json',dict(time=f.b.now(),after=power()))
     except Exception as e:
      error=dict(model=name,profile=profile,error=str(e),traceback=traceback.format_exc());errors.append(error);save(folder/'error.json',error);state('trial_failed',**error)
  finally:
   result=run(['powerprofilesctl','set',prior]);restored=run(['powerprofilesctl','get']).stdout.strip()
   save(O/'profile-restoration.json',dict(requested=prior,actual=restored,returncode=result.returncode,stderr=result.stderr))
   try:f.restore()
   finally:
    if paused:subprocess.run(['systemctl','--user','start','evo-rocm-server.service'],check=False)
   save(O/'complete.json',dict(time=f.b.now(),errors=errors,profile_restored=restored==prior))
   state('complete',errors=len(errors),profile_restored=restored==prior)
if __name__=='__main__':main()
