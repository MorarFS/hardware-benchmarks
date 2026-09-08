# Three-model SYCL follow-up

**All three models completed.** Qwen3.6 35B-A3B is the fastest measured candidate for the approximately 40 generated-token/s goal on this external Intel Arc Pro B70 32 GB. Gemma 4 26B-A4B also clears the target; Qwen3.8 27B falls below it. This comparison measures throughput and memory use, not answer quality.

| Candidate | Generation at depth 0 (tokens/s) | Generation at depth 2,048 (tokens/s) | Approximately 40 tokens/s target |
| --- | ---: | ---: | --- |
| Qwen3.6 35B-A3B UD-Q4_K_M | 73.33 | 71.53 | Exceeded at both depths; fastest measured |
| Gemma 4 26B-A4B Instruct Q4_K_M | 64.27 | 56.68 | Exceeded at both depths |
| Qwen3.8 27B UD-Q4_K_M | 20.92 | 20.42 | Below at both depths |

## Protocol and model differences

The same Windows laptop, AC power, Intel driver 32.0.101.8805 and llama.cpp b10852 SYCL runtime are used. Downloads and benchmarks run sequentially. Each test uses one selected Arc, all layers requested on the GPU, flash attention, FP16 KV, batch/microbatch 512, ten threads, five measured repetitions after warmup, and 256 generated tokens at initial depths 0 and 2,048. Prompt processing uses 512 tokens separately at depth 0. Timed throughput excludes loading, tokenization and sampling.

These are text-only llama-bench tests. Image, audio, video, multimodal processing, application response latency and answer quality were not evaluated. Short synthetic runs do not establish performance at longer production contexts or on representative user tasks.

Gemma uses bartowski **Q4_K_M**; the Qwen artifacts use Unsloth **UD-Q4_K_M** dynamic quantization. These are different four-bit quantization recipes on different models and architectures. Equal nominal bit depth does not make them identical quality or performance treatments.

| Model | Artifact recipe | Download bytes | Status |
| --- | --- | ---: | --- |
| Gemma 4 26B-A4B Instruct | bartowski Q4_K_M | 17,035,039,872 | Completed |
| Qwen3.6 35B-A3B | Unsloth UD-Q4_K_M | 22,134,528,992 | Completed |
| Qwen3.8 27B | Unsloth UD-Q4_K_M | 16,464,440,224 | Completed |

The Gemma artifact's branded model name remains **26B-A4B**. Its GGUF reports **25,233,142,046 parameters**; the raw count is preserved without renaming the model.

Qwen3.6 35B-A3B reports **34,660,610,688 parameters** in its GGUF. Its download passed the pinned SHA-256 check.

Qwen3.8 27B reports **27,320,697,856 parameters** in its GGUF. All three downloads passed their pinned SHA-256 checks.

## Completed measurements

| Model | Test | Initial depth | Mean tokens/s | SD tokens/s |
| --- | --- | ---: | ---: | ---: |
| Gemma 4 26B-A4B Instruct | Prompt processing 512 | 0 | 1089.895706 | 96.083135 |
| Gemma 4 26B-A4B Instruct | Generation 256 | 0 | 64.274290 | 0.174561 |
| Gemma 4 26B-A4B Instruct | Generation 256 | 2048 | 56.677035 | 0.041391 |
| Qwen3.6 35B-A3B | Prompt processing 512 | 0 | 882.535001 | 145.248203 |
| Qwen3.6 35B-A3B | Generation 256 | 0 | 73.334245 | 0.169815 |
| Qwen3.6 35B-A3B | Generation 256 | 2048 | 71.525257 | 0.889735 |
| Qwen3.8 27B | Prompt processing 512 | 0 | 308.945183 | 1.890944 |
| Qwen3.8 27B | Generation 256 | 0 | 20.922442 | 0.017169 |
| Qwen3.8 27B | Generation 256 | 2048 | 20.418157 | 0.039988 |

Qwen3.6 and Gemma exceeded the approximately 40-token/s generation target at both tested depths. Qwen3.8 completed successfully with all layers offloaded, but generated below the target. The observed throughput ranking does not establish a quality winner, a general architecture ranking, or maximum possible performance.

