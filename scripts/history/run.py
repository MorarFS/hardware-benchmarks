#!/usr/bin/env python3
"""Portable historical workflow runner. Requires a dedicated local LM Studio server."""
import argparse,fcntl,json,pathlib,shutil,sys,time
import engine as b

def configure(args):
 b.ROOT=pathlib.Path(args.work_dir).resolve();b.ROOT.mkdir(parents=True,exist_ok=True)
 b.API=args.api.rstrip('/');b.LMS=args.lms
 lock=(b.ROOT/'benchmark.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 def unload(config):
  rows=json.loads(b.command([b.LMS,'ps','--json'])['output'])
  owned={m['identifier'] for m in config['models']}
  if any(x.get('status')!='idle' or x.get('queued',0)>0 for x in rows):raise RuntimeError('Inference is active; retry after it finishes.')
  if any(x['identifier'] not in owned for x in rows):raise RuntimeError('Unrelated models are loaded. Use a dedicated server or unload them yourself.')
  for x in rows:b.command([b.LMS,'unload',x['identifier']])
 b.unload_ours=unload
 return lock

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--work-dir',required=True);p.add_argument('--config',required=True)
 p.add_argument('--source-dir',required=True);p.add_argument('--mode',choices=['original','reasoning'],default='original')
 p.add_argument('--model',required=True,help='Exact identifier in config')
 p.add_argument('--model-file',required=True);p.add_argument('--model-sha256',required=True)
 p.add_argument('--api',default='http://127.0.0.1:1234');p.add_argument('--lms',default=shutil.which('lms') or str(pathlib.Path.home()/'.lmstudio/bin/lms'))
 a=p.parse_args();lock=configure(a)
 if b.digest(a.model_file)!=a.model_sha256:raise RuntimeError('Model SHA-256 mismatch')
 cfg=json.loads(pathlib.Path(a.config).read_text());m=next(x for x in cfg['models'] if x['identifier']==a.model)
 source=pathlib.Path(a.source_dir).resolve();meta=json.loads((source/'source.json').read_text());pages=json.loads((source/'pages.json').read_text())
 if not meta.get('approved_for_comparison'):raise RuntimeError('Source metadata must explicitly mark this public source approved_for_comparison.')
 import hashlib
 for page in pages:
  if hashlib.sha256(page['text'].encode()).hexdigest()!=page['text_sha256']:raise RuntimeError('Page text checksum mismatch')
 if a.mode=='reasoning':
  import reasoning_requests as rr
  rr.API=b.API;b.request=rr.request
 t=time.perf_counter();model=None
 try:
  model,folder=b.load_model(m,cfg);b.book(model,m,folder,source)
 finally:
  b.command([b.LMS,'unload',m['identifier']])
  b.save(b.ROOT/'phase.json',dict(wall_seconds=time.perf_counter()-t,model=m,mode=a.mode,model_sha256=a.model_sha256,source_sha256=meta['pdf_sha256']))
if __name__=='__main__':main()
