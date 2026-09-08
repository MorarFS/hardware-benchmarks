#!/usr/bin/env python3
"""Build comparison tables from measured speed files and reviewed source ledgers.

This script does not evaluate factual accuracy or infer scores for pending runs.
"""
import csv
import json
from pathlib import Path
import re
from collections import Counter
from mac_runtime import model_specs

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/2026-09-08/mac'
BASE=ROOT/'results/2026-09-08'


def read(path):return json.loads(path.read_text())


def model_inventory(specs,fits):
    moe={
        'gemma4-26b':(3.8,'https://huggingface.co/google/gemma-4-26B-A4B-it'),
        'evo-gemma26':(3.8,'https://huggingface.co/google/gemma-4-26B-A4B-it'),
        'qwen36-35b':(3,'https://huggingface.co/Qwen/Qwen3.6-35B-A3B'),
        'evo-qwen35-community':(3,'https://huggingface.co/Qwen/Qwen3.6-35B-A3B'),
        'evo-qwen35-mtp-off':(3,'https://huggingface.co/Qwen/Qwen3.6-35B-A3B'),
        'qwen35-122b-iq2xxs':(10,'https://huggingface.co/Qwen/Qwen3.5-122B-A10B')}
    rows=[]
    for model,spec in specs.items():
        measured=[f for f in fits if f['model_id']==model and f['depth']==0]
        observed=[read(OUT/(f['run']+'.json'))[0] for f in measured]
        if observed:assert len({(r['model_n_params'],r['model_size']) for r in observed})==1
        row=dict(model_id=model,name=spec.get('name',spec['filename']),repository=spec['repository'],revision=spec['revision'],filename=spec['filename'],sha256=spec['sha256'],file_bytes=spec.get('file_size_bytes',5027783488 if model=='qwen3-8b' else None),observed_tensor_parameters=observed[0]['model_n_params'] if observed else None,observed_tensor_bytes=observed[0]['model_size'] if observed else None,observed_runtime_model_type=observed[0]['model_type'] if observed else None,architecture='MoE' if model in moe else 'Dense',reported_active_parameters_billions=moe[model][0] if model in moe else None,active_parameter_source=moe[model][1] if model in moe else None,measurement_files=[f['run']+'.json' for f in measured])
        rows.append(row)
    (OUT/'model-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
    lines=['# Mac artifact and parameter inventory','','Exact file identities are retained below and in the [JSON inventory](model-inventory.json). Total tensor parameters and tensor bytes come from accepted llama-bench output; file bytes include headers/tokenizer metadata and therefore differ. Pending measurements are not filled from a similarly named artifact. No image/audio projector is loaded in these text tests.','','The MoE active figures are rounded model-author descriptions, not measured per-token FLOPs: [Gemma26](https://huggingface.co/google/gemma-4-26B-A4B-it) reports 3.8B, [Qwen35](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) 3B, and [Qwen122](https://huggingface.co/Qwen/Qwen3.5-122B-A10B) 10B. Dense models have no sparse-expert active subset to report here. Branded model sizes can differ from exact language-model tensor counts; the names remain unchanged. An MTP-containing file does not mean MTP was enabled: all Mac runs disable speculative decoding.','','| Artifact / pinned source | Architecture | Observed tensor parameters | Author-reported active parameters | File bytes | File GiB |','| --- | --- | ---: | --- | ---: | ---: |']
    for row in rows:
        model=row['model_id'];url='https://huggingface.co/'+row['repository']+'/tree/'+row['revision'];count=f"{row['observed_tensor_parameters']:,}" if row['observed_tensor_parameters'] else 'Pending'
        active=str(row['reported_active_parameters_billions'])+'B' if row['architecture']=='MoE' else 'Dense; no sparse subset'
        lines.append(f"| [{model}]({url}) | {row['architecture']} | {count} | {active} | {row['file_bytes']:,} | {row['file_bytes']/2**30:.2f} |")
    lines+=['','SHA-256 values and exact filenames are in the JSON inventory and manifests. Actual history contexts, RAM prompt-cache limits, offload and memory measurements are in the [memory report](memory-summary.md). A short-context capacity result does not establish support for the full history workload.']
    (OUT/'model-inventory.md').write_text('\n'.join(lines)+'\n')


def campaign_index(specs,speed,accuracy):
    measured={r['model_id']:r for r in speed if r['machine_backend']=='M5 Pro / Metal' and {'pp512','tg0'}.issubset(r['values']) and any(k in r['values'] for k in ['tg2048','tg1792'])}
    reviewed={r['model_id']:r for r in accuracy if 'extraction' in r}
    lines=['# Apple M5 Pro: speed and source fidelity','',f"The campaign contains {len(specs)} selected artifacts. Repeated synthetic speed is collected for {len(measured)}; frozen-source outputs are adjudicated for {len(reviewed)}. A partial battery or context exclusion remains explicit. The [main Mac report](../../../MAC-M5-PRO.md) records the verified 48 GiB computer, runtime, capacity findings and reproduction commands.",'','## Joint view of separate measurements','','Visible-phase speed retokenizes the actual held-out outputs and uses the original stream intervals. Request-wall rate includes prompt processing but excludes server startup, preflight tokenization calls and pauses between requests. These are separate from synthetic generation, whose five-sample means and standard deviations are in the [matched speed table](matched-speed-comparison.md). Extraction includes four absent-answer questions within 20; partial answers receive no numeric credit. Full-source coverage measures represented source topics, not their correctness.','','| Artifact | Synthetic generation depth 0 / 2048, tokens/s | Visible phase tokens/s | Tokens / request wall second | Extraction: correct / partial / other, out of 20 | Full source: covered / partial / omitted, out of 16 |','| --- | --- | ---: | ---: | --- | --- |']
    for model in specs:
        v=measured.get(model,{}).get('values',{});throughput='Pending'
        if v:
            long=v.get('tg2048',v.get('tg1792'));throughput=f"{v['tg0']['mean']:.2f} / {long['mean']:.2f}"+(' at 1792*' if 'tg1792'in v else '')
        phase=wall='—';path=OUT/'accuracy'/model/'visible-speed.json'
        if path.exists():
            a=read(path)['aggregate_heldout'];phase=f"{a['visible_phase_tokens_per_second']:.2f}";wall=f"{a['visible_tokens_per_total_wall_second']:.2f}"
        r=reviewed.get(model);answers=coverage='Pending'
        if r:
            c=r['extraction'];answers=f"{c.get('correct',0)} / {c.get('partial',0)} / {sum(n for k,n in c.items() if k not in ['correct','partial'])}"
            u=r['coverage'].get('full-source-control',{});coverage=' / '.join(str(u.get(k,0)) for k in ['covered','partial','omitted']) if u else 'Not submitted'
        if model=='falcon180b-chat-iq1s':answers=coverage='Context exclusion'
        lines.append(f'| {model} | {throughput} | {phase} | {wall} | {answers} | {coverage} |')
    lines+=['','*Falcon’s longer depth is 1792 within its supported 2048-token context. Gemma2’s full-source control was not submitted because the complete prompt plus output allowance exceeds 8,192 tokens. Its other 11 requests completed. Missing coverage is not scored as 16 omissions. The separate delayed Gemma26 speed repeat remains in the speed table without pooling.','','The target is **above 40 visible generated tokens/sec**, with source fidelity assessed separately. A rate above 40 does not remove contradictions, unsupported additions, citation errors, lost qualifications or summary omissions. The [accuracy report](accuracy/README.md) includes these distinctions, exact counts, word limits, waiting times and per-request timing. Judgments are **Codex (GPT-6), AI-assisted source review without independent human adjudication**, against the supplied Oman OCR rather than modern historical truth.','','## Evidence and reproduction','','- [Matched synthetic speed, including Evo/Arc/laptop rows](matched-speed-comparison.md) and [raw Mac summary CSV](summary.csv).','- [Accuracy report](accuracy/README.md), [per-artifact states](accuracy/scoreboard.md), exact requests, streams, outputs and source ledgers in each model directory.','- [Artifact hashes, bytes and parameter counts](model-inventory.md).','- [Observed memory, offload and failed configurations](memory-summary.md); [capacity candidate inventory](capacity-candidates.json).','- [Frozen Mac delivery and grading protocol](../../../experiments/history-v2-mac/README.md).','','![Measured synthetic speed and source fidelity](speed-and-accuracy.png)','','The four-panel chart keeps speed, extraction and coverage separate. Raw evidence is immutable during collection; report tables can be regenerated with `python3 scripts/report-mac.py`, and the chart with `python3 scripts/plot-mac.py` using Matplotlib. See the main report for acquisition, generation, validation and retokenization commands. Exact weight matches permit matched speed comparisons; differing history settings and grading conventions prevent unadjusted accuracy counts from isolating hardware effects.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')


def accuracy_report(accuracy):
    reviewed=[r for r in accuracy if 'extraction' in r]
    lines=['# Mac source-fidelity accuracy results','','Both speed and accuracy are measured. See the [complete accuracy scoreboard](scoreboard.md) for every artifact’s current state and the [matched speed comparison](../matched-speed-comparison.md) for repeated synthetic throughput. Pending models have no inferred accuracy score.','','The [frozen protocol](../../../../experiments/history-v2-mac/README.md) supplies four passages, 20 extraction questions including four source-absent items, four direct summaries, synthesis from those summaries and an independent full-source control. Two development requests are excluded from scores. **Evaluator: Codex (GPT-6), AI-assisted source adjudication, without independent human review.** This measures fidelity to the supplied Charles Oman OCR, not modern historical truth or general model accuracy. One generation per request/configuration is retained.','','## Extraction, citations and quotations','','A correct answer can have an incorrect page citation. Partial answers receive no numeric weight. The source-absent items are included in 20 and shown separately out of 4 in the scoreboard. Complete answers include their supporting quotations. Explicit-quotation counts measure marking, not guaranteed verbatim fidelity; reordered or altered quotations are noted in individual reviews.','','| Artifact / source ledger | Correct | Partial | Contradiction | Other categories | Fully supported citations /16 | Explicit quotations /16 |','| --- | ---: | ---: | ---: | --- | ---: | ---: |']
    ledgers={}
    for row in reviewed:
        model=row['model_id'];ledger=read(OUT/'accuracy'/model/'adjudication.json');ledgers[model]=ledger;c=row['extraction']
        other=', '.join(k+': '+str(v) for k,v in c.items() if k not in ['correct','partial','contradiction']) or '0'
        citation=sum(x['citation_judgment']=='supported' for x in ledger['extraction'])
        quotes=sum(x['quotation_form']=='explicit' for x in ledger['extraction'])
        lines.append(f"| [{model}]({model}/adjudication.json) | {c.get('correct',0)} | {c.get('partial',0)} | {c.get('contradiction',0)} | {other} | {citation} | {quotes} |")
    lines+=['','The ledgers retain each answer, source pages, citation category, quotation form and rationale. In the common Mac completeness convention, H3-Q3 requires both removal stages and H4-Q2 requires the uncle/brother relationships. An added unsupported detail or lost numeric bound can change a judgment even when the requested name is correct. A quotation can supply a qualifier missing from the answer’s first sentence. These conventions are stated to make the judgments reviewable.','','Development outputs receive separate `development-review.json` files with source judgments and output hashes. They remain excluded from held-out counts. Reviews of completed stages from failed configurations stay with the diagnostic evidence; an incomplete run receives no full-battery score.','','## Summary coverage and claim flags','','Coverage has 16 predeclared compound units. A unit can be covered even when a represented claim is wrong; the claim ledger records that separately. Omissions, ambiguous wording, citation drift and clear claim errors are distinct. Error families link a direct error to its propagation or independent recurrence. Counts are not standardized atomic-claim precision rates and should not be ranked as such.','','| Artifact | Four direct summaries: covered / partial / omitted | Merged: covered / partial / omitted | Full source: covered / partial / omitted | Unique clear families | Manifestations |','| --- | --- | --- | --- | ---: | ---: |']
    for model,ledger in ledgers.items():
        cv=ledger['summary']['coverage_by_stage'];direct=Counter()
        for p in ['H1','H2','H3','H4']:direct.update(cv.get(p+'-summary',{}))
        def triple(v):return ' / '.join(str(v.get(k,0)) for k in ['covered','partial','omitted']) if v else 'Not submitted'
        lines.append(f"| {model} | {triple(direct)} | {triple(cv.get('merged-summary-synthesis',{}))} | {triple(cv.get('full-source-control',{}))} | {ledger['summary']['unique_clear_error_families']} | {ledger['summary']['clear_error_manifestations']} |")
    lines+=['','Extraction scores alone do not show whether a model preserves the source in a longer response. Read each ledger’s synthesis review for propagated errors and lost coverage. A short or prematurely self-ended control can omit whole passages without reaching its output cap; that remains an observed omission, not a context exclusion. Context-excluded stages were never submitted and receive no omission score.','','## Length and application timing','','Normalized prose words remove PDF citation groups, numeric parenthetical references, Markdown styling and punctuation-only tokens before counting whitespace-separated tokens containing letters or numbers. This declared format metric differs from raw whitespace counts, which are also retained. Numeric parentheses can be ambiguous; manual citation review remains necessary. Page references expressed in prose remain in the prose count.','','| Artifact | H1 words | H2 words | H3 words | H4 words | Merged words | Full-source words | Full-source first content delta / total seconds |','| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for model in ledgers:
        metrics={r['request']:r for r in csv.DictReader((OUT/'accuracy'/model/'request-metrics.csv').open())}
        stages=['H1-summary','H2-summary','H3-summary','H4-summary','merged-summary-synthesis','full-source-control']
        words=[metrics.get(s,{}).get('prose_words_normalized','') or '—' for s in stages]
        ctrl=metrics.get('full-source-control',{});timing='—'
        if ctrl.get('first_visible_seconds') and ctrl.get('wall_seconds'):timing=f"{float(ctrl['first_visible_seconds']):.2f} / {float(ctrl['wall_seconds']):.2f}"
        lines.append('| ['+model+']('+model+'/request-metrics.csv) | '+' | '.join(words+[timing])+' |')
    lines+=['','Requested lengths are 180–220 words per direct summary and 350–450 per synthesis/control. Length compliance is not factual accuracy. Application timing includes prompt processing, actual response length and common-prefix cache reuse; model downloads may continue. It is separate from the matched synthetic speed measurements, whose inference intervals suspend this workspace’s download/hash workers. Per-request CSVs include token counts, first nonempty content delta (including whitespace), total time and server decode throughput. The legacy field name is first_visible_seconds; it need not be the first readable word.']
    lines+=['','## Visible output speed and the 40-token target','','The user’s target is above 40 visible generated tokens per second. The following rates retokenize exact assembled output bytes with the same GGUF vocabulary using the pinned [vocabulary-only tokenizer](https://github.com/ggml-org/llama.cpp/blob/050dde50c/tools/tokenize/tokenize.cpp). No model generation is repeated. BOS/EOS insertion, special-token parsing and escape conversion are disabled. Counts include visible formatting whitespace and exclude API-only reasoning/control tokens.','','Visible-phase rate is total retokenized tokens divided by the sum of last-minus-first nonempty content-delta intervals. It is a stream-boundary estimate, includes the first delta in the numerator and can include network scheduling; the first delta can be whitespace. First readable-delta delays are also retained in each CSV. Request-wall rate divides by the sum of generation-request wall times, including prompt processing and completion. It excludes server startup, preflight tokenization calls and pauses between requests. These measures differ from synthetic throughput, server prediction time and Evo’s SDK method. Development requests are excluded from this table.','','| Artifact / evidence | Submitted held-out requests | Visible-phase tokens/s | Tokens / request wall second | Above 40 in visible phase |','| --- | ---: | ---: | ---: | --- |']
    for model in ledgers:
        path=OUT/'accuracy'/model/'visible-speed.json'
        if not path.exists():
            lines.append(f'| {model} | — | — | — | Post-processing pending |');continue
        a=read(path)['aggregate_heldout'];phase=a['visible_phase_tokens_per_second'];wall=a['visible_tokens_per_total_wall_second']
        lines.append(f"| [{model}]({model}/visible-speed.csv) | {a['submitted_requests']} | {phase:.2f} | {wall:.2f} | {'Yes' if phase>40 else 'No'} |")
    lines+=['','Passing the speed target is not an accuracy pass. Actual outputs, citation failures, omissions, context exclusions and word-limit compliance remain separate. These are one-battery application observations, without repeated-battery uncertainty estimates.','','## Evidence and interpretation','','Each model directory retains exact requests, timestamped raw stream data events, assembled outputs, finish reasons, observed runtime sampling/speculation settings, memory samples and full-offload evidence. The generator verifies completion of the stream; collection independently reconstructs payloads from frozen fixtures, checks hashes and stream/output agreement, and confirms observed settings. Gold never enters the model requests. Source judgments are separate files and are not generated by the metric collector.','','Falcon 180B Chat’s supported 2048-token context cannot fit this complete battery plus the output allowance. It receives separate speed/capacity/coherence checks. Gemma2 uses 8192 tokens and explicitly excludes only stages whose complete prompts cannot fit. Other load or memory failures are reported as failures, never fabricated accuracy scores.','','The published Arc and Evo ledgers use some different completeness conventions and configurations. Unadjusted counts do not establish cross-computer accuracy differences. Exact weight matches support the speed comparison; they do not remove differences in context, templates, reasoning/MTP settings, outputs or evaluator conventions.']
    (OUT/'accuracy/README.md').write_text('\n'.join(lines)+'\n')


def memory_report(fits,accuracy):
    lines=['# Mac sampled memory evidence','','RSS is process resident memory, not a dedicated GPU-memory counter. System swap/compression includes other apps and must not be attributed entirely to inference. Sampling every approximately two seconds can miss short peaks. Do not add RSS to Metal allocations as separate pools. Passing the 1 GiB swap-growth guard is not a zero-swap result.','','## Accepted speed runs','','| Run | Peak process RSS GiB | System swap before MiB | Peak swap MiB | Swap growth MiB | Compressor before / peak GiB | Full offload / all samples AC |','| --- | ---: | ---: | ---: | ---: | --- | --- |']
    for fit in fits:
        lines.append(f"| {fit['run']} | {fit['peak_process_rss_bytes']/2**30:.2f} | {fit['swap_before_bytes']/2**20:.2f} | {fit['peak_system_swap_bytes']/2**20:.2f} | {fit['swap_growth_bytes']/2**20:.2f} | {fit['compressor_before_bytes']/2**30:.2f} / {fit['peak_system_compressor_bytes']/2**30:.2f} | {fit['full_layer_offload']} / {fit['all_samples_ac']} |")
    lines+=['','Raw speed memory CSVs and filtered runtime allocations accompany each run. The [machine-readable fit summary](fit-summary.json) also retains wall time including loading, which differs from timed token throughput.','','## Completed history generation','','| Artifact | Context tokens | Server ready seconds | RAM prompt-cache limit MiB | Peak server RSS GiB | System swap before MiB | Peak swap MiB | Growth MiB |','| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in accuracy:
        model=row['model_id'];folder=OUT/'accuracy'/model
        if not (folder/'complete.json').exists():continue
        ready=read(folder/'load.json')['ready_seconds']
        m=read(folder/'memory-summary.json');before=m['before']['swap_used_bytes'];peak=m['peak_swap_used_bytes']
        cache=read(folder/'prompt-cache-summary.json')['observed_limit_mib'] if (folder/'prompt-cache-summary.json').exists() else 'Uncollected'
        lines.append(f"| [{model}](accuracy/{model}/memory-summary.json) | {row['actual_context']} | {ready:.2f} | {cache} | {m['peak_process_rss_bytes']/2**30:.2f} | {before/2**20:.2f} | {peak/2**20:.2f} | {max(0,peak-before)/2**20:.2f} |")
    lines+=['','Server-ready time ends at a health check polled about every two seconds; with mmap/lazy loading and filesystem caching, it is not proof that every weight page has been read or a controlled cold-load measurement. Accuracy uses the declared larger application context and may overlap model downloads. Its memory load differs from the short synthetic benchmark. Complete generation is not an accuracy pass; see [the source review](accuracy/README.md).']
    failures=[]
    for p in sorted((OUT/'diagnostic').glob('*/failure.json')):
        folder=p.parent
        if not (folder/'memory-summary.json').exists():continue
        failure=read(p);m=read(folder/'memory-summary.json');protocol=read(folder/'protocol.json')
        failures.append((folder,failure,m,protocol))
    if failures:
        lines+=['','## Failed history configurations','','These failures receive no full-battery accuracy score. Context changes are separate configurations with new receipts.','','| Evidence | Context | Failed stage / reason | Swap before / peak during / after cleanup MiB |','| --- | ---: | --- | --- |']
        for folder,failure,m,protocol in failures:
            swap=' / '.join(f'{n/2**20:.2f}' for n in [m['before']['swap_used_bytes'],m['peak_swap_used_bytes'],m['after']['swap_used_bytes']])
            lines.append(f"| [{protocol['model_id']}]({folder.relative_to(OUT)}/failure.json) | {protocol['actual_context']} | {failure['stage']}: {failure['error']} | {swap} |")
    (OUT/'memory-summary.md').write_text('\n'.join(lines)+'\n')


def rates(paths):
    values={}
    for path in paths:
        if not path.exists() or not path.read_text().strip():continue
        for e in read(path):
            required={'build_commit':'050dde50c','n_batch':512,'n_ubatch':512,'n_threads':10,'type_k':'f16','type_v':'f16','n_gpu_layers':99,'split_mode':'none','flash_attn':1,'n_cpu_moe':0}
            for k,v in required.items():assert e[k]==v,(path.name,k,e[k],v)
            assert len(e['samples_ns'])==5
            key='pp512' if e['n_prompt']==512 else 'tg'+str(e['n_depth'])
            assert key not in values,(path,key)
            values[key]={'mean':e['avg_ts'],'sd':e['stddev_ts'],'source':str(path.relative_to(ROOT))}
    return values


def main():
    specs=model_specs(ROOT)
    rows=[]
    def add(model,machine,paths,note=''):
        values=rates(paths)
        rows.append({'model_id':model,'machine_backend':machine,'sha256':specs[model]['sha256'],'values':values,'note':note or ('Measured' if values else 'No accepted measured result')})
    fits=read(OUT/'fit-summary.json')
    groups={}
    for fit in fits:
        session=re.sub(r'-depth\d+$','',fit['run'])
        groups.setdefault((fit['model_id'],session),[]).append(OUT/(fit['run']+'.json'))
    for (model,session),paths in groups.items():
        suffix=' (delayed repeat)' if 'delayed-repeat' in session else ''
        note='Five retained samples; see memory/offload evidence.'
        if model=='gemma4-26b' and not suffix:note='Clean run following history accuracy workload; declining samples retained. Separate first attempt excluded for overlapping I/O.'
        if model=='falcon180b-chat-iq1s':note='Longer generation uses depth1792 within supported 2048 context; not depth2048.'
        add(model,'M5 Pro / Metal'+suffix,paths,note)
    # Arc artifact receipts agree with the unchanged shared original manifest.
    for source in read(BASE/'modern/model-sources.json'):
        assert source['source']['sha256']==specs[source['model_id']]['sha256']
    for model in ['gemma4-26b','qwen36-35b','qwen38-27b']:
        add(model,'Arc Pro B70 / SYCL',[BASE/'modern'/('intel-sycl-'+model+'-depth'+str(d)+'.json') for d in [0,2048]])
    add('nemotron-49b','Arc Pro B70 / SYCL',[BASE/'capacity'/('intel-sycl-49b-depth'+str(d)+'.json') for d in [0,2048]])
    for name,label in [('intel-sycl','Arc Pro B70 / SYCL, initial'),('intel-sycl-repeat','Arc Pro B70 / SYCL, repeat'),('intel-vulkan','Arc Pro B70 / Vulkan, initial'),('intel-vulkan-repeat','Arc Pro B70 / Vulkan, repeat'),('nvidia-cuda','RTX5060 Laptop / CUDA'),('nvidia-vulkan','RTX5060 Laptop / Vulkan')]:
        add('qwen3-8b',label,[BASE/(name+'-depth'+str(d)+'.json') for d in [0,2048]])
    add('qwen3-8b','Evo X3 / Vulkan',[BASE/'evo/raw/synthetic-qwen8/vulkan'/('depth'+str(d)+'.json') for d in [0,2048]])
    for model,spec in specs.items():
        if 'evo_matrix_id' not in spec:continue
        folder=BASE/'evo/raw/vulkan-model-matrix'/spec['evo_matrix_id']
        files=read(folder/'model-files.json')
        assert len(files)==1 and files[0]['sha256']==spec['sha256'] and files[0]['bytes']==spec['file_size_bytes']
        add(model,'Evo X3 / Vulkan',[folder/('depth'+str(d)+'.json') for d in [0,2048]],'Loading timeout before measured inference' if (folder/'error.json').exists() else '')
    (OUT/'matched-speed-comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
    def fmt(v):return f"{v['mean']:.2f} ± {v['sd']:.2f}" if v else '—'
    lines=['# Matched-artifact speed comparison','','Every row uses b10852, five samples, default warmup, FP16 K/V, flash attention, ten threads and batch/microbatch 512. Means ± sample SD are tokens/s. Model IDs distinguish different artifacts with similar names. Compare computer/backend rows within the same ID; different IDs can have different quantizers, MTP tensors or file sizes. All individual samples and source paths remain in [the JSON table](matched-speed-comparison.json).','','| Artifact ID | Computer / backend | pp512 | tg256, depth0 | tg256, depth2048 | Note |','| --- | --- | ---: | ---: | ---: | --- |']
    for model in specs:
        matched=[r for r in rows if r['model_id']==model]
        if not matched:continue
        for row in matched:
            v=row['values'];note=row['note']
            if 'tg1792' in v:note+=' Depth1792: '+fmt(v['tg1792'])+' tokens/s.'
            lines.append('| '+model+' | '+row['machine_backend']+' | '+fmt(v.get('pp512'))+' | '+fmt(v.get('tg0'))+' | '+fmt(v.get('tg2048'))+' | '+note+' |')
    lines+=['','Missing Mac rows remain pending or explicitly excluded; a reference row is not a Mac result. The first Gemma Mac attempt is retained under diagnostic/ and excluded from this table because repository checkout and a resumed transfer overlapped it. Gemma’s clean post-accuracy samples decline; temperatures/frequencies were not measured and no thermal cause is established. A separately labeled delayed repeat, when available, is not pooled with it.','','The Evo exact GPT-OSS120, Qwen3.8 Flash Next and DeepSeek V4 Flash artifacts exceed physical Mac memory in weights alone. See [the crosswalk](evo-artifact-crosswalk.json). These preflight exclusions do not establish a largest possible model. All-layer offload permits CPU work and host allocations; use per-run memory evidence. These are complete-system/backend comparisons, with uncontrolled cache, thermal and ordinary desktop background conditions.']
    (OUT/'matched-speed-comparison.md').write_text('\n'.join(lines)+'\n')
    accuracy=[]
    for model,spec in specs.items():
        folder=OUT/'accuracy'/model
        item={'model_id':model,'sha256':spec['sha256'],'state':'pending'}
        if model=='nemotron-49b' and (OUT/'diagnostic/nemotron-context32768-memory/failure.json').exists():item['state']='32768-context memory failure; explicit16384 recovery pending'
        if model=='falcon180b-chat-iq1s':item['state']='context exclusion: supported 2048 cannot contain complete frozen passages and output'
        if (folder/'complete.json').exists():
            terminal=read(folder/'complete.json')
            item.update(state='generated; source adjudication pending',stages=terminal['stages'],actual_context=read(folder/'protocol.json')['actual_context'])
        if (folder/'adjudication.json').exists():
            ledger=read(folder/'adjudication.json');a=ledger['extraction'];assert len(a)==20
            counts=dict(__import__('collections').Counter(x['judgment'] for x in a))
            assert counts==ledger['summary']['extraction_categories']
            state='source adjudicated'
            statuses=set(item.get('stages',{}).values())
            if statuses & {'context_excluded','blocked_by_parent'}:state+='; partial battery'
            if 'capped' in statuses:state+='; output cap reached'
            if 'empty' in statuses:state+='; empty output'
            item.update(state=state,extraction=counts,source_absent_correct=ledger['summary']['source_absent_correct'],coverage=ledger['summary']['coverage_by_stage'],ledger=str((folder/'adjudication.json').relative_to(ROOT)))
        accuracy.append(item)
    (OUT/'accuracy/scoreboard.json').write_text(json.dumps(accuracy,indent=2)+'\n')
    lines=['# Mac history accuracy scoreboard','','Codex (GPT-6), AI-assisted source review; no independent human adjudication. Same frozen source tasks and acceptable variants. Counts measure fidelity to supplied OCR, not modern historical truth or general accuracy. Citation support and quotation compliance are separate. Source-absent items are included in the 20-question denominator and also shown out of 4. Partial answers are not assigned a numeric weight.','','| Artifact ID | Correct /20 | Partial /20 | Contradiction /20 | Other /20 | Correct absent /4 | Full-source coverage: covered / partial / omitted | State |','| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |']
    for row in accuracy:
        c=row.get('extraction');coverage=row.get('coverage',{}).get('full-source-control',{})
        values=[str(c.get(k,0)) for k in ['correct','partial','contradiction']] if c else ['—']*3
        other=str(sum(v for k,v in c.items() if k not in ['correct','partial','contradiction'])) if c else '—'
        units=' / '.join(str(coverage.get(k,0)) for k in ['covered','partial','omitted']) if coverage else '—'
        lines.append('| '+row['model_id']+' | '+' | '.join(values+[other,str(row.get('source_absent_correct','—')),units,row['state']])+' |')
    lines+=['','All three count columns for coverage total 16 units when that stage is adjudicated. A context-excluded control must not receive 16 omissions: it was not submitted. Pending generation/review is not an accuracy score. See model directories for exact requests, outputs, telemetry, source anchors and separate citation findings.','','The published Arc and Evo ledgers use some different completeness conventions and configurations. Their unadjusted counts must not be interpreted as calibrated cross-computer accuracy differences. Cross-machine weight matches are documented in the speed table; histories also differ in context and some original MTP/reasoning settings.']
    (OUT/'accuracy/scoreboard.md').write_text('\n'.join(lines)+'\n')
    accuracy_report(accuracy)
    memory_report(fits,accuracy)
    model_inventory(specs,fits)
    campaign_index(specs,rows,accuracy)
    print('Generated',len(rows),'speed comparison rows and',sum('extraction'in x for x in accuracy),'adjudicated accuracy rows')


if __name__=='__main__':main()
