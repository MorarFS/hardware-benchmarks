#!/usr/bin/env python3
"""Portable matched llama-bench protocol. Python 3.10+, standard library only.
Default hash is official Qwen3-8B Q4_K_M. No downloads or runtime installation.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

QWEN8_SHA = 'd98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785'

def commands(executable, model, device):
    return [[str(executable), '-m', str(model), '-dev', device, '-sm', 'none', '-ngl', '99',
             '-fa', 'on', '-b', '512', '-ub', '512', '-t', '10', '-ctk', 'f16', '-ctv', 'f16',
             '-p', '512' if depth == 0 else '0', '-n', '256', '-d', str(depth), '-r', '5',
             '-o', 'json', '--progress', '-v'] for depth in [0, 2048]]

def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

def model_files(model):
    match = re.match(r'^(.*)-00001-of-(\d{5})\.gguf$', model.name)
    if not match:
        return [model]
    count = int(match.group(2))
    files = [model.with_name(f'{match.group(1)}-{i:05d}-of-{count:05d}.gguf') for i in range(1, count + 1)]
    if not all(p.is_file() for p in files):
        raise ValueError('Missing GGUF shard; no download attempted')
    return files

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', required=True, type=Path)
    parser.add_argument('--device', required=True, help='Exact identifier from llama-bench --list-devices')
    parser.add_argument('--backend', required=True, help='Expected measured backend, e.g. Metal, Vulkan, HIP, CUDA')
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--sha256', default=QWEN8_SHA, help='Expected first/single GGUF hash; default is pinned official Qwen8')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--expected-commit', default='050dde50c')
    parser.add_argument('--metadata', type=Path, help='Optional reviewed machine/power metadata JSON')
    parser.add_argument('--dry-run', action='store_true', help='Print exact commands; do not hash, load, or execute')
    args = parser.parse_args(argv)
    exe, model = args.executable.resolve(), args.model.resolve()
    jobs = commands(exe, model, args.device)
    if args.dry_run:
        print(json.dumps(jobs, indent=2))
        return 0
    args.output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    # Linux release packages may require sibling shared libraries. macOS uses its normal loader.
    if sys.platform.startswith('linux'):
        env['LD_LIBRARY_PATH'] = str(exe.parent) + (':' + env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
    manifest = dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        machine=dict(os=platform.system(), release=platform.release(), architecture=platform.machine(), processor=platform.processor()),
        operator_metadata=json.loads(args.metadata.read_text(encoding='utf-8')) if args.metadata else None,
        expected_commit=args.expected_commit, expected_backend=args.backend, device=args.device,
        repetitions=5, default_warmup=True, speculation='OFF; no draft model or sampler',
        cache_policy='No OS cache flush; filesystem cache uncontrolled',
        timing_note='Per-process wall time includes loading and warmup. Timed pp/tg excludes loading; process wall is not pure load time.',
        tests=[])
    save(args.output / 'protocol.json', manifest)
    try:
        files = model_files(model)
        manifest['model_files'] = [dict(file=p.name, bytes=p.stat().st_size, sha256=sha256(p)) for p in files]
        if manifest['model_files'][0]['sha256'] != args.sha256:
            raise ValueError('Model SHA-256 mismatch; no model loaded')
        for name, target, flags in [
            ('devices', exe, ['--list-devices']),
            ('help', exe, ['--help']),
            ('version', exe.with_name('llama-server.exe' if exe.suffix == '.exe' else 'llama-server'), ['--version'])]:
            result = subprocess.run([str(target)] + flags, env=env, capture_output=True, text=True, timeout=60)
            text = result.stdout + result.stderr
            (args.output / (name + '.txt')).write_text(text, encoding='utf-8')
            if result.returncode:
                raise RuntimeError(name + ' probe failed')
            if name == 'version' and args.expected_commit not in text:
                raise ValueError('Runtime version differs from expected commit')
            if name == 'help':
                for flag in ['--list-devices', '-dev', '-ctk', '-ctv', '-d', '-r', '-fa', '-ub', '--progress']:
                    if flag not in text:
                        raise ValueError('Required flag absent from executable help: ' + flag)
        for depth, command in zip([0, 2048], jobs):
            record = dict(depth=depth, command=[model.name if x == str(model) else exe.name if x == str(exe) else x for x in command])
            manifest['tests'].append(record)
            save(args.output / 'protocol.json', manifest)
            started = time.perf_counter()
            with (args.output / f'depth{depth}.json').open('w', encoding='utf-8') as stdout, (args.output / f'depth{depth}.log').open('w', encoding='utf-8') as stderr:
                process = subprocess.Popen(command, env=env, stdout=stdout, stderr=stderr)
                try:
                    code = process.wait(timeout=900)
                    timed_out = False
                except subprocess.TimeoutExpired:
                    timed_out = True
                    process.terminate()
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    code = process.returncode
            save(args.output / f'depth{depth}-execution.json', dict(returncode=code, timed_out=timed_out, process_wall_seconds=time.perf_counter() - started))
            if code or timed_out:
                raise RuntimeError(f'Depth {depth} failed: exit={code}, timeout={timed_out}; logs preserved')
            entries = json.loads((args.output / f'depth{depth}.json').read_text(encoding='utf-8'))
            if len(entries) != (2 if depth == 0 else 1):
                raise ValueError('Unexpected benchmark test count')
            for row in entries:
                if not args.expected_commit.startswith(row['build_commit']) and not row['build_commit'].startswith(args.expected_commit):
                    raise ValueError('Measured build commit differs')
                if args.backend.lower() not in row['backends'].lower() or row['devices'] != args.device:
                    raise ValueError('Measured device/backend differs; no fallback accepted')
                if row['n_gpu_layers'] != 99 or row['n_depth'] != depth or len(row['samples_ts']) != 5:
                    raise ValueError('Measured protocol differs')
                row['model_filename'] = model.name
            save(args.output / f'depth{depth}.json', entries)
        save(args.output / 'complete.json', dict(status='timings_complete', full_gpu_placement='Review verbose loader offload lines; requested ngl99 is not independent placement proof', accuracy='Not tested'))
        return 0
    except Exception as error:
        save(args.output / 'error.json', dict(error=str(error), status='failed', no_cpu_fallback_accepted=True))
        print(str(error), file=sys.stderr)
        return 2
    finally:
        save(args.output / 'protocol.json', manifest)

if __name__ == '__main__':
    raise SystemExit(main())
