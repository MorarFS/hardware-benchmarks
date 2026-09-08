"""Shared lock for sequential local GPU workloads in this repository."""
from contextlib import contextmanager
import fcntl
import os
import signal
import subprocess
import json
from pathlib import Path


def model_specs(root):
    models=json.loads((Path(root)/'scripts/models.json').read_text())
    extra=Path(root)/'scripts/mac-extra-models.json'
    if extra.exists():
        additions=json.loads(extra.read_text())
        if set(models)&set(additions):raise RuntimeError('Duplicate model ID in Mac extension')
        models.update(additions)
    return models


def storage_relative(spec):
    path=Path(spec.get('local_path',spec['filename']))
    if path.is_absolute() or '..' in path.parts:raise RuntimeError('Model storage must stay within its directory')
    return path

@contextmanager
def gpu_lock(root):
    folder=Path(root)/'local-results'
    folder.mkdir(exist_ok=True)
    with (folder/'.gpu.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        yield


@contextmanager
def pause_model_downloads(root):
    """Pause this workspace's active download/hash workers for timed inference.

    Leave already suspended processes alone and restore only our own changes.
    Parents are paused before curl children, preventing a retry during the run.
    """
    suspended=[]
    rows=subprocess.check_output(['ps','-axo','pid=,stat=,args='],text=True).splitlines()
    selected=[]
    for row in rows:
        parts=row.strip().split(None,2)
        if len(parts)!=3 or 'T' in parts[1]:continue
        pid,state,command=parts
        executable=Path(command.split(None,1)[0]).name
        is_worker=executable in ['Python','python3','python'] and 'scripts/get-model.py' in command
        if is_worker:
            cwd=subprocess.run(['lsof','-a','-p',pid,'-d','cwd','-Fn'],text=True,capture_output=True)
            is_worker=('n'+str(root.resolve())) in cwd.stdout.splitlines()
        is_curl=executable=='curl' and str(root/'work') in command and '.gguf.partial' in command
        if int(pid)!=os.getpid() and (is_worker or is_curl):selected.append((is_curl,int(pid)))
    try:
        for _,pid in sorted(selected):
            try:os.kill(pid,signal.SIGSTOP);suspended.append(pid)
            except ProcessLookupError:pass
        yield
    finally:
        for pid in reversed(suspended):
            try:os.kill(pid,signal.SIGCONT)
            except ProcessLookupError:pass
