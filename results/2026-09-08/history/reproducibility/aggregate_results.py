#!/usr/bin/env python3
"""Audit-friendly aggregation of actual requests, including archived and capped attempts."""
import pathlib,json,csv,statistics,datetime
R=pathlib.Path(__file__).resolve().parent
OUT=R/"analysis";OUT.mkdir(exist_ok=True)
rows=[];seen=set()
for folder in sorted((R/"runs").glob("*")):
 for p in sorted(folder.rglob("*.json")):
  try:d=json.loads(p.read_text())
  except (ValueError,OSError):continue
  if not isinstance(d,dict) or not all(k in d for k in ("stats","wall_seconds","started_at","name")):continue
  key=(d.get("fingerprint"),d["started_at"])
  if key in seen:continue
  seen.add(key);s=d["stats"];peak=d.get("peak_metrics",{})
  archived="superseded" in p.parts
  lifecycle="archived" if archived else ("superseded" if d.get("superseded_by") else ("capped" if d.get("output_limit_reached") else ("accepted" if d.get("status")=="ok" else "error")))
  row=dict(model=d["model"],request=d["name"],kind=d["kind"],lifecycle=lifecycle,status=d.get("status"),
    started_at=d["started_at"],finished_at=d.get("finished_at"),input_tokens=s.get("input_tokens"),output_tokens=s.get("total_output_tokens"),
    reasoning_tokens=s.get("reasoning_output_tokens"),
    visible_text_tokens=d.get("visible_text_tokens"),
    visible_api_difference=d.get("visible_output_tokens_api_difference"),
    first_visible_token_seconds=d.get("first_visible_token_seconds"),
    visible_phase_tps=d.get("visible_phase_tokens_per_second"),
    visible_per_total_wall_tps=d.get("visible_tokens_per_total_wall_second"),
    reasoning_observed=d.get("reasoning_observed"),
    source_pdf_pages=json.dumps(d.get("metadata",{}).get("pdf_pages",[])),
    generation_tps=s.get("tokens_per_second"),ttft_seconds=s.get("time_to_first_token_seconds"),
    request_wall_seconds=d["wall_seconds"],output_per_wall_tps=d.get("output_tokens_per_wall_second"),
    output_limit=d["output_limit"],capped=d.get("output_limit_reached"),context=d["context"],
    context_verified=d.get("actual_context_verified"),retry_of=d.get("metadata",{}).get("retry_of"),
    system_used_GiB=peak.get("system_used_excluding_available_bytes",0)/2**30,
    swap_GiB=peak.get("swap_used_bytes",0)/2**30,
    largest_runtime_RSS_GiB=peak.get("runtime_largest_process_rss_bytes",0)/2**30,
    runtime_PSS_GiB=peak.get("runtime_total_pss_bytes",0)/2**30,
    GPU_VRAM_GiB=peak.get("card1_vram_used_bytes",0)/2**30,
    GPU_GTT_GiB=peak.get("card1_gtt_used_bytes",0)/2**30,
    max_llama_server_processes=peak.get("llama_server_process_count"),artifact=str(p.relative_to(R)))
  rows.append(row)
# Current files are visited before archived copies; key removes identical execution copies.
if rows:
 with (OUT/"all-requests.csv").open("w") as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
def visible_aggregate(rr):
 measured=[r for r in rr if r.get("visible_text_tokens") is not None]
 if not measured:return None
 tokens=sum(r["visible_text_tokens"] for r in measured)
 wall=sum(r["request_wall_seconds"] for r in measured)
 rates=[r["visible_phase_tps"] for r in measured if r["visible_phase_tps"] is not None]
 durations=[r["request_wall_seconds"]-r["first_visible_token_seconds"] for r in measured if r["first_visible_token_seconds"] is not None]
 first=[r["first_visible_token_seconds"] for r in measured if r["first_visible_token_seconds"] is not None]
 return dict(measured_requests=len(measured),total_requests=len(rr),literal_visible_tokens=tokens,
  native_reasoning_tokens=sum(r["reasoning_tokens"] or 0 for r in measured),
  every_request_showed_reasoning=all(r["reasoning_observed"] for r in measured),
  visible_phase_tps_min=min(rates) if rates else None,visible_phase_tps_max=max(rates) if rates else None,
  visible_phase_tps_aggregate=tokens/sum(durations) if len(durations)==len(measured) and sum(durations)>0 else None,
  visible_tokens_per_total_request_wall_second=tokens/wall if wall else None,
  first_visible_seconds_min=min(first) if first else None,first_visible_seconds_max=max(first) if first else None,
  note="Visible phase runs from first visible delta through final response receipt. Literal text tokenization excludes reasoning and may differ from native visible-token accounting.")
