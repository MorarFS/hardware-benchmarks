#!/usr/bin/env python3
"""Independently check retained M4 speed arithmetic and source-review integrity."""
import gzip,hashlib,importlib.util,json,sys,math,re,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/2026-09-10/m4-max'
sys.path.insert(0,str(ROOT/'scripts'))
from mac_runtime import model_specs
loader=importlib.util.spec_from_file_location('collector',ROOT/'scripts/collect-mac-results.py')
collector=importlib.util.module_from_spec(loader);loader.loader.exec_module(collector)
manifest=model_specs(ROOT);runs=[];reviews=[];cpu=[]
for p in sorted((OUT/'speed').glob('*/*-status.json')):
 status=json.loads(p.read_text())
 if not status.get('validation_passed'):continue
 data=json.loads(p.with_name(p.name.replace('-status','')).read_text())
 collector.validate(data,status,manifest)
 runs.append({'path':str(p.relative_to(ROOT)),'rows':len(data),'samples':sum(len(x['samples_ns']) for x in data)})
for p in sorted((OUT/'cpu').glob('*-status.json')):
 status=json.loads(p.read_text());assert status['returncode']==0 and not status['abort']
 data=json.loads(p.with_name(p.name.replace('-status','')).read_text())
 off=p.with_name(p.name.replace('-status.json','-offload.txt.gz'))
 log=gzip.decompress(off.read_bytes()).decode() if off.exists() else p.with_name(p.name.replace('-status.json','-offload.txt')).read_text()
 matches=re.findall(r'offloaded\s+(\d+)/(\d+)\s+layers to GPU',log)
 assert matches and all(int(a)==0 and int(b)>0 for a,b in matches)
 for row in data:
  assert row['n_gpu_layers']==0 and row['devices']=='none' and row['build_commit']=='050dde50c'
  assert Path(row['model_filename']).name==manifest['qwen3-8b']['filename']
  assert len(row['samples_ns'])==len(row['samples_ts'])==5
  rates=[(row['n_prompt']+row['n_gen'])*1e9/ns for ns in row['samples_ns']]
  assert math.isclose(statistics.mean(rates),row['avg_ts'],abs_tol=1e-5)
  assert math.isclose(statistics.stdev(rates),row['stddev_ts'],abs_tol=1e-5)
 cpu.append({'path':str(p.relative_to(ROOT)),'rows':len(data),'samples':sum(len(r['samples_ns']) for r in data)})
folders=list((OUT/'history').glob('*'))+list((OUT/'history-repeat').glob('*'))+list((OUT/'capacity-history').glob('*'))+[OUT/'mlx-history',OUT/'flash-next/history']
for folder in folders:
 if not folder.is_dir():continue
 p=folder/'adjudication.json'
 if not p.exists():p=folder/'review.json'
 if not p.exists():continue
 review=json.loads(p.read_text());assert len(review['extraction'])==20,p
 assert len({x['question_id'] for x in review['extraction']})==20,p
 assert len(review['coverage'])==48,p
 assert len({(x['stage'],x.get('unit',x.get('id'))) for x in review['coverage']})==48,p
 for name,sha in review['output_sha256'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==sha,(p,name)
 for row in review['claims']:assert row['output_anchor'] in (folder/(row['stage']+'.md')).read_text(),(p,row)
 reviews.append({'path':str(p.relative_to(ROOT)),'extraction_answers':20,'coverage_dispositions':48,'coverage_judgments':sum(x['judgment'] is not None for x in review['coverage']),'grouped_claim_annotations':len(review['claims'])})
receipt={'scope':'Available completed measurements only; generation protocol validation is performed separately by collect_mac.py. This check does not adjudicate source truth or rerun inference.','speed_runs':runs,'cpu_runs':cpu,'cpu_rows':sum(x['rows'] for x in cpu),'cpu_samples':sum(x['samples'] for x in cpu),'review_integrity':reviews,'speed_rows':sum(x['rows'] for x in runs),'speed_samples':sum(x['samples'] for x in runs)}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['speed_runs','cpu_runs','review_integrity']}));print(len(reviews),'source-review ledgers verified')
