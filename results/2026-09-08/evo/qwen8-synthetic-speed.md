# Qwen3-8B matched synthetic speed

Exact official Q4_K_M GGUF, SHA-256 `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`. Evo X3, Ryzen AI MAX+ 395, Radeon 8060S. Five measured repetitions, default warmup enabled. Full GPU layer offload, split none, flash attention ON, FP16 KV, logical/physical batch 512, ten CPU threads. Power profile remains balanced.

| Backend / build | pp512 at depth 0 | tg256 at depth 0 | tg256 at depth 2048 | Validation state |
|---|---:|---:|---:|---|
| Vulkan b10852 / 050dde50c | 1237.73 ± 5.22 | 43.62 ± 0.05 | 40.90 ± 0.08 | Matches laptop source revision |
| Stock HIP b10852 / 050dde50c | 1218.52 ± 30.65 | 42.70 ± 0.13 | 40.21 ± 0.10 | Failed long prose; do not treat raw speed as useful generation |
| AMD HIP b10606 / 03d2068a1 | 1376.09 ± 50.72 | 43.51 ± 0.10 | 40.20 ± 0.39 | Repeated short/long prose recovered; different backend source and bundled libraries |

All cells are tokens/s, mean ± sample standard deviation. Pending means no completed result yet. The first two rows match the laptop source build. The repaired AMD row is a backend-build-plus-runtime comparison, not pure backend isolation. Stock HIP loads the installed ROCm 7.2.70204 libraries; AMD’s package supplies ROCm 10.1.0a20260822. The two runtimes are isolated.

Synthetic generation excludes tokenization, chat templates, sampling, and source checking. These are not measured user-visible chat rates or first-token latency. A synthetic result cannot certify that a model answers correctly. `pp512` is prompt processing and must not be compared with decode speed. Context depth is seeded tokens before generation, not the allocated chat context.

Exact core commands, with paths and device chosen per backend:

```sh
llama-bench -m Qwen3-8B-Q4_K_M.gguf -dev DEVICE -sm none -ngl 99 -fa on -b 512 -ub 512 -t 10 -ctk f16 -ctv f16 -p 512 -n 256 -d 0 -r 5 -o json --progress
llama-bench -m Qwen3-8B-Q4_K_M.gguf -dev DEVICE -sm none -ngl 99 -fa on -b 512 -ub 512 -t 10 -ctk f16 -ctv f16 -p 0 -n 256 -d 2048 -r 5 -o json --progress
```

Devices are `Vulkan0` and `ROCm0`. This benchmark uses synthetic token streams. Full JSON retains the five sample rates, hardware, build, buffer settings, and timing counters. No OS cache flush was performed. One benchmark process runs at a time, after model-server instances are unloaded.

See [application timings](amd-speed-comparison.md) and [ROCm repair evidence](rocm-repair-status.md) for separate practical generation results.
