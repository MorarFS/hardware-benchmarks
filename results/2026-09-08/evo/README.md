# Evo X3 completed speed measurements

Ten of twelve installed models completed both Vulkan depths. Ministral14 and DeepSeek4 Flash timed out during initial loading, before measured output. The original Qwen8 reference adds one separately identified row. All terminal records and failed logs are retained.

| Evidence | Contents |
| --- | --- |
| [Installed-model table](vulkan-model-speed.md) / [CSV](vulkan-model-speed.csv) | Final means and sample standard deviations |
| [Vulkan raw matrix](raw/vulkan-model-matrix/) | Per-repetition JSON, exact command arrays, all GGUF/shard hashes, logs, telemetry, and terminal records |
| [Qwen8 backend table](qwen8-synthetic-speed.md) / [CSV](qwen8-synthetic-speed.csv) | Matched Vulkan, stock HIP, and patched AMD synthetic timings |
| [Qwen8 raw samples](raw/synthetic-qwen8/) | Every synthetic sample for all three backends |
| [Application comparison](amd-speed-comparison.md) / [CSV](amd-speed-comparison.csv) | Separate Gemma26 and Qwen8 source-based prose requests |
| [Application evidence](raw/optimization/) / [Qwen8 evidence](raw/optimization-qwen8/) | Inputs, outputs, timings, load settings, and invalid-generation cases |
| [ROCm repair](rocm-repair-status.md) / [validation evidence](raw/rocm-amd-validation/) | Bounded readability/retrieval checks, failed alternatives, and source/build provenance |
| [Mac/Metal reproduction](../../../MAC-BENCHMARK.md) | Exact Qwen8 baseline and portable runner instructions |

## Machine and software

The Evo has a Ryzen AI MAX+395 and Radeon 8060S, reported as gfx1151. Ubuntu 26.04 ran kernel 7.0.0-31. Mesa Vulkan drivers were 26.0.3-1ubuntu1, with libvulkan1 1.4.341.0-1. A later read-only [environment receipt](environment.json) records these packages and balanced power mode. The observed split exposed about 30.47 GiB to the CPU and reserved 96 GiB for the GPU. Swap capacity was 8 GiB, with roughly 3–4 GiB in use during this session. These are configuration observations, not independent quantities to sum with RSS, PSS, GTT, or VRAM usage.

The recorded power profile was balanced. CPU control used amd_pstate/powersave EPP; GPU power control was automatic. Observed GPU SCLK was about 2833 MHz, with a reported maximum of 2900 MHz. MCLK was 1000 MHz. No performance-profile tuning, driver update, kernel change, or BIOS change is part of this matrix. Thermal/power and background conditions were not laboratory controlled.

The installed-model synthetic matrix uses official llama.cpp b10852, commit `050dde50c`, Linux Vulkan, with one benchmark process at a time. Settings are full requested GPU offload, Vulkan0, no split, flash attention, F16 K/V, batch/microbatch 512, ten CPU threads, default warmup, and five repetitions. There is no draft/MTP execution. Each selected text GGUF and every shard was hashed; unrelated vision projectors were excluded from weight accounting.

The matrix began at 09:20:49 UTC and reached terminal completion at 10:20:37 UTC on September 8, 2026. Each depth had a 900-second deadline. The two timeout logs stopped among model/tokenizer metadata; they do not prove hardware incapacity or a specific root cause. No CPU fallback or substitute quantization was accepted.

## Backend comparison boundaries

Vulkan and stock HIP use the same b10852 source. Stock HIP uses the installed ROCm 7.2.70204 libraries. Its synthetic numbers remain raw compute measurements because separate source-based requests produced repetitive, capped output. Do not present stock HIP throughput as usable prose performance.

The repaired AMD row uses a different source build, b10606 / `03d2068a1`, and its bundled ROCm 10.1 alpha libraries. This is a combined software-stack comparison. Stock b10852 with those newer libraries still failed the prose checks. The patched build passed two short and two long readability/retrieval checks for both Qwen8 and Gemma26. Citation and factual qualifications remained; this is not general accuracy certification.

The application comparison uses LM Studio Vulkan/HIP 2.33.0 and longer, meaningful source inputs. Its batch sizes, contexts, reasoning settings, visible timing, and native timing are recorded separately. Repetitive special-token strings can inflate retokenized visible speed; those invalid figures are excluded from useful-prose conclusions.

## Provenance and interpretation

The Qwen8 GGUF is the official Q4_K_M file at revision `7c41481f57cb95916b40956ab2f0b139b296d974`, SHA-256 `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`, 5,027,783,488 bytes. Other exact model paths and hashes are in each matrix model's `model-files.json` and the queue manifest.

Means and standard deviations describe five within-run samples. They do not establish maximum hardware throughput. Prompt processing, synthetic generation, visible prose speed, first-visible latency, and total request wall time are different measurements. No source-fidelity score follows from synthetic speed.

Loading and warmup are outside timed pp/tg. Process wall time and timestamped logs are retained separately. Some native logs include a load-time counter, but it was not independently isolated as a cold-load measurement. Filesystem cache was not flushed. UMA memory categories overlap and must not be summed.

Only private home/root paths and private host identifiers were redacted from raw evidence. Numeric measurements, samples, model-output prose, public model identifiers, and hashes were retained. Secrets, private provider backups, user databases, model binaries, and unrelated documents were excluded. The archived runtime metadata may enumerate adapters; use the selected-device and offload evidence when interpreting placement.

The earlier history audit and new frozen accuracy pilot are separate from these speed measurements. No new accuracy outcomes are claimed in this speed publication.

- [Official b10852 release](https://github.com/ggml-org/llama.cpp/releases/tag/b10852)
- [Measured llama-bench source](https://github.com/ggml-org/llama.cpp/tree/050dde50c/tools/llama-bench)
- [AMD gfx11 release used for the repair](https://github.com/AMD-Ecosystem/llama.cpp/releases/tag/gfx11-rocm-nightly-20260906)
- [Reported gfx1151 pinned-memory issue](https://github.com/ggml-org/llama.cpp/issues/28211)
