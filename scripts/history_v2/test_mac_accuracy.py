"""Transport/provenance checks; these do not test or score model factual quality."""
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import shutil
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_mac
import collect_mac
from mac_prompt_adapter import adapter_receipt, messages


class StreamChecks(unittest.TestCase):
    def run_stream(self, events, done=True):
        encoded=b''.join(b'data: '+json.dumps(e).encode()+b'\n\n' for e in events)
        if done:encoded+=b'data: [DONE]\n\n'
        with tempfile.TemporaryDirectory() as tmp:
            result={}
            with patch.object(run_mac.urllib.request,'urlopen',return_value=io.BytesIO(encoded)):
                run_mac.stream('http://127.0.0.1:1',{},Path(tmp),'fixture',result)
            return result

    def test_separate_visible_reasoning_usage(self):
        r=self.run_stream([{'choices':[{'delta':{'reasoning_content':'reason'}}]}, {'choices':[{'delta':{'content':'answer'},'finish_reason':'stop'}]}, {'usage':{'completion_tokens':3}}])
        self.assertEqual((r['status'],r['output'],r['reasoning_output']),('ok','answer','reason'))
        self.assertEqual(r['usage']['completion_tokens'],3)
        self.assertIsNotNone(r['first_visible_seconds'])

    def test_capped_is_not_ok(self):
        r=self.run_stream([{'choices':[{'delta':{'content':'partial'},'finish_reason':'length'}]}])
        self.assertEqual(r['status'],'capped')

    def test_missing_done_is_error(self):
        r=self.run_stream([{'choices':[{'delta':{'content':'partial'}}]}],done=False)
        self.assertEqual(r['status'],'error')
        self.assertIn('without DONE',r['error'])

    def test_server_error_is_error(self):
        r=self.run_stream([{'error':{'message':'failed'}}])
        self.assertEqual(r['status'],'error')


class PayloadChecks(unittest.TestCase):
    def test_prose_counts_both_pdf_citation_delimiters(self):
        self.assertEqual(collect_mac.prose_words('One claim [PDF p. 61, 62]. Another (PDF p. 169–170). Final (p. 365).'),4)
        self.assertEqual(len(collect_mac.PDF_MARKER.findall('[PDF p. 61] (PDF p. 62–63)')),2)

    def test_nemotron_control_preserves_frozen_task_text(self):
        system='Frozen system text';prompt='Frozen source and questions'
        adapted=messages('nemotron-49b',system,prompt)
        self.assertEqual(adapted[0]['content'],system+'\n\n/no_think')
        self.assertEqual(adapted[1],{'role':'user','content':prompt})
        self.assertEqual(messages('qwen3-8b',system,prompt)[0]['content'],system)
        self.assertIsNone(adapter_receipt('qwen3-8b'))

    def test_explicit_none_serialization_and_active_draft_rejection(self):
        self.assertTrue(collect_mac.speculation_disabled('none'))
        self.assertTrue(collect_mac.speculation_disabled('none,none'))
        for value in ['none,draft-mtp','draft-mtp','',None,'none,']:
            self.assertFalse(collect_mac.speculation_disabled(value),value)

    def test_original_fixture_payloads_validate(self):
        folder=collect_mac.ROOT/'results/2026-09-08/mac/accuracy/qwen3-8b'
        if not folder.exists():self.skipTest('Collected reference run unavailable')
        self.assertEqual(len(collect_mac.validate(folder)),12)

    def test_extra_gold_text_is_rejected(self):
        folder=collect_mac.ROOT/'results/2026-09-08/mac/accuracy/qwen3-8b'
        if not folder.exists():self.skipTest('Collected reference run unavailable')
        original=collect_mac.frozen.read_json
        def modified(path):
            value=original(path)
            if Path(path).name=='H1-extraction-request.json':
                value['messages'][1]['content']+='\nGOLD ANSWER LEAK'
            return value
        with patch.object(collect_mac.frozen,'read_json',side_effect=modified):
            with self.assertRaises(AssertionError):collect_mac.validate(folder)

    def test_oversized_prompt_requires_explicit_unsubmitted_exclusion(self):
        source=collect_mac.ROOT/'results/2026-09-08/mac/accuracy/qwen3-8b'
        if not source.exists():self.skipTest('Collected reference run unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'fixture'
            shutil.copytree(source,folder)
            def edit(name,fn):
                p=folder/name;value=json.loads(p.read_text());fn(value);p.write_text(json.dumps(value))
            edit('protocol.json',lambda x:x.update(actual_context=8192))
            edit('load.json',lambda x:x.update(context=8192))
            with self.assertRaises(AssertionError):collect_mac.validate(folder)
            edit('full-source-control.json',lambda x:x.update(status='context_excluded',submitted=False,output='',usage=None))
            edit('complete.json',lambda x:x['stages'].update({'full-source-control':'context_excluded'}))
            # A submitted stream cannot masquerade as an unsubmitted exclusion.
            with self.assertRaises(AssertionError):collect_mac.validate(folder)
            (folder/'full-source-control-stream.jsonl').unlink()
            (folder/'full-source-control.md').unlink()
            metrics=collect_mac.validate(folder)
            excluded=next(x for x in metrics if x['request']=='full-source-control')
            self.assertEqual(excluded['status'],'context_excluded')
            self.assertIsNone(excluded['completion_tokens_api'])


if __name__=='__main__':unittest.main()
