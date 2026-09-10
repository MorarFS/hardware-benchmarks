# Same-artifact system comparisons

Means ± sample SD in tokens/s, five retained samples per measurement. Each group uses the identical pinned model hash and b10852 pp512/tg256 settings. Historical rows are reproduced without pooling or replacement. M4 downloads continue; prior M5 synthetic transfers were paused, and OS, desktop load, power/thermal history and complete backend implementations differ. These are observed configurations, not an isolated chip ranking.

| Artifact | Computer/backend | pp512 | tg256 depth0 | tg256 depth2048 |
|---|---|---:|---:|---:|
| gemma4-26b | M4 Max / Metal | 1395.34 ± 6.41 | 94.34 ± 0.19 | 87.66 ± 1.57 |
| gemma4-26b | M5 Pro / Metal | 1414.08 ± 8.60 | 54.74 ± 3.08 | 47.21 ± 2.01 |
| gemma4-26b | M5 Pro / Metal (delayed repeat) | 1764.37 ± 4.89 | 72.61 ± 0.11 | 67.66 ± 0.08 |
| gemma4-26b | Arc Pro B70 / SYCL | 1089.90 ± 96.08 | 64.27 ± 0.17 | 56.68 ± 0.04 |
| nemotron-49b | M4 Max / Metal | 127.35 ± 6.51 | 14.93 ± 0.46 | 11.41 ± 1.09 |
| nemotron-49b | M5 Pro / Metal | 165.66 ± 4.05 | 8.69 ± 0.71 | 8.89 ± 0.01 |
| nemotron-49b | Arc Pro B70 / SYCL | 185.73 ± 0.18 | 15.99 ± 0.04 | 15.55 ± 0.01 |
| qwen235-thinking-iq1s | M4 Max / Metal | 208.18 ± 2.02 | 27.06 ± 0.05 | 24.12 ± 0.48 |
| qwen3-8b | M4 Max / Metal | 818.98 ± 2.29 | 74.91 ± 0.58 | 68.16 ± 0.84 |
| qwen3-8b | M5 Pro / Metal | 1223.44 ± 1.05 | 45.43 ± 0.05 | 42.71 ± 0.17 |
| qwen3-8b | Arc Pro B70 / SYCL, initial | 1172.08 ± 47.78 | 77.70 ± 10.27 | 72.84 ± 0.27 |
| qwen3-8b | Arc Pro B70 / SYCL, repeat | 1252.82 ± 3.00 | 83.51 ± 0.27 | — |
| qwen3-8b | Arc Pro B70 / Vulkan, initial | 2548.87 ± 223.32 | 20.23 ± 0.17 | 45.69 ± 0.09 |
| qwen3-8b | Arc Pro B70 / Vulkan, repeat | 2945.25 ± 46.04 | 20.43 ± 0.13 | — |
| qwen3-8b | RTX5060 Laptop / CUDA | 2499.24 ± 198.11 | 67.09 ± 0.80 | 62.01 ± 1.42 |
| qwen3-8b | RTX5060 Laptop / Vulkan | 2219.15 ± 162.17 | 64.40 ± 1.16 | 60.08 ± 0.15 |
| qwen3-8b | Evo X3 / Vulkan | 1237.73 ± 5.22 | 43.62 ± 0.05 | 40.90 ± 0.08 |
| qwen35-122b-iq2xxs | M4 Max / Metal | 391.70 ± 5.37 | 42.25 ± 0.08 | 41.68 ± 0.14 |
| qwen35-122b-iq2xxs | M5 Pro / Metal | 527.59 ± 2.89 | 31.05 ± 0.07 | 30.90 ± 1.00 |
| qwen36-35b | M4 Max / Metal | 1420.81 ± 12.83 | 79.18 ± 0.19 | 77.65 ± 0.86 |
| qwen36-35b | M5 Pro / Metal | 1212.62 ± 136.28 | 47.92 ± 0.37 | 48.35 ± 1.30 |
| qwen36-35b | Arc Pro B70 / SYCL | 882.54 ± 145.25 | 73.33 ± 0.17 | 71.53 ± 0.89 |
| qwen38-27b | M4 Max / Metal | 239.97 ± 3.31 | 21.19 ± 0.24 | 21.10 ± 0.39 |
| qwen38-27b | M5 Pro / Metal | 377.79 ± 0.12 | 14.64 ± 0.29 | 14.27 ± 0.01 |
| qwen38-27b | Arc Pro B70 / SYCL | 308.95 ± 1.89 | 20.92 ± 0.02 | 20.42 ± 0.04 |

The separate Gemma M5 delayed repeat remains visible because run-to-run variation was substantial; neither session replaces the other. Empty cells mean unavailable, not zero. Exact hashes, samples where available and historical evidence paths are in the accompanying JSON.

Source-workload timings and fidelity judgments use different inputs and timing boundaries; see the M4 main report. Synthetic generation alone does not establish the 40-visible-token research target.
