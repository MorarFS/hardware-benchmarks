#!/usr/bin/env python3
"""Validate and collect accepted Mac measurements without replacing prior data."""
import csv
import argparse
import getpass
import io
import json
import math
from pathlib import Path
import re
import statistics
from mac_runtime import model_specs

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/2026-09-08/mac'
FIELDS=['run','test','depth','selected_gpu','device','backend','mean_tokens_per_second','sd_tokens_per_second']

def validate(entries, status, manifest):
    spec=manifest[status['model_id']]
    assert status['model_sha256']==spec['sha256'], 'Artifact mismatch'
    assert status['exit_code']==0 and not status['abort_reason'] and status['full_layer_offload'], 'Unaccepted run'
    assert status['all_samples_ac'], 'Battery measurement'
    depth=status['depth']
    expected=[(512,0),(0,256)] if depth==0 else [(0,256)]
    assert [(e['n_prompt'],e['n_gen']) for e in entries]==expected
    for e in entries:
        required={'build_commit':'050dde50c','build_number':10852,'devices':'MTL0','n_batch':512,'n_ubatch':512,'n_threads':10,'type_k':'f16','type_v':'f16','n_gpu_layers':99,'n_cpu_moe':0,'split_mode':'none','no_kv_offload':False,'flash_attn':1,'n_depth':depth,'fit_target':0,'model_filename':spec['filename']}
        for key,value in required.items():assert e[key]==value, f'{key} mismatch'
        assert len(e['samples_ns'])==len(e['samples_ts'])==5
        rates=[(e['n_prompt']+e['n_gen'])*1e9/ns for ns in e['samples_ns']]
        assert math.isclose(statistics.mean(rates),e['avg_ts'],abs_tol=1e-5)
        assert math.isclose(statistics.stdev(rates),e['stddev_ts'],abs_tol=1e-5)


def collect(update_main_summary=False):
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=model_specs(ROOT)
    rows=[]
    inventory=[]
    names=set()
    for status_path in sorted((ROOT/'local-results').glob('apple-metal-*/*-status.json')):
        if (status_path.parent/'exclusion.json').exists():
            print('Excluded documented protocol deviation:',status_path.parent.name)
            continue
        status=json.loads(status_path.read_text())
        if status['exit_code'] or status['abort_reason'] or not status['full_layer_offload'] or status.get('validation_passed') is False:
            print('Excluded failed/unvalidated attempt:',status_path.parent.name,status['model_id'],status['depth'])
            continue
        stem=str(status_path).removesuffix('-status.json')
        measurement=Path(stem+'.json')
        entries=json.loads(measurement.read_text())
        validate(entries,status,manifest)
        name=measurement.stem
        if name in names:raise RuntimeError('Multiple accepted sessions require explicit selection: '+name)
        names.add(name)
        for suffix in ['.json','-status.json','-memory.csv','-offload.txt']:
            src=Path(stem+suffix);dst=OUT/src.name
            content=src.read_text()
            private_pattern=r'/Users/|Serial Number|\b'+re.escape(getpass.getuser())+r'\b'
            if re.search(private_pattern,content):raise RuntimeError('Private path/identifier requires review: '+src.name)
            if dst.exists() and dst.read_text()!=content:raise RuntimeError('Refusing to replace differing evidence: '+dst.name)
            dst.write_text(content)
        for e in entries:
            rows.append(dict(zip(FIELDS,[name,'Prompt processing 512' if e['n_prompt'] else 'Generation 256',e['n_depth'],'Apple M5 Pro (20 GPU cores)','MTL0','Metal',f"{e['avg_ts']:.6f}",f"{e['stddev_ts']:.6f}"])))
        memory=list(csv.DictReader(Path(stem+'-memory.csv').open()))
        inventory.append({'run':name,'model_id':status['model_id'],'depth':status['depth'],'wall_seconds_including_load':status['wall_seconds_including_load'],'peak_process_rss_bytes':status['peak_rss_bytes'],'swap_before_bytes':status['before']['swap_used_bytes'],'peak_system_swap_bytes':status['peak_swap_used_bytes'],'swap_growth_bytes':status['swap_growth_bytes'],'compressor_before_bytes':status['before']['pages_occupied_by_compressor_bytes'],'peak_system_compressor_bytes':max(float(r['pages_occupied_by_compressor_bytes']) for r in memory),'full_layer_offload':True,'all_samples_ac':True})
    with (OUT/'summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,quoting=csv.QUOTE_ALL);w.writeheader();w.writerows(rows)
    (OUT/'fit-summary.json').write_text(json.dumps(inventory,indent=2)+'\n')
    if update_main_summary:
        path=ROOT/'results/summary.csv'
        original=path.read_bytes()
        reader=csv.DictReader(io.StringIO(original.decode('utf-8-sig')))
        assert reader.fieldnames==FIELDS, 'Unexpected main summary schema'
        existing=list(reader)
        def key(row):return row['run'],row['test'],row['depth']
        by_key={key(row):row for row in existing}
        additions=[]
        for row in rows:
            row={k:str(v) for k,v in row.items()}
            if key(row) in by_key:
                assert by_key[key(row)]==row, 'Existing summary evidence differs; explicit review required'
            else:additions.append(row)
        if additions:
            stream=io.StringIO(newline='')
            writer=csv.DictWriter(stream,fieldnames=FIELDS,quoting=csv.QUOTE_ALL,lineterminator='\r\n' if b'\r\n' in original else '\n')
            writer.writerows(additions)
            assert original.endswith(b'\n'), 'Main summary requires newline before safe append'
            path.write_bytes(original+stream.getvalue().encode())
        print('Appended',len(additions),'main-summary rows; previous bytes preserved')
    print(f'Validated and collected {len(rows)} measurements from {len(inventory)} depth runs')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-main-summary',action='store_true')
    collect(parser.parse_args().update_main_summary)
