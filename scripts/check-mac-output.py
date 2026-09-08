#!/usr/bin/env python3
"""Generate an inspectable local chat response; not an accuracy benchmark."""
import argparse
import csv
import datetime
import importlib.util
import json
from pathlib import Path
import re
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
from mac_runtime import model_specs, storage_relative

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.util.spec_from_file_location('macbench', ROOT/'scripts/run-mac-benchmark.py')
bench = importlib.util.module_from_spec(loader)
loader.loader.exec_module(bench)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model_id')
    p.add_argument('--context', type=int, default=4096)
    a = p.parse_args()
    spec = model_specs(ROOT)[a.model_id]
    model = ROOT/'work'/storage_relative(spec)
    if bench.sha256(model) != spec['sha256']: raise RuntimeError('Model hash mismatch')
    out = ROOT/'local-results'/('output-'+a.model_id+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    out.mkdir()
    prompt = 'Answer in three short sentences. What is 17 plus 25? Name the capital of France. Explain why a larger language model may run more slowly on the same computer.'
    with socket.socket() as available:
        available.bind(('127.0.0.1',0))
        port=available.getsockname()[1]
    command = [str(ROOT/'work/llama-metal/llama-b10852/llama-server'), '-m',str(model), '-dev','MTL0','-ngl','99','-sm','none','-fit','off','-fa','on','-ctk','f16','-ctv','f16','-b','512','-ub','512','-t','10','-c',str(a.context),'-np','1','--host','127.0.0.1','--port',str(port),'--alias',a.model_id,'--jinja','--reasoning','off','-v']
    request={'model':a.model_id,'messages':[{'role':'user','content':prompt}],'max_tokens':160,'temperature':0,'seed':1234,'chat_template_kwargs':{'enable_thinking':False},'stream':False}
    (out/'request.json').write_text(json.dumps(request,indent=2)+'\n')
    before=bench.snapshot()
    if not before['ac_connected']: raise RuntimeError('AC required')
    start=time.monotonic()
    samples=[dict(elapsed_seconds=0,**before)]
    abort=None
    reply={}
    def complete():
        try:
            req=urllib.request.Request(f'http://127.0.0.1:{port}/v1/chat/completions',data=json.dumps(request).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=1800) as response: reply['data']=json.load(response)
        except Exception as exc: reply['error']=str(exc)
    worker=None
    server_ready_seconds=None
    with (out/'runtime.log').open('w') as log:
        process=subprocess.Popen(command,stdout=log,stderr=log,stdin=subprocess.DEVNULL)
        try:
            while process.poll() is None:
                s=dict(elapsed_seconds=round(time.monotonic()-start,3),**bench.snapshot(process.pid));samples.append(s)
                if s['swap_used_bytes']-before['swap_used_bytes']>1024**3:abort='Swap growth exceeded 1 GiB'
                if not s['ac_connected']:abort='AC disconnected'
                if time.monotonic()-start>1800:abort='30 minute smoke-check timeout'
                if abort:break
                if worker is None:
                    try:
                        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1) as response:
                            ready=json.load(response).get('status')=='ok'
                        if ready:
                            server_ready_seconds=time.monotonic()-start
                            worker=threading.Thread(target=complete,daemon=True);worker.start()
                    except (urllib.error.URLError,TimeoutError):pass
                elif not worker.is_alive():break
                time.sleep(2)
            natural_exit=process.poll()
        finally:
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=15)
                except subprocess.TimeoutExpired:process.kill();process.wait()
            if worker:worker.join(timeout=5)
    samples.append(dict(elapsed_seconds=round(time.monotonic()-start,3),**bench.snapshot()))
    with (out/'memory.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=samples[0].keys());w.writeheader();w.writerows(samples)
    log=(out/'runtime.log').read_text(encoding='utf-8',errors='replace')
    offloads=re.findall(r'offloaded\s+(\d+)/(\d+)\s+layers to GPU',log)
    full=bool(offloads) and all(int(x)>0 and x==y for x,y in offloads)
    (out/'offload.txt').write_text('\n'.join(line for line in log.splitlines() if re.search(r'offloaded |buffer size|recommendedMaxWorkingSetSize|n_ctx\s+=|load time|eval time',line))+'\n')
    data=reply.get('data')
    if data:
        (out/'response.json').write_text(json.dumps(data,indent=2)+'\n')
        message=data['choices'][0]['message']
        (out/'output.txt').write_text(message.get('content','')+'\n')
    status={'model_id':a.model_id,'model_sha256':spec['sha256'],'prompt':prompt,'context':a.context,'max_generated_tokens':160,'temperature':0,'seed':1234,'reasoning':'disabled in request template kwargs','server_exit_before_cleanup':natural_exit,'server_returncode_after_cleanup':process.returncode,'response_received':bool(data),'request_error':reply.get('error'),'full_layer_offload':full,'abort_reason':abort,'server_ready_seconds':server_ready_seconds,'wall_seconds':time.monotonic()-start,'before':before,'after':samples[-1],'peak_rss_bytes':max(s['process_rss_bytes'] for s in samples),'swap_growth_bytes':max(s['swap_used_bytes'] for s in samples)-before['swap_used_bytes'],'command':[Path(x).name if x.startswith(str(ROOT)) else x for x in command],'output_review':'pending; inspect output.txt and record evaluator identity in a separate review.json'}
    (out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    print(out)
    if not data or abort or not full:raise RuntimeError('Smoke check did not complete with full GPU offload')

if __name__=='__main__':
    from mac_runtime import gpu_lock
    with gpu_lock(ROOT): main()
