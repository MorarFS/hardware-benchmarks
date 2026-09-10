#!/usr/bin/env python3
"""Run unchanged frozen history prompts with a documented local Metal adaptation."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from mac_prompt_adapter import adapter_receipt, messages

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from mac_runtime import gpu_lock, model_specs, storage_relative
import runner as frozen
loader=importlib.util.spec_from_file_location('macbench',ROOT/'scripts/run-mac-benchmark.py')
bench=importlib.util.module_from_spec(loader);loader.loader.exec_module(bench)


def post(base,path,payload,timeout=30):
    req=urllib.request.Request(base+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as response:return json.load(response)


def stream(base,payload,folder,name,result):
    started=time.monotonic();content=[];reasoning=[];usage=None;timings=None;first=None;finish=None;done=False
    try:
        req=urllib.request.Request(base+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=900) as response,(folder/(name+'-stream.jsonl')).open('w') as events:
            for raw in response:
                if not raw.startswith(b'data:'):continue
                data=raw[5:].strip()
                if data==b'[DONE]':done=True;break
                event=json.loads(data);elapsed=time.monotonic()-started
                events.write(json.dumps({'elapsed_seconds':elapsed,'event':event})+'\n');events.flush()
                if event.get('error'):raise RuntimeError(str(event['error']))
                usage=event.get('usage') or usage;timings=event.get('timings') or timings
                for choice in event.get('choices',[]):
                    delta=choice.get('delta',{})
                    if delta.get('content'):
                        content.append(delta['content'])
                        if first is None:first=elapsed
                    if delta.get('reasoning_content'):reasoning.append(delta['reasoning_content'])
                    finish=choice.get('finish_reason') or finish
        if not done:raise RuntimeError('Stream ended without DONE')
        text=''.join(content)
        status='capped' if finish=='length' else 'ok' if text.strip() else 'empty'
        result.update(status=status,output=text,reasoning_output=''.join(reasoning),finish_reason=finish,usage=usage,timings=timings,first_visible_seconds=first,wall_seconds=time.monotonic()-started,word_count=len(text.split()))
    except Exception as exc:result.update(status='error',error=str(exc),wall_seconds=time.monotonic()-started)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('model_id')
    p.add_argument('--output',type=Path)
    p.add_argument('--context',type=int,default=16384)
    p.add_argument('--cache-ram-mib',type=int,help='Explicit RAM prompt-cache limit for a separately recorded memory configuration; default uses the pinned runtime default')
    a=p.parse_args()
    if a.cache_ram_mib is not None and a.cache_ram_mib <= 0:p.error('Explicit cache limit must be positive; omit the option to preserve the runtime default')
    protocol=json.loads((ROOT/'experiments/history-v2-mac/protocol.json').read_text())
    protocol.update(version='history-v2-m4-capacity-1.0',context_tokens=a.context,context_reason='Bounded 16K capacity workload on M4 Max 64 GiB; full prompt plus output must fit.',reasoning='Native thinking, server auto, explicit 512-token budget per thinking block; total output cap2048',models=[a.model_id],comparison_limit='Separate thinking-budget configuration, not reasoning-off matched history results.')
    suite=frozen.load_suite(ROOT/'experiments/history-v2')
    spec=model_specs(ROOT)[a.model_id]
    model=ROOT/'work'/storage_relative(spec)
    if bench.sha256(model)!=spec['sha256']:raise RuntimeError('Model hash mismatch')
    folder=a.output or ROOT/'local-results'/('history-v2-mac-'+a.model_id)
    folder.mkdir(parents=True,exist_ok=True)
    receipt={'protocol':protocol,'model_id':a.model_id,'model':spec,'actual_context':a.context,'freeze_sha256':frozen.sha256(ROOT/'experiments/history-v2/freeze.json'),'fixture_hashes':suite['freeze']['files']}
    if adapter_receipt(a.model_id):receipt['message_adapter']=adapter_receipt(a.model_id)
    if a.cache_ram_mib is not None:receipt['prompt_cache_ram_mib']=a.cache_ram_mib
    receipt_path=folder/'protocol.json'
    if receipt_path.exists() and frozen.read_json(receipt_path)!=receipt:raise RuntimeError('Changed protocol requires new output directory')
    frozen.save(receipt_path,receipt)
    if (folder/'complete.json').exists():print('Existing terminal generation:',folder);return
    before=bench.snapshot()
    if not before['ac_connected']:raise RuntimeError('AC required')
    with socket.socket() as available:available.bind(('127.0.0.1',0));port=available.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    command=[str(ROOT/'work/llama-metal/llama-b10852/llama-server'),'-m',str(model),'-dev','MTL0','-ngl','99','-sm','none','-fit','off','-fa','on','-ctk','f16','-ctv','f16','-b','512','-ub','512','-t','10','-c',str(a.context),'-np','1','--host','127.0.0.1','--port',str(port),'--alias',a.model_id,'--jinja','--reasoning','auto','--reasoning-budget','512','--spec-type','none','--no-context-shift','-v']
    if a.cache_ram_mib is not None:command+=['--cache-ram',str(a.cache_ram_mib)]
    frozen.save(folder/'server-command.json',[Path(x).name if x.startswith(str(ROOT)) else x for x in command])
    log_path=folder/'runtime.log'
    started=time.monotonic();samples=[];current='loading';abort=None;results={}
    with log_path.open('a') as log,(folder/'memory.csv').open('w',newline='') as memory:
        writer=None
        process=subprocess.Popen(command,stdout=log,stderr=log,stdin=subprocess.DEVNULL)
        def monitor():
            nonlocal writer,abort
            s=dict(elapsed_seconds=round(time.monotonic()-started,3),stage=current,**bench.snapshot(process.pid))
            if writer is None:writer=csv.DictWriter(memory,fieldnames=s.keys());writer.writeheader()
            writer.writerow(s);memory.flush();samples.append(s)
            if s['swap_used_bytes']-before['swap_used_bytes']>1024**3:abort='System swap growth exceeded 1 GiB'
            if not s['ac_connected']:abort='AC disconnected'
            if process.poll() is not None:abort='Server exited unexpectedly'
            if abort:raise RuntimeError(abort)
        def request(name,prompt,inputs,parents=None):
            nonlocal current
            current=name
            if any(x.startswith('gold/') for x in inputs):raise RuntimeError('Gold must not enter generator')
            payload={'model':a.model_id,'messages':messages(a.model_id,suite['prompts']['system'],prompt),'stream':True,'stream_options':{'include_usage':True},'max_tokens':2048,**protocol['sampling']}
            fp=frozen.fingerprint(payload);path=folder/(name+'.json')
            if path.exists():
                record=frozen.read_json(path)
                if record.get('fingerprint')!=fp:raise RuntimeError('Changed request fingerprint')
                if record.get('status') in ['running','error','timeout']:raise RuntimeError('Prior interrupted request requires deliberate recovery; no automatic retry')
                return record
            rendered=post(base,'/apply-template',{'messages':payload['messages']})['prompt']
            if a.model_id=='nemotron-49b':
                if '/no_think' in rendered or not rendered.endswith('<think>\n\n</think>\n\n'):
                    raise RuntimeError('Native Nemotron no-think rendering was not verified')
            tokens=post(base,'/tokenize',{'content':rendered,'add_special':True})['tokens']
            frozen.save(folder/(name+'-request.json'),payload)
            record={'name':name,'fingerprint':fp,'source_files':inputs,'parent_requests':parents or [],'rendered_prompt_tokens':len(tokens),'output_budget':2048,'status':'running','quality':'Unadjudicated','started_at':frozen.now()}
            if len(tokens)+2048+256>a.context:
                record.update(status='context_excluded',submitted=False,reason='Complete prompt plus output allowance and margin exceeds actual context; no truncation or extrapolation',finished_at=frozen.now())
                frozen.save(path,record)
                print(a.model_id,name,'context excluded; not submitted',len(tokens),a.context,flush=True)
                return record
            frozen.save(path,record)
            current=name;frozen.save(folder/'status.json',{'state':'request','name':name,'time':frozen.now()})
            print(a.model_id,name,'prompt tokens',len(tokens),flush=True)
            result={};worker=threading.Thread(target=stream,args=(base,payload,folder,name,result),daemon=True);worker.start();request_start=time.monotonic()
            try:
                while worker.is_alive():
                    monitor()
                    if time.monotonic()-request_start>900:raise RuntimeError('900-second request deadline; no retry')
                    time.sleep(2)
            except Exception as exc:
                record.update(status='error',error=str(exc),finished_at=frozen.now());frozen.save(path,record)
                raise
            record.update(result,finished_at=frozen.now());frozen.save(path,record)
            (folder/(name+'.md')).write_text(record.get('output','')+'\n')
            print(a.model_id,name,record['status'],record.get('usage'),flush=True)
            if record['status']=='error':raise RuntimeError(record.get('error','Transport failed'))
            return record
        try:
            while True:
                monitor()
                if time.monotonic()-started>600:raise RuntimeError('Server startup exceeded 600 seconds')
                try:
                    with urllib.request.urlopen(base+'/health',timeout=1) as response:
                        if json.load(response).get('status')=='ok':break
                except (urllib.error.URLError,TimeoutError):pass
                time.sleep(2)
            loadlog=log_path.read_text(encoding='utf-8',errors='replace')
            if 'build 10852 (050dde50c)' not in loadlog:raise RuntimeError('Unexpected llama.cpp runtime build')
            native_context=re.findall(r'n_ctx_train\s*=\s*(\d+)',loadlog)
            if native_context and a.context>min(map(int,native_context)):raise RuntimeError('Requested context exceeds trained context; use an explicitly recorded supported context')
            offloads=re.findall(r'offloaded\s+(\d+)/(\d+)\s+layers to GPU',loadlog)
            if not offloads or not all(int(x)>0 and x==y for x,y in offloads):raise RuntimeError('Full GPU offload not verified')
            load={'full_layer_offload':True,'ready_seconds':time.monotonic()-started,'context':a.context,'before':before}
            if a.cache_ram_mib is not None:
                observed_cache=re.findall(r'prompt cache is enabled, size limit: (\d+) MiB',loadlog)
                if a.cache_ram_mib:
                    if not observed_cache or int(observed_cache[-1])!=a.cache_ram_mib:raise RuntimeError('Requested RAM prompt-cache limit not observed')
                elif 'prompt cache is disabled' not in loadlog:raise RuntimeError('Disabled RAM prompt cache not observed')
                load['prompt_cache_ram_mib']=a.cache_ram_mib
            frozen.save(folder/'load.json',load)
            stages,control=frozen.source_stages(suite)
            for name,prompt,inputs in stages:results[name]=request(name,prompt,inputs)
            parents=[h['id']+'-summary' for h in suite['questions']]
            if all(results[name]['status']=='ok' for name in parents):
                material='\n\n'.join(h['id']+'\n'+results[h['id']+'-summary']['output'] for h in suite['questions'])
                name='merged-summary-synthesis';results[name]=request(name,suite['prompts']['synthesis'].format(source=material),['prompts.json'],parents)
            else:
                results['merged-summary-synthesis']={'status':'blocked_by_parent','parents':parents};frozen.save(folder/'merged-summary-synthesis.json',results['merged-summary-synthesis'])
            name,prompt,inputs=control;results[name]=request(name,prompt,inputs)
            frozen.save(folder/'complete.json',{'time':frozen.now(),'stages':{n:r['status'] for n,r in results.items()},'quality':'Source adjudication pending; generation completion is not an accuracy pass'})
        except Exception as exc:
            frozen.save(folder/'failure.json',{'stage':current,'error':str(exc),'time':frozen.now(),'status':'failed; no silent context or offload reduction'})
            raise
        finally:
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=15)
                except subprocess.TimeoutExpired:process.kill();process.wait()
            excerpts=[line for line in log_path.read_text(encoding='utf-8',errors='replace').splitlines() if re.search(r'common_params_print_info: build|offloaded |buffer size|recommendedMaxWorkingSetSize|n_ctx\s+=|load time|eval time',line)]
            (folder/'offload.txt').write_text('\n'.join(excerpts)+'\n')
            frozen.save(folder/'memory-summary.json',{'before':before,'after':bench.snapshot(),'peak_process_rss_bytes':max((s['process_rss_bytes'] for s in samples),default=0),'peak_swap_used_bytes':max((s['swap_used_bytes'] for s in samples),default=0),'sample_interval_seconds':2,'server_returncode_after_cleanup':process.returncode})
    print('Generation terminal:',folder,flush=True)

if __name__=='__main__':
    with gpu_lock(ROOT):main()
