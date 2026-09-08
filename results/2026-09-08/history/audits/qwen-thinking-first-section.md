# Qwen3.6 with reasoning: first-section check

The first completed source summary does not establish faithful research output. Ten targeted checks reveal a severe date error, unsupported citations, and causal distortions. The full-book run continues; this is an early section audit, not a complete final-summary review.

The accepted retry generated 7,408 reasoning tokens and 999 literal visible-text tokens. Native total output was 8,410 tokens. Native totals and literal-text tokenization use slightly different accounting. The first visible answer arrived after 102.00 seconds. The request completed in 113.94 seconds. Visible generation measured 83.66 tokens/s; visible output over the entire request measured 8.77 tokens/s. The native rate of 74.20 tokens/s includes reasoning.

The preceding attempt reached its 8,192-token total limit. Both attempts together took 245.54 seconds of request wall time. The accepted retry reused the exact prompt, so its much shorter initial processing delay is cache-eligible. Actual cached-token counts remain unavailable.

The summary turns AD 196 into 1996, cites library stamps for preface claims, and presents adopting an emblem as the reason the city survived Philip. These are source-faithfulness errors regardless of the high visible generation rate.

Configuration: Qwen3.6 35B A3B UD-Q4_K_M with bundled MTP, reasoning on, context 65,536, full GPU offload. Temperature 1, top-p 0.95, top-k 20, minimum-p 0, repetition penalty 1. The recommended presence penalty is unavailable in the native API and was not applied.

[Targeted claim ledger](qwen-thinking-first-section.csv)
