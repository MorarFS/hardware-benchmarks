"""Durable generation runner for the unchanged history-v2.0 suite.
Gold files are hashed for integrity only. Request builders cannot access their content.
Requires the preinstalled benchmark engine, LM Studio SDK, and installed weights.
"""
import pathlib,json,time,subprocess,fcntl,hashlib,signal,urllib.request,urllib.error,importlib.util,traceback,os,sys
R=pathlib.Path(__file__).resolve().parent
S=R/'accuracy-v2-suite';O=R/'accuracy-v2-results';O.mkdir(exist_ok=True)
s=importlib.util.spec_from_file_location('f',R/'followup_controller.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
B=f.b;API='http://127.0.0.1:1234';UNIT='evo-vulkan-model-matrix.service';RESUME='evo-vulkan-model-matrix-resume.service'
def save(p,d):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def state(st,**kw):
 d=dict(time=B.now(),state=st,**kw);save(O/'status.json',d);print(json.dumps(d),flush=True)
def digest(p):
 with p.open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def verify_suite():
 freeze=json.loads((S/'freeze.json').read_text())
 for name,sha in freeze['files'].items():
  assert digest(S/name)==sha,'Frozen fixture mismatch: '+name
 return freeze
FREEZE=verify_suite();CFG=json.loads((S/'configurations.json').read_text());P=json.loads((S/'prompts.json').read_text());Q=json.loads((S/'questions.json').read_text());D=json.loads((S/'development-questions.json').read_text())
STAGES=['development-extraction','development-summary']+[h['id']+'-'+k for h in Q for k in ['extraction','summary']]+['merged-summary-synthesis','full-source-control']
NOTE={'frozen_suite_version':FREEZE['version'],'frozen_files_unchanged':True,'seed_requested':CFG['seed'],'seed_actual':'CLI has no seed option; actual SDK seed is recorded after load, not claimed fixed at 42. No sampler or question tuning follows outputs.','eval_batch_size':'Actual native load configuration recorded; not controlled by CLI.','evaluator':'Codex/AI-assisted source adjudication, not independent human adjudication. Automated checks do not certify factual accuracy.','development':'Two frozen refined-prompt probes. No extra baseline prompt invented outside the freeze.','timeouts':'900 seconds per request, no automatic cap retry; errors checkpointed.','gold_exclusion':'Gold files are read as binary for SHA256 verification only. Their text is never parsed or used by request builders.'}
save(O/'operational-method-note.json',NOTE)
save(O/'queue.json',dict(created=B.now(),models=CFG['models'],stages=STAGES,requests_per_model=len(STAGES),dependency_units=[UNIT,RESUME],required_speed_completion='All 12 per-model complete.json or error.json records plus top-level complete.json',lock=str(R/'benchmark.lock'),fixture_freeze=FREEZE,configuration=CFG,operational_note=NOTE))
def idle_bounded(seconds=180):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  rows=f.snapshot()
  if all(x.get('status')=='idle' and not x.get('queued',0) for x in rows):return
  time.sleep(5)
 raise TimeoutError('LM Studio remained busy; no concurrent request launched')
def rocm_pause():
 was=f.active('evo-rocm-server.service')
 if not was:return False
 key=(R/'integration/<PRIVATE_API_KEY_FILE>').read_text().strip()
 end=time.monotonic()+600
 while time.monotonic()<end:
  req=urllib.request.Request('http://127.0.0.1:1235/slots',headers={'Authorization':'Bearer '+key})
  with urllib.request.urlopen(req,timeout=5) as res:slots=json.load(res)
  if not any(x.get('is_processing') for x in slots):
   subprocess.run(['systemctl','--user','stop','evo-rocm-server.service'],check=True);return True
  state('waiting_for_rocm_user_request');time.sleep(5)
 raise TimeoutError('Optional ROCm server remained busy; not interrupted')
def deadline(signum,frame):raise TimeoutError('900-second request deadline')
def stream(payload,path):
 start=time.perf_counter();timing={};result=None
 signal.signal(signal.SIGALRM,deadline);signal.alarm(CFG['request_policy']['timeout_seconds'])
 try:
  req=urllib.request.Request(API+'/api/v1/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=90) as response,path.open('w') as log:
   for line in response:
    if not line.startswith(b'data:'):continue
    event=json.loads(line[5:]);elapsed=time.perf_counter()-start
    log.write(json.dumps(dict(elapsed_seconds=elapsed,event=event))+'\n');log.flush()
    typ=event.get('type')
    if typ=='message.delta' and event.get('content'):
     timing.setdefault('first_visible_seconds',elapsed);timing['last_visible_delta_seconds']=elapsed
    if typ=='reasoning.delta' and event.get('content'):timing.setdefault('first_reasoning_seconds',elapsed)
    if typ in ['prompt_processing.start','prompt_processing.end','message.end','reasoning.end']:timing.setdefault(typ,elapsed)
    if typ=='error':raise RuntimeError('Native stream error: '+json.dumps(event))
    if typ=='chat.end':result=event.get('result');break
  if result is None:raise RuntimeError('Stream ended without aggregated result')
  return result,timing,time.perf_counter()-start
 finally:signal.alarm(0)
def request(model,m,folder,name,prompt,source_files,parents=None):
 budget=CFG['request_policy']['reasoning_output_budget' if m.get('template_reasoning') else 'reasoning_off_output_budget']
 payload=dict(model='evo-accuracy-'+m['id'],input=prompt,system_prompt=P['system'],stream=True,store=False,context_length=CFG['context'],max_output_tokens=budget,**m['sampling'])
 if m.get('reasoning') is not None:payload['reasoning']=m['reasoning']
 assert all(not x.startswith('gold/') for x in source_files)
 fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest();out=folder/(name+'.json')
 if out.exists():
  old=json.loads(out.read_text());assert old['fingerprint']==fingerprint,'Checkpoint input changed'
  return old
 save(folder/(name+'-request.json'),payload)
 rec=dict(name=name,model=m['id'],fingerprint=fingerprint,started_at=B.now(),source_files=source_files,parent_requests=parents or [],gold_in_payload=False,quality='Unadjudicated',output_budget=budget)
 state('request',model=m['id'],request=name)
 try:
  idle_bounded()
  rendered=model.apply_prompt_template({'messages':[{'role':'system','content':P['system']},{'role':'user','content':prompt}]})
  rec['preflight_input_tokens']=len(model.tokenize(rendered))
  assert rec['preflight_input_tokens']+budget+256<CFG['context'],'Context budget exceeded'
  with B.Monitor(folder/(name+'-telemetry.jsonl')) as mon:result,timing,wall=stream(payload,folder/(name+'-stream.jsonl'))
  text='\n\n'.join(x.get('content','') for x in result.get('output',[]) if x.get('type')=='message');stats=result.get('stats',{});total=stats.get('total_output_tokens',0);reason=stats.get('reasoning_output_tokens',0)
  literal=len(model.tokenize(text));first=timing.get('first_visible_seconds');capped=total>=budget
  rec.update(status='capped' if capped else 'ok' if text.strip() else 'empty',response=result,output=text,stats=stats,wall_seconds=wall,stream_timing=timing,first_visible_token_seconds=first,visible_text_tokens=literal,visible_tokens_per_total_wall_second=literal/wall,visible_phase_tokens_per_second=literal/(wall-first) if first is not None and wall>first else None,reasoning_tokens=reason,reasoning_observed=reason>0,output_limit_reached=capped,peak_metrics=mon.peaks(),word_count=len(text.split()))
  (folder/(name+'.md')).write_text(text+'\n')
 except Exception as e:
  rec.update(status='error',error=str(e),traceback=traceback.format_exc())
  if isinstance(e,urllib.error.HTTPError):rec['http_error_body']=e.read().decode(errors='replace')
 rec['finished_at']=B.now();save(out,rec);progress();return rec

def progress():
 rows=[]
 for m in CFG['models']:
  for name in STAGES:
   p=O/m['id']/(name+'.json')
   if p.exists():
    d=json.loads(p.read_text());rows.append({k:d.get(k) for k in ['model','name','status','wall_seconds','first_visible_token_seconds','visible_phase_tokens_per_second','reasoning_tokens','word_count']})
 save(O/'metrics.json',rows)
def fmtq(q):return '\n'.join(x['id']+': '+x['question'] for x in q)
def run_model(m):
 import lmstudio as lms,psutil
 folder=O/m['id'];folder.mkdir(exist_ok=True)
 if (folder/'complete.json').exists():return
 ident='evo-accuracy-'+m['id'];client=None
 try:
  idle_bounded();B.unload_ours(dict(models=[{'identifier':'evo-accuracy-'+x['id']} for x in CFG['models']]))
  file=pathlib.Path.home()/'.lmstudio/models'/m['resource'];state('hashing_installed_model',model=m['id'])
  sha=digest(file);save(folder/'model-file.json',dict(file=m['resource'],bytes=file.stat().st_size,sha256=sha));assert sha==m['sha256'],'Model hash mismatch'
  runtime=B.command([B.LMS,'runtime','select','llama.cpp-linux-x86_64-vulkan-avx2@2.33.0']);save(folder/'runtime-selection.json',runtime);assert runtime['returncode']==0
  indexed=json.loads(B.command([B.LMS,'ls','--json'])['output']);key=next(x['modelKey'] for x in indexed if x.get('path')==m['resource'])
  cmd=[B.LMS,'load',key,'--identifier',ident,'--gpu','max','--context-length',str(CFG['context']),'--parallel','1','--ttl','7200','-y']
  cmd+=['--speculative-draft-mtp','--speculative-draft-max-tokens','3'] if m['mtp'] else ['--no-speculative-draft-mtp']
  state('loading',model=m['id']);load=B.command(cmd,900);save(folder/'load.json',load);assert load['returncode']==0,'Model load failed'
  client=lms.Client('127.0.0.1:1234');client.__enter__();model=client.llm.model(ident)
  actual=next(i for x in B.loaded() for i in x.get('loaded_instances',[]) if i['id']==ident);sdk=model.get_load_config().to_dict()
  libraries=[]
  for p in psutil.process_iter(['name']):
   if p.info['name']=='llama-server':
    try:libraries+=sorted({x.path for x in p.memory_maps() if 'libggml-' in x.path})
    except (psutil.AccessDenied,psutil.NoSuchProcess):pass
  save(folder/'actual-load-config.json',dict(native=actual,sdk=sdk,libraries=libraries,seed_requested=42,seed_actual=sdk.get('seed'),seed_fixed_42_verified=sdk.get('seed')==42))
  a=actual['config'];assert a['context_length']==CFG['context'] and a['flash_attention'] and a['offload_kv_cache_to_gpu'];assert bool(a.get('speculative_draft_mtp'))==m['mtp'];assert sdk['gpu']['ratio']==1.0
  assert a['parallel']==1
  assert sdk.get('llamaKCacheQuantizationType')=='f16' and sdk.get('llamaVCacheQuantizationType')=='f16','F16 KV cache not explicitly verified'
  assert any('libggml-vulkan' in x for x in libraries) and not any('libggml-hip' in x for x in libraries),'Vulkan placement not verified'
  if m.get('template_reasoning'):
   template=model.apply_prompt_template({'messages':[{'role':'user','content':'Template verification.'}]});save(folder/'template-check.json',dict(rendered=template,medium_verified='Reasoning: medium' in template));assert 'Reasoning: medium' in template
  dev=(S/'inputs/development.txt').read_text()
  request(model,m,folder,'development-extraction',P['extraction'].format(questions=fmtq(D),source=dev),['prompts.json','development-questions.json','inputs/development.txt'])
  request(model,m,folder,'development-summary',P['summary'].format(source=dev),['prompts.json','inputs/development.txt'])
  summaries=[];sources=[]
  for h in Q:
   source=(S/h['source_file']).read_text();sources.append(source)
   request(model,m,folder,h['id']+'-extraction',P['extraction'].format(questions=fmtq(h['questions']),source=source),['prompts.json','questions.json',h['source_file']])
   summaries.append(request(model,m,folder,h['id']+'-summary',P['summary'].format(source=source),['prompts.json',h['source_file']]))
  parents=[h['id']+'-summary' for h in Q]
  if all(x['status']=='ok' for x in summaries):
   material='\n\n'.join(h['id']+'\n'+x['output'] for h,x in zip(Q,summaries))
   request(model,m,folder,'merged-summary-synthesis',P['synthesis'].format(source=material),['prompts.json'],parents)
  else:
   save(folder/'merged-summary-synthesis.json',dict(model=m['id'],name='merged-summary-synthesis',status='blocked_by_parent',fingerprint='not-issued',parents=parents,reason='At least one direct summary failed, was empty, or reached its cap. No silent substitution.'))
  request(model,m,folder,'full-source-control',P['synthesis'].format(source='\n\n'.join(sources)),['prompts.json']+[h['source_file'] for h in Q])
  save(folder/'complete.json',dict(time=B.now(),meaning='All planned stages reached a terminal record; inspect request statuses, not an accuracy pass.'));progress()
 except Exception as e:
  save(folder/'error.json',dict(time=B.now(),error=str(e),traceback=traceback.format_exc()));state('model_failed_continuing',model=m['id'],error=str(e))
 finally:
  if client:
   try:client.__exit__(None,None,None)
   except Exception:pass
  try:idle_bounded();B.command([B.LMS,'unload',ident],180)
  except Exception as e:save(folder/'cleanup-error.json',dict(error=str(e)))
def speed_terminal():
 root=R/'vulkan-model-matrix'
 if not (root/'complete.json').exists():return False,'Speed service stopped without top-level completion'
 queue=json.loads((root/'queue.json').read_text())['models']
 missing=[x['id'] for x in queue if not any((root/x['id']/n).exists() for n in ['complete.json','error.json'])]
 if len(queue)!=12 or missing:return False,'Missing terminal model records: '+repr(missing)
 save(O/'speed-completion-verified.json',dict(time=B.now(),completion=json.loads((root/'complete.json').read_text()),models=[x['id'] for x in queue],record_hashes={x['id']:{n:digest(root/x['id']/n) for n in ['complete.json','error.json'] if (root/x['id']/n).exists()} for x in queue}))
 return True,''
def main():
 if (O/'complete.json').exists():return
 state('waiting_for_speed',dependency_units=[UNIT,RESUME],models=[m['id'] for m in CFG['models']],stages=STAGES)
 while f.active(UNIT) or f.active(RESUME):time.sleep(10)
 ok,reason=speed_terminal()
 if not ok:
  state('blocked_abnormal_speed_termination',reason=reason);save(O/'blocked.json',dict(time=B.now(),reason=reason));return
 state('waiting_for_benchmark_lock')
 with (R/'benchmark.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  if f.active(UNIT) or f.active(RESUME):raise RuntimeError('Speed job restarted; refusing overlap')
  ok,reason=speed_terminal();assert ok,reason
  verify_suite();paused=False
  try:
   paused=rocm_pause()
   for m in CFG['models']:run_model(m)
  finally:
   state('restoring_browser_availability')
   try:
    idle_bounded();B.unload_ours(dict(models=[{'identifier':'evo-accuracy-'+x['id']} for x in CFG['models']]));f.restore()
   finally:
    B.command([B.LMS,'runtime','select','llama.cpp-linux-x86_64-vulkan-avx2@2.33.0'])
    if paused:subprocess.run(['systemctl','--user','start','evo-rocm-server.service'],check=False)
  progress();save(O/'complete.json',dict(time=B.now(),models={m['id']:'complete' if (O/m['id']/'complete.json').exists() else 'error' for m in CFG['models']},quality='Generation terminal; source adjudication pending'));state('generation_complete_source_audit_pending')
if __name__=='__main__':
 if '--preflight-only' in sys.argv:
  assert len(Q)==4 and sum(len(h['questions']) for h in Q)==20 and len(STAGES)==12
  for h in Q:
   assert h['source_file'].startswith('inputs/')
   source=(S/h['source_file']).read_text()
   assert P['extraction'].format(questions=fmtq(h['questions']),source=source)
   assert P['summary'].format(source=source)
  assert P['synthesis'].format(source='Dry-run material')
  save(O/'preflight.json',dict(time=B.now(),status='passed',frozen_checksums_verified=True,models=len(CFG['models']),stages_per_model=len(STAGES),fixed_questions=20,heldout_passages=4,no_model_loaded=True,no_generation=True,request_inputs_allowlist=['prompts.json','questions.json','development-questions.json','inputs/*.txt','prior direct-summary outputs for merged stage only']))
  print('Preflight passed: unchanged frozen suite; three models; 12 stages each; no GPU operation.');sys.exit(0)
 try:main()
 except Exception as e:save(O/'fatal-error.json',dict(time=B.now(),error=str(e),traceback=traceback.format_exc()));state('fatal_error',error=str(e));raise
