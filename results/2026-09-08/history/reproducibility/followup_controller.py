#!/usr/bin/env python3
"""Autonomous, sequential reasoning follow-ups; no dependency on the controlling Mac."""
import pathlib,json,time,sys,subprocess,urllib.request,urllib.error,hashlib,importlib.util,fcntl,os,shutil,concurrent.futures,threading
R=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("followup_engine",R/"followup-engine.py")
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
CFG=json.loads((R/"followup-config.json").read_text())
def write(p,d):b.save(p,d)
def status(state,**kw):
 d=dict(state=state,time=b.now(),**kw);write(R/"followup-status.json",d);print(json.dumps(d),flush=True)
def active(unit):
 return subprocess.run(["systemctl","--user","show",unit,"-p","ActiveState","--value"],capture_output=True,text=True).stdout.strip() in {"active","activating","reloading","deactivating"}
def original_wait():
 status("waiting_for_original_benchmark_and_completion")
 while active("evo-history-benchmark.service") or active("evo-history-completion.service"):time.sleep(15)
def snapshot():
 r=subprocess.run([b.LMS,"ps","--json"],capture_output=True,text=True,timeout=30)
 if r.returncode:raise RuntimeError("Cannot verify model activity")
 return json.loads(r.stdout)
def wait_idle():
 while True:
  try:busy=[x for x in snapshot() if x.get("status")!="idle" or x.get("queued",0)]
  except Exception:busy=[{"identifier":"unverified"}]
  if not busy:return
  status("waiting_for_model_activity",models=[x.get("identifier") for x in busy]);time.sleep(15)
def original_finalization():
 # If Flash exhausted its bounded repair before Qwen's original completion turn,
 # attempt the stale Qwen completion once, then retain failure and continue.
 installed=CFG["installed_at"]
 original=json.loads((R/"config.json").read_text())
 for m in original["models"]:
  folder=R/"runs"/m["identifier"];phase=folder/"phase-book.json"
  d=json.loads(phase.read_text()) if phase.exists() else {}
  done=b.accepted_record(folder,"book-final-summary")
  if done:continue
  if d.get("finished_at","")>=installed:continue
  status("finishing_unattempted_original_completion",model=m["identifier"])
  cfg=folder/"single-model-config.json"
  ret=subprocess.run([sys.executable,str(R/"benchmark.py"),"run","--config",str(cfg),"--book"]).returncode
  write(folder/"autonomous-original-completion-attempt.json",dict(returncode=ret,time=b.now()))
