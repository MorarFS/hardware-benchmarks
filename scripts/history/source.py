#!/usr/bin/env python3
"""Download and checksum the public Oman scan, then extract physical-page text."""
import argparse,pathlib,urllib.request,json,hashlib,sys
import engine as b
URL='https://archive.org/download/byzantineempire00omanrich/byzantineempire00omanrich.pdf'
SHA='0187c4b558c683d5349b4cf427db4ca9713298f0e99660767d8dfbc2aa83c5f2'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work-dir',required=True);a=p.parse_args()
 b.ROOT=pathlib.Path(a.work_dir).resolve();b.ROOT.mkdir(parents=True,exist_ok=True);pdf=b.ROOT/'oman.pdf'
 if not pdf.exists():
  with urllib.request.urlopen(URL,timeout=120) as r,pdf.with_suffix('.partial').open('wb') as f:
   while x:=r.read(4*1024*1024):f.write(x)
  pdf.with_suffix('.partial').rename(pdf)
 if b.digest(pdf)!=SHA:raise RuntimeError('Source SHA-256 mismatch')
 meta=b.ROOT/'metadata.json';b.save(meta,dict(title='The Byzantine Empire',author='Charles Oman',source_url=URL,approved_for_comparison=True,rights='Public-domain historical scan',citation_policy='Physical PDF pages; not printed pagination'))
 b.ingest(pdf,meta,b.ROOT/'source')
 print('Inspect OCR warnings. For exact text replication use the published canonical pages.json; OCR versions can differ.')
if __name__=='__main__':main()
