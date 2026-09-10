# Qwen3 8B CPU baseline

Same exact Q4_K_M artifact and b10852 revision as the Metal run; ten CPU threads, FP16 KV, flash attention, 512 batch/microbatch and five repetitions after warmup. Explicit `-ngl 0 -dev none` produced **0/37 GPU layers**, CPU mapped/repacked model buffers and CPU KV buffers. Compiled backend string `MTL,BLAS` does not establish actual Metal inference.

| Test | Depth | Mean ± SD tokens/s |
|---|---:|---:|
| tg256 | 2048 | 21.034 ± 2.266 |
| pp512 | 0 | 127.924 ± 2.814 |
| tg256 | 0 | 40.066 ± 1.824 |

Downloads continued by user request. CPU runs followed Metal sequentially, with no separate randomized or thermally controlled session. All samples and memory time series are under `cpu/`. The CPU experiment is a separate configuration, not a claim about peak CPU performance.

Reproduce with `python3 scripts/check-m4-cpu.py` after downloading the pinned Qwen8 artifact and installing the official runtime.

Artifact provenance: the original CPU run used the same retained Qwen8 file as the immediately preceding hash-verified Metal run. Its original status does not contain an independent CPU hash check. The reproduction script now verifies the pinned hash before running. Independent post-processing recomputes all three CPU means/SDs from the 15 raw nanosecond samples and checks actual zero-layer offload.
