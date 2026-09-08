# Installed-model Vulkan speed matrix

Incremental autonomous results. Same b10852 / 050dde50c Vulkan binary; no new model downloads. Five repetitions, warmup ON, full GPU layer offload, FP16 KV, batch/ubatch 512, CPU threads 10, speculation OFF. Depth 0 and 2048, tg256; pp512 at depth 0. The Qwen8 reference is reused from the completed matched protocol.

| Installed model | pp512 t/s | tg256 depth 0 t/s | tg256 depth 2048 t/s | State |
|---|---:|---:|---:|---|
| Qwen3-8B official Q4_K_M | 1237.73 ± 5.22 | 43.62 ± 0.05 | 40.90 ± 0.08 | Complete |
| Gemma4 26B A4B UD-Q4_K_M | 1277.60 ± 8.55 | 52.00 ± 0.24 | 47.37 ± 0.11 | Complete |
| Qwen3.6 35B A3B UD-Q4_K_M, MTP OFF | 1120.51 ± 9.75 | 60.81 ± 0.41 | 59.60 ± 0.08 | Complete |
| Qwen3.8 Flash Next UD-IQ4_XS, MTP OFF | 211.30 ± 0.66 | 24.07 ± 0.04 | 23.47 ± 0.04 | Complete |
| GPT-OSS120 MXFP4 | 665.44 ± 4.20 | 54.11 ± 0.14 | 52.59 ± 0.37 | Complete |
| Gemma4 31B Q4_K_M | 292.12 ± 5.65 | 11.33 ± 0.02 | 10.56 ± 0.02 | Complete |
| Qwen3.8 27B Q4_K_M | 351.79 ± 1.19 | 12.77 ± 0.03 | 12.58 ± 0.02 | Complete |
| Qwen3.6 35B A3B community Q4_K_M, speculation OFF | 1126.14 ± 9.43 | 71.49 ± 0.48 | 69.43 ± 0.13 | Complete |
| Gemma4 12B QAT Q4_0 | 732.46 ± 8.78 | 28.57 ± 0.13 | 26.66 ± 0.07 | Complete |
| Ministral3 14B Reasoning Q4_K_M | Pending | Pending | Pending | Failed: depth 0: exit -15, timeout=True; inspect preserved stderr |
| DeepSeek V4 Flash 0731 UD-IQ2_M | Pending | Pending | Pending | Failed: depth 0: exit -15, timeout=True; inspect preserved stderr |
| Gemma4 Coding 12B Q4_K_M | 802.30 ± 4.91 | 27.21 ± 0.03 | 25.37 ± 0.06 | Complete |
| Gemma2 9B IT Q4_K_M | 1000.48 ± 3.09 | 34.52 ± 0.04 | 29.57 ± 0.01 | Complete |

These are raw synthetic compute rates, not user-visible prose speed or factual accuracy. GPT-OSS reasoning is not invoked: no chat template or sampling runs. MoE draft/MTP sidecars are not executed. Full JSON retains runtime placement and samples; stderr logs preserve allocation/support errors. Model tensor bytes exclude unrelated projectors. Each selected text GGUF and every shard is hashed before measurement.

Process wall time and timestamped load/warmup logs are separate from timed decode. Startup-to-first-progress is an observable phase boundary, not a pure model-load estimate. No OS cache flush; filesystem cache is uncontrolled. RAM/VRAM/GTT/RSS/PSS overlap on UMA and must not be summed.

One benchmark process runs at a time. The optional ROCm browser service is paused after checking it is idle and restored on completion. The normal Vulkan service stays configured; idle LM Studio models are unloaded for measurement and restored afterward. Per-command timeout is 900 seconds. Each failed model is recorded and later models continue.
