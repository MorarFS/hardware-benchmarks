"""Frozen history-v2 prompts on existing Arc SYCL weights; a documented configuration variant."""
import sys, json, time, subprocess, urllib.request, threading, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/history_v2'))
import runner as frozen
SUITE = ROOT / 'experiments/history-v2'
OUT = ROOT / 'outputs/history-arc-v2'
BASE = 'http://127.0.0.1:18984'
MODELS = [('qwen36-35b', 'qwen36-model-metadata.json'), ('gemma4-26b', 'gemma-model-metadata.json'), ('qwen38-27b', 'qwen38-model-metadata.json')]

def save(path, data):
    frozen.save(path, data)

def api(path, payload=None, timeout=30):
    req = urllib.request.Request(BASE + path, data=None if payload is None else json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)

def payload_for(name, prompt, suite):
    return dict(model=name, messages=[{'role':'system','content':suite['prompts']['system']}, {'role':'user','content':prompt}], temperature=0, top_p=1, top_k=40, min_p=0, repeat_penalty=1, seed=42, max_tokens=2048, stream=True, stream_options={'include_usage':True}, cache_prompt=False, chat_template_kwargs={'enable_thinking':False})

def request(folder, name, prompt, inputs, suite, parents=None):
    assert not any(x.startswith('gold/') for x in inputs)
    payload = payload_for(folder.name, prompt, suite)
    fp = frozen.fingerprint(payload)
    path = folder / (name + '.json')
    if path.exists():
        old = frozen.read_json(path)
        if old['fingerprint'] != fp or old['status'] in ('error','timeout'):
            raise RuntimeError('Cannot resume changed or failed request: ' + name)
        return old
    save(folder / (name + '-request.json'), payload)
    save(OUT / 'status.json', dict(model=folder.name, request=name, state='running', time=frozen.now()))
    print(folder.name, name, 'started', flush=True)
    result = {}
    def worker():
        start = time.perf_counter()
        text, reason, usage, timing, finish = '', '', {}, {}, None
        done = False
        try:
            req = urllib.request.Request(BASE + '/v1/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req, timeout=90) as response, (folder / (name + '-stream.jsonl')).open('w', encoding='utf-8') as stream:
                for line in response:
                    if not line.startswith(b'data:'): continue
                    elapsed = time.perf_counter() - start
                    raw = line[5:].strip()
                    if raw == b'[DONE]':
                        done = True
                        break
                    event = json.loads(raw)
                    stream.write(json.dumps({'elapsed_seconds':elapsed,'event':event}, ensure_ascii=False)+'\n')
                    stream.flush()
                    if event.get('error'): raise RuntimeError(str(event['error']))
                    if event.get('usage'): usage = event['usage']
                    if event.get('timings'): timing = event['timings']
                    for choice in event.get('choices', []):
                        delta = choice.get('delta', {})
                        if delta.get('content'):
                            result.setdefault('first_visible_seconds', elapsed)
                            text += delta['content']
                        reason += delta.get('reasoning_content') or ''
                        finish = choice.get('finish_reason') or finish
            if not done or finish is None: raise RuntimeError('Incomplete stream')
            wall = time.perf_counter()-start
            result.update(status='capped' if finish=='length' else 'ok' if text.strip() else 'empty', output=text, reasoning=reason, usage=usage, timings=timing, finish_reason=finish, wall_seconds=wall, word_count=len(text.split()))
            if reason.strip(): raise RuntimeError('Unexpected reasoning in reasoning-OFF profile')
        except Exception as e:
            result.update(status='error', error=str(e), partial_output=text)
    thread = threading.Thread(target=worker, daemon=True)
    thread.start(); thread.join(900)
    if thread.is_alive(): result.update(status='timeout', error='900-second deadline; no retry')
    result.update(name=name, fingerprint=fp, source_files=inputs, parent_requests=parents or [], quality='Unadjudicated', finished_at=frozen.now())
    save(path, result)
    if result.get('output'): (folder / (name + '.md')).write_text(result['output']+'\n', encoding='utf-8')
    print(folder.name, name, result['status'], round(result.get('wall_seconds',0),2), flush=True)
    if result['status'] in ('error','timeout'): raise RuntimeError(result.get('error'))
    return result

def run_model(name, manifest, suite):
    folder = OUT / name
    folder.mkdir(parents=True, exist_ok=True)
    if (folder/'complete.json').exists(): return
    meta = json.loads((ROOT/'work'/manifest).read_text(encoding='utf-8-sig'))
    model = ROOT/'work'/meta['file']['path']
    actual = frozen.sha256(model)
    if actual != meta['file']['lfs']['oid']: raise RuntimeError('Model checksum mismatch')
    save(folder/'model-source.json', meta)
    args = [str(ROOT/'work/llama-sycl/llama-server.exe'), '-m', str(model), '--host','127.0.0.1','--port','18984','--alias',name,'-dev','SYCL0','-sm','none','-ngl','99','-fa','on','-ctk','f16','-ctv','f16','-c','65536','-np','1','-b','512','-ub','512','-t','10','--seed','42','--reasoning','off','--spec-type','none','--fit','off']
    args += ['-v']
    save(folder/'configuration.json', dict(model_sha256=actual, backend='llama.cpp b10852 SYCL, Intel Arc Pro B70', context=65536, seed=42, reasoning='off', mtp=False, kv='f16', parallel=1, sampling=dict(temperature=0, top_p=1, top_k=40,min_p=0,repeat_penalty=1), command=['llama-server','-m',model.name]+args[3:], deviations=['SYCL instead of Evo LM Studio Vulkan native API','Existing verified weights differ from frozen Evo profiles; Qwen has no MTP','Qwen3.8 27B is an added model; GPT-OSS 120B is not installed','OpenAI-compatible stream timings kept separate from Evo native/SDK token measurements']))
    with (folder/'server.log').open('w',encoding='utf-8') as log:
        proc = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline = time.monotonic()+600
            while True:
                if proc.poll() is not None: raise RuntimeError('Server exited: '+str(proc.returncode))
                try:
                    if api('/health', timeout=3).get('status')=='ok': break
                except Exception: pass
                if time.monotonic()>deadline: raise RuntimeError('Server load deadline exceeded')
                time.sleep(2)
            props=api('/props'); save(folder/'server-properties.json',props)
            import re
            contents=(folder/'server.log').read_text(encoding='utf-8',errors='replace')
            match=re.search(r'offloaded\s+(\d+)/(\d+)\s+layers to GPU',contents)
            if not match or match[1]!=match[2]: raise RuntimeError('Full GPU layer offload not confirmed')
            (folder/'offload.txt').write_text('\n'.join(line for line in contents.splitlines() if any(s in line for s in ('offloaded','KV buffer','model buffer','n_ctx','Intel(R) Arc')))+'\n',encoding='utf-8')
            stages, control = frozen.source_stages(suite)
            results={}
            for stage,prompt,inputs in stages:
                results[stage]=request(folder,stage,prompt,inputs,suite)
            parents=[h['id']+'-summary' for h in suite['questions']]
            if all(results[p]['status']=='ok' for p in parents):
                material='\n\n'.join(h['id']+'\n'+results[h['id']+'-summary']['output'] for h in suite['questions'])
                stage='merged-summary-synthesis'
                results[stage]=request(folder,stage,suite['prompts']['synthesis'].format(source=material),['prompts.json'],suite,parents)
            else:
                results['merged-summary-synthesis']={'status':'blocked_by_parent'}
                save(folder/'merged-summary-synthesis.json',results['merged-summary-synthesis'])
            stage,prompt,inputs=control
            results[stage]=request(folder,stage,prompt,inputs,suite)
            save(folder/'complete.json',dict(stages={k:v['status'] for k,v in results.items()}, quality='Source adjudication pending', time=frozen.now()))
        finally:
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(20)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()

def main():
    suite=frozen.load_suite(SUITE)
    OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'protocol.json',dict(suite='history-v2.0', frozen_files=suite['freeze'], models=[m[0] for m in MODELS], request_count_per_model=12, gold_in_prompts=False, variant='Arc SYCL on existing weights; not exact Evo configuration reproduction'))
    for name,manifest in MODELS:
        try: run_model(name,manifest,suite)
        except Exception as e:
            save(OUT/name/'error.json',dict(error=str(e),time=frozen.now()))
            print(name, 'ERROR', str(e),flush=True)
    save(OUT/'status.json',dict(state='generation_finished',quality='Adjudication pending',time=frozen.now()))

if __name__=='__main__': main()
