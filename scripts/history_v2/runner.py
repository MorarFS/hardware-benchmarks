#!/usr/bin/env python3
"""Run the frozen history-v2 source-fidelity pilot through LM Studio's native API.
Python 3.10+, standard library only. No model downloads, loading, or factual judge.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

DEFAULT_SUITE = Path(__file__).resolve().parents[2] / 'experiments' / 'history-v2'

def now():
    return datetime.now(timezone.utc).isoformat()

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def load_suite(root):
    """Gold is hashed as bytes here, never parsed or passed to the generator."""
    root = Path(root).resolve()
    freeze = read_json(root / 'freeze.json')
    for name, expected in freeze['files'].items():
        path = (root / name).resolve()
        if root not in path.parents or sha256(path) != expected:
            raise ValueError('Frozen fixture mismatch: ' + name)
    suite = {'freeze': freeze}
    for key, name in [('config', 'configurations.json'), ('prompts', 'prompts.json'),
                      ('questions', 'questions.json'), ('development', 'development-questions.json')]:
        suite[key] = read_json(root / name)
    suite['sources'] = {}
    for name in ['inputs/development.txt'] + [h['source_file'] for h in suite['questions']]:
        if not name.startswith('inputs/') or (root / name).resolve().parent != root / 'inputs':
            raise ValueError('Source outside inputs allowlist: ' + name)
        suite['sources'][name] = (root / name).read_text(encoding='utf-8')
    if len(suite['questions']) != 4 or sum(len(h['questions']) for h in suite['questions']) != 20:
        raise ValueError('Expected four passages and 20 fixed questions')
    return suite

def question_text(questions):
    return '\n'.join(q['id'] + ': ' + q['question'] for q in questions)

def source_stages(suite):
    p, sources = suite['prompts'], suite['sources']
    dev = sources['inputs/development.txt']
    stages = [
        ('development-extraction', p['extraction'].format(questions=question_text(suite['development']), source=dev), ['prompts.json', 'development-questions.json', 'inputs/development.txt']),
        ('development-summary', p['summary'].format(source=dev), ['prompts.json', 'inputs/development.txt'])]
    for h in suite['questions']:
        source = sources[h['source_file']]
        stages += [
            (h['id'] + '-extraction', p['extraction'].format(questions=question_text(h['questions']), source=source), ['prompts.json', 'questions.json', h['source_file']]),
            (h['id'] + '-summary', p['summary'].format(source=source), ['prompts.json', h['source_file']])]
    control = ('full-source-control', p['synthesis'].format(source='\n\n'.join(sources[h['source_file']] for h in suite['questions'])), ['prompts.json'] + [h['source_file'] for h in suite['questions']])
    return stages, control

def payload_for(suite, profile, model_id, prompt):
    policy = suite['config']['request_policy']
    budget = policy['reasoning_output_budget' if profile.get('template_reasoning') else 'reasoning_off_output_budget']
    payload = dict(model=model_id, input=prompt, system_prompt=suite['prompts']['system'],
                   stream=True, store=False, context_length=suite['config']['context'],
                   max_output_tokens=budget, **profile['sampling'])
    if profile.get('reasoning') is not None:
        payload['reasoning'] = profile['reasoning']
    return payload

def fingerprint(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

def stream_worker(url, key, payload, stream_file, result_file):
    """A separate process lets the parent enforce a wall deadline on every OS."""
    started = time.perf_counter()
    timing, result = {}, None
    try:
        headers = {'Content-Type': 'application/json'}
        if key:
            headers['Authorization'] = 'Bearer ' + key
        req = urllib.request.Request(url + '/api/v1/chat', data=json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=90) as response, open(stream_file, 'w', encoding='utf-8') as log:
            for line in response:
                if not line.startswith(b'data:'):
                    continue
                event = json.loads(line[5:])
                elapsed = time.perf_counter() - started
                log.write(json.dumps(dict(elapsed_seconds=elapsed, event=event)) + '\n')
                log.flush()
                typ = event.get('type')
                if typ == 'message.delta' and event.get('content'):
                    timing.setdefault('first_visible_seconds', elapsed)
                    timing['last_visible_delta_seconds'] = elapsed
                if typ == 'reasoning.delta' and event.get('content'):
                    timing.setdefault('first_reasoning_seconds', elapsed)
                if typ in ['prompt_processing.start', 'prompt_processing.end', 'message.end', 'reasoning.end']:
                    timing.setdefault(typ, elapsed)
                if typ == 'error':
                    raise RuntimeError('Native stream error: ' + json.dumps(event))
                if typ == 'chat.end':
                    result = event.get('result')
                    break
        if result is None:
            raise RuntimeError('Stream ended without aggregated result')
        save(result_file, dict(status='received', response=result, timing=timing, wall_seconds=time.perf_counter() - started))
    except Exception as error:
        value = dict(status='error', error=str(error), wall_seconds=time.perf_counter() - started)
        if isinstance(error, urllib.error.HTTPError):
            value['http_error_body'] = error.read().decode(errors='replace')
        save(result_file, value)

def request(suite, profile, args, name, prompt, inputs, parents=None):
    if any(x.startswith('gold/') for x in inputs):
        raise ValueError('Evaluator references cannot enter model requests')
    folder = args.output / profile['id']
    payload = payload_for(suite, profile, args.model_id, prompt)
    out = folder / (name + '.json')
    fp = fingerprint(payload)
    if out.exists():
        old = read_json(out)
        if old['fingerprint'] != fp:
            raise ValueError('Checkpoint payload changed; use a new output directory')
        return old
    save(folder / (name + '-request.json'), payload)
    record = dict(name=name, profile=profile['id'], fingerprint=fp, started_at=now(),
                  source_files=inputs, parent_requests=parents or [], quality='Unadjudicated')
    save(args.output / 'status.json', dict(state='request', profile=profile['id'], request=name, time=now()))
    temporary = folder / (name + '-transport.json')
    if temporary.exists():
        temporary.unlink()
    process = mp.get_context('spawn').Process(target=stream_worker,
        args=(args.base_url.rstrip('/'), os.environ.get(args.api_key_env, ''), payload,
              str(folder / (name + '-stream.jsonl')), str(temporary)))
    process.start()
    process.join(suite['config']['request_policy']['timeout_seconds'])
    if process.is_alive():
        process.terminate()
        process.join(10)
        if process.is_alive():
            process.kill()
            process.join()
        record.update(status='timeout', error='900-second wall deadline exceeded; no retry')
    elif not temporary.exists():
        record.update(status='error', error='Transport worker exited without result', exitcode=process.exitcode)
    else:
        transport = read_json(temporary)
        if transport['status'] == 'error':
            record.update(transport)
        else:
            response, timing, wall = transport['response'], transport['timing'], transport['wall_seconds']
            text = '\n\n'.join(x.get('content', '') for x in response.get('output', []) if x.get('type') == 'message')
            stats = response.get('stats', {})
            total, reason = stats.get('total_output_tokens'), stats.get('reasoning_output_tokens')
            capped = total >= payload['max_output_tokens'] if isinstance(total, int) else None
            visible = total - reason if isinstance(total, int) and isinstance(reason, int) else None
            first = timing.get('first_visible_seconds')
            record.update(status='capped' if capped else 'ok' if text.strip() else 'empty',
                output=text, response=response, stats=stats, stream_timing=timing, wall_seconds=wall,
                output_limit_reached=capped, word_count=len(text.split()), first_visible_token_seconds=first,
                visible_tokens_api_difference=visible,
                visible_tokens_per_total_wall_second=visible / wall if visible is not None else None,
                visible_phase_tokens_per_second=visible / (wall - first) if visible is not None and first is not None and wall > first else None,
                token_measurement_note='API total minus reasoning, when both are returned; may include control tokens. Not SDK retokenization or synthetic llama-bench speed.')
            (folder / (name + '.md')).write_text(text + '\n', encoding='utf-8')
    record['finished_at'] = now()
    save(out, record)
    return record

def verify_loaded(suite, profile, args):
    headers = {}
    if os.environ.get(args.api_key_env):
        headers['Authorization'] = 'Bearer ' + os.environ[args.api_key_env]
    req = urllib.request.Request(args.base_url.rstrip('/') + '/api/v1/models', headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        models = json.load(response)['models']
    matches = [(m, i) for m in models for i in m.get('loaded_instances', []) if i['id'] == args.model_id]
    if len(matches) != 1:
        raise ValueError('Load exactly one matching model instance before running this profile')
    model, instance = matches[0]
    config = instance['config']
    if config.get('context_length') != suite['config']['context'] or config.get('parallel') != 1:
        raise ValueError('Expected context 65536 and parallel capacity 1')
    if bool(config.get('speculative_draft_mtp')) != bool(profile['mtp']):
        raise ValueError('MTP setting differs from the frozen profile')
    if not config.get('flash_attention') or not config.get('offload_kv_cache_to_gpu'):
        raise ValueError('Flash attention and GPU KV offload must be enabled')
    weight = {'verification': 'not independently verified; provide --model-file to hash weights'}
    if args.model_file:
        weight = dict(sha256=sha256(args.model_file), expected=profile['sha256'])
        if weight['sha256'] != profile['sha256']:
            raise ValueError('Model SHA-256 differs from the frozen configuration')
    save(args.output / profile['id'] / 'loaded-model.json', dict(model=model, instance=instance,
         weight_verification=weight, operator_settings=read_json(args.loaded_settings) if args.loaded_settings else None,
         verification_limits='Native API does not fully establish backend, F16 KV, seed, full layer placement, or GPT template. Inspect server logs/settings and record them with --loaded-settings.'))

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'plan', 'run'])
    parser.add_argument('--suite', type=Path, default=DEFAULT_SUITE)
    parser.add_argument('--profile', default='gemma26-off')
    parser.add_argument('--model-id', help='An already loaded LM Studio instance identifier')
    parser.add_argument('--base-url', default='http://127.0.0.1:1234')
    parser.add_argument('--api-key-env', default='LM_STUDIO_API_KEY', help='Environment variable name; its value is never saved')
    parser.add_argument('--output', type=Path, default=Path('work/history-v2'))
    parser.add_argument('--model-file', type=Path, help='Optional local GGUF for frozen SHA-256 verification')
    parser.add_argument('--loaded-settings', type=Path, help='Operator-reviewed runtime/seed/KV/template metadata JSON')
    args = parser.parse_args(argv)
    suite = load_suite(args.suite)
    profile = next((m for m in suite['config']['models'] if m['id'] == args.profile), None)
    if profile is None:
        parser.error('Unknown profile. Use: ' + ', '.join(m['id'] for m in suite['config']['models']))
    if args.command == 'validate':
        print(json.dumps(dict(status='valid', version=suite['freeze']['version'], checked_files=len(suite['freeze']['files']), profiles=[m['id'] for m in suite['config']['models']], questions=20, requests_per_model=12)))
        return 0
    if not args.model_id:
        parser.error('--model-id is required for plan and run')
    stages, control = source_stages(suite)
    if args.command == 'plan':
        for name, prompt, _ in stages + [control]:
            save(args.output / args.profile / (name + '-request.json'), payload_for(suite, profile, args.model_id, prompt))
        save(args.output / args.profile / 'merged-summary-dependency.json', dict(stage='merged-summary-synthesis', parents=[h['id'] + '-summary' for h in suite['questions']], requires='All four direct summaries completed without reaching their output cap'))
        print('Prepared 11 source-based payloads; merged synthesis requires four generated summaries. No server request sent.')
        return 0
    verify_loaded(suite, profile, args)
    results = {}
    for name, prompt, inputs in stages:
        results[name] = request(suite, profile, args, name, prompt, inputs)
        if results[name]['status'] in {'error', 'timeout'}:
            save(args.output / profile['id'] / 'interrupted.json', dict(time=now(), request=name, status=results[name]['status'], reason='Transport failed. Confirm server idle before retrying with a new output directory. Completed and failed checkpoints are retained.'))
            return 2
    parents = [h['id'] + '-summary' for h in suite['questions']]
    if all(results[name]['status'] == 'ok' for name in parents):
        material = '\n\n'.join(h['id'] + '\n' + results[h['id'] + '-summary']['output'] for h in suite['questions'])
        results['merged-summary-synthesis'] = request(suite, profile, args, 'merged-summary-synthesis', suite['prompts']['synthesis'].format(source=material), ['prompts.json'], parents)
    else:
        results['merged-summary-synthesis'] = dict(status='blocked_by_parent', parents=parents)
        save(args.output / profile['id'] / 'merged-summary-synthesis.json', results['merged-summary-synthesis'])
    name, prompt, inputs = control
    results[name] = request(suite, profile, args, name, prompt, inputs)
    save(args.output / profile['id'] / 'complete.json', dict(time=now(), stages={n: r['status'] for n, r in results.items()}, quality='Source adjudication pending; terminal generation is not an accuracy pass'))
    print(json.dumps({name: result['status'] for name, result in results.items()}))
    return 0 if all(r['status'] == 'ok' for r in results.values()) else 2

if __name__ == '__main__':
    mp.freeze_support()
    raise SystemExit(main())
