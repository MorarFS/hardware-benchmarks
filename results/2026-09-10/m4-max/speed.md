# M4 Max synthetic speed results

Measurements collected with model downloads continuing, as requested. Means ± sample standard deviations; five measured repetitions after default warmup. Exact b10852/model hashes and original settings match the repository protocol, but background load differs. No isolated hardware ranking is implied.

| Model | Test | Depth | Mean ± SD tokens/s | Peak process RSS GiB | Sampled swap growth MiB |
|---|---|---:|---:|---:|---:|
| gemma4-26b | tg256 | 2048 | 87.665 ± 1.571 | 16.64 | 0.00 |
| gemma4-26b | pp512 | 0 | 1395.337 ± 6.410 | 16.16 | 0.00 |
| gemma4-26b | tg256 | 0 | 94.344 ± 0.190 | 16.16 | 0.00 |
| qwen36-35b | tg256 | 2048 | 77.650 ± 0.856 | 21.00 | 0.00 |
| qwen36-35b | pp512 | 0 | 1420.810 ± 12.834 | 20.86 | 0.00 |
| qwen36-35b | tg256 | 0 | 79.176 ± 0.191 | 20.86 | 0.00 |
| qwen38-27b | tg256 | 2048 | 21.101 ± 0.389 | 15.76 | 0.00 |
| qwen38-27b | pp512 | 0 | 239.973 ± 3.310 | 15.37 | 0.00 |
| qwen38-27b | tg256 | 0 | 21.190 ± 0.238 | 15.37 | 0.00 |
| qwen3-8b | pp512 | 0 | 818.982 ± 2.288 | 4.89 | 0.00 |
| qwen3-8b | tg256 | 0 | 74.915 ± 0.583 | 4.89 | 0.00 |
| qwen3-8b | tg256 | 2048 | 68.159 ± 0.841 | 5.42 | 0.00 |

RSS is process memory, not dedicated GPU memory. Do not add RSS to unified GPU buffer allocations. Samples can miss brief peaks. Zero sampled swap does not alone prove all weight pages stayed resident. All sample values, requested flags and offload evidence are retained in the linked subdirectories.

Qwen8 generation samples decline within the session: 75.69→74.33 tokens/s at depth0 and 69.20→67.33 at depth2048. No temperature/frequency measurement identifies the cause. The initial driver reported no thermal warning.
