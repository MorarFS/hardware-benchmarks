# Local GPU inference benchmarks

**History source-fidelity on Arc:** [SYCL results and source adjudication](results/2026-09-08/arc-history-v2/README.md), using the frozen Evo history-v2 suite. Runtime, weight and grading differences are documented.

Windows laptop measurements from September 8, 2026, comparing an external Intel Arc Pro B70 with an internal NVIDIA RTX 5060 Laptop GPU using the same Qwen3 model, followed by a Nemotron 49B capacity test and three newer-model tests on the Intel GPU. These measure this complete machine and software configuration, including the external GPU connection.

**8B comparison completed:** Intel Vulkan and SYCL were repeated at depth 0; initial and repeat results are retained separately. SYCL produced the highest measured generation throughput among the working backends in these tests. OpenVINO failed during GPU compilation before timed inference; CPU fallback is excluded. These results do not establish Intel's best backend or either GPU's maximum throughput.

## Newer-model follow-up

The completed [three-model comparison](MODERN-MODELS.md) tested the approximately 40 generated-token/s goal. **Qwen3.6 35B-A3B was the fastest measured candidate**, Gemma 4 26B-A4B also exceeded the target, and Qwen3.8 27B fell below it.

| Candidate | Depth 0 generation (tokens/s) | Depth 2,048 generation (tokens/s) | Target result |
| --- | ---: | ---: | --- |
| Qwen3.6 35B-A3B UD-Q4_K_M | 73.334245 | 71.525257 | Exceeded; fastest measured |
| Gemma 4 26B-A4B Instruct Q4_K_M | 64.274290 | 56.677035 | Exceeded |
| Qwen3.8 27B UD-Q4_K_M | 20.922442 | 20.418157 | Below |

All three completed with all layers offloaded. These text-only tests use different bartowski Q4_K_M and Unsloth UD-Q4_K_M recipes; they do not establish an answer-quality winner or multimodal/application performance. The linked report includes standard deviations, all nine modern measurements and memory evidence.

## Hardware and setup

| Component | Configuration |
| --- | --- |
| CPU | AMD Ryzen AI 9 365 |
| System memory | Approximately 16 GB |
| External GPU | Intel Arc Pro B70, 32 GB VRAM, through a detected Intel TBT5 USB4 dock |
| Internal GPU | NVIDIA GeForce RTX 5060 Laptop GPU, 8 GB VRAM |
| Drivers | Intel 32.0.101.8805; NVIDIA reported 610.88 |
| Power | AC connected |

The Intel workstation driver was installed from Intel's official package after signature and hash verification. Windows reported a device error before the restart; restarting cleared it and device/display health checks passed. No driver binaries or full diagnostic logs are included; selected sanitized capacity offload excerpts are provided. The detected dock does not prove the negotiated link speed or effective PCIe bandwidth.

## Model and method

- Official **Qwen/Qwen3-8B-GGUF**, **Qwen3-8B-Q4_K_M.gguf**, approximately 5.03 GB on disk (5,027,783,488 bytes; llama-bench reports 5,021,827,072 bytes of model tensors).
- Model revision: `7c41481f57cb95916b40956ab2f0b139b296d974`.
- Verified SHA-256: `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`.
- Official llama.cpp **b10852**, commit `050dde50c`; Windows Vulkan, SYCL and CUDA 13.3 packages for the completed comparison.
- Sequential single-device runs, full GPU offload (`-ngl 99`), no tensor split (`-sm none`), flash attention on, FP16 K/V cache, batch/microbatch 512, ten CPU threads.
- Five measured repetitions after llama-bench's default warmup. Generate 256 tokens at initial context depths 0 and 2,048. Separately process 512 prompt tokens at depth 0.
- Values are mean tokens/second and sample standard deviation reported by llama-bench. Prefilled depth is not an application context-window setting. llama-bench excludes tokenization and sampling; this is not end-to-end chat latency.

## Measured results