def aggregate(rr):
 if not rr:return {}
 toks=sum(r["output_tokens"] for r in rr)
 secs=sum(r["request_wall_seconds"] for r in rr)
 gen=sum(r["output_tokens"]/r["generation_tps"] for r in rr if r["generation_tps"])
 return dict(requests=len(rr),generated_tokens=toks,request_wall_seconds=secs,visible_metrics=visible_aggregate(rr),
  generation_tps_min=min(r["generation_tps"] for r in rr),generation_tps_max=max(r["generation_tps"] for r in rr),
  generation_tps_token_weighted=toks/gen,output_per_wall_tps=toks/secs,
  ttft_min=min(r["ttft_seconds"] for r in rr),ttft_max=max(r["ttft_seconds"] for r in rr),
  input_tokens_min=min(r["input_tokens"] for r in rr),input_tokens_max=max(r["input_tokens"] for r in rr),
  capped_requests=sum(bool(r["capped"]) for r in rr),
  all_actual_contexts_verified=all(r["context_verified"] for r in rr),
  uncontaminated=all(r["max_llama_server_processes"]==1 for r in rr),
  peak_metrics={k:max(r[k] for r in rr) for k in ("system_used_GiB","swap_GiB","largest_runtime_RSS_GiB","runtime_PSS_GiB","GPU_VRAM_GiB","GPU_GTT_GiB")})
models={}
for ident in sorted({r["model"] for r in rows}):
 rr=[r for r in rows if r["model"]==ident];folder=R/"runs"/ident
 book=[r for r in rr if r["kind"] in ("book_subchunk","hierarchical_reduction","chunk_synthesis","final_synthesis")]
 plan=json.loads((folder/"book-plan.json").read_text()) if (folder/"book-plan.json").exists() else {}
 groups=plan.get("chunks",[]);page_sets=[p for g in groups for ps in g["subchunk_page_sets"] for p in ps]
 completed_pages=set()
 for row in book:
  if row["kind"]=="book_subchunk" and row["lifecycle"]=="accepted":
   completed_pages.update(json.loads(row["source_pdf_pages"]))
 phasefiles=list(folder.glob("phase-book*.json"))
 phases=[dict(file=p.name,**json.loads(p.read_text())) for p in phasefiles]
 loads=[]
 for p in folder.glob("load-*.json"):
  d=json.loads(p.read_text());loads.append(dict(file=p.name,wall_seconds=d.get("wall_seconds"),returncode=d.get("returncode"),peak_metrics=d.get("peak_metrics")))
 sensor_values={};sensor_seen=set()
 for p in folder.rglob("book*-telemetry-*.jsonl"):
  for line in p.open():
   try:d=json.loads(line)
   except ValueError:continue
   if d.get("time") in sensor_seen:continue
   sensor_seen.add(d.get("time"))
   for k,v in d.get("sensors_raw_millidegrees_or_microwatts",{}).items():
    if isinstance(v,(int,float)):sensor_values.setdefault(k,[]).append(v)
 sensors={k:dict(min_raw=min(v),max_raw=max(v),mean_raw=sum(v)/len(v),samples=len(v)) for k,v in sensor_values.items()}
 models[ident]=dict(sensors_raw=sensors,short=aggregate([r for r in rr if r["kind"]=="short_control"]),
  history5k=aggregate([r for r in rr if r["kind"]=="history_excerpt_control"]),
  cached=aggregate([r for r in rr if r["kind"]=="cached_repeat"]),
  history25k=aggregate([r for r in rr if r["kind"]=="long_history_excerpt_control"]),
  book_all_executed=aggregate(book),book_current_accepted=aggregate([r for r in book if r["lifecycle"]=="accepted"]),
  book_phase_wall_sum_seconds=sum(p["end_to_end_wall_seconds"] for p in phases),book_phases=phases,loads=loads,
  nominal_groups=len(groups),source_subchunks=sum(g["subchunks"] for g in groups),
  source_pages_planned=len(set(page_sets)),planned_coverage_exact_396=set(page_sets)==set(range(1,397)),
  source_pages_covered=len(completed_pages),coverage_exact_396=completed_pages==set(range(1,397)),
  inferred_complete=(folder/"book.complete").exists() or (folder/"followup.complete").exists(),
  accepted_final=json.loads((folder/"accepted-final-record.json").read_text()) if (folder/"accepted-final-record.json").exists() else None)
summary=dict(generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 followup_queue_finished=(R/"followups.complete").exists(),all_model_inference_complete=(R/"book.complete").exists(),completion_pass_finished=(R/"completion.complete").exists(),
 notes=["Generation aggregate = total generated tokens / sum(output tokens / per-request generation rate).",
 "Book all-executed includes capped and superseded requests, but excludes the separately archived prefix-only pilot.",
 "Phase wall sum includes loading, token counting, requests and retries; excludes source acquisition, download, manual audit and gaps between phases.",
 "TTFT is not a pure prompt-processing measurement. Cache counts are unavailable.",
 "RAM, RSS, PSS, VRAM and GTT overlap on UMA and must never be added.",
 "Native generation rates include reasoning where enabled. Use separately measured visible metrics for visible-answer throughput.",
 "Source coverage counts only completed, currently accepted source requests, not merely planned pages.",
 "No score is inferred from citation syntax, speed, completion markers or model self-review."],models=models)
(OUT/"metrics.json").write_text(json.dumps(summary,indent=2))
print(json.dumps({m:{k:v for k,v in d.items() if k in ("short","history5k","book_all_executed","source_subchunks","source_pages_covered","coverage_exact_396")} for m,d in models.items()},indent=2))
