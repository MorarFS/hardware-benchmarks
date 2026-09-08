#!/usr/bin/env python3
import pathlib,json,time,subprocess,fcntl,sys,urllib.request
R=pathlib.Path(__file__).resolve().parent
LMS='<LM_STUDIO_HOME>/bin/lms'
units=['evo-history-benchmark.service','evo-history-completion.service','evo-history-followups.service']
def active():
 return [u for u in units if subprocess.run(['systemctl','--user','show',u,'-p','ActiveState','--value'],capture_output=True,text=True).stdout.strip() in {'active','activating','reloading','deactivating'}]
def status(state,**kw):
 d=dict(state=state,time=time.time(),**kw);(R/'gemma9-status.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
status('waiting_for_all_measured_runs_to_finish')
lock=open(R/'benchmark.lock','a')
while True:
 while active():time.sleep(15)
 fcntl.flock(lock,fcntl.LOCK_EX)
 if active():fcntl.flock(lock,fcntl.LOCK_UN);time.sleep(15);continue
 try:models=json.loads(subprocess.check_output([LMS,'ps','--json'],text=True,timeout=30))
 except Exception:fcntl.flock(lock,fcntl.LOCK_UN);time.sleep(15);continue
 if any(m.get('status')!='idle' or m.get('queued',0) for m in models):
  fcntl.flock(lock,fcntl.LOCK_UN);status('waiting_for_user_inference');time.sleep(15);continue
 break
status('downloading_gemma2_9b_it_q4_k_m',expected_bytes=5761057728)
ret=subprocess.run([sys.executable,str(R/'gemma9-download/download.py')]).returncode
if ret:status('download_or_checksum_failed',returncode=ret);sys.exit(ret)
entry=json.loads((R/'gemma9-download/downloads-manifest.json').read_text())[0]
expected='13b2a7b4115bbd0900162edcebe476da1ba1fc24e718e8b40d32f6e300f56dfe'
if entry.get('verified_sha256')!=expected:raise RuntimeError('Missing verified Gemma checksum receipt')
target='bartowski/gemma-2-9b-it-GGUF/gemma-2-9b-it-Q4_K_M.gguf'
for attempt in range(30):
 indexed=json.loads(subprocess.check_output([LMS,'ls','--json'],text=True,timeout=30))
 found=[m for m in indexed if m.get('path')==target]
 if found:break
 time.sleep(2)
else:raise RuntimeError('Verified Gemma file not indexed yet')
try:
 available=json.load(urllib.request.urlopen('http://127.0.0.1:1234/v1/models',timeout=30))
 api_ids=[m.get('id') for m in available.get('data',[]) if 'gemma-2-9b' in m.get('id','').lower()]
except Exception as e:api_ids=[];status('indexed_api_check_unavailable',error=str(e))
receipt=dict(state='verified_and_indexed',time=time.time(),file=entry,indexed=found,openai_model_ids=api_ids,inference_test='Not requested; download/install only')
(R/'gemma9.complete').write_text(json.dumps(receipt,indent=2))
status('gemma2_9b_installed',bytes=entry['size'],sha256=expected,openai_model_ids=api_ids)
