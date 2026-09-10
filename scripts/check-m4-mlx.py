"""Separate MLX application and hardware observations, not GGUF matched rows."""
import json,time,statistics,subprocess
from pathlib import Path
import mlx.core as mx
from mlx_lm import load,stream_generate
from mlx_lm.sample_utils import make_sampler
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'local-results'/'m4-mlx'; OUT.mkdir(exist_ok=True)
results={'device':mx.device_info(),'matrix':[],'application':[]}
# Synchronized matrix work; one warmup then five samples per shape.
for n in [2048,4096,8192]:
 mx.random.seed(42); a=mx.random.normal((n,n)).astype(mx.float16); b=mx.random.normal((n,n)).astype(mx.float16);mx.eval(a,b)
 c=a@b;mx.eval(c);mx.synchronize()
 samples=[]
 for _ in range(5):
  start=time.perf_counter();c=a@b;mx.eval(c);mx.synchronize();samples.append(time.perf_counter()-start)
 results['matrix'].append({'n':n,'dtype':'float16','seconds':samples,'mean_tflops':statistics.mean(2*n**3/s/1e12 for s in samples),'note':'Synchronized MLX matmul, excludes input initialization. Not theoretical peak or sustained training throughput.'})
 del a,b,c;mx.clear_cache()
start=time.perf_counter();model,tok=load(str(BASE/'work/mlx-qwen8'));results['load_seconds']=time.perf_counter()-start
prompt='Explain in plain English how unified memory affects local language-model inference. Discuss weights, KV cache, and why a model can fit yet be slow. Use about 180 words.'
rendered=tok.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
for i in range(4):
 start=time.perf_counter();first=None;text='';last=None
 for response in stream_generate(model,tok,rendered,max_tokens=256,sampler=make_sampler(temp=0)):
  if response.text and first is None:first=time.perf_counter()-start
  text+=response.text;last=response
 results['application'].append({'warmup':i==0,'wall_seconds':time.perf_counter()-start,'first_content_seconds':first,'prompt_tokens':last.prompt_tokens,'prompt_tps':last.prompt_tps,'generation_tokens':last.generation_tokens,'generation_tps':last.generation_tps,'peak_memory_gb':last.peak_memory,'finish_reason':last.finish_reason,'text':text})
results['prompt']=prompt;results['model_revision']='545dc4251c05440727734bcd94334791f6ab0192';results['note']='MLX 4-bit group quantization differs from Q4_K_M GGUF; application counts/timing differ from llama-bench synthetic tests.'
(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
