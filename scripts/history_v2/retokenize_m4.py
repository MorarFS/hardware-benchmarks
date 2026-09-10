#!/usr/bin/env python3
"""Retokenize saved visible output with the pinned GGUF vocabulary, without inference.

Stream times come from the original requests. This is post-processing, not a rerun.
"""
import argparse,csv,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from mac_runtime import gpu_lock,model_specs,storage_relative
OUT=ROOT/'results/2026-09-10/m4-max/history'
EXE=ROOT/'work/llama-metal/llama-b10852/llama-tokenize'


def aggregate(rows):
    good=[r for r in rows if r['visible_phase_seconds'] is not None]
    tokens=sum(r['visible_tokens_retokenized'] for r in good)
    phase=sum(r['visible_phase_seconds'] for r in good)
    wall=sum(r['wall_seconds'] for r in good)
    return dict(submitted_requests=len(good),visible_tokens=tokens,visible_phase_seconds=phase,total_wall_seconds=wall,visible_phase_tokens_per_second=tokens/phase if phase else None,visible_tokens_per_total_wall_second=tokens/wall if wall else None)


def run(model):
    folder=OUT/model;protocol=json.loads((folder/'protocol.json').read_text());spec=model_specs(ROOT)[model]
    assert protocol['model']==spec
    weights=ROOT/'work'/storage_relative(spec)
    assert weights.is_file()
    if 'file_size_bytes' in spec:assert weights.stat().st_size==spec['file_size_bytes']
    version=subprocess.run([str(EXE),'--version'],capture_output=True,check=True)
    ver=(version.stdout+version.stderr).decode(errors='replace')
    assert '10852' in ver and '050dde50c' in ver,ver
    rows=[];evidence=[]
    for name,status in json.loads((folder/'complete.json').read_text())['stages'].items():
        if status in ['context_excluded','blocked_by_parent']:continue
        record=json.loads((folder/(name+'.json')).read_text());output=record['output']
        events=[json.loads(line) for line in (folder/(name+'-stream.jsonl')).read_text().splitlines()]
        deltas=[(x['elapsed_seconds'],c.get('delta',{}).get('content')) for x in events for c in x['event'].get('choices',[]) if c.get('delta',{}).get('content')]
        assert ''.join(t for _,t in deltas)==output
        command=[str(EXE),'-m',str(weights),'--stdin','--ids','--no-bos','--no-parse-special','--no-escape','--offline']
        result=subprocess.run(command,input=output.encode('utf-8'),capture_output=True,timeout=60)
        if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace')[-2000:])
        ids=json.loads(result.stdout.decode('utf-8'));assert isinstance(ids,list) and all(type(v) is int for v in ids)
        first=deltas[0][0] if deltas else None;last=deltas[-1][0] if deltas else None
        readable=[t for t,s in deltas if s.strip()]
        span=last-first if last is not None and last>first else None
        rows.append(dict(model_id=model,request=name,status=status,visible_tokens_retokenized=len(ids),first_content_delta_seconds=first,first_readable_delta_seconds=readable[0] if readable else None,last_content_delta_seconds=last,visible_phase_seconds=span,wall_seconds=record['wall_seconds'],visible_phase_tokens_per_second=len(ids)/span if span else None,visible_tokens_per_total_wall_second=len(ids)/record['wall_seconds']))
        evidence.append(dict(request=name,output_sha256=hashlib.sha256(output.encode()).hexdigest(),visible_token_ids=ids))
    receipt=dict(model_id=model,model_sha256_from_validated_generation_receipt=spec['sha256'],model_file_bytes=weights.stat().st_size,tokenizer_build='b10852 (050dde50c)',tokenizer_source='https://github.com/ggml-org/llama.cpp/blob/050dde50c/tools/tokenize/tokenize.cpp',flags=['--stdin','--ids','--no-bos','--no-parse-special','--no-escape','--offline'],method='Exact assembled content bytes, including formatting whitespace, retokenized using vocabulary-only loading. No generation, BOS/EOS insertion, special-token parsing or escape conversion. Original validated model receipt identifies the artifact; this post-processing does not rehash all weight tensors.',timing_definition='N divided by original last-minus-first nonempty content-delta arrival time. This boundary-based estimate includes the first delta in N and can differ from server prediction time or Evo SDK metrics. First content can be whitespace; first readable delta is also retained. Network/stream scheduling remains in the interval. Total-wall rate includes prompt processing and any reasoning before visible content.',aggregate_all_submitted=aggregate(rows),aggregate_heldout=aggregate([r for r in rows if not r['request'].startswith('development-')]),requests=evidence)
    (folder/'visible-speed.json').write_text(json.dumps(receipt,indent=2)+'\n')
    with (folder/'visible-speed.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(model,receipt['aggregate_heldout'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('models',nargs='*');parser.add_argument('--evidence-root',type=Path,default=OUT);args=parser.parse_args();OUT=args.evidence_root
    with gpu_lock(ROOT):
        for model in args.models or [p.parent.name for p in sorted(OUT.glob('*/complete.json'))]:run(model)
