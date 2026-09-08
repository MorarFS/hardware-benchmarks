#!/usr/bin/env python3
"""Resume a pinned GGUF download and verify SHA-256 before atomic promotion."""
import argparse
import hashlib
import fcntl
import json
from pathlib import Path
import shutil
import subprocess
import time
from mac_runtime import gpu_lock, model_specs, storage_relative

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def _download(model_id, directory):
    spec = model_specs(ROOT)[model_id]
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / storage_relative(spec)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if digest(target) != spec['sha256']:
            raise RuntimeError(f'Existing model hash mismatch: {target}')
        return target
    partial = target.with_suffix(target.suffix + '.partial')
    remaining = spec.get('file_size_bytes', 6_000_000_000) - (partial.stat().st_size if partial.exists() else 0)
    if shutil.disk_usage(directory).free < remaining + 10 * 1024**3:
        raise RuntimeError('Insufficient disk space with 10 GiB reserve')
    url = f"https://huggingface.co/{spec['repository']}/resolve/{spec['revision']}/{spec['filename']}"
    for attempt in range(20):
        # Retry transport errors as well as HTTP errors. Each new process resumes
        # from the current file size instead of restarting a large artifact.
        if partial.exists() and partial.stat().st_size == spec.get('file_size_bytes'):
            break
        result = subprocess.run(['curl', '--http1.1', '-fL', '--connect-timeout', '30', '--speed-limit', '1024', '--speed-time', '120', '-C', '-', url, '-o', str(partial)])
        if result.returncode == 0:
            break
        if attempt == 19:
            raise RuntimeError('Download failed after 20 resumable attempts')
        print(f'Retrying transport failure {result.returncode}, attempt {attempt+2}/20', flush=True)
        time.sleep(min(30, 5*(attempt+1)))
    if digest(partial) != spec['sha256']:
        raise RuntimeError(f'Download hash mismatch; retained for inspection: {partial}')
    partial.rename(target)
    print(f'Verified {model_id}: {spec["sha256"]}', flush=True)
    return target

def download(model_id, directory=ROOT / 'work'):
    # A worker launched during inference waits before starting transfer/hash I/O.
    # Existing workers are suspended by the timed runner while it holds this lock.
    with gpu_lock(ROOT):
        pass
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    # Independent jobs may queue the same artifact; only one writes it.
    spec = model_specs(ROOT)[model_id]
    target = directory / storage_relative(spec)
    target.parent.mkdir(parents=True, exist_ok=True)
    with Path(str(target)+'.download.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _download(model_id, directory)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model_id')
    p.add_argument('--directory', type=Path, default=ROOT / 'work')
    a = p.parse_args()
    print(download(a.model_id, a.directory))