| Run | Test | Initial depth | Mean tokens/s | SD tokens/s |
| --- | --- | ---: | ---: | ---: |
| intel-sycl-depth0 | Prompt processing 512 | 0 | 1172.082569 | 47.775965 |
| intel-sycl-depth0 | Generation 256 | 0 | 77.695988 | 10.265358 |
| intel-sycl-depth2048 | Generation 256 | 2048 | 72.838920 | 0.272410 |
| intel-sycl-repeat-depth0 | Prompt processing 512 | 0 | 1252.820604 | 3.004581 |
| intel-sycl-repeat-depth0 | Generation 256 | 0 | 83.505046 | 0.270528 |
| intel-vulkan-depth0 | Prompt processing 512 | 0 | 2548.869875 | 223.324914 |
| intel-vulkan-depth0 | Generation 256 | 0 | 20.229451 | 0.169184 |
| intel-vulkan-depth2048 | Generation 256 | 2048 | 45.686410 | 0.089258 |
| intel-vulkan-repeat-depth0 | Prompt processing 512 | 0 | 2945.253634 | 46.040867 |
| intel-vulkan-repeat-depth0 | Generation 256 | 0 | 20.430074 | 0.127100 |
| nvidia-cuda-depth0 | Prompt processing 512 | 0 | 2499.242882 | 198.107840 |
| nvidia-cuda-depth0 | Generation 256 | 0 | 67.091562 | 0.795381 |
| nvidia-cuda-depth2048 | Generation 256 | 2048 | 62.005866 | 1.415181 |
| nvidia-vulkan-depth0 | Prompt processing 512 | 0 | 2219.146074 | 162.169020 |
| nvidia-vulkan-depth0 | Generation 256 | 0 | 64.397618 | 1.155568 |
| nvidia-vulkan-depth2048 | Generation 256 | 2048 | 60.081314 | 0.145006 |

Intel Vulkan depth-0 generation repeated at 20.430074 tokens/s (SD 0.127100), close to its initial 20.229451. Its difference from depth 2,048 remains unexplained; this does not establish a general context-length effect. SYCL depth-0 generation repeated at 83.505046 tokens/s (SD 0.270528). Both repeat logs confirmed 37/37 layers offloaded. Vulkan provides a common-backend comparison; CUDA and SYCL add vendor-specific backends. SYCL depth-0 generation samples were 59.3363, 81.9580, 82.3074, 82.4912 and 82.3871 tokens/s; all five are retained in the reported mean, with no outlier removal.

Machine-readable JSON in `results/2026-09-08/` retains original measured values and samples. Only the model path is replaced with its basename. Original `gpu_info` lists enumerated adapters, not necessarily the selected GPU: use `devices` and the clean summary's `selected_gpu`. Intel Vulkan selected `Vulkan1`; NVIDIA Vulkan selected `Vulkan2`; NVIDIA CUDA selected `CUDA0`; Intel SYCL selected `SYCL0`.

## Reproduce

Use PowerShell on Windows with compatible, healthy GPU drivers and AC power. Device IDs can differ between machines and backend packages.

