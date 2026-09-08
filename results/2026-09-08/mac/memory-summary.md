# Mac sampled memory evidence

RSS is process resident memory, not a dedicated GPU-memory counter. System swap/compression includes other apps and must not be attributed entirely to inference. Sampling every approximately two seconds can miss short peaks. Do not add RSS to Metal allocations as separate pools. Passing the 1 GiB swap-growth guard is not a zero-swap result.

## Accepted speed runs

| Run | Peak process RSS GiB | System swap before MiB | Peak swap MiB | Swap growth MiB | Compressor before / peak GiB | Full offload / all samples AC |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| apple-metal-evo-gemma12-coding-depth0 | 7.20 | 0.00 | 0.00 | 0.00 | 0.90 / 0.90 | True / True |
| apple-metal-evo-gemma12-coding-depth2048 | 7.89 | 0.00 | 0.00 | 0.00 | 0.90 / 0.90 | True / True |
| apple-metal-evo-gemma12-qat-depth0 | 6.83 | 0.00 | 0.00 | 0.00 | 0.93 / 0.93 | True / True |
| apple-metal-evo-gemma12-qat-depth2048 | 7.52 | 0.00 | 0.00 | 0.00 | 0.93 / 0.93 | True / True |
| apple-metal-evo-gemma2-9b-depth0 | 5.65 | 1390.31 | 1390.31 | 0.00 | 1.33 / 1.33 | True / True |
| apple-metal-evo-gemma2-9b-depth2048 | 6.89 | 1390.31 | 1390.31 | 0.00 | 1.33 / 1.33 | True / True |
| apple-metal-evo-gemma26-depth0 | 16.05 | 2078.31 | 2078.31 | 0.00 | 0.34 / 0.34 | True / True |
| apple-metal-evo-gemma26-depth2048 | 16.52 | 2078.31 | 2078.31 | 0.00 | 0.34 / 0.34 | True / True |
| apple-metal-evo-gemma31-depth0 | 18.01 | 2606.75 | 2606.75 | 0.00 | 0.58 / 0.58 | True / True |
| apple-metal-evo-gemma31-depth2048 | 19.87 | 2558.75 | 2558.75 | 0.00 | 0.41 / 0.41 | True / True |
| apple-metal-evo-ministral14-depth0 | 7.88 | 1390.31 | 1390.31 | 0.00 | 1.00 / 1.00 | True / True |
| apple-metal-evo-ministral14-depth2048 | 8.47 | 1390.31 | 1390.31 | 0.00 | 0.98 / 0.98 | True / True |
| apple-metal-evo-qwen35-community-depth0 | 19.94 | 2110.31 | 2110.31 | 0.00 | 0.33 / 0.33 | True / True |
| apple-metal-evo-qwen35-community-depth2048 | 20.08 | 2102.31 | 2102.31 | 0.00 | 0.33 / 0.33 | True / True |
| apple-metal-evo-qwen35-mtp-off-depth0 | 20.84 | 2078.31 | 2078.31 | 0.00 | 0.34 / 0.34 | True / True |
| apple-metal-evo-qwen35-mtp-off-depth2048 | 20.98 | 2078.31 | 2078.31 | 0.00 | 0.34 / 0.34 | True / True |
| apple-metal-evo-qwen38-27b-depth0 | 15.76 | 2262.31 | 2262.31 | 0.00 | 0.28 / 0.31 | True / True |
| apple-metal-evo-qwen38-27b-depth2048 | 16.14 | 2190.31 | 2190.31 | 0.00 | 0.31 / 0.32 | True / True |
| apple-metal-falcon180b-chat-iq1s-depth0 | 35.93 | 1390.31 | 1390.31 | 0.00 | 0.97 / 0.97 | True / True |
| apple-metal-falcon180b-chat-iq1s-depth1792 | 36.43 | 1382.31 | 1382.31 | 0.00 | 0.91 / 0.91 | True / True |
| apple-metal-gemma4-26b-depth0 | 16.14 | 0.00 | 0.00 | 0.00 | 1.06 / 1.06 | True / True |
| apple-metal-gemma4-26b-depth2048 | 16.61 | 0.00 | 0.00 | 0.00 | 1.06 / 1.06 | True / True |
| apple-metal-gemma4-26b-delayed-repeat-depth0 | 16.14 | 2078.31 | 2078.31 | 0.00 | 0.34 / 0.34 | True / True |
| apple-metal-gemma4-26b-delayed-repeat-depth2048 | 16.61 | 2078.31 | 2078.31 | 0.00 | 0.34 / 0.34 | True / True |
| apple-metal-nemotron-49b-depth0 | 28.39 | 1.50 | 1.50 | 0.00 | 2.63 / 2.63 | True / True |
| apple-metal-nemotron-49b-depth2048 | 29.11 | 1.50 | 1.50 | 0.00 | 2.41 / 2.41 | True / True |
| apple-metal-qwen3-8b-depth0 | 4.88 | 0.00 | 0.00 | 0.00 | 0.00 / 0.00 | True / True |
| apple-metal-qwen3-8b-depth2048 | 5.41 | 0.00 | 0.00 | 0.00 | 0.00 / 0.00 | True / True |
| apple-metal-qwen35-122b-iq2xxs-depth0 | 34.44 | 1343.31 | 1343.31 | 0.00 | 0.88 / 0.88 | True / True |
| apple-metal-qwen35-122b-iq2xxs-depth2048 | 34.68 | 1335.31 | 1335.31 | 0.00 | 0.88 / 0.89 | True / True |
| apple-metal-qwen36-35b-depth0 | 17.56 | 0.50 | 0.50 | 0.00 | 1.70 / 1.70 | True / True |
| apple-metal-qwen36-35b-depth2048 | 20.98 | 0.50 | 0.50 | 0.00 | 1.70 / 1.70 | True / True |
| apple-metal-qwen38-27b-depth0 | 15.36 | 0.00 | 0.00 | 0.00 | 0.90 / 0.90 | True / True |
| apple-metal-qwen38-27b-depth2048 | 15.74 | 0.00 | 0.00 | 0.00 | 0.90 / 0.90 | True / True |

