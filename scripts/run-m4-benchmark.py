#!/usr/bin/env python3
"""Run matched Metal benchmarks, retaining measured samples and memory evidence."""
import argparse
import csv
import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time
from mac_runtime import model_specs, storage_relative

ROOT = Path(__file__).resolve().parents[1]

def output(*args):
    return subprocess.check_output(args, text=True).strip()

def snapshot(pid=None):
    vm = output('vm_stat')
    page_size = int(re.search(r'page size of (\d+)', vm)[1])
    counters = {k.strip('"'): int(v) for k, v in re.findall(r'^([^:\n]+):\s+(\d+)\.', vm, re.M)}
    swap = output('sysctl', '-n', 'vm.swapusage')
    used = re.search(r'used = ([\d.]+)([MG])', swap)
    row = {'swap_used_bytes': float(used[1]) * (1024**2 if used[2] == 'M' else 1024**3)}
    for key in ['Pages free', 'Pages active', 'Pages inactive', 'Pages speculative', 'Pages wired down', 'Pages occupied by compressor', 'Pageins', 'Pageouts', 'Swapins', 'Swapouts']:
        row[key.lower().replace(' ', '_') + '_bytes'] = counters.get(key, 0) * page_size
    row['process_rss_bytes'] = 0
    if pid:
        r = subprocess.run(['ps', '-o', 'rss=', '-p', str(pid)], text=True, capture_output=True)
        if r.stdout.strip():
            row['process_rss_bytes'] = int(r.stdout.strip()) * 1024
    row['ac_connected'] = 'AC Power' in output('pmset', '-g', 'batt')
    return row

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8*1024**2), b''): h.update(block)
    return h.hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model_id')
    p.add_argument('--executable', type=Path, default=ROOT/'work/llama-metal/llama-b10852/llama-bench')
    p.add_argument('--output', type=Path, default=ROOT/'local-results')
    p.add_argument('--depths', type=int, nargs='+', default=[0,2048])
    p.add_argument('--repetitions', type=int, default=5)
    p.add_argument('--allow-battery', action='store_true')
    p.add_argument('--max-swap-growth-gib', type=float, default=1.0)
    p.add_argument('--timeout-seconds', type=float, default=3600)
    p.add_argument('--run-label', default='', help='Optional label for a separately retained repeat')
    a = p.parse_args()
    if a.repetitions < 1 or any(d < 0 for d in a.depths) or a.max_swap_growth_gib < 0 or a.timeout_seconds <= 0:
        p.error('Repetitions and timeout must be positive; depths and swap guard must be nonnegative')
    if a.run_label and not re.fullmatch(r'[a-z0-9-]+',a.run_label):p.error('Run label must contain lowercase letters, digits or hyphens')
    spec = model_specs(ROOT)[a.model_id]
    model = ROOT/'work'/storage_relative(spec)
    if sha256(model) != spec['sha256']: raise RuntimeError('Model hash mismatch')
    run_name=f'apple-metal-{a.model_id}'+('-'+a.run_label if a.run_label else '')
    directory = a.output / (run_name+'-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    directory.mkdir(parents=True, exist_ok=False)
    for depth in a.depths:
        before = snapshot()
        if not before['ac_connected'] and not a.allow_battery: raise RuntimeError('AC power required; connect power or explicitly label a battery test with --allow-battery')
        stem = directory/f'{run_name}-depth{depth}'
        command = [str(a.executable.resolve()), '-m', str(model), '-dev', 'MTL0', '-sm', 'none', '-ngl', '99', '-fa', 'on', '-b', '512', '-ub', '512', '-t', '10', '-ctk', 'f16', '-ctv', 'f16', '-p', '512' if depth == 0 else '0', '-n', '256', '-d', str(depth), '-r', str(a.repetitions), '-o', 'json', '--progress', '-v']
        print('Starting', a.model_id, 'depth', depth, flush=True)
        start = time.monotonic()
        samples = [dict(elapsed_seconds=0, **before)]
        abort = None
        with stem.with_suffix('.json').open('w') as stdout, stem.with_suffix('.log').open('w') as stderr:
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
            try:
                while process.poll() is None:
                    s = dict(elapsed_seconds=round(time.monotonic()-start, 3), **snapshot(process.pid))
                    samples.append(s)
                    if s['swap_used_bytes'] - before['swap_used_bytes'] > a.max_swap_growth_gib*1024**3:
                        abort = 'Swap growth exceeded configured guard; not a fit result'
                    if not s['ac_connected'] and not a.allow_battery: abort = 'AC disconnected during run'
                    if time.monotonic()-start > a.timeout_seconds: abort = 'Run exceeded configured timeout'
                    if abort:
                        process.terminate()
                        try: process.wait(timeout=15)
                        except subprocess.TimeoutExpired: process.kill(); process.wait()
                        break
                    time.sleep(2)
            finally:
                if process.poll() is None: process.terminate(); process.wait()
        samples.append(dict(elapsed_seconds=round(time.monotonic()-start, 3), **snapshot()))
        with Path(str(stem)+'-memory.csv').open('w') as f:
            writer = csv.DictWriter(f, fieldnames=samples[0].keys()); writer.writeheader(); writer.writerows(samples)
        # Verbose vocab diagnostics may contain isolated token bytes. Preserve
        # the raw log and decode only its selected ASCII telemetry permissively.
        log = stem.with_suffix('.log').read_text(encoding='utf-8', errors='replace')
        offloads = re.findall(r'offloaded\s+(\d+)/(\d+)\s+layers to GPU', log)
        full = bool(offloads) and all(int(x)>0 and x==y for x,y in offloads)
        excerpts = [line for line in log.splitlines() if re.search(r'offloaded |buffer size|recommendedMaxWorkingSetSize|n_ctx\s+=|using device|load time', line)]
        Path(str(stem)+'-offload.txt').write_text('\n'.join(excerpts)+'\n')
        summary = {'validation_passed': False, 'model_id': a.model_id, 'model_sha256': spec['sha256'], 'depth': depth, 'exit_code': process.returncode, 'abort_reason': abort, 'full_layer_offload': full, 'wall_seconds_including_load': round(time.monotonic()-start,3), 'sample_interval_seconds': 2, 'before': before, 'after': samples[-1], 'peak_rss_bytes': max(s['process_rss_bytes'] for s in samples), 'peak_swap_used_bytes': max(s['swap_used_bytes'] for s in samples), 'swap_growth_bytes': max(s['swap_used_bytes'] for s in samples)-before['swap_used_bytes'], 'all_samples_ac': all(s['ac_connected'] for s in samples), 'command': [Path(x).name if x.startswith(str(ROOT)) else x for x in command]}
        Path(str(stem)+'-status.json').write_text(json.dumps(summary, indent=2)+'\n')
        if process.returncode or abort or not full: raise RuntimeError(f'Run not accepted; inspect {stem}')
        entries = json.loads(stem.with_suffix('.json').read_text())
        if len(entries) != (2 if depth == 0 else 1): raise RuntimeError('Unexpected measurement count')
        for e in entries:
            if e['build_commit'] != '050dde50c' or e['devices'] != 'MTL0': raise RuntimeError('Unexpected runtime revision or selected device')
            if len(e['samples_ts']) != a.repetitions or e['n_depth'] != depth: raise RuntimeError('Unexpected repetition count or depth')
            e['model_filename'] = model.name
            if not math.isfinite(e['avg_ts']) or e['avg_ts'] <= 0: raise RuntimeError('Invalid throughput')
        stem.with_suffix('.json').write_text(json.dumps(entries, indent=2)+'\n')
        summary['validation_passed'] = True
        Path(str(stem)+'-status.json').write_text(json.dumps(summary, indent=2)+'\n')
        print('Completed', [(e['n_prompt'],e['n_gen'],e['avg_ts']) for e in entries], flush=True)
    print(directory, flush=True)

if __name__ == '__main__':
    from mac_runtime import gpu_lock, pause_model_downloads
    with gpu_lock(ROOT): main()
