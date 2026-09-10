#!/usr/bin/env python3
"""Plot measured research rates and separate source-adjudicated categories.

Optional dependency: matplotlib==3.10.8. This never generates a quality score.
"""
import json
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/2026-09-10/m4-max'
rows=[]
labels={'qwen3-8b':'Qwen3 8B · GGUF','qwen36-35b':'Qwen3.6 35B · GGUF','gemma4-26b':'Gemma4 26B · GGUF','qwen38-27b':'Qwen3.8 27B · GGUF','nemotron-49b':'Nemotron 49B · GGUF','qwen35-122b-iq2xxs':'Qwen3.5 122B · IQ2_XXS'}
for mid,label in labels.items():
 folder=OUT/'history'/mid
 p=folder/'adjudication.json'
 if not p.exists():p=folder/'review.json'
 if not p.exists() or not (folder/'visible-speed.json').exists():continue
 rv=json.loads(p.read_text());sp=json.loads((folder/'visible-speed.json').read_text())['aggregate_heldout']
 rows.append(dict(label=label,visible=sp['visible_phase_tokens_per_second'],wall=sp['visible_tokens_per_total_wall_second'],review=rv))
p=OUT/'mlx-history/review.json'
if p.exists():
 sp=json.loads((p.parent/'complete.json').read_text());rows.insert(1,dict(label='Qwen3 8B · MLX four-bit',visible=sp['visible_phase_tokens_per_second'],wall=sp['visible_tokens_per_wall_second'],review=json.loads(p.read_text())))
assert rows
colors={'correct':'#247c78','partial':'#e8b557','contradiction':'#bb5356','other':'#8571a7','covered':'#247c78','omitted':'#dbe1e6'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
fig,axs=plt.subplots(1,3,figsize=(15,max(6.2,3.2+len(rows)*.57)),sharey=True,gridspec_kw={'width_ratios':[1.25,1,1]})
fig.subplots_adjust(left=.22,right=.98,top=.73,bottom=.24,wspace=.28)
fig.suptitle('M4 Max: research speed and source fidelity',x=.035,y=.96,ha='left',fontsize=21,fontweight='bold')
fig.text(.035,.89,'64 GiB unified memory · Downloads active · Completed reviews only; campaign in progress',fontsize=11,color='#4b5563')
for ax,title in zip(axs,['Actual source workload','Extraction answers','Full-source coverage']):ax.set_title(title,loc='left',pad=40,fontweight='bold')
for i,row in enumerate(rows):
 for off,key,c in [(-.15,'visible','#386ca2'),(.15,'wall','#5ba5b0')]:
  axs[0].barh(i+off,row[key],height=.25,color=c);axs[0].text(row[key]+1,i+off,f"{row[key]:.1f}",va='center',fontsize=9)
 ec=Counter(v['judgment'] for v in row['review']['extraction']);ec['other']=sum(v for k,v in ec.items() if k not in ['correct','partial','contradiction'])
 cc=Counter(v['judgment'] for v in row['review']['coverage'] if v['stage']=='full-source-control')
 for ax,counts,keys,total in [(axs[1],ec,['correct','partial','contradiction','other'],20),(axs[2],cc,['covered','partial','omitted'],16)]:
  assert sum(counts[k] for k in keys)==total
  left=0
  for k in keys:
   n=counts[k]
   if n:
    ax.barh(i,n,left=left,height=.49,color=colors[k]);ax.text(left+n/2,i,str(n),va='center',ha='center',fontsize=9,color='white' if k in ['correct','covered','contradiction','other'] else '#29343b')
   left+=n
axs[0].set_yticks(range(len(rows)),[r['label'] for r in rows]);axs[0].invert_yaxis()
axs[0].axvline(40,color='#6d7781',linestyle=':',linewidth=1)
axs[0].set_xlim(0,max(r['visible'] for r in rows)*1.16);axs[0].set_xlabel('tokens / second · dotted line = 40')
axs[1].set_xlim(0,20);axs[1].set_xticks([0,5,10,15,20]);axs[1].set_xlabel('20 answers')
axs[2].set_xlim(0,16);axs[2].set_xticks([0,4,8,12,16]);axs[2].set_xlabel('16 compound source units')
for ax in axs:
 ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color('#cbd2d9');ax.tick_params(axis='y',length=0);ax.xaxis.grid(alpha=.15);ax.set_axisbelow(True)
axs[0].legend(handles=[Patch(color='#386ca2',label='Visible phase'),Patch(color='#5ba5b0',label='Including prompt processing')],bbox_to_anchor=(0,1.015),loc='lower left',frameon=False,fontsize=8)
axs[1].legend(handles=[Patch(color=colors[k],label=k.title()) for k in ['correct','partial','contradiction','other']],bbox_to_anchor=(0,1.015),loc='lower left',frameon=False,ncol=2,fontsize=8)
axs[2].legend(handles=[Patch(color=colors[k],label=k.title()) for k in ['covered','partial','omitted']],bbox_to_anchor=(0,1.015),loc='lower left',frameon=False,ncol=2,fontsize=8)
fig.text(.035,.14,'One frozen battery per configuration; ten held-out requests. Wall rate excludes startup and inter-request work.',fontsize=10,color='#4b5563')
fig.text(.035,.095,'MLX uses different weights, quantization and cache behavior. These observations do not isolate backend or hardware effects.',fontsize=10,color='#4b5563')
fig.text(.035,.05,'Source fidelity: Codex-assisted review, no independent human adjudication. Coverage, citations and factual errors remain separate.',fontsize=10,color='#4b5563')
for ext in ['png','svg']:fig.savefig(OUT/('research-comparison.'+ext),dpi=160)
print(len(rows),'configurations plotted')
