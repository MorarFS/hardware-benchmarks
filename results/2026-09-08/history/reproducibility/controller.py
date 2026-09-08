#!/usr/bin/env python3
"""Persistent orchestrator. Models remain sequential; each completes controls and book before switching."""
import pathlib,subprocess,time,json,sys,hashlib
R=pathlib.Path(__file__).resolve().parent
def state(x,**kw):(R/"controller-status.json").write_text(json.dumps({"state":x,"time":time.time(),**kw}))
state("verifying_flash")
if not (R/"flash-verification.json").exists():subprocess.run([sys.executable,str(R/"verify_flash.py")],check=True)
state("waiting_for_downloads")
while not (R/"downloads.complete").exists():time.sleep(15)
other=pathlib.Path.home()/"Documents/Codex/2026-09-07/lm-studio-install/work/pipeline-complete.json"
while subprocess.run(["systemctl","--user","is-active","--quiet","codex-model-pipeline.service"]).returncode==0 and not other.exists():
 state("waiting_for_existing_user_model_pipeline");time.sleep(30)
config=json.loads((R/"config.json").read_text())
ordered=sorted(config["models"],key=lambda m:(R/"runs"/m["identifier"]/"book.complete").exists())
for model in ordered:
 ident=model["identifier"];single=dict(config,models=[model])
 folder=R/"runs"/ident;folder.mkdir(parents=True,exist_ok=True)
 cfg=folder/"single-model-config.json";cfg.write_text(json.dumps(single,indent=2))
 for phase in ["controls","book"]:
  receipt=folder/(phase+".complete")
  source=R/config.get("source_directory","source")/"pages.json"
  material=json.dumps(single,sort_keys=True)+phase+hashlib.sha256((R/"benchmark.py").read_bytes()).hexdigest()
  if phase=="book" and source.exists():material+=hashlib.sha256(source.read_bytes()).hexdigest()
  phase_fingerprint=hashlib.sha256(material.encode()).hexdigest()
  if receipt.exists():
   try:
    if json.loads(receipt.read_text()).get("fingerprint")==phase_fingerprint:continue
   except (ValueError,AttributeError):pass
  state("running_"+phase,model=ident)
  args=[sys.executable,str(R/"benchmark.py"),"run","--config",str(cfg)]
  if phase=="book":args+=["--book"]
  ret=subprocess.run(args).returncode
  if ret:state(phase+"_errors_need_review",model=ident);sys.exit(ret)
  st=json.loads((R/"status.json").read_text())
  if phase=="book" and st["state"]!="book_runs_finished_needs_fidelity_review":
   state(st["state"],model=ident);sys.exit(0)
  receipt.write_text(json.dumps({"finished_at":time.time(),"fingerprint":phase_fingerprint}))
(R/"controls.complete").write_text(str(time.time()))
(R/"book.complete").write_text(str(time.time()))
state("book_finished_pending_source_fidelity_review")
p=R/"idle-models-unloaded.json"
if p.exists():
 results=[];lms=str(pathlib.Path.home()/".lmstudio/bin/lms")
 for m in json.loads(p.read_text()):
  snapshot=subprocess.run([lms,"ps","--json"],capture_output=True,text=True)
  try:current=json.loads(snapshot.stdout)
  except ValueError:
   results.append({"model":m["identifier"],"state":"deferred","reason":"Cannot verify current model state"});continue
  if any(x.get("identifier")==m["identifier"] for x in current):
   results.append({"model":m["identifier"],"state":"already_loaded"});continue
  if any(x.get("status")!="idle" or x.get("queued",0) for x in current):
   results.append({"model":m["identifier"],"state":"deferred","reason":"An active user model is running"});continue
  args=[lms,"load",m["modelKey"],"--identifier",m["identifier"],"--context-length",str(m.get("contextLength",8192)),"--parallel",str(m.get("parallel",1)),"--ttl","3600","-y"]
  ret=subprocess.run(args,capture_output=True,text=True)
  results.append({"model":m["identifier"],"returncode":ret.returncode,"output":ret.stdout+ret.stderr})
 previous=R/"idle-models-restored.json"
 if previous.exists():previous.rename(R/("idle-models-restored-previous-"+str(time.time_ns())+".json"))
 previous.write_text(json.dumps(results,indent=2))
