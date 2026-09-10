"""Download the pinned complete MLX Flash-Next artifact and verify Hub hashes."""
import argparse,hashlib,json
from pathlib import Path

def main():
 from huggingface_hub import HfApi,snapshot_download
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--verify-only',action='store_true');a=p.parse_args()
 repository='Sawfwair/Qwen3.8-Flash-Next-MLX-Mixed-2bit';revision='a6e3d7a43efb8803cd6b847299a54084dc4e8ef4'
 info=HfApi().model_info(repository,revision=revision,files_metadata=True);assert info.sha==revision
 if not a.verify_only:snapshot_download(repo_id=repository,revision=revision,local_dir=a.output,max_workers=4)
 entries=[]
 for file in info.siblings:
  path=a.output/file.rfilename;size=path.stat().st_size;assert size==file.size,file.rfilename
  sha=hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(8*1024**2),b''):sha.update(block)
  if file.lfs:assert sha.hexdigest()==file.lfs.sha256,file.rfilename
  else:assert hashlib.sha1(b'blob '+str(size).encode()+b'\0'+path.read_bytes()).hexdigest()==file.blob_id,file.rfilename
  entries.append({'path':file.rfilename,'bytes':size,'sha256':sha.hexdigest()})
 a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps({'repository':repository,'revision':revision,'files':entries},indent=2)+'\n')
 print('Verified',len(entries),'files,',sum(x['bytes'] for x in entries),'bytes')
if __name__=='__main__':main()