1. Run `./scripts/Get-Model.ps1` to download the pinned official model and verify its SHA-256.
2. Download the Windows Vulkan, SYCL and CUDA 13 packages from the [b10852 release](https://github.com/ggml-org/llama.cpp/releases/tag/b10852). Extract into separate `work/llama-vulkan`, `work/llama-cuda` and `work/llama-sycl` directories. Add the release's CUDA 13.3 DLL package to the CUDA directory if needed. Preserve the accompanying DLLs.
3. Run each executable with `--list-devices`. Select the intended physical GPU explicitly. The script accepts configurable executable, model, device and output paths.
4. Run these commands sequentially, replacing device IDs with your enumeration:

```powershell
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-vulkan/llama-bench.exe -Device Vulkan1 -RunName intel-vulkan
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-vulkan/llama-bench.exe -Device Vulkan2 -RunName nvidia-vulkan
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-cuda/llama-bench.exe -Device CUDA0 -RunName nvidia-cuda
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-sycl/llama-bench.exe -Device SYCL0 -RunName intel-sycl
```

Inspect local logs for actual GPU offload and fallback before sharing results. Raw local logs stay ignored. The reusable scripts were syntax-checked; this publishing task did not rerun GPU workloads. Measured data came from the original benchmark invocation with the same settings (FP16 KV used the runtime default).

## Limits

One laptop, five four-bit model artifacts, one session and short generation tests cannot isolate hardware performance. Power limits, temperatures, background load, link bandwidth and run order were not controlled as a laboratory experiment. Five within-run samples are not five independent sessions. No energy, quality, tokenization, sampling, application latency or concurrency benchmark was performed.

OpenVINO 2026.3.1 failed before timed inference. Its C API identified `GPU.0` as the Intel Arc Pro B70 and `GPU.1` as NVIDIA on this machine. The generic `GPU` name failed the llama backend device-availability match and silently fell back to CPU; those runs are excluded. Explicit `GPU.0` tests in both stateful and stateless modes failed during GPU program compilation with `clWaitForEvents CL_INVALID_EVENT (-58)`, after an initial sandbox cache-access issue was resolved. No OpenVINO throughput was measured. See `results/2026-09-08/openvino-failure.json` for the sanitized failure record.

## Completed 49B capacity test

The tested model is **Llama 3.3 Nemotron Super 49B v1.5, Q4_K_M**, quantized by **bartowski**, with a GGUF file of **30,215,579,136 bytes (30.22 GB; about 28.14 GiB)**. It supersedes the planned Qwen3-32B baseline. Keeping Q4_K_M preserves the earlier quantization choice while exploring a model closer to the Arc's 32 GB memory limit. This is not proof of the largest fitting model across all architectures or quantization levels, nor a direct speed comparison with the 8B model.

**The model download passed SHA-256 verification, and both SYCL capacity runs completed with 81/81 layers offloaded.** The measured configuration used llama.cpp b10852, single-device SYCL0, FP16 KV, flash attention, batch/microbatch 512, ten threads and five repetitions after warmup, matching the earlier protocol. Generation produced 256 tokens at initial depths 0 and 2,048; prompt processing used 512 tokens separately at depth 0.

Pinned source: [bartowski GGUF revision](https://huggingface.co/bartowski/nvidia_Llama-3_3-Nemotron-Super-49B-v1_5-GGUF/tree/98fc9722ebffe74e41685c477cf2982012d3f0ad), revision `98fc9722ebffe74e41685c477cf2982012d3f0ad`, filename `nvidia_Llama-3_3-Nemotron-Super-49B-v1_5-Q4_K_M.gguf`. Verified SHA-256: `eb619df799350250d51148874e6033f0b395b6b867291644e03225a71bda8c01`. This third-party quantization is distinct from the official Qwen 8B model used above.

### 49B throughput and fit evidence

| Test | Initial depth | Mean tokens/s | SD tokens/s |
| --- | ---: | ---: | ---: |
| Prompt processing 512 | 0 | 185.733742 | 0.182183 |
| Generation 256 | 0 | 15.988204 | 0.038298 |
| Generation 256 | 2048 | 15.547394 | 0.014298 |

This demonstrates a near-capacity Q4_K_M model running with all 81 layers offloaded on this Arc configuration at the tested depths. It does not establish the largest possible model, support for larger contexts, or comparable speed or quality to the different 8B model.

Both logs report a **28,244.70 MiB SYCL0 model buffer** and a **563.62 MiB CPU_Mapped model buffer**. KV buffers were on SYCL0: 98 MiB for the short prompt-processing context, 49 MiB for short generation, and 441 MiB for depth-2,048 generation. GPU compute buffers were 133.25–266.50 MiB, with SYCL host compute buffers of about 16.13–34.26 MiB. All-layer offload therefore does not mean zero host-memory use.

| Initial depth | Peak dedicated GPU memory (GiB) | Peak shared GPU memory (GiB) |
| --- | ---: | ---: |
| 0 | 30.925652 | 0.090973 |
| 2048 | 30.191582 | 0.083160 |

These are Windows **GPU Process Memory** samples taken approximately every six seconds, including model loading and inference. The selected counter instance is the process adapter with the largest dedicated-memory sample. Each column is its own sampled maximum and need not occur at the same instant; the short run also includes prompt processing. These counters are not an exact sum of llama.cpp's buffer reports, can miss brief peaks, and do not prove that paging never occurred. The small measured shared-memory use is retained explicitly. There is no zero-CPU or zero-paging claim.

Sanitized benchmark JSON, offload excerpts, memory time series and `capacity-fit-summary.json` are in `results/2026-09-08/capacity/`. CSV adapter names are `primary-benchmark-adapter` for the peak-dedicated instance and `other-adapter-N` for the remaining instances; process IDs and adapter LUIDs are removed. The primary label follows the counter-selection rule, not an independently verified LUID-to-device mapping. Original values and elapsed times are retained. `results/summary.csv` contains **28 measurements**: the original 19 plus nine completed newer-model follow-up rows; the original 16-row 8B summary is preserved.

The raw runtime `model_type` remains `deci 70B Q4_K - Medium`; this is a heuristic label, not the artifact's actual size. The verified model identity is Nemotron Super 49B v1.5, and JSON reports **49,867,145,280 parameters**. The GGUF file has 30,215,579,136 bytes; llama-bench reports 30,207,721,728 bytes of model tensors.

### Reproduce the capacity test
The following commands request the same depth-0/2,048, FP16 KV, five-repetition protocol on a single SYCL GPU. Confirm the Arc's current device ID first. Use `-MonitorGpuMemory` to reproduce the per-process Windows counter sampling alongside loading and inference:

```powershell
./scripts/Get-Model.ps1 -ModelId nemotron-49b
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-sycl/llama-bench.exe -Device SYCL0 -RunName intel-sycl-nemotron49b -ModelId nemotron-49b -MonitorGpuMemory
```

The download and benchmark scripts use the pinned manifest in `scripts/models.json`. `Watch-GpuMemory.ps1` uses the same five-second process wait plus counter-query loop as the original runner, giving roughly six-second sampling. It requires the English Windows counter names and writes adapter aliases instead of machine/process identifiers; missing counters produce a warning. The benchmark requests all layers on the GPU and rejects a 49B run if its log does not confirm all layers offloaded. Also inspect device allocation and cache placement in the local log before claiming fully GPU-resident inference. Failure to fit is a valid capacity-test outcome; do not silently reduce offload and present it as the same test. These script additions were syntax-checked without downloading the 49B model or running GPU work in the publishing task. The capacity results are stored separately from the 8B measurements.

## Sources

- [Pinned official Qwen GGUF files](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/7c41481f57cb95916b40956ab2f0b139b296d974)
- [Official llama.cpp b10852 release and runtime downloads](https://github.com/ggml-org/llama.cpp/releases/tag/b10852)
- [llama-bench source and documentation at the measured commit](https://github.com/ggml-org/llama.cpp/tree/050dde50c/tools/llama-bench)
- [Intel Arc Pro Windows driver](https://www.intel.com/content/www/us/en/download/741626/intel-arc-pro-graphics-windows.html)


## Separated history accuracy pilot

The [frozen history-v2 package](experiments/history-v2/USAGE.md) provides fixed source passages, 20 questions, evaluator references, and a portable Python runner for LM Studio. It separates extraction, direct summaries, merged summaries, and a full-source control. It includes no completed accuracy scores. See the [method notes](experiments/history-v2/METHOD-NOTES.md) for the seed limitation, API compatibility, and Codex-assisted evaluator identity.

## Evo X3 and Mac reproduction

The [completed Evo speed package](results/2026-09-08/evo/README.md) includes the twelve-model Vulkan matrix, every measured repetition, two retained loading timeouts, exact model hashes, matched Qwen8 backend comparisons, and separate prose/ROCm repair evidence. Use the [Mac/Metal guide](MAC-BENCHMARK.md) to prepare the same Qwen8 synthetic baseline on Apple Silicon. No Mac inference was run during publication.

## Historical source evaluation

The [corrected original history audit](results/2026-09-08/history/README.md) includes full-book run evidence, source text, retries, and revised claim ledgers. Two Gemma OFF objections were withdrawn after closer review. The [research notes](RESEARCH-NOTES.md) distinguish external leads from measured findings. These Codex-assisted audits do not establish general suitability or unsuitability for supervised research.

## Completed history accuracy pilot

The [frozen pilot results](results/2026-09-08/history-v2/README.md) separate extraction, synthesis, citations, coverage, and latency. The [historical-research lessons](HISTORY-RESEARCH-LESSONS.md) summarize findings and proposed prompting improvements.

The [completed supported power-profile comparison](results/2026-09-08/power-profiles/README.md) found no meaningful overall benefit from performance mode. The test restored balanced mode and serving services. The user subsequently chose performance as the daily profile, saved through the enabled system daemon.

The [Mac handoff](MAC-HANDOFF.md) records the user’s requested next comparisons for the separate running Mac task.

## Presentation

[Six-slide Evo X3 / Windows Arc comparison](presentations/2026-09-08/evo-arc/README.md), with editable tables, visible reasoning settings, an accessible companion, and build sources.
