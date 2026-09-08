import json,time,urllib.request,urllib.error,hashlib,shutil,pathlib
import engine as b
API="http://127.0.0.1:1234"
def write(p,d):b.save(p,d)
def status(state,**kw):b.status(state,**kw)
def stream_once(payload,path):
 req=urllib.request.Request(API+"/api/v1/chat",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
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
