# Qwen8 single-request context/logging diagnostic

Purpose: investigate the gap between the original source battery and short synthetic decoding. These are five fresh-server H1-summary trials, each with the identical original 3,440-token prompt, greedy seed 42 and 2,048-token cap. No prompt-cache tokens were reused. Model hash and runtime fingerprint validate; every completed output matches the original. Downloads continued. This is separate from the frozen battery.

The completed attempt's sequence was 32K verbose, 8K verbose, 32K quiet, 8K quiet, 32K verbose. Server-reported decoding rates were 75.75, 75.89, 75.22, 74.92 and 75.09 tokens/s. Prompt rates were 829.05, 816.99, 730.33, 682.03 and 683.33 tokens/s. System swap stayed zero in sampled snapshots.

Both context sizes and both logging modes decode near 75 in this later sequence. Thus allocated context or verbose logging alone does not explain the earlier roughly 43 tokens/s on this request. This sequential single-prompt diagnostic does not identify the cause of run-to-run variation or establish controlled effects. Temperature/frequency and previous-run effects were not measured.

Verbose trials independently verify all layers on GPU. Quiet logs omit that placement receipt: quiet rows record null for verified offload and are diagnostic observations only, never accepted matched-benchmark rows. The earlier attempt stopped at that assertion after its third response; its failure, accepted first two rows and raw third stream are retained. The retry explicitly distinguishes requested from verified placement.

Retained evidence includes exact streams, request/command settings, result records, resource samples and selected runtime placement/timing lines. Full verbose logs include rendered prompts and local paths and remain local. The full 32K battery was subsequently repeated with the original verbose checks; see `../history-repeat/qwen3-8b`.
