# Qwen3 8B delayed repeat

All 12 requests passed the same original 32K, FP16 KV, cache-1024, reasoning-off validator. All 12 assembled outputs exactly equal the original run (see `output-comparison.json`); the source ledger is inherited only after this equality check. Downloads continued.

The ten held-out requests produced the same 4,899 visible tokens in 148.934 request-wall seconds: **60.805 visible tokens/s** and **32.894 tokens per request-wall second**, versus the original **38.747 / 21.609**. Both observations remain separate. The repeat clears 40 during visible generation but remains below 40 including prompt processing.

This was a predeclared delayed repeat after the five fresh-server context/logging diagnostic trials, which themselves followed an interrupted diagnostic attempt. It was not a controlled thermal, idle-time, or download experiment. The original run followed the CPU baseline; later tests and other workspace work changed the machine's run history. Temperatures and frequencies were not measured. Do not infer a cause or pool these runs into a stable-rate estimate.

Source fidelity is unchanged: 18 correct / 1 partial / 1 contradiction among 20 extraction answers, with all four truly absent answers correctly abstained; full-source coverage is 3 complete / 9 partial / 4 omitted. See the original source review and this folder's hash-checked inherited ledger. No independent human adjudication.
