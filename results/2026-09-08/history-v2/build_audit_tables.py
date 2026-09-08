"""Rebuild tables from fixed Codex review decisions and saved generation records.
This performs bookkeeping and span checks, not automated factual adjudication.
"""
import argparse,csv,json,re,unicodedata,hashlib,collections
from pathlib import Path
MODELS=['gemma26-off','qwen35-off-mtp','gptoss120-medium']
STAGES=['H1-summary','H2-summary','H3-summary','H4-summary','merged-summary-synthesis','full-source-control']
CITE=re.compile(r'\[(?:PDF\s+p{1,2}\.?\s*)[\d\s,;\-–‑]+?\]|【(?:PDF\s+p{1,2}\.?\s*)[\d\s,;\-–‑]+?】|\((?:p{1,2}\.?\s*)?[\d\s,;\-–‑]+\)')
def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s).translate(str.maketrans({'‑':'-','–':'-','—':'-'}))).strip()
def cited(s):
 nums=[]
 for m in CITE.finditer(s):
  t=norm(m.group())
  for a,b in re.findall(r'(\d+)(?:\s*-\s*(\d+))?',t):
   nums.extend(range(int(a),int(b)+1) if b else [int(a)])
 return sorted(set(nums))
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def csvout(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
  for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--raw',type=Path,required=True);ap.add_argument('--suite',type=Path,required=True);ap.add_argument('--decisions',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 a.output.mkdir(exist_ok=True,parents=True);notes=json.loads(a.decisions.read_text());gold=json.loads((a.suite/'gold/answers.json').read_text())
 texts={(m,s):(a.raw/m/(s+'.md')).read_text().strip() for m in MODELS for s in STAGES}
 extraction=[]
 partial={(x['model'],x['question']):x for x in notes['extraction_partial']}
 false={(x['model'],x['question']):x for x in notes['extraction_false_absence']}
 missing={('qwen35-off-mtp',x) for x in ['H1-Q2','H1-Q3','H3-Q1','H3-Q2','H3-Q3','H3-Q4']}|{('gptoss120-medium','H1-Q1')}
 altered={('gptoss120-medium','H3-Q2'):'Changes the Saracens to they inside a quotation.',('gptoss120-medium','H4-Q4'):'Reorders source wording, changes reveal herself to revealed herself, and drops report wording within the quotation. Substantive presented-as answer remains supported.'}
 for m in MODELS:
  for h in range(1,5):
   t=(a.raw/m/f'H{h}-extraction.md').read_text().strip()
   matches=list(re.finditer(r'H([1-4])[-‑]Q([1-5])',t))
   assert len(matches)==5
   for i,match in enumerate(matches):
    qid=f'H{match[1]}-Q{match[2]}';q=next(x for x in gold if x['id']==qid)
    answer=t[match.end():matches[i+1].start() if i+1<len(matches) else len(t)].strip(' \n:*')
    key=(m,qid);state='correct_absence' if q['answerability']=='not_stated' else 'fully_supported'
    reason='Source-absent after review of the complete supplied passage.' if state=='correct_absence' else 'Required answer meaning is supported by the supplied passage.'
    if key in partial:state='partial';reason=partial[key]['reason']
    if key in false:state='false_abstention';reason=false[key]['reason']
    quote='not_applicable' if state in ['correct_absence','false_abstention'] else 'supporting_quote_present'
    qnote=''
    if key in missing:quote='missing';qnote='Supporting quotation required but absent; substantive answer scored separately.'
    if key in altered:quote='altered_wording';qnote=altered[key]
    fmt=[]
    if '‑' in match[0]:fmt.append('nonbreaking hyphen in question ID; normalized for matching')
    if state in ['correct_absence','false_abstention'] and answer.endswith('.'):fmt.append('adds period to exact absence phrase')
    if '【' in answer:fmt.append('alternative citation brackets')
    extraction.append(dict(model=m,question_id=qid,question=q['question'],answerability=q['answerability'],output_answer=answer,judgment=state,reason=reason,evidence_pages=q['evidence_pages'],gold_answer=q['answer'],cited_pages=cited(answer),citation_support='not_applicable' if not cited(answer) else 'supports stated content; partial-answer omissions remain separate',quotation=quote,quotation_note=qnote,format_notes=fmt))
 assert len(extraction)==60
 csvout(a.output/'extraction-ledger.csv',extraction);dump(a.output/'extraction-ledger.json',extraction)
 coverage=[];criteria=[]
 for h in range(1,5):criteria+=json.loads((a.suite/f'gold/H{h}-coverage.json').read_text())['coverage_units']
 for m in MODELS:
  for st in STAGES:
   cs=criteria if not st.startswith('H') else [x for x in criteria if x['id'].startswith(st[:2])]
   decisions=notes['coverage'][m][st];assert len(cs)==len(decisions)
   for c,j in zip(cs,decisions):
    coverage.append(dict(model=m,stage=st,coverage_id=c['id'],criterion=c['description'],evidence_pages=c['evidence_pages'],judgment=j.split(':')[0],detail=j.partition(':')[2],note='Coverage presence does not imply factual correctness. Compound units require their specified components for covered.'))
 assert len(coverage)==144;csvout(a.output/'coverage-ledger.csv',coverage)
 flags=[];quality=[]
 for key,output in [('material_flags',flags),('quality_notes',quality),('citation_notes',quality)]:
  for f in notes.get(key,[]):
   for st in f['stages']:
    assert norm(f['span']) in norm(texts[f['model'],st]),(f['model'],st,f['span'])
    output.append(dict(model=f['model'],stage=st,span=f['span'],family=f['family'],dimension=f['dimension'],judgment=f['judgment'],evidence_pages=f['pages'],reason=f['reason'],origin=f['origin']))
 dump(a.output/'issue-ledger.json',flags);csvout(a.output/'issue-ledger.csv',flags);dump(a.output/'precision-notes.json',quality)
 units=[]
 for m in MODELS:
  for st in STAGES:
   text=texts[m,st];start=0;segments=[]
   for match in CITE.finditer(text):
    end=match.end()
    while end<len(text) and text[end] in '.,;:':end+=1
    segments.append(text[start:end]);start=end
   if text[start:].strip():segments.append(text[start:])
   for i,u in enumerate(segments,1):
    ff=[x for x in flags if x['model']==m and x['stage']==st and norm(x['span']) in norm(u)]
    qq=[x for x in quality if x['model']==m and x['stage']==st and norm(x['span']) in norm(u)]
    units.append(dict(model=m,stage=st,unit_id=f'{st}-U{i:03}',output_text=u.strip(),cited_pages=cited(u),issue_families=sorted({x['family'] for x in ff}),precision_families=sorted({x['family'] for x in qq}),review_status='issue recorded' if ff else 'precision note' if qq else 'no additional material issue identified in supplied-text review',unit_definition='Citation-delimited segment, possibly multiple claims or a sentence fragment. Not an atomic claim or accuracy denominator.'))
 for x in flags+quality:
  assert any(x['family'] in u['issue_families']+u['precision_families'] for u in units if u['model']==x['model'] and u['stage']==x['stage']),(x['model'],x['stage'],x['family'])
 csvout(a.output/'citation-segment-ledger.csv',units)
 instructions=[];metrics=[]
 for m in MODELS:
  for st in STAGES:
   t=texts[m,st];plain=CITE.sub('',t);plain=re.sub(r'[*_#]','',plain)
   words=[x for x in plain.split() if re.search(r'\w',x)]
   low,high=(180,220) if st.startswith('H') else (350,450)
   pmap={'gemma26-off':['H1','H1','H1','H3'],'qwen35-off-mtp':['H1','H1','H2+H3','H4'],'gptoss120-medium':['H1','H2','H3','H4']}[m] if st=='full-source-control' else ['H1','H2','H3','H4'] if st=='merged-summary-synthesis' else []
   instructions.append(dict(model=m,stage=st,raw_whitespace_words=len(t.split()),prose_words_without_citation_markers=len(words),requested_min=low,requested_max=high,within_word_range=low<=len(words)<=high,paragraph_count=len(re.split(r'\n\s*\n',t)),paragraph_mapping=pmap,em_dash_count=t.count('—'),physical_page_reference_style='parenthesized page numbers' if st=='full-source-control' else 'PDF markers',four_paragraph_mapping_pass=(pmap==['H1','H2','H3','H4']) if not st.startswith('H') else None))
  for p in sorted((a.raw/m).glob('*.json')):
   d=json.loads(p.read_text())
   if not isinstance(d,dict) or not d.get('name') or 'wall_seconds' not in d:continue
   assert d['status']=='ok' and not d['output_limit_reached']
   metrics.append(dict(model=m,request=d['name'],status=d['status'],input_tokens=d['stats'].get('input_tokens'),total_output_tokens=d['stats'].get('total_output_tokens'),reasoning_tokens=d.get('reasoning_tokens'),native_generation_tps=d['stats'].get('tokens_per_second'),visible_tokens=d.get('visible_text_tokens'),first_visible_seconds=d.get('first_visible_token_seconds'),wall_seconds=d['wall_seconds'],visible_phase_tps=d.get('visible_phase_tokens_per_second'),visible_total_wall_tps=d.get('visible_tokens_per_total_wall_second'),output_limit_reached=d['output_limit_reached']))
 assert len(metrics)==36;csvout(a.output/'request-metrics.csv',metrics);csvout(a.output/'instruction-checks.csv',instructions)
 summaries=[]
 for m in MODELS:
  extraction_counts=dict(collections.Counter(x['judgment'] for x in extraction if x['model']==m))
  cov={}
  for phase in ['direct','merged-summary-synthesis','full-source-control']:
   cov[phase]=dict(collections.Counter(x['judgment'] for x in coverage if x['model']==m and (x['stage'].startswith('H') if phase=='direct' else x['stage']==phase)))
  joined='\n\n'.join(texts[m,f'H{h}-summary'] for h in range(1,5))
  summaries.append(dict(model=m,extraction=extraction_counts,answerable_questions=16,source_absent_questions=4,coverage=cov,merged_is_whitespace_normalized_concatenation=norm(joined)==norm(texts[m,'merged-summary-synthesis']),issue_families_by_stage={s:sorted({x['family'] for x in flags if x['model']==m and x['stage']==s}) for s in STAGES},fact_families_by_stage={s:sorted({x['family'] for x in flags if x['model']==m and x['stage']==s and x['dimension'] in ['factual','chronology']}) for s in STAGES}))
 dump(a.output/'summary.json',summaries)
 dump(a.output/'bookkeeping-verification.json',dict(extraction_rows=len(extraction),coverage_rows=len(coverage),request_rows=len(metrics),summary_outputs=len(texts),citation_segments=len(units),issue_manifestations=len(flags),precision_manifestations=len(quality),all_issue_spans_found=True,note='Numeric checks and deterministic tables do not independently validate the Codex source judgments.'))
 print(json.dumps(summaries,indent=2))
if __name__=='__main__':main()
