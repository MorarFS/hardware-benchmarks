#!/usr/bin/env python3
"""Plot collected measurements and source-adjudicated counts; never score outputs.

Optional dependency: matplotlib. Run report-mac.py before this script.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/2026-09-08/mac'


def main():
    speed=json.loads((OUT/'matched-speed-comparison.json').read_text())
    accuracy={r['model_id']:r for r in json.loads((OUT/'accuracy/scoreboard.json').read_text())}
    rows=[r for r in speed if r['machine_backend'].startswith('M5 Pro') and r['values']]
    assert rows
    labels=[r['model_id']+(' · repeat' if 'repeat' in r['machine_backend'] else '') for r in rows]
    colors={'correct':'#277a80','partial':'#dda63a','contradiction':'#bd504a','other':'#8b739d','covered':'#277a80','omitted':'#d2d8df'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none','axes.titleweight':'bold'})
    height=max(6.8,2.8+len(rows)*.5)
    fig,axes=plt.subplots(1,4,figsize=(17,height),sharey=True,gridspec_kw={'width_ratios':[1.25,1.25,1.1,1.1]})
    fig.subplots_adjust(left=.235,right=.987,bottom=.23,top=.78,wspace=.25)
    fig.suptitle('Apple M5 Pro: speed and source fidelity',x=.035,y=.97,ha='left',fontsize=20,fontweight='bold')
    fig.text(.035,.90,'48 GiB unified memory · Metal / llama.cpp b10852 · AC / Automatic power mode',fontsize=11,color='#4b5563')
    axes[0].set_title('Prompt processing',loc='left',pad=32)
    axes[1].set_title('Generation',loc='left',pad=32)
    axes[2].set_title('Extraction answers',loc='left',pad=32)
    axes[3].set_title('Full-source coverage',loc='left',pad=32)
    for i,row in enumerate(rows):
        v=row['values'];p=v.get('pp512')
        if p:axes[0].barh(i,p['mean'],xerr=p['sd'],height=.45,color='#277a80',error_kw={'elinewidth':1,'capsize':2})
        for offset,key,color in [(-.14,'tg0','#365f9d'),(.14,'tg2048','#dd9a3c')]:
            rate=v.get(key)
            if key=='tg2048' and not rate:rate=v.get('tg1792')
            if rate:
                axes[1].barh(i+offset,rate['mean'],xerr=rate['sd'],height=.25,color=color,error_kw={'elinewidth':1,'capsize':2},hatch='//' if key=='tg2048' and 'tg1792'in v else None)
        review=accuracy[row['model_id']]
        if 'repeat'in row['machine_backend']:
            for ax in axes[2:]:ax.text(.02,i,'Separate timing repeat',transform=ax.get_yaxis_transform(),va='center',fontsize=8,color='#657080')
            continue
        counts=review.get('extraction')
        if counts:
            values={k:counts.get(k,0) for k in ['correct','partial','contradiction']}
            values['other']=sum(v for k,v in counts.items() if k not in values)
            assert sum(values.values())==20
            left=0
            for key,n in values.items():
                if n:
                    axes[2].barh(i,n,left=left,height=.45,color=colors[key])
                    axes[2].text(left+n/2,i,str(n),va='center',ha='center',fontsize=8,color='white' if key in ['correct','contradiction','other'] else '#28323d')
                left+=n
        else:axes[2].text(.02,i,'Context exclusion' if row['model_id'].startswith('falcon') else 'Review pending',transform=axes[2].get_yaxis_transform(),va='center',fontsize=8,color='#657080')
        units=review.get('coverage',{}).get('full-source-control')
        if units:
            assert sum(units.values())==16
            left=0
            for key in ['covered','partial','omitted']:
                n=units.get(key,0)
                if n:
                    axes[3].barh(i,n,left=left,height=.45,color=colors[key])
                    axes[3].text(left+n/2,i,str(n),va='center',ha='center',fontsize=8,color='white' if key=='covered' else '#28323d')
                left+=n
        else:axes[3].text(.02,i,'Not submitted' if row['model_id'].startswith('falcon') or review.get('stages',{}).get('full-source-control')=='context_excluded' else 'Review pending',transform=axes[3].get_yaxis_transform(),va='center',fontsize=8,color='#657080')
    axes[0].set_yticks(range(len(rows)),labels)
    axes[0].invert_yaxis()
    for ax in axes:
        ax.spines[['top','right','left']].set_visible(False)
        ax.spines['bottom'].set_color('#c7ced6')
        ax.tick_params(axis='y',length=0)
        ax.tick_params(axis='x',colors='#4b5563')
        ax.xaxis.grid(True,alpha=.14)
        ax.set_axisbelow(True)
    axes[0].set_xlabel('tokens/second · pp512')
    axes[1].set_xlabel('tokens/second · tg256')
    axes[2].set_xlabel('20 questions');axes[2].set_xlim(0,20);axes[2].set_xticks([0,5,10,15,20])
    axes[3].set_xlabel('16 compound source units');axes[3].set_xlim(0,16);axes[3].set_xticks([0,4,8,12,16])
    axes[1].legend(handles=[Patch(color='#365f9d',label='Depth 0'),Patch(color='#dd9a3c',label='Depth 2048*')],loc='lower left',bbox_to_anchor=(-.04,1.005),ncol=2,frameon=False,fontsize=8,handlelength=1,columnspacing=.8)
    axes[2].legend(handles=[Patch(color=colors[k],label=k.title()) for k in ['correct','partial','contradiction','other']],loc='lower left',bbox_to_anchor=(-.04,1.005),ncol=2,frameon=False,fontsize=7,handlelength=1,columnspacing=.8)
    axes[3].legend(handles=[Patch(color=colors[k],label=k.title()) for k in ['covered','partial','omitted']],loc='lower left',bbox_to_anchor=(-.04,1.005),ncol=2,frameon=False,fontsize=7,handlelength=1,columnspacing=.8)
    fig.text(.035,.125,'Speed: five retained samples; whiskers show within-run sample SD. *Falcon’s longer run, if present, uses depth 1792 and is hatched.',fontsize=9,color='#4b5563')
    fig.text(.035,.085,'Accuracy: Codex (GPT-6), AI-assisted review of frozen supplied OCR; no independent human adjudication. Partial answers have no numeric weight.',fontsize=9,color='#4b5563')
    fig.text(.035,.045,'Coverage measures represented source topics, not correctness. Artifacts differ in quantization and architecture. Pending speed tests are absent; no overall score is computed.',fontsize=9,color='#4b5563')
    fig.savefig(OUT/'speed-and-accuracy.png',dpi=180,facecolor='white')
    fig.savefig(OUT/'speed-and-accuracy.svg',facecolor='white')
    plt.close(fig)
    print('Plotted',len(rows),'accepted Mac speed sessions; unavailable accuracy remains labeled.')


if __name__=='__main__':main()
