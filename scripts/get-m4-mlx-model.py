#!/usr/bin/env python3
"""Fetch the measured pinned MLX artifact and verify every recorded file hash."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,default=ROOT/'work/mlx-qwen8')
 parser.add_argument('--verify-only',action='store_true')
 args=parser.parse_args()
 manifest=json.loads((ROOT/'results/2026-09-10/m4-max/mlx-model-files.json').read_text())
 if not args.verify_only:
  from huggingface_hub import snapshot_download
  snapshot_download(repo_id=manifest['repository'],revision=manifest['revision'],local_dir=args.output,allow_patterns=[x['path'] for x in manifest['files']])
 for entry in manifest['files']:
  path=args.output/entry['path']
  if path.stat().st_size!=entry['bytes']:raise RuntimeError('Size mismatch: '+entry['path'])
  digest=hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(8*1024**2),b''):digest.update(block)
  if digest.hexdigest()!=entry['sha256']:raise RuntimeError('Hash mismatch: '+entry['path'])
 print('Verified',len(manifest['files']),'files at revision',manifest['revision'])
if __name__=='__main__':main()
