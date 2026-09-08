# Three-model SYCL follow-up

**In progress: Gemma completed; Qwen3.6 and Qwen3.8 are pending.** This follow-up targets approximately 40 generated tokens/second on the external Intel Arc Pro B70 32 GB. It measures throughput and memory use, not answer quality.

## Protocol and model differences

The same Windows laptop, AC power, Intel driver 32.0.101.8805 and llama.cpp b10852 SYCL runtime are used. Downloads and benchmarks run sequentially. Each test uses one selected Arc, all layers requested on the GPU, flash attention, FP16 KV, batch/microbatch 512, ten threads, five measured repetitions after warmup, and 256 generated tokens at initial depths 0 and 2,048. Prompt processing uses 512 tokens separately at depth 0. Timed throughput excludes loading, tokenization and sampling.

Gemma uses bartowski **Q4_K_M**; the Qwen artifacts use Unsloth **UD-Q4_K_M** dynamic quantization. These are different four-bit quantization recipes on different models and architectures. Equal nominal bit depth does not make them identical quality or performance treatments.

| Model | Artifact recipe | Download bytes | Status |
| --- | --- | ---: | --- |
| Gemma 4 26B-A4B Instruct | bartowski Q4_K_M | 17,035,039,872 | Completed |
| Qwen3.6 35B-A3B | Unsloth UD-Q4_K_M | 22,134,528,992 | Pending |
| Qwen3.8 27B | Unsloth UD-Q4_K_M | 16,464,440,224 | Pending |

The Gemma artifact's branded model name remains **26B-A4B**. Its GGUF reports **25,233,142,046 parameters**; the raw count is preserved without renaming the model.

## Completed measurements

| Model | Test | Initial depth | Mean tokens/s | SD tokens/s |
| --- | --- | ---: | ---: | ---: |
| Gemma 4 26B-A4B Instruct | Prompt processing 512 | 0 | 1089.895706 | 96.083135 |
| Gemma 4 26B-A4B Instruct | Generation 256 | 0 | 64.274290 | 0.174561 |
| Gemma 4 26B-A4B Instruct | Generation 256 | 2048 | 56.677035 | 0.041391 |

Gemma exceeded the approximately 40-token/s generation target at both tested depths. No ranking against the two pending models or quality conclusion is established.

## Offload and memory evidence

Both Gemma logs confirm **31/31 layers offloaded**, with a **16,230.86 MiB SYCL0 model buffer** and **577.50 MiB CPU_Mapped model buffer**. Host/shared memory use is retained explicitly.

| Initial depth | Peak dedicated GiB | Peak shared GiB |
| --- | ---: | ---: |
| 0 | 17.214104 | 0.055817 |
| 2048 | 17.657158 | 0.055878 |

Windows GPU Process Memory counters were sampled approximately every six seconds through loading and inference. The primary adapter is selected as the process adapter with the largest dedicated-memory sample. Each counter's maximum may occur at a different time; brief peaks can be missed. This is not an independently verified LUID-to-device mapping and does not prove zero CPU work, zero host/shared use, or zero paging.

Sanitized JSON, offload excerpts, memory CSVs, source metadata and fit summaries are in [results/2026-09-08/modern](results/2026-09-08/modern). CSVs retain elapsed times and measured values but replace process/adapter identifiers with `primary-benchmark-adapter` and `other-adapter-N`. The combined [results/summary.csv](results/summary.csv) contains the previous 19 measurements plus these three Gemma measurements; pending models have no numeric rows.

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

The downloader verifies each pinned SHA-256. The benchmark rejects any new-model run whose log does not confirm all layers offloaded. Prepared commands for pending models are not evidence of successful fit. The publishing task syntax-checked these changes without downloading or running the models.

## Pinned sources

- [Gemma GGUF revision](https://huggingface.co/bartowski/google_gemma-4-26B-A4B-it-GGUF/tree/10f3b41bcf8d3047f4e136e7197ffc2dd1654c9d): `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`; SHA-256 `a07f72221e8e3f77455ab0d7f7652d01a9f63c262b954aa6932a53275a0e895a`.
- [Qwen3.6 GGUF revision](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/tree/a483e9e6cbd595906af30beda3187c2663a1118c): `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf`; SHA-256 `ac0e2c1189e055faa36eff361580e79c5bd6f8e76bffb4ce547f167d53e31a61`.
- [Qwen3.8 GGUF revision](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/4ca720788d1e01f1bff70c033e0d0028fd02e502): `Qwen3.8-27B-UD-Q4_K_M.gguf`; SHA-256 `322e194ff79741c7baa497c240f677f54b201b0efab44ca8e50f122b39123482`.
