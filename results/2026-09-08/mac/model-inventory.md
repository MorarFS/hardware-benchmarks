# Mac artifact and parameter inventory

Exact file identities are retained below and in the [JSON inventory](model-inventory.json). Total tensor parameters and tensor bytes come from accepted llama-bench output; file bytes include headers/tokenizer metadata and therefore differ. Pending measurements are not filled from a similarly named artifact. No image/audio projector is loaded in these text tests.

The MoE active figures are rounded model-author descriptions, not measured per-token FLOPs: [Gemma26](https://huggingface.co/google/gemma-4-26B-A4B-it) reports 3.8B, [Qwen35](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) 3B, and [Qwen122](https://huggingface.co/Qwen/Qwen3.5-122B-A10B) 10B. Dense models have no sparse-expert active subset to report here. Branded model sizes can differ from exact language-model tensor counts; the names remain unchanged. An MTP-containing file does not mean MTP was enabled: all Mac runs disable speculative decoding.

| Artifact / pinned source | Architecture | Observed tensor parameters | Author-reported active parameters | File bytes | File GiB |
| --- | --- | ---: | --- | ---: | ---: |
| [qwen3-8b](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/7c41481f57cb95916b40956ab2f0b139b296d974) | Dense | 8,190,735,360 | Dense; no sparse subset | 5,027,783,488 | 4.68 |
| [nemotron-49b](https://huggingface.co/bartowski/nvidia_Llama-3_3-Nemotron-Super-49B-v1_5-GGUF/tree/98fc9722ebffe74e41685c477cf2982012d3f0ad) | Dense | 49,867,145,280 | Dense; no sparse subset | 30,215,579,136 | 28.14 |
| [gemma4-26b](https://huggingface.co/bartowski/google_gemma-4-26B-A4B-it-GGUF/tree/10f3b41bcf8d3047f4e136e7197ffc2dd1654c9d) | MoE | 25,233,142,046 | 3.8B | 17,035,039,872 | 15.87 |
| [qwen36-35b](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/tree/a483e9e6cbd595906af30beda3187c2663a1118c) | MoE | 34,660,610,688 | 3B | 22,134,528,992 | 20.61 |
| [qwen38-27b](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/4ca720788d1e01f1bff70c033e0d0028fd02e502) | Dense | 27,320,697,856 | Dense; no sparse subset | 16,464,440,224 | 15.33 |
| [qwen35-122b-iq2xxs](https://huggingface.co/unsloth/Qwen3.5-122B-A10B-GGUF/tree/51eab4d59d53f573fb9206cb3ce613f1d0aa392b) | MoE | 122,111,526,912 | 10B | 36,637,668,544 | 34.12 |
| [falcon180b-chat-iq1s](https://huggingface.co/mradermacher/falcon-180B-chat-i1-GGUF/tree/bc1174ce59d9b51286e204b5745216b1c1189d12) | Dense | 179,522,565,120 | Dense; no sparse subset | 38,322,520,576 | 35.69 |
| [evo-gemma26](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/tree/c099eb48e663fd284577b04978a94ffccb261841) | MoE | 25,233,142,046 | 3.8B | 16,947,541,728 | 15.78 |
| [evo-qwen35-mtp-off](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-MTP-GGUF/tree/5bc3e238d916f48a861bac2f8a1990a0e9b7e98d) | MoE | 35,505,251,456 | 3B | 22,663,387,424 | 21.11 |
| [evo-gemma31](https://huggingface.co/lmstudio-community/gemma-4-31B-it-GGUF/tree/67a72ce462184ca84e9531dfe657ee73b4ecc89d) | Dense | 30,697,345,596 | Dense; no sparse subset | 18,687,063,904 | 17.40 |
| [evo-qwen38-27b](https://huggingface.co/lmstudio-community/Qwen3.8-27B-GGUF/tree/5a7da681f60570ab5b439a587e912d2e5eddb582) | Dense | 27,320,697,856 | Dense; no sparse subset | 16,810,714,336 | 15.66 |
| [evo-qwen35-community](https://huggingface.co/lmstudio-community/Qwen3.6-35B-A3B-GGUF/tree/68a34855558af61cbef0324d31f411be8a506b08) | MoE | 34,660,610,688 | 3B | 21,166,757,728 | 19.71 |
| [evo-gemma12-qat](https://huggingface.co/lmstudio-community/gemma-4-12B-it-QAT-GGUF/tree/aaec3dd9d1012557147a627142759994d1fd8d37) | Dense | 11,907,350,576 | Dense; no sparse subset | 6,975,879,008 | 6.50 |
| [evo-ministral14](https://huggingface.co/lmstudio-community/Ministral-3-14B-Reasoning-2512-GGUF/tree/5a7eddeccc65cb59551db79d0d0bc32312c5ea8d) | Dense | 13,506,073,600 | Dense; no sparse subset | 8,239,066,144 | 7.67 |
| [evo-gemma12-coding](https://huggingface.co/yuxinlu1/gemma-4-12B-coder-fable5-composer2.5-v1-GGUF/tree/1380be1796e559fca96b4107599285cab3ddbb92) | Dense | 11,907,350,576 | Dense; no sparse subset | 7,381,381,664 | 6.87 |
| [evo-gemma2-9b](https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/tree/d731033f3dc4018261fd39896e50984d398b4ac5) | Dense | 9,241,705,984 | Dense; no sparse subset | 5,761,057,728 | 5.37 |

SHA-256 values and exact filenames are in the JSON inventory and manifests. Actual history contexts, RAM prompt-cache limits, offload and memory measurements are in the [memory report](memory-summary.md). A short-context capacity result does not establish support for the full history workload.
