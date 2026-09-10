import csv,importlib.util,json,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE;sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('bench',ROOT/'scripts/run-mac-benchmark.py');bench=importlib.util.module_from_spec(spec);spec.loader.exec_module(bench)
OUT=BASE/'local-results/m4-cpu';OUT.mkdir(exist_ok=True)
for depth in [0,2048]:
 command=[str(ROOT/'work/llama-metal/llama-b10852/llama-bench'),'-m',str(ROOT/'work/Qwen3-8B-Q4_K_M.gguf'),'-ngl','0','-dev','none','-sm','none','-fa','on','-ctk','f16','-ctv','f16','-b','512','-ub','512','-t','10','-p','512' if depth==0 else '0','-n','256','-d',str(depth),'-r','5','-o','json','-v']
 stem=OUT/f'qwen8-cpu-depth{depth}';before=bench.snapshot();samples=[];started=time.monotonic();abort=None
 with stem.with_suffix('.json').open('w') as stdout,stem.with_suffix('.log').open('w') as stderr:
  p=subprocess.Popen(command,stdout=stdout,stderr=stderr)
  try:
   while p.poll() is None:
    row={'elapsed_seconds':time.monotonic()-started,**bench.snapshot(p.pid)};samples.append(row)
    if row['swap_used_bytes']-before['swap_used_bytes']>1024**3:abort='swap growth above 1 GiB'
    if not row['ac_connected']:abort='AC disconnected'
    if time.monotonic()-started>1800:abort='timeout'
    if abort:p.terminate();break
    time.sleep(2)
   p.wait(timeout=15)
  finally:
   if p.poll() is None:p.kill();p.wait()
 with Path(str(stem)+'-memory.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=samples[0].keys());w.writeheader();w.writerows(samples)
 Path(str(stem)+'-status.json').write_text(json.dumps({'command':command,'returncode':p.returncode,'abort':abort,'wall_seconds':time.monotonic()-started,'before':before,'after':bench.snapshot()},indent=2))
 if p.returncode or abort:raise RuntimeError('CPU run failed')
 print('CPU completed depth',depth,flush=True)
