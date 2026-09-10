# MLX on the frozen research-source workload

The same 17 frozen fixture hashes and all 12 reconstructed requests passed validation, including stream/output agreement. Ten held-out requests exclude the two development requests. The full-source prompt contained 13,738 tokens, the same count as the GGUF run; no source was truncated.

| Configuration | Visible phase tokens/s | Visible tokens/request wall second | Held-out request time |
|---|---:|---:|---:|
| MLX Qwen3-8B group64 four-bit |73.106|32.040|121.41 seconds|
| llama.cpp Qwen3-8B Q4_K_M |38.747|21.609|226.71 seconds|

These are **configuration-level observations**, not an isolated backend comparison. MLX uses different quantized weights, BF16 model dtype, dynamically growing fresh default KV per request and no cross-request prefix cache. llama.cpp uses FP16 KV with a 32K allocated context and server prefix reuse. Both use the same source prompts, greedy sampling, seed 42, a 2,048-token output cap and reasoning off. All token counts and timing boundaries are in the records. Output lengths differ. Downloads continued; a runtime-help invocation also overlapped part of the MLX battery. No controlled estimate of background interference is claimed.

Peak MLX allocator memory was 7.175 GB, while sampled process RSS peaked at 4.944 GB and sampled system swap remained zero. These counters have different accounting; do not add them or treat either as a complete independent physical-memory pool.

## Source review

Codex-assisted review of all 20 extraction answers found **16 correct, one partial, one contradiction and two false abstentions**. All four genuinely source-absent questions were answered by abstention. Page and quotation compliance are separate.

The false abstentions miss explicitly stated Fritigern and Thessalonica answers. H3-Q3 confuses the agents in Romanus’s removal and his sons’ expulsion. H4-Q2 fails to explain the rival claimants and their uncle/brother relationships. `review.json` records the exceptions and criteria.

Selected summary findings: H4 invents 1448 as Manuel’s death year and propagates it to synthesis. The merged synthesis omits the entire H3 literary-emperors passage, supplies only three sections, and has 651 prose words against the 350–450 target. The full-source control has 532 words and no PDF citation markers. Direct summaries also show citation/length problems. These examples are not an exhaustive claim or coverage adjudication.

Thus MLX was faster on this specific workload, but this small trial does not establish a factual-quality improvement or general research reliability. Quantization/backend changes cannot be separated as causes of the output differences.

## Reproduction

Install the pinned MLX versions and model listed in the parent MLX report. Then run:

```sh
caffeinate -i work/mlx-env/bin/python scripts/history_v2/run_m4_mlx.py --model work/mlx-qwen8 --output local-results/m4-mlx-history
```

The generator validates fixtures and never submits gold references. Output directories must be new; no silent retries. Each request preserves its exact source-derived messages, token events and final output. Streams are gzip-compressed in GitHub storage; decompress with `gzip -dk -- *-stream.jsonl.gz` to restore the original JSONL bytes. `validation.json` records the subsequent independent prompt/stream checks; `review.json` supplies separate source judgments.