def stream_once(payload,path):
 req=urllib.request.Request("http://127.0.0.1:1234/api/v1/chat",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
 timing={};result=None;errors=[];t=time.perf_counter()
 with urllib.request.urlopen(req,timeout=180) as response,path.open("w") as log:
  for line in response:
   if time.perf_counter()-t>1800:raise TimeoutError("Bounded 30-minute request limit")
   if not line.startswith(b"data:"):continue
   event=json.loads(line[5:].decode());elapsed=time.perf_counter()-t
   log.write(json.dumps({"elapsed_seconds":elapsed,"event":event})+"\n");log.flush()
   typ=event.get("type")
   if typ=="message.delta" and event.get("content"):
    timing.setdefault("first_visible_seconds",elapsed);timing["last_visible_delta_seconds"]=elapsed
   if typ=="reasoning.delta" and event.get("content"):timing.setdefault("first_reasoning_seconds",elapsed)
   if typ in ("prompt_processing.start","prompt_processing.end","message.end","reasoning.end"):timing.setdefault(typ,elapsed)
   if typ=="error":errors.append(event)
   if typ=="chat.end":result=event.get("result");break
 wall=time.perf_counter()-t
 if not result:raise RuntimeError("Stream ended without aggregated result")
 if errors:raise RuntimeError("Native stream error: "+json.dumps(errors))
 return result,timing,wall
def request(model,m,folder,name,prompt,limit,kind,extra=None,retry_depth=0):
 initial=max(12288 if kind=="final_synthesis" else 8192,limit*4)
 ceiling=min(initial*(2**retry_depth),m["context"]-b.count(model,prompt)-256)
 if ceiling<4096:raise RuntimeError("Insufficient room for the reasoning budget")
 rendered,system=b.rendered(prompt)
 payload=dict(model=m["identifier"],input=rendered,system_prompt=system or b.STYLE,stream=True,
  max_output_tokens=ceiling,context_length=m["context"],store=False,**m["sampling"])
 if m.get("reasoning") is not None:payload["reasoning"]=m["reasoning"]
 fingerprint=hashlib.sha256(json.dumps({"payload":payload,"profile":m},sort_keys=True).encode()).hexdigest()
 path=folder/(name+".json")
 if path.exists():
  old=json.loads(path.read_text())
  if old.get("fingerprint")==fingerprint:
   if old.get("status")=="ok" and not old.get("output_limit_reached"):return old
   if old.get("output_limit_reached"):
    if retry_depth>=1:raise RuntimeError("Reasoning/output ceiling reached after bounded retry")
    r=request(model,m,folder,name+"-completion-retry",prompt,limit,kind,extra,retry_depth+1)
    old["superseded_by"]=r["name"];write(path,old);return r
  else:
   archive=folder/"superseded";archive.mkdir(exist_ok=True)
   for p in [path,folder/(name+".md"),folder/(name+"-request.json"),folder/(name+"-stream.jsonl")]:
    if p.exists():shutil.copy2(p,archive/(p.stem+"-"+str(time.time_ns())+p.suffix))
 write(folder/(name+"-request.json"),payload)
 status("reasoning_request",model=m["identifier"],request=name,total_output_budget=ceiling)
 record=dict(model=m["identifier"],name=name,kind=kind,started_at=b.now(),fingerprint=fingerprint,
   preflight_input_tokens=b.count(model,prompt),context=m["context"],output_limit=ceiling,metadata=extra or {},
   settings=m,quality="Unreviewed",timing_note="SSE times measured on Evo loopback; visible phase includes final response overhead.")
 try:
  with b.Monitor(folder/(name+"-telemetry-0.jsonl")) as mon:
   result,timing,wall=stream_once(payload,folder/(name+"-stream.jsonl"))
  text="\n\n".join(x.get("content","") for x in result.get("output",[]) if x.get("type")=="message")
  stats=result.get("stats",{});total=stats.get("total_output_tokens",0);reason=stats.get("reasoning_output_tokens",0)
  literal=len(model.tokenize(text));first=timing.get("first_visible_seconds")
  record.update(status="ok",finished_at=b.now(),output=text,response=result,stats=stats,wall_seconds=wall,
   output_tokens_per_wall_second=total/wall,peak_metrics=mon.peaks(),output_limit_reached=total>=ceiling,
   actual_context_verified=stats.get("input_tokens",m["context"])+total<=m["context"],
   reasoning_observed=reason>0 and "first_reasoning_seconds" in timing,
   visible_output_tokens_api_difference=total-reason,visible_text_tokens=literal,
   visible_tokens_per_total_wall_second=literal/wall,
   visible_phase_tokens_per_second=literal/(wall-first) if first is not None and wall>first else None,
   first_visible_token_seconds=first,stream_timing=timing)
  write(path,record);(folder/(name+".md")).write_text(text+"\n")
  if record["output_limit_reached"]:
   if retry_depth>=1:raise RuntimeError("Reasoning/output ceiling reached after bounded retry")
   r=request(model,m,folder,name+"-completion-retry",prompt,limit,kind,extra,retry_depth+1)
   record["superseded_by"]=r["name"];write(path,record);return r
  if not text.strip():raise RuntimeError("No visible answer")
  if not record["actual_context_verified"]:raise RuntimeError("Actual context invariant failed")
  return record
 except Exception as e:
  if isinstance(e,urllib.error.HTTPError):record["http_error_body"]=e.read().decode("utf-8",errors="replace")
  record.update(status="error",error=str(e),finished_at=b.now());write(path,record);raise
b.request=request
def run_model(m):
 folder=R/"runs"/m["identifier"];folder.mkdir(parents=True,exist_ok=True)
 receipt=folder/"followup.complete"
 fp=hashlib.sha256(json.dumps(m,sort_keys=True).encode()+(R/"source/pages.json").read_bytes()).hexdigest()
 if receipt.exists() and json.loads(receipt.read_text()).get("fingerprint")==fp:return
 errors=[];started=b.now();t=time.perf_counter()
 try:
  wait_idle();model,folder=b.load_model(m,dict(CFG,models=[m]))
  if m["identifier"]=="evo-gptoss120-thinking":
   rendered=model.apply_prompt_template({"messages":[{"role":"user","content":"Template verification."}]})
   write(folder/"rendered-template-check.json",dict(rendered=rendered,medium_verified="Reasoning: medium" in rendered,time=b.now()))
   if "Reasoning: medium" not in rendered:raise RuntimeError("GPT template default medium not verified")
  write(folder/"profile.json",m)
  # Same book and prompts, sufficient bounded thinking budgets, all eight groups.
  # Every output remains explicitly unreviewed; no automatic fidelity pass.
  b.book(model,m,folder,R/"source")
  write(receipt,dict(fingerprint=fp,finished_at=b.now(),state="inference_complete_needs_source_audit"))
 except Exception as e:
  errors.append(str(e));status("followup_model_failed",model=m["identifier"],error=str(e))
 finally:
  b.command([b.LMS,"unload",m["identifier"]])
  p=folder/"phase-book.json"
  if p.exists():p.rename(folder/("phase-book-previous-"+str(time.time_ns())+".json"))
  write(p,dict(started_at=started,finished_at=b.now(),end_to_end_wall_seconds=time.perf_counter()-t,
    includes="load, token preflight, streaming inference, bounded retries; excludes downloads and source audit",errors=errors))
 return errors
def download_gpt():
 manifest=json.loads((R/"gptoss-download-manifest.json").read_text());entry=manifest[0]
 dst=pathlib.Path(entry["path"]);dst.parent.mkdir(parents=True,exist_ok=True)
 # No measured follow-up runs execute concurrently. Original services must also be inactive.
 original_wait();wait_idle();status("downloading_gptoss_isolated",bytes=entry["size"])
 # Downloader is a separate pinned copy of the previously verified four-stream implementation.
 ret=subprocess.run([sys.executable,str(R/"gptoss-download"/"download.py")]).returncode
 if ret:raise RuntimeError("GPT-OSS download/checksum failed; retained resumable segments")
 verified=json.loads((R/"gptoss-download"/"downloads-manifest.json").read_text())[0]
 if verified.get("verified_sha256")!=entry["lfs"]["sha256"]:raise RuntimeError("GPT-OSS verification receipt mismatch")
 write(R/"gptoss-download.verified",verified)
 status("gptoss_verified",sha256=verified["verified_sha256"],bytes=verified["size"])
 target=CFG["models"][2]["resource"]
 for attempt in range(30):
  indexed=json.loads(b.command([b.LMS,"ls","--json"])["output"])
  if any(x.get("path")==target for x in indexed):break
  time.sleep(2)
 else:raise RuntimeError("Verified GPT-OSS file not yet indexed by LM Studio")
def restore():
 p=R/"idle-models-unloaded.json"
 if not p.exists():return
 result=[]
 for m in json.loads(p.read_text()):
  wait_idle()
  if any(x.get("identifier")==m["identifier"] for x in snapshot()):continue
  r=b.command([b.LMS,"load",m["modelKey"],"--identifier",m["identifier"],"--context-length",str(m.get("contextLength",8192)),"--parallel","1","--ttl","3600","-y"])
  result.append(dict(model=m["identifier"],returncode=r["returncode"],output=r["output"][-1500:]))
 write(R/"followup-restoration.json",result)
def main():
 lock=open(R/"followup.lock","w");fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 original_wait();original_finalization()
 benchmark_lock=open(R/"benchmark.lock","a");fcntl.flock(benchmark_lock,fcntl.LOCK_EX)
 outcomes=[]
 for m in CFG["models"][:2]:outcomes.append({"model":m["identifier"],"errors":run_model(m) or []})
 try:
  download_gpt();m=CFG["models"][2];outcomes.append({"model":m["identifier"],"errors":run_model(m) or []})
 except Exception as e:outcomes.append({"model":"evo-gptoss120-thinking","errors":[str(e)]});status("gptoss_stage_failed",error=str(e))
 restore()
 subprocess.run([sys.executable,str(R/"prepare_audit.py")])
 subprocess.run([sys.executable,str(R/"aggregate_results.py")],stdout=subprocess.DEVNULL)
 write(R/"followups.complete",dict(time=b.now(),outcomes=outcomes,source_audit="Pending Codex review"))
 status("followup_queue_finished_needs_source_audit",outcomes=outcomes)
if __name__=="__main__":main()
