#!/usr/bin/env python3
"""Optional Linux scheduler: wait for a terminal benchmark, lock, then run a command.
No credentials or machine-specific paths. The direct API runner does not need this.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wait-unit', action='append', required=True)
    parser.add_argument('--speed-root', type=Path, required=True,
                        help='Contains queue.json, complete.json, and per-model terminal records')
    parser.add_argument('--lock', type=Path, required=True)
    parser.add_argument('--status', type=Path, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if sys.platform != 'linux':
        parser.error('This optional scheduler requires Linux systemd and flock')
    import fcntl
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('Provide the command after --')
    def status(state, **extra):
        args.status.parent.mkdir(parents=True, exist_ok=True)
        args.status.write_text(json.dumps(dict(state=state, **extra), indent=2) + '\n', encoding='utf-8')
    def active():
        for unit in args.wait_unit:
            r = subprocess.run(['systemctl', '--user', 'show', unit, '-p', 'ActiveState', '--value'], capture_output=True, text=True, check=True)
            if r.stdout.strip() in {'active', 'activating', 'reloading', 'deactivating'}:
                return True
        return False
    def terminal():
        if not (args.speed_root / 'complete.json').is_file():
            raise RuntimeError('Predecessor stopped without complete.json')
        models = json.loads((args.speed_root / 'queue.json').read_text(encoding='utf-8'))['models']
        if not models:
            raise RuntimeError('Predecessor queue is empty')
        for model in models:
            name = model['id']
            if Path(name).name != name:
                raise RuntimeError('Invalid model identifier in predecessor queue')
            if not any((args.speed_root / name / suffix).is_file() for suffix in ['complete.json', 'error.json']):
                raise RuntimeError('Missing terminal model record: ' + name)
        return len(models)
    try:
        status('waiting_for_speed', units=args.wait_unit)
        while active():
            time.sleep(10)
        count = terminal()
        args.lock.parent.mkdir(parents=True, exist_ok=True)
        with args.lock.open('a') as lock:
            status('waiting_for_lock', predecessor_models=count)
            fcntl.flock(lock, fcntl.LOCK_EX)
            if active():
                raise RuntimeError('Predecessor restarted; refusing overlap')
            terminal()
            status('running_command')
            result = subprocess.run(command, check=False)
            status('command_terminal', returncode=result.returncode)
            return result.returncode
    except Exception as error:
        status('blocked', error=str(error))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
