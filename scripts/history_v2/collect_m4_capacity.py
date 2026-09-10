#!/usr/bin/env python3
"""Validate the separately labeled M4 native-thinking capacity history profile.

This validates payload provenance and transport records. It never grades truth.
Source judgments must be supplied in a separately reviewed adjudication.json.
"""
import argparse
import getpass
import csv
import json
from pathlib import Path
import re
import sys
import runner as frozen
from mac_prompt_adapter import adapter_receipt, messages

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from mac_runtime import model_specs
DEFAULT_OUT = ROOT / 'results/2026-09-10/m4-max/capacity-history'
PDF_PAGES=r'PDF p\.\s*\d+(?:\s*[,–-]\s*\d+)*'
PDF_MARKER=re.compile(r'(?:\['+PDF_PAGES+r'\]|\('+PDF_PAGES+r'\))')
PAREN_PAGE=re.compile(r'\((?:p\.\s*)?\d{1,3}(?:\s*[,–-]\s*\d{1,3})*\)')


def prose_words(text):
    text=PAREN_PAGE.sub('',PDF_MARKER.sub('',text))
    text=re.sub(r'[*_`#]','',text)
    return sum(any(ch.isalnum() for ch in token) for token in text.split())


def speculation_disabled(value):
    # b10852 appends --spec-type entries to its default [none], so explicit
    # --spec-type none is serialized as "none,none". Reject every active type.
    return isinstance(value,str) and set(value.split(',')) == {'none'}


