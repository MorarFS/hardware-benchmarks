"""Offline protocol tests. The mock server is not a model or an accuracy judge."""
import contextlib
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runner

class ProtocolTests(unittest.TestCase):
    def test_freeze_and_gold_exclusion(self):
        parsed = []
        original = runner.read_json
        def track(path):
            parsed.append(str(path))
            return original(path)
        with patch.object(runner, 'read_json', side_effect=track):
            suite = runner.load_suite(runner.DEFAULT_SUITE)
        self.assertFalse(any('/gold/' in name.replace('\\', '/') for name in parsed))
        self.assertNotIn('gold', suite)
        stages, control = runner.source_stages(suite)
        self.assertEqual(len(stages), 10)
        for profile in suite['config']['models']:
            for _, prompt, sources in stages + [control]:
                payload = runner.payload_for(suite, profile, 'mock', prompt)
                self.assertEqual(payload['input'], prompt)
                self.assertEqual(payload['system_prompt'], suite['prompts']['system'])
                self.assertFalse(any(name.startswith('gold/') for name in sources))
                self.assertNotIn('answers', payload)
        gpt = suite['config']['models'][2]
        payload = runner.payload_for(suite, gpt, 'mock', 'test')
        self.assertNotIn('top_k', payload)
        self.assertNotIn('reasoning', payload)

    def test_tampered_fixture_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as folder:
            copied = Path(folder) / 'suite'
            shutil.copytree(runner.DEFAULT_SUITE, copied)
            (copied / 'inputs/H1.txt').write_text('changed', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Frozen fixture mismatch'):
                runner.load_suite(copied)

    def test_native_sse_end_to_end_and_checkpoint(self):
        requests = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_GET(self):
                data = {'models': [{'loaded_instances': [{'id': 'mock', 'config': {
                    'context_length': 65536, 'parallel': 1, 'speculative_draft_mtp': False,
                    'flash_attention': True, 'offload_kv_cache_to_gpu': True}}]}]}
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            def do_POST(self):
                requests.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                events = [{'type': 'message.delta', 'content': 'Mock response.'},
                    {'type': 'chat.end', 'result': {'output': [{'type': 'message', 'content': 'Mock response.'}],
                    'stats': {'total_output_tokens': 3, 'reasoning_output_tokens': 0}}}]
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.end_headers()
                for event in events:
                    self.wfile.write(('data: ' + json.dumps(event) + '\n\n').encode())
                    self.wfile.flush()
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as folder:
                cmd = [sys.executable, str(HERE / 'runner.py'), 'run', '--model-id', 'mock',
                       '--base-url', 'http://127.0.0.1:' + str(server.server_port), '--output', folder]
                for _ in range(2):
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(len(requests), 12, 'Checkpoint resume must not repeat completed requests')
                complete = runner.read_json(Path(folder) / 'gemma26-off/complete.json')
                self.assertEqual(len(complete['stages']), 12)
                self.assertTrue(all(value == 'ok' for value in complete['stages'].values()))
                merged = requests[10]['input']
                self.assertIn('Mock response.', merged)
                self.assertNotIn('Fritigern', merged, 'Merged stage must use summaries, not hidden source/gold')
        finally:
            server.shutdown()
            server.server_close()

if __name__ == '__main__':
    unittest.main()
