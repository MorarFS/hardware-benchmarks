"""Build an immutable-weight MLX view with disk-backed full PLE tables.

Sawfwair stores PLE names as shard_N; current upstream storage expects shards.N.
This adapter builds the upstream manifest directly from original byte ranges.
No tensor bytes, norm values, expert counts, or quantization values are changed.
The optional MTP draft is excluded from target-only decoding, but kept in source.
"""
import argparse,json,os,re,shutil,struct,hashlib
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 source=a.source.resolve();target=a.output.resolve();target.mkdir(parents=True,exist_ok=False)
 index=json.loads((source/'model.safetensors.index.json').read_text());config=json.loads((source/'config.json').read_text());headers={};counts={}
 for f in sorted(set(index['weight_map'].values())):
  with (source/f).open('rb') as stream:
   size=struct.unpack('<Q',stream.read(8))[0];header=json.loads(stream.read(size))
  headers[f]=(size+8,header)
  for key,info in header.items():
   if key=='__metadata__':continue
   group='ple' if '.ngram_embedding.' in key else 'mtp' if key.startswith('mtp.') else 'vision' if key.startswith('vision_tower.') else 'core'
   counts[group]=counts.get(group,0)+info['data_offsets'][1]-info['data_offsets'][0]
 prefixes=sorted({k.rsplit('.',1)[0] for k in index['weight_map'] if '.ngram_embedding.' in k},key=lambda k:int(re.search(r'(?:shard_|shards\.)(\d+)$',k).group(1)))
 assert len(prefixes)==128,len(prefixes)
 shards=[];row=0
 for prefix in prefixes:
  q=config['quantization'][prefix];assert q=={'bits':4,'group_size':32,'mode':'affine'},q
  entry={'row_start':row}
  for name,dtype in [('weight','U32'),('scales','BF16'),('biases','BF16')]:
   key=prefix+'.'+name;file=index['weight_map'][key];start,header=headers[file];info=header[key];assert info['dtype']==dtype
   entry[name]={'file':file,'offset':start+info['data_offsets'][0],'shape':info['shape'],'dtype':dtype}
  n=entry['weight']['shape'][0];assert entry['weight']['shape']==[n,20];assert entry['scales']['shape']==entry['biases']['shape']==[n,5]
  entry['row_count']=n;row+=n;shards.append(entry)
 manifest={'version':2,'source_root':os.path.relpath(source,target),'layout':'safetensors_ranges','row_width':160,'row_count':row,'quantization':{'bits':4,'group_size':32,'mode':'affine'},'cache_rows':0,'shards':shards}
 (target/'ple-store.json').write_text(json.dumps(manifest,indent=2)+'\n')
 weight_map={k:v for k,v in index['weight_map'].items() if '.ngram_embedding.' not in k and not k.startswith('mtp.')}
 # Files may also contain PLE/MTP tensors. Upstream sanitize discards these
 # lazy arrays before parameter evaluation; original files remain byte-identical.
 for f in sorted(set(weight_map.values())):os.link(source/f,target/f)
 for f in source.iterdir():
  if f.is_file() and f.suffix!='.safetensors' and f.name not in ['config.json','model.safetensors.index.json']:shutil.copy2(f,target/f.name)
 config['text_config']['ple_storage']={'manifest':'ple-store.json','cache_rows':0}
 for name in ['quantization','quantization_config']:
  if name in config:config[name]={k:v for k,v in config[name].items() if '.ngram_embedding.' not in k and not k.startswith('mtp.')}
 (target/'config.json').write_text(json.dumps(config,indent=2)+'\n')
 (target/'model.safetensors.index.json').write_text(json.dumps({'metadata':{'total_size':counts['core']+counts['vision'],'external_ple_bytes':counts['ple']},'weight_map':weight_map},indent=2)+'\n')
 receipt={'repository':'Sawfwair/Qwen3.8-Flash-Next-MLX-Mixed-2bit','revision':'a6e3d7a43efb8803cd6b847299a54084dc4e8ef4','bytes_by_group':counts,'ple_rows':row,'ple_shards':128,'cache_rows':0,'target_only':True,'source_tensor_values_changed':False,'notes':'Original safetensors are hard-linked. The PLE manifest indexes original shard_N byte ranges. Upstream model sanitize handles name aliases and discards PLE/MTP lazy arrays before eval. No pruning, rescaling, or requantization.'}
 (target/'ADAPTER-PROVENANCE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