Qwen3.6 prompt-processing samples were **668.212, 794.600, 976.567, 976.644 and 996.651 tokens/s**. All five, including the slower first sample, remain in the mean and standard deviation; no sample was discarded. This variation limits interpretation of its prompt-processing average.

## Offload and memory evidence

Both Gemma logs confirm **31/31 layers offloaded**, with a **16,230.86 MiB SYCL0 model buffer** and **577.50 MiB CPU_Mapped model buffer**. Host/shared memory use is retained explicitly.

Both Qwen3.6 logs confirm **41/41 layers offloaded**, with a **20,583.34 MiB SYCL0 model buffer** and **515.31 MiB CPU_Mapped model buffer**.

Both Qwen3.8 logs confirm **66/66 layers offloaded**, with a **14,674.45 MiB SYCL0 model buffer** and **682.03 MiB CPU_Mapped model buffer**.

| Model | Initial depth | Peak dedicated GiB | Peak shared GiB |
| --- | ---: | ---: | ---: |
| Gemma 4 26B-A4B | 0 | 17.214104 | 0.055817 |
| Gemma 4 26B-A4B | 2048 | 17.657158 | 0.055878 |
| Qwen3.6 35B-A3B | 0 | 21.750420 | 0.053886 |
| Qwen3.6 35B-A3B | 2048 | 22.100578 | 0.053864 |
| Qwen3.8 27B | 0 | 15.935905 | 0.071465 |
| Qwen3.8 27B | 2048 | 16.362785 | 0.065643 |

Windows GPU Process Memory counters were sampled approximately every six seconds through loading and inference. The primary adapter is selected as the process adapter with the largest dedicated-memory sample. Each counter's maximum may occur at a different time; brief peaks can be missed. This is not an independently verified LUID-to-device mapping and does not prove zero CPU work, zero host/shared use, or zero paging.

Sanitized JSON, offload excerpts, memory CSVs, source metadata and fit summaries are in [results/2026-09-08/modern](results/2026-09-08/modern). CSVs retain elapsed times and measured values but replace process/adapter identifiers with `primary-benchmark-adapter` and `other-adapter-N`. The combined [results/summary.csv](results/summary.csv) contains **28 measurements**: the previous 19 plus three measurements for each of these three models. All five samples per test are preserved in JSON.

## Reproduce sequentially

Use the runtime setup in [README.md](README.md), check that `SYCL0` identifies the intended Arc on your machine, then run:

```powershell
./scripts/Get-Model.ps1 -ModelId gemma4-26b
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-sycl/llama-bench.exe -Device SYCL0 -RunName intel-sycl-gemma4-26b -ModelId gemma4-26b -MonitorGpuMemory
./scripts/Get-Model.ps1 -ModelId qwen36-35b
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-sycl/llama-bench.exe -Device SYCL0 -RunName intel-sycl-qwen36-35b -ModelId qwen36-35b -MonitorGpuMemory
./scripts/Get-Model.ps1 -ModelId qwen38-27b
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-sycl/llama-bench.exe -Device SYCL0 -RunName intel-sycl-qwen38-27b -ModelId qwen38-27b -MonitorGpuMemory
```

The downloader verifies each pinned SHA-256. The benchmark rejects any new-model run whose log does not confirm all layers offloaded. The publishing task syntax-checked these changes without downloading or running the models; measurements came from the original sequential benchmark runs.

## Pinned sources

- [Gemma GGUF revision](https://huggingface.co/bartowski/google_gemma-4-26B-A4B-it-GGUF/tree/10f3b41bcf8d3047f4e136e7197ffc2dd1654c9d): `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`; SHA-256 `a07f72221e8e3f77455ab0d7f7652d01a9f63c262b954aa6932a53275a0e895a`.
- [Qwen3.6 GGUF revision](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/tree/a483e9e6cbd595906af30beda3187c2663a1118c): `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf`; SHA-256 `ac0e2c1189e055faa36eff361580e79c5bd6f8e76bffb4ce547f167d53e31a61`.
- [Qwen3.8 GGUF revision](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/4ca720788d1e01f1bff70c033e0d0028fd02e502): `Qwen3.8-27B-UD-Q4_K_M.gguf`; SHA-256 `322e194ff79741c7baa497c240f677f54b201b0efab44ca8e50f122b39123482`.
