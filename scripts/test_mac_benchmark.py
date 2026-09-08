"""Offline integration checks for false fit claims and invalid measurements."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

loader = importlib.util.spec_from_file_location('macbench', Path(__file__).with_name('run-mac-benchmark.py'))
bench = importlib.util.module_from_spec(loader)
loader.loader.exec_module(bench)

class RunnerChecks(unittest.TestCase):
    def run_case(self, offload='37/37', revision='050dde50c', sample_count=5, ac=True, bad_hash=False, hang=False, growth=0, binary_log=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'work').mkdir();(root/'scripts').mkdir()
            (root/'work/model.gguf').write_bytes(b'fixture')
            digest=hashlib.sha256(b'wrong' if bad_hash else b'fixture').hexdigest()
            (root/'scripts/models.json').write_text(json.dumps({'fixture':{'filename':'model.gguf','sha256':digest}}))
            fake=root/'fake-bench'
            fake.write_text(f'''#!{sys.executable}
import json,sys,time
if {binary_log!r}: sys.stderr.buffer.write(bytes([196]));sys.stderr.buffer.flush()
print('offloaded {offload} layers to GPU',file=sys.stderr,flush=True)
if {hang!r}: time.sleep(60)
depth=int(sys.argv[sys.argv.index('-d')+1])
rows=[{{'build_commit':{revision!r},'devices':'MTL0','n_depth':depth,'n_prompt':0,'n_gen':256,'avg_ts':42,'samples_ts':[42]*{sample_count}}}]
if depth==0: rows.insert(0,dict(rows[0],n_prompt=512,n_gen=0))
print(json.dumps(rows))
''');fake.chmod(0o755)
            snap={'ac_connected':ac,'swap_used_bytes':0,'process_rss_bytes':1}
            def snapshot(pid=None):
                return dict(snap,swap_used_bytes=growth if pid else 0)
            argv=['run','fixture','--executable',str(fake),'--output',str(root/'output'),'--depths','0']
            error=None
            with patch.object(bench,'ROOT',root),patch.object(sys,'argv',argv),patch.object(bench,'snapshot',snapshot),contextlib.redirect_stdout(io.StringIO()):
                try:bench.main()
                except RuntimeError as exc:error=str(exc)
            statuses=[json.loads(p.read_text()) for p in (root/'output').glob('*/*-status.json')]
            return error,statuses

    def test_accept_full_gpu_valid_measurements(self):
        error,status=self.run_case()
        self.assertIsNone(error)
        self.assertTrue(status[0]['validation_passed'])

    def test_vocabulary_byte_diagnostics_do_not_destroy_results(self):
        error,status=self.run_case(binary_log=True)
        self.assertIsNone(error)
        self.assertTrue(status[0]['validation_passed'])

    def test_reject_partial_offload(self):
        error,status=self.run_case(offload='12/37')
        self.assertIn('not accepted',error)
        self.assertFalse(status[0]['full_layer_offload'])

    def test_reject_wrong_runtime_or_samples(self):
        for kwargs in [{'revision':'wrong'},{'sample_count':4}]:
            with self.subTest(**kwargs):
                error,status=self.run_case(**kwargs)
                self.assertIsNotNone(error)
                self.assertFalse(status[0]['validation_passed'])

    def test_reject_modified_model_before_process(self):
        error,status=self.run_case(bad_hash=True)
        self.assertEqual(error,'Model hash mismatch')
        self.assertEqual(status,[])

    def test_reject_battery_before_process(self):
        error,status=self.run_case(ac=False)
        self.assertIn('AC power required',error)
        self.assertEqual(status,[])

    def test_terminate_swap_growth_and_preserve_failure(self):
        error,status=self.run_case(hang=True,growth=2*1024**3)
        self.assertIsNotNone(error)
        self.assertIn('Swap growth',status[0]['abort_reason'])
        self.assertNotEqual(status[0]['exit_code'],0)
        self.assertFalse(status[0]['validation_passed'])

if __name__=='__main__':unittest.main()
