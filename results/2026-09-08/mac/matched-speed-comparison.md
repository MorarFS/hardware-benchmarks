# Matched-artifact speed comparison

Every row uses b10852, five samples, default warmup, FP16 K/V, flash attention, ten threads and batch/microbatch 512. Means ± sample SD are tokens/s. Model IDs distinguish different artifacts with similar names. Compare computer/backend rows within the same ID; different IDs can have different quantizers, MTP tensors or file sizes. All individual samples and source paths remain in [the JSON table](matched-speed-comparison.json).

| Artifact ID | Computer / backend | pp512 | tg256, depth0 | tg256, depth2048 | Note |
| --- | --- | ---: | ---: | ---: | --- |
| qwen3-8b | M5 Pro / Metal | 1223.44 ± 1.05 | 45.43 ± 0.05 | 42.71 ± 0.17 | Five retained samples; see memory/offload evidence. |
| qwen3-8b | Arc Pro B70 / SYCL, initial | 1172.08 ± 47.78 | 77.70 ± 10.27 | 72.84 ± 0.27 | Measured |
| qwen3-8b | Arc Pro B70 / SYCL, repeat | 1252.82 ± 3.00 | 83.51 ± 0.27 | — | Measured |
| qwen3-8b | Arc Pro B70 / Vulkan, initial | 2548.87 ± 223.32 | 20.23 ± 0.17 | 45.69 ± 0.09 | Measured |
| qwen3-8b | Arc Pro B70 / Vulkan, repeat | 2945.25 ± 46.04 | 20.43 ± 0.13 | — | Measured |
| qwen3-8b | RTX5060 Laptop / CUDA | 2499.24 ± 198.11 | 67.09 ± 0.80 | 62.01 ± 1.42 | Measured |
| qwen3-8b | RTX5060 Laptop / Vulkan | 2219.15 ± 162.17 | 64.40 ± 1.16 | 60.08 ± 0.15 | Measured |
| qwen3-8b | Evo X3 / Vulkan | 1237.73 ± 5.22 | 43.62 ± 0.05 | 40.90 ± 0.08 | Measured |
| nemotron-49b | M5 Pro / Metal | 165.66 ± 4.05 | 8.69 ± 0.71 | 8.89 ± 0.01 | Five retained samples; see memory/offload evidence. |
| nemotron-49b | Arc Pro B70 / SYCL | 185.73 ± 0.18 | 15.99 ± 0.04 | 15.55 ± 0.01 | Measured |
| gemma4-26b | M5 Pro / Metal | 1414.08 ± 8.60 | 54.74 ± 3.08 | 47.21 ± 2.01 | Clean run following history accuracy workload; declining samples retained. Separate first attempt excluded for overlapping I/O. |
| gemma4-26b | M5 Pro / Metal (delayed repeat) | 1764.37 ± 4.89 | 72.61 ± 0.11 | 67.66 ± 0.08 | Five retained samples; see memory/offload evidence. |
| gemma4-26b | Arc Pro B70 / SYCL | 1089.90 ± 96.08 | 64.27 ± 0.17 | 56.68 ± 0.04 | Measured |
| qwen36-35b | M5 Pro / Metal | 1212.62 ± 136.28 | 47.92 ± 0.37 | 48.35 ± 1.30 | Five retained samples; see memory/offload evidence. |
| qwen36-35b | Arc Pro B70 / SYCL | 882.54 ± 145.25 | 73.33 ± 0.17 | 71.53 ± 0.89 | Measured |
| qwen38-27b | M5 Pro / Metal | 377.79 ± 0.12 | 14.64 ± 0.29 | 14.27 ± 0.01 | Five retained samples; see memory/offload evidence. |
| qwen38-27b | Arc Pro B70 / SYCL | 308.95 ± 1.89 | 20.92 ± 0.02 | 20.42 ± 0.04 | Measured |
| qwen35-122b-iq2xxs | M5 Pro / Metal | 527.59 ± 2.89 | 31.05 ± 0.07 | 30.90 ± 1.00 | Five retained samples; see memory/offload evidence. |
| falcon180b-chat-iq1s | M5 Pro / Metal | 48.32 ± 0.60 | 3.08 ± 0.07 | — | Longer generation uses depth1792 within supported 2048 context; not depth2048. Depth1792: 3.59 ± 0.03 tokens/s. |
| evo-gemma26 | M5 Pro / Metal | 1798.97 ± 6.02 | 63.63 ± 0.08 | 60.19 ± 0.11 | Five retained samples; see memory/offload evidence. |
| evo-gemma26 | Evo X3 / Vulkan | 1277.60 ± 8.55 | 52.00 ± 0.24 | 47.37 ± 0.11 | Measured |
| evo-qwen35-mtp-off | M5 Pro / Metal | 1674.95 ± 8.60 | 62.82 ± 0.04 | 61.57 ± 0.23 | Five retained samples; see memory/offload evidence. |
| evo-qwen35-mtp-off | Evo X3 / Vulkan | 1120.51 ± 9.75 | 60.81 ± 0.41 | 59.60 ± 0.08 | Measured |
| evo-gemma31 | M5 Pro / Metal | 318.52 ± 1.79 | 13.64 ± 0.08 | 12.74 ± 0.07 | Five retained samples; see memory/offload evidence. |
| evo-gemma31 | Evo X3 / Vulkan | 292.12 ± 5.65 | 11.33 ± 0.02 | 10.56 ± 0.02 | Measured |
| evo-qwen38-27b | M5 Pro / Metal | 339.29 ± 4.70 | 14.56 ± 0.02 | 14.39 ± 0.07 | Five retained samples; see memory/offload evidence. |
| evo-qwen38-27b | Evo X3 / Vulkan | 351.79 ± 1.19 | 12.77 ± 0.03 | 12.58 ± 0.02 | Measured |
| evo-qwen35-community | M5 Pro / Metal | 1573.63 ± 102.19 | 68.64 ± 0.67 | 68.70 ± 3.04 | Five retained samples; see memory/offload evidence. |
| evo-qwen35-community | Evo X3 / Vulkan | 1126.14 ± 9.43 | 71.49 ± 0.48 | 69.43 ± 0.13 | Measured |
| evo-gemma12-qat | M5 Pro / Metal | 972.91 ± 0.43 | 36.04 ± 0.07 | 34.04 ± 0.19 | Five retained samples; see memory/offload evidence. |
| evo-gemma12-qat | Evo X3 / Vulkan | 732.46 ± 8.78 | 28.57 ± 0.13 | 26.66 ± 0.07 | Measured |
| evo-ministral14 | M5 Pro / Metal | 724.52 ± 2.54 | 25.26 ± 0.14 | 24.22 ± 0.15 | Five retained samples; see memory/offload evidence. |
| evo-ministral14 | Evo X3 / Vulkan | — | — | — | Loading timeout before measured inference |
| evo-gemma12-coding | M5 Pro / Metal | 907.06 ± 0.75 | 31.39 ± 0.55 | 29.74 ± 0.30 | Five retained samples; see memory/offload evidence. |
| evo-gemma12-coding | Evo X3 / Vulkan | 802.30 ± 4.91 | 27.21 ± 0.03 | 25.37 ± 0.06 | Measured |
| evo-gemma2-9b | M5 Pro / Metal | 1177.71 ± 0.27 | 40.67 ± 1.33 | 34.64 ± 2.91 | Five retained samples; see memory/offload evidence. |
| evo-gemma2-9b | Evo X3 / Vulkan | 1000.48 ± 3.09 | 34.52 ± 0.04 | 29.57 ± 0.01 | Measured |

Missing Mac rows remain pending or explicitly excluded; a reference row is not a Mac result. The first Gemma Mac attempt is retained under diagnostic/ and excluded from this table because repository checkout and a resumed transfer overlapped it. Gemma’s clean post-accuracy samples decline; temperatures/frequencies were not measured and no thermal cause is established. A separately labeled delayed repeat, when available, is not pooled with it.

The Evo exact GPT-OSS120, Qwen3.8 Flash Next and DeepSeek V4 Flash artifacts exceed physical Mac memory in weights alone. See [the crosswalk](evo-artifact-crosswalk.json). These preflight exclusions do not establish a largest possible model. All-layer offload permits CPU work and host allocations; use per-run memory evidence. These are complete-system/backend comparisons, with uncontrolled cache, thermal and ordinary desktop background conditions.
