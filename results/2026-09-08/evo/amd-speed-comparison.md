# Evo X3 speed comparison: live measured results

Updated snapshot, 8 September 2026. New user target: **above 40 visible tokens/s**. The original benchmark threshold was at least 35. Neither threshold establishes source accuracy.

Both backends use the same GGUF file per model. Installed LM Studio llama.cpp runtimes are version 2.33.0. Full GPU offload, FP16 KV, flash attention enabled, MTP disabled. Requests run sequentially; configured parallel capacity is four. Gemma context is 65,536; Qwen context is 32,768. Gemma batch is 2,048 and Qwen batch 512; native physical batch is 512. Sampling is matched within each backend pair, not across models.

| Model / quant | Backend | Source pages | Runs | Visible decode t/s | Raw native t/s | First visible s | Request wall s | Status |
|---|---|---|---:|---:|---:|---:|---:|---|
| Gemma4 26B A4B UD-Q4_K_M | rocm | PDF 101–102 | 3 | 43.85 | 43.87 | 1.10 | 11.91 | Readable; detailed fidelity not scored here |
| Gemma4 26B A4B UD-Q4_K_M | rocm | PDF 1–50 | 3 | — | 36.11 | 13.69 | 70.41 | Invalid/capped output; raw speed only |
| Gemma4 26B A4B UD-Q4_K_M | vulkan | PDF 101–102 | 3 | 46.15 | 46.16 | 3.74 | 14.27 | Readable; detailed fidelity not scored here |
| Gemma4 26B A4B UD-Q4_K_M | vulkan | PDF 1–50 | 3 | 41.79 | 41.81 | 20.90 | 31.25 | Readable; detailed fidelity not scored here |
| Qwen3-8B official Q4_K_M | rocm | PDF 101–102 | 3 | — | 38.46 | 0.97 | 54.19 | Invalid/capped output; raw speed only |
| Qwen3-8B official Q4_K_M | rocm | PDF 1–50 | 3 | — | 28.40 | 18.80 | 90.88 | Invalid/capped output; raw speed only |
| Qwen3-8B official Q4_K_M | vulkan | PDF 101–102 | 3 | 40.35 | 40.36 | 1.84 | 10.14 | Readable; detailed fidelity not scored here |
| Qwen3-8B official Q4_K_M | vulkan | PDF 1–50 | 3 | 29.02 | 29.03 | 35.94 | 50.56 | Readable; detailed fidelity not scored here |

Cache treatment: each backend has one short warmup. Measured requests use fresh trial markers at the start of the system prompt. Models unload between backends. No filesystem cache flush or hard KV-cache reset was performed; these are neither guaranteed cold-start nor fully cached latency measurements. Native prompt-processing events are retained. Four configured slots do not mean four simultaneous requests. Actual per-instance context was verified, and every request checks input plus output against that limit. Values are means of completed repetitions. Pending rows are not zero. Readable means an ordinary prose response without a token cap; it is not a factual accuracy judgment. ROCm Gemma long outputs repeated `<unused24>` to the cap. Retokenizing that string inflates the apparent visible rate fourfold, so that rate is excluded. Qwen ROCm short outputs repeat source prose; long outputs repeat digits. Their raw rates are diagnostic only. The cause remains unresolved.

Visible decode is visible tokens divided by elapsed time after the first visible response. It excludes initial waiting. First visible time and full request wall time are reported separately. Counts are retokenized visible text, while native rates use runtime token accounting. Memory pools overlap on AMD UMA; RAM, RSS, PSS, VRAM, and GTT must not be added.

The official Qwen3-8B file was verified at 08:43:14 UTC: 5,027,783,488 bytes; SHA-256 `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`. ROCm uses those identical weights.

## Earlier long-book results, separate protocol

| Configuration | Visible decode range | Final visible decode | First visible final | Scope |
|---|---:|---:|---:|---|
| Qwen3.6 35B A3B UD-Q4_K_M, Vulkan, reasoning ON, MTP ON | 80.29–87.76 | 87.76 | 125.08 s | 396-page workflow; final accepted |
| Gemma4 26B A4B UD-Q4_K_M, Vulkan, reasoning ON | 38.16–40.80 | 38.77 | 558.38 s | 396-page workflow; final accepted |
| GPT-OSS 120B MXFP4, Vulkan, template medium reasoning | 41.20–44.24 | 44.24 | 13.05 s | 396-page workflow; final accepted retry |

These reasoning configurations have different prompts, sampling, and output lengths. High visible decode can coexist with long reasoning delays. Accepted means generation completed, not that its content passed review. Original reasoning-OFF runs used nonstreaming timing: native generation was roughly 55.5–59.6 t/s for Qwen35 source chunks and 37.6–38.7 for Gemma26. Those are not retrospectively verified visible-phase rates.

Historical audit failures apply to the tested quantization, runtime, prompts, chunk reduction, and provisional rubric. They do not establish that these models are unusable for research. The new bounded accuracy experiment will separate extraction, citations, coverage, and synthesis. Prompt improvements remain unproven until tested.

The exact b10852 llama-bench matrix matching the laptop is queued separately. Synthetic decode excludes chat tokenization and sampling, and must not be confused with these application timings.
