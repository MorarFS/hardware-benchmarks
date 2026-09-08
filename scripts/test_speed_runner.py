"""Protocol smoke tests with a fake executable. No GPU inference is performed."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).with_name('Run-Benchmark.py')

class SpeedRunnerTests(unittest.TestCase):
    def test_dry_run_protocol(self):
        result = subprocess.run([sys.executable, str(RUNNER), '--executable', 'fake-bench', '--device', 'Metal', '--backend', 'Metal', '--model', 'fake.gguf', '--output', 'unused', '--dry-run'], capture_output=True, text=True, check=True)
        jobs = json.loads(result.stdout)
        self.assertEqual(len(jobs), 2)
        for job, depth in zip(jobs, ['0', '2048']):
            for flag, value in [('-d', depth), ('-n', '256'), ('-r', '5'), ('-t', '10'), ('-ngl', '99'), ('-b', '512'), ('-ub', '512'), ('-ctk', 'f16'), ('-ctv', 'f16'), ('-fa', 'on'), ('-sm', 'none')]:
                self.assertEqual(job[job.index(flag) + 1], value)
            self.assertNotIn('--no-warmup', job)
            self.assertNotIn('--speculative', ' '.join(job))

    @unittest.skipIf(sys.platform == 'win32', 'The fake executable fixture uses a POSIX shebang; runner itself is cross-platform')
    def test_fake_executable_and_hash_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            model = root / 'fixture.gguf'
            model.write_bytes(b'Not a real model. Offline protocol fixture.')
            expected = hashlib.sha256(model.read_bytes()).hexdigest()
            exe = root / 'llama-bench'
            exe.write_text('''#!/usr/bin/env python3
import json,sys
args=sys.argv[1:]
if '--help' in args:
 print('--list-devices -dev -ctk -ctv -d -r -fa -ub --progress');sys.exit(0)
if '--list-devices' in args:
 print('Metal: mock device');sys.exit(0)
depth=int(args[args.index('-d')+1]);prompt=int(args[args.index('-p')+1])
base=dict(build_commit='050dde50c',backends='Metal',devices='Metal',n_gpu_layers=99,n_depth=depth,samples_ts=[1,2,3,4,5],avg_ts=3,stddev_ts=1.58113883,model_filename='fixture.gguf')
rows=[dict(base,n_prompt=0,n_gen=256)]
if prompt:rows.insert(0,dict(base,n_prompt=512,n_gen=0))
print(json.dumps(rows))
''', encoding='utf-8')
            exe.chmod(0o755)
            version = root / 'llama-server'
            version.write_text('#!/usr/bin/env python3\nprint("version: 10852 (050dde50c)")\n', encoding='utf-8')
            version.chmod(0o755)
            cmd = [sys.executable, str(RUNNER), '--executable', str(exe), '--device', 'Metal', '--backend', 'Metal', '--model', str(model), '--sha256', expected]
            result = subprocess.run(cmd + ['--output', str(root / 'good')], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / 'good/complete.json').exists())
            self.assertEqual(len(json.loads((root / 'good/depth0.json').read_text())), 2)
            self.assertEqual(len(json.loads((root / 'good/depth2048.json').read_text())), 1)
            model.write_bytes(b'Changed weights')
            result = subprocess.run(cmd + ['--output', str(root / 'bad')], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 2)
            self.assertIn('SHA-256 mismatch', (root / 'bad/error.json').read_text())
            self.assertFalse((root / 'bad/depth0.json').exists())

if __name__ == '__main__':
    unittest.main()