def validate(folder):
    suite = frozen.load_suite(ROOT / 'experiments/history-v2')
    receipt = frozen.read_json(folder / 'protocol.json')
    assert receipt['model_id']=='qwen235-thinking-iq1s', 'Wrong capacity artifact'
    assert receipt['protocol']['version']=='history-v2-m4-capacity-1.0', 'Not native-thinking profile'
    assert receipt['actual_context']==16384, 'Unexpected capacity context'
    command=frozen.read_json(folder/'server-command.json')
    assert command[command.index('--reasoning')+1]=='auto'
    assert command[command.index('--reasoning-budget')+1]=='512'
    runtime=(folder/'runtime.log').read_text(errors='replace')
    activations=re.findall(r'activated, budget=(\d+) tokens',runtime)
    assert activations and set(activations)=={'512'}, 'Missing or different observed thinking-budget activation'

    assert receipt['fixture_hashes'] == suite['freeze']['files']
    assert receipt['freeze_sha256'] == frozen.sha256(ROOT / 'experiments/history-v2/freeze.json')
    spec = model_specs(ROOT)[receipt['model_id']]
    assert receipt['model'] == spec
    assert receipt.get('message_adapter') == adapter_receipt(receipt['model_id'])
    stages, control = frozen.source_stages(suite)
    expected = {name: (prompt, inputs) for name, prompt, inputs in stages + [control]}
    parents = [h['id'] + '-summary' for h in suite['questions']]
    records = {name: frozen.read_json(folder / (name + '.json')) for name in expected}
    merged = frozen.read_json(folder / 'merged-summary-synthesis.json')
    if merged.get('status') != 'blocked_by_parent':
        material = '\n\n'.join(h['id'] + '\n' + records[h['id'] + '-summary']['output'] for h in suite['questions'])
        expected['merged-summary-synthesis'] = (suite['prompts']['synthesis'].format(source=material), ['prompts.json'])
        records['merged-summary-synthesis'] = merged
        assert merged['parent_requests'] == parents
    metrics = []
    for name, (prompt, inputs) in expected.items():
        record = records[name]
        payload = frozen.read_json(folder / (name + '-request.json'))
        assert payload['messages'] == messages(receipt['model_id'],suite['prompts']['system'],prompt), name
        assert payload['model'] == receipt['model_id']
        assert 'chat_template_kwargs' not in payload and payload['stream'] is True
        assert payload['max_tokens'] == receipt['protocol']['max_output_tokens']
        for key, value in receipt['protocol']['sampling'].items():
            assert payload[key] == value
        assert record['source_files'] == inputs and not any(p.startswith('gold/') for p in inputs)
        assert record['fingerprint'] == frozen.fingerprint(payload)
        if record['status']=='context_excluded':
            assert record['submitted'] is False
            assert not record.get('output') and record.get('usage') is None
            assert record['rendered_prompt_tokens'] + record['output_budget'] + 256 > receipt['actual_context']
            assert not (folder / (name+'-stream.jsonl')).exists()
            assert not (folder / (name+'.md')).exists()
            metrics.append(dict(model_id=receipt['model_id'], request=name, status=record['status'], prompt_tokens=record['rendered_prompt_tokens'], completion_tokens_api=None, reasoning_characters=None, first_visible_seconds=None, last_visible_seconds=None, wall_seconds=None, words_whitespace=None, words_excluding_pdf_markers=None, prose_words_normalized=None, pdf_marker_count=None, parenthesized_numeric_marker_count=None, server_decode_tokens_per_second=None, timing_note='Not submitted: complete prompt plus output and margin exceeds supported actual context. No source truncation.'))
            continue
        assert record['rendered_prompt_tokens'] + record['output_budget'] + 256 <= receipt['actual_context']
        if record['status'] in ['ok', 'capped', 'empty']:
            events = [json.loads(line) for line in (folder / (name + '-stream.jsonl')).read_text().splitlines()]
            observed=[x['event']['__verbose'] for x in events if x['event'].get('__verbose',{}).get('generation_settings')]
            assert observed, 'Missing observed generation settings'
            for info in observed:
                for key,value in receipt['protocol']['sampling'].items():assert info['generation_settings'][key]==value,(name,key)
                assert speculation_disabled(info['generation_settings']['speculative.types'])
                assert info['truncated'] is False
            deltas = [(event['elapsed_seconds'], choice.get('delta', {})) for event in events for choice in event['event'].get('choices', [])]
            visible = [(t, d['content']) for t, d in deltas if d.get('content')]
            assert ''.join(text for _, text in visible) == record['output']
            assert ''.join(d.get('reasoning_content') or '' for _, d in deltas) == record['reasoning_output']
            assert all(info['generation_settings']['generation_prompt'].rstrip().endswith('<think>') for info in observed), 'Missing native open-thinking prefix'
            assert all(info['generation_settings']['reasoning_format']=='deepseek' for info in observed), 'Unexpected reasoning parser'
            if receipt['model_id']=='nemotron-49b':
                assert all(x['generation_settings']['generation_prompt'].endswith('<think>\n\n</think>\n\n') for x in observed)
            assert (folder / (name + '.md')).read_text().rstrip('\n') == record['output'].rstrip('\n')
            assert record['word_count'] == len(record['output'].split())
            if visible:
                assert record['first_visible_seconds'] == visible[0][0]
            words_without_citations = len(PDF_MARKER.sub('', record['output']).split())
            usage = record.get('usage') or {}
            timings = record.get('timings') or {}
            metrics.append(dict(model_id=receipt['model_id'], request=name, status=record['status'], prompt_tokens=record['rendered_prompt_tokens'], completion_tokens_api=usage.get('completion_tokens'), reasoning_characters=len(record['reasoning_output']), first_visible_seconds=record.get('first_visible_seconds'), last_visible_seconds=visible[-1][0] if visible else None, wall_seconds=record['wall_seconds'], words_whitespace=record['word_count'], words_excluding_pdf_markers=words_without_citations, prose_words_normalized=prose_words(record['output']), pdf_marker_count=len(PDF_MARKER.findall(record['output'])), parenthesized_numeric_marker_count=len(PAREN_PAGE.findall(record['output'])), server_decode_tokens_per_second=timings.get('predicted_per_second'), timing_note='Native-thinking capacity request with512-token budget per thinking block,2048-token overall cap,16K context and prefix reuse; downloads continued. API completion tokens can include control tokens. Not matched synthetic throughput or factual accuracy. Normalized prose removes PDF markers, numeric parenthetical references, Markdown styling and punctuation-only tokens. Parenthesized numbers can be ambiguous; source support requires separate review.'))
    assert all(x['status'] in ['ok', 'capped', 'empty', 'context_excluded'] for x in records.values()), 'Incomplete/error run needs explicit failure reporting'
    with (folder / 'memory.csv').open() as stream:
        memory = list(csv.DictReader(stream))
    assert memory and all(row['ac_connected'] == 'True' for row in memory)
    loaded=frozen.read_json(folder / 'load.json')
    assert loaded['full_layer_offload'] and loaded['context']==receipt['actual_context']
    if 'prompt_cache_ram_mib' in receipt:
        assert loaded['prompt_cache_ram_mib']==receipt['prompt_cache_ram_mib']
        command=frozen.read_json(folder/'server-command.json')
        assert command[command.index('--cache-ram')+1]==str(receipt['prompt_cache_ram_mib'])
    terminal=frozen.read_json(folder / 'complete.json')['stages']
    assert all(terminal[name]==record['status'] for name,record in records.items())
    return metrics


