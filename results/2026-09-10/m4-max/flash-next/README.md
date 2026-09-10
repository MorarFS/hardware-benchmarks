# Qwen3.8-Flash-Next MLX on M4 Max 64 GB

Completed with a required runtime compatibility fix and a major synthesis failure.

| Observation | Result |
|---|---:|
| Complete pinned repository | 68.10 GiB |
| Target and vision tensor payload | 36.89 GiB |
| Complete disk-backed n-gram payload | 29.80 GiB |
| Optional MTP payload, downloaded but unused | 1.39 GiB |
| Warm generation, three samples | 36.4883 ± 0.1067 tokens/s |
| Frozen source visible generation | 32.0083 tokens/s |
| Frozen source including request wall time | 16.6347 tokens/s |
| Extraction, including four absent questions | 18 correct / 2 partial |
| Full-source summary coverage | 2 complete / 0 partial / 14 omitted |
| Peak MLX allocation during source battery | 41.7855 GB |
| Source-battery sampled swap growth | 0 |
| Later context-diagnostic global swap growth | Approximately 390 MiB |

The artifact is `Sawfwair/Qwen3.8-Flash-Next-MLX-Mixed-2bit` at `a6e3d7a43efb8803cd6b847299a54084dc4e8ef4`, derived from official Qwen at `f5d08274bafd880402bd16f5e3e6c514136ec06c`. All 146 files were verified; all 48 layers and 512 experts in each of 144 expert weight banks are present. Routed experts use affine Q2/group 128; the full n-gram table uses Q4/group 32. This is target-only decoding, with no pruned or ablated substitute and no Flash-Next GGUF.

Upstream MLX-VLM provides row-addressable, read-only PLE storage. The adapter indexes the original safetensors ranges and hard-links unchanged files. The exact loaded parameter-byte count equals the target/vision payload. Logical row bytes reported by the lookup implementation are not physical SSD throughput; macOS filesystem caching remains uncontrolled.

The first run generated garbage despite successful strict loading. The [publisher converter](https://github.com/sawfwair/mere-run/blob/3ed0a15826605c77d9017e33c0a40c9e4e1d1952/scripts/model-conversion/convert_qwen38_flash_next_mlx.py) adds 1 to 148 base text-normalization scales; the selected runtime added 1 again. The explicit `flash_next_compat.py` helper uses those stored scales directly, without modifying tensor values or gated/vision norms. The initial failure remains in `smoke-unadapted-norms/`; only corrected results enter comparisons. The isolated runtime is MLX 0.32.2 / MLX-VLM 0.7.0 at `8f5dc3ddddbb8d7dd2b88ac51015def6f81fed21`. PyTorch/Torchvision are processor dependencies, not the inference backend.

[Source review](history/README.md) retains all 12 requests, output hashes, stream receipts, and 192 grouped claim annotations. The full-source request stops naturally below its output cap but summarizes only the opening H1 narrative. [Context diagnostics](context/review.json) retrieve later-source answers and all markers at 15,317 input tokens. They do not replace the failed synthesis or establish general long-context reasoning quality. The advertised 262,144-token limit was not tested.

Source-battery RSS and MLX allocation are different overlapping measurements and must not be added. Approximately 123 KiB of system swap existed before the corrected runs. There was no growth during the source battery, but the later diagnostic increased global swap by approximately 390 MiB; the cause is not isolated. Do not describe the overall experiment as swap-free.

Ten upstream storage tests, 38 architecture tests with 18 subtests, and direct comparisons of actual PLE rows passed. These check runtime/transport behavior, not source accuracy. The source ledger is AI-assisted and has no independent human adjudication.
