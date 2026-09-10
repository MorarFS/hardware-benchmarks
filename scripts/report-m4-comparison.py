#!/usr/bin/env python3
"""Combine accepted M4 measurements with existing same-artifact system results."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/2026-09-10/m4-max'
history=json.loads((ROOT/'results/2026-09-08/mac/matched-speed-comparison.json').read_text());current=[]
for folder in sorted((OUT/'speed').glob('*')):
 row=None
 for p in sorted(folder.glob('*-status.json')):
  s=json.loads(p.read_text())
  if not s.get('validation_passed'):continue
  if row is None:row={'model_id':s['model_id'],'machine_backend':'M4 Max / Metal','sha256':s['model_sha256'],'values':{},'note':'Active downloads and other desktop/workspace load; five samples.'}
  for e in json.loads(p.with_name(p.name.replace('-status','')).read_text()):
   key='pp512' if e['n_prompt'] else 'tg'+str(e['n_depth'])
   row['values'][key]={'mean':e['avg_ts'],'sd':e['stddev_ts'],'samples':e['samples_ts'],'source':str(p.with_name(p.name.replace('-status','')).relative_to(ROOT))}
 if row:current.append(row)
combined=[]
for row in current:
 combined.append(row)
 for old in history:
  if old['model_id']==row['model_id']:
   assert old['sha256']==row['sha256'],old
   combined.append(old)
(OUT/'matched-system-comparison.json').write_text(json.dumps(combined,indent=2)+'\n')
lines=['# Same-artifact system comparisons','', 'Means ± sample SD in tokens/s, five retained samples per measurement. Each group uses the identical pinned model hash and b10852 pp512/tg256 settings. Historical rows are reproduced without pooling or replacement. M4 downloads continue; prior M5 synthetic transfers were paused, and OS, desktop load, power/thermal history and complete backend implementations differ. These are observed configurations, not an isolated chip ranking.','', '| Artifact | Computer/backend | pp512 | tg256 depth0 | tg256 depth2048 |','|---|---|---:|---:|---:|']
def val(row,k):
 v=row['values'].get(k)
 return f"{v['mean']:.2f} ± {v['sd']:.2f}" if v else '—'
for row in combined:lines.append(f"| {row['model_id']} | {row['machine_backend']} | {val(row,'pp512')} | {val(row,'tg0')} | {val(row,'tg2048')} |")
lines+=['','The separate Gemma M5 delayed repeat remains visible because run-to-run variation was substantial; neither session replaces the other. Empty cells mean unavailable, not zero. Exact hashes, samples where available and historical evidence paths are in the accompanying JSON.','', 'Source-workload timings and fidelity judgments use different inputs and timing boundaries; see the M4 main report. Synthetic generation alone does not establish the 40-visible-token research target.','']
(OUT/'matched-system-comparison.md').write_text('\n'.join(lines));print(len(current),'M4 sessions,',len(combined),'system rows')
