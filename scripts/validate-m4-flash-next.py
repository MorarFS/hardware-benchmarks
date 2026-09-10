"""Validate frozen Flash-Next prompts, streams, timing arithmetic and review integrity.

Run with the isolated benchmark environment and the verified original model
folder for tokenizer access. This validates receipts, not historical truth.
"""
import argparse,gzip,hashlib,importlib.util,json,math,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts/history_v2'))
import runner as frozen

def main():
 from transformers import AutoTokenizer
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);a=p.parse_args()
 out=ROOT/'results/2026-09-10/m4-max/flash-next';b=out/'history';suite=frozen.load_suite(ROOT/'experiments/history-v2');tok=AutoTokenizer.from_pretrained(a.model)
 protocol=json.loads((b/'protocol.json').read_text());assert protocol['fixture_hashes']==suite['freeze']['files'];assert protocol['temperature']==0 and protocol['thinking'] is False and protocol['MTP'] is False
 stages,control=frozen.source_stages(suite);expected={name:prompt for name,prompt,_ in [*stages,control]}
 merge='\n\n'.join(h['id']+'\n'+json.loads((b/(h['id']+'-summary.json')).read_text())['output'] for h in suite['questions']);expected['merged-summary-synthesis']=suite['prompts']['synthesis'].format(source=merge)
 records=[]
 for name,prompt in expected.items():
  request=json.loads((b/(name+'-request.json')).read_text());assert request['messages']==[{'role':'system','content':suite['prompts']['system']},{'role':'user','content':prompt}],name
  assert request['max_tokens']==2048 and request['temperature']==0 and request['seed']==42 and request['enable_thinking'] is False
  stream=b/(name+'-stream.jsonl');raw=stream.read_text() if stream.exists() else gzip.decompress(stream.with_name(stream.name+'.gz').read_bytes()).decode();events=[json.loads(line) for line in raw.splitlines()]
  r=json.loads((b/(name+'.json')).read_text());assert ''.join(x['text'] for x in events)==r['output'];assert (b/(name+'.md')).read_text()==r['output']+'\n'
  assert r['status']=='ok' and r['finish_reason']=='stop',name
  rendered=tok.apply_chat_template(request['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False);assert len(tok.encode(rendered,add_special_tokens=False))==r['prompt_tokens']
  assert len(tok.encode(r['output'],add_special_tokens=False))==r['visible_tokens_retokenized']
  times=[x['elapsed_seconds'] for x in events];assert times==sorted(times);content=[x['elapsed_seconds'] for x in events if x['text']]
  assert math.isclose(content[0],r['first_content_seconds'],abs_tol=1e-8);assert math.isclose(content[-1],r['last_content_seconds'],abs_tol=1e-8);assert math.isclose(content[-1]-content[0],r['visible_phase_seconds'],abs_tol=1e-8);assert times[-1]<=r['wall_seconds']
  if not name.startswith('development-'):records.append(r)
 complete=json.loads((b/'complete.json').read_text());assert len(records)==complete['heldout_requests']==10
 tokens=sum(x['visible_tokens_retokenized'] for x in records);phase=sum(x['visible_phase_seconds'] for x in records);wall=sum(x['wall_seconds'] for x in records)
 assert tokens==complete['visible_tokens'];assert math.isclose(tokens/phase,complete['visible_phase_tokens_per_second']);assert math.isclose(tokens/wall,complete['visible_tokens_per_wall_second'])
 smoke=json.loads((out/'smoke/complete.json').read_text())['requests'];warm=[x for x in smoke if x['name'].startswith('warm-')];review=json.loads((out/'smoke-review.json').read_text())['warm'];assert len(warm)==3;assert math.isclose(statistics.mean(x['generation_tps'] for x in warm),review['mean_generation_tokens_per_second'])
 receipt={'frozen_requests_validated':len(expected),'heldout_requests':10,'all_finished_naturally':True,'full_source_input_tokens':next(x['prompt_tokens'] for x in records if x['name']=='full-source-control'),'heldout_visible_tokens':tokens,'heldout_visible_phase_seconds':phase,'heldout_wall_seconds':wall,'visible_phase_tokens_per_second':tokens/phase,'visible_tokens_per_wall_second':tokens/wall,'warm_samples_validated':3,'scope':'Exact frozen prompt reconstruction, retained stream/output identity, tokenizer counts and timing arithmetic. Semantic source review is separate; this is not an independent human accuracy assessment.'}
 (out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
