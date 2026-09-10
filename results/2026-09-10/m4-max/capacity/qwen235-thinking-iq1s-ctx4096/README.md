# Qwen235 IQ1_S 4K native-thinking capacity check

The pinned 235B-total/22B-active IQ1_S artifact completed one short native-thinking request at 4,096 context, FP16 KV and all layers on GPU. It answered 42 and Paris correctly and gave a coherent explanation of computational/memory demand in three sentences. This is a fit/coherence observation, not a general accuracy result or proof of a universal largest usable model.

Peak sampled process RSS was 48,890,478,592 bytes (45.53 GiB), with zero sampled system swap growth. Server-ready time was 4.092 seconds in a warm filesystem state; this is not cold-load timing. Total check wall time including startup/monitoring was 14.495 seconds. The response used 185 completion tokens including native reasoning; server prediction rate was 25.117 tokens/s. These are not visible-only source throughput.

The separate 16K native-thinking battery uses the frozen source tasks and a 512-token budget per thinking block. It must validate and receive its own source review. All downloads finished naturally before this check; no transfer was paused.

Exact request/response, output, selected offload lines, sampled memory, status and a separate Codex-assisted review are retained. The full private runtime log remains local. No GPU memory limits were raised.