def collect(folder, output):
    metrics = validate(folder)
    output.mkdir(parents=True, exist_ok=True)
    # Raw debug logs can contain private paths. Publish only selected evidence.
    for src in folder.iterdir():
        if src.suffix not in ['.json', '.jsonl', '.md', '.csv', '.txt']:
            continue
        content = src.read_text()
        private_pattern=r'/Users/|Serial Number|\b'+re.escape(getpass.getuser())+r'\b'
        if re.search(private_pattern, content):
            raise RuntimeError('Private field requires review: ' + src.name)
        dst = output / src.name
        if dst.exists() and dst.read_text() != content:
            raise RuntimeError('Refusing to replace differing evidence: ' + str(dst))
        dst.write_text(content)
    with (output / 'request-metrics.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(metrics[0]))
        writer.writeheader()
        writer.writerows(metrics)
    settings=[]
    for path in sorted(folder.glob('*-stream.jsonl')):
        for line in path.read_text().splitlines():
            meta=json.loads(line)['event'].get('__verbose',{})
            if meta.get('generation_settings'):
                settings.append({'request':path.name.removesuffix('-stream.jsonl'),'generation_settings':meta['generation_settings'],'truncated':meta['truncated'],'stop_type':meta.get('stop_type'),'tokens_evaluated':meta.get('tokens_evaluated'),'tokens_predicted':meta.get('tokens_predicted')})
    (output/'observed-request-settings.json').write_text(json.dumps(settings,indent=2)+'\n')
    log=(folder/'runtime.log').read_text(encoding='utf-8',errors='replace')
    limits=re.findall(r'prompt cache is enabled, size limit: (\d+) MiB',log)
    assert limits and len(set(limits))==1, 'Missing or changing observed RAM prompt-cache limit'
    cache_states=re.findall(r' - cache state: (\d+) prompts, ([\d.]+) MiB',log)
    cache={'observed_limit_mib':int(limits[0]),'peak_logged_cache_mib':max((float(size) for _,size in cache_states),default=0),'peak_logged_prompt_count':max((int(n) for n,_ in cache_states),default=0),'note':'Runtime RAM prompt-cache estimate, not an additional independent memory pool to add to RSS. Global cache differs from within-slot prefix reuse and GPU KV storage.'}
    (output/'prompt-cache-summary.json').write_text(json.dumps(cache,indent=2)+'\n')
    budget={'requested_tokens_per_thinking_block':512,'overall_output_token_cap':2048,'observed_activation_count':len(re.findall(r'activated, budget=512 tokens',log)),'forced_end_count':len(re.findall(r'budget exhausted, forcing end sequence',log)),'utf8_wait_count':len(re.findall(r'budget exhausted, waiting for UTF-8 completion',log)),'natural_end_count':len(re.findall(r'deactivated \(natural end\)',log)),'sources':['https://github.com/ggml-org/llama.cpp/blob/050dde50c/common/arg.cpp','https://github.com/ggml-org/llama.cpp/blob/050dde50c/common/reasoning-budget.cpp'],'note':'Budget restarts for a new thinking block and may finish a UTF-8 sequence before forcing closing tokens. This is distinct from the total output cap and from visible answer tokens.'}
    (output/'thinking-budget.json').write_text(json.dumps(budget,indent=2)+'\n')
    print('Validated and collected', len(metrics), 'native-thinking requests:', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model_id')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    collect(args.source or ROOT / 'local-results' / ('history-v2-mac-' + args.model_id), args.output or DEFAULT_OUT / args.model_id)