Raw speed memory CSVs and filtered runtime allocations accompany each run. The [machine-readable fit summary](fit-summary.json) also retains wall time including loading, which differs from timed token throughput.

## Completed history generation

| Artifact | Context tokens | Server ready seconds | RAM prompt-cache limit MiB | Peak server RSS GiB | System swap before MiB | Peak swap MiB | Growth MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [qwen3-8b](accuracy/qwen3-8b/memory-summary.json) | 32768 | 2.06 | 8192 | 14.84 | 0.00 | 0.00 | 0.00 |
| [nemotron-49b](accuracy/nemotron-49b/memory-summary.json) | 16384 | 2.05 | 8192 | 37.54 | 1470.31 | 1470.31 | 0.00 |
| [gemma4-26b](accuracy/gemma4-26b/memory-summary.json) | 32768 | 2.06 | 8192 | 23.80 | 0.00 | 0.00 | 0.00 |
| [qwen36-35b](accuracy/qwen36-35b/memory-summary.json) | 32768 | 2.07 | 8192 | 25.82 | 0.50 | 1.50 | 1.00 |
| [qwen38-27b](accuracy/qwen38-27b/memory-summary.json) | 32768 | 2.06 | 8192 | 23.60 | 0.00 | 0.00 | 0.00 |
| [qwen35-122b-iq2xxs](accuracy/qwen35-122b-iq2xxs/memory-summary.json) | 32768 | 2.05 | 1024 | 36.62 | 2542.75 | 2542.75 | 0.00 |
| [evo-gemma26](accuracy/evo-gemma26/memory-summary.json) | 32768 | 2.06 | 8192 | 24.87 | 2078.31 | 2078.31 | 0.00 |
| [evo-qwen35-mtp-off](accuracy/evo-qwen35-mtp-off/memory-summary.json) | 32768 | 2.06 | 8192 | 25.83 | 2078.31 | 2078.31 | 0.00 |
| [evo-gemma31](accuracy/evo-gemma31/memory-summary.json) | 32768 | 2.07 | 8192 | 28.57 | 2454.75 | 2454.75 | 0.00 |
| [evo-qwen38-27b](accuracy/evo-qwen38-27b/memory-summary.json) | 32768 | 2.06 | 8192 | 26.15 | 2190.31 | 2190.31 | 0.00 |
| [evo-qwen35-community](accuracy/evo-qwen35-community/memory-summary.json) | 32768 | 2.06 | 8192 | 24.93 | 2102.31 | 2102.31 | 0.00 |
| [evo-gemma12-qat](accuracy/evo-gemma12-qat/memory-summary.json) | 32768 | 2.06 | 8192 | 15.67 | 0.00 | 0.00 | 0.00 |
| [evo-ministral14](accuracy/evo-ministral14/memory-summary.json) | 32768 | 2.04 | 8192 | 19.39 | 1358.88 | 1358.88 | 0.00 |
| [evo-gemma12-coding](accuracy/evo-gemma12-coding/memory-summary.json) | 32768 | 2.05 | 8192 | 16.04 | 0.00 | 0.00 | 0.00 |
| [evo-gemma2-9b](accuracy/evo-gemma2-9b/memory-summary.json) | 8192 | 2.06 | 8192 | 16.15 | 1358.69 | 1358.69 | 0.00 |

Server-ready time ends at a health check polled about every two seconds; with mmap/lazy loading and filesystem caching, it is not proof that every weight page has been read or a controlled cold-load measurement. Accuracy uses the declared larger application context and may overlap model downloads. Its memory load differs from the short synthetic benchmark. Complete generation is not an accuracy pass; see [the source review](accuracy/README.md).

## Failed history configurations

These failures receive no full-battery accuracy score. Context changes are separate configurations with new receipts.

| Evidence | Context | Failed stage / reason | Swap before / peak during / after cleanup MiB |
| --- | ---: | --- | --- |
| [nemotron-49b](diagnostic/nemotron-context32768-memory/failure.json) | 32768 | H3-extraction: System swap growth exceeded 1 GiB | 1.50 / 1208.12 / 1550.31 |
| [qwen35-122b-iq2xxs](diagnostic/qwen122-context16384-memory/failure.json) | 16384 | H4-summary: System swap growth exceeded 1 GiB | 2110.06 / 3715.50 / 3313.44 |
| [qwen35-122b-iq2xxs](diagnostic/qwen122-context32768-memory/failure.json) | 32768 | H4-extraction: System swap growth exceeded 1 GiB | 1335.31 / 2984.75 / 2129.00 |
