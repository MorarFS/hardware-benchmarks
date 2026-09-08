# Qwen3.6 reasoning-off review

The tested workflow fails the combined requirement. Generation speed exceeds 35 tokens/s, but the final summary never completes. Source-level checks also reveal material factual and causal errors.

All 396 pages reached completed source summaries after bounded retries. The final synthesis exhausted allowances of 1,800, 3,600, and 7,200 tokens. Its last output contains 4,345 whitespace-separated words against a requested 900-word summary. It stops mid-sentence near the end of the sixth source group. Its highest physical-page citation is 299, leaving the late history unsynthesized. This output is retained as rejected evidence.

The audit contains 12 first-section checks and 27 later-section checks. Examples include the wrong perpetrators of the Megarian massacre, a vanished golden tripod described as surviving, confusion between the two Heracliuses, the wrong opponent in Justinian II’s coinage dispute, Leontius assigned Justinian’s exile, and a reversed battle outcome at Durazzo. The rejected final repeats the Durazzo reversal verbatim.

Several criticisms were deliberately excluded. Oman’s dates for Theodora and Baduila are assessed as supplied, without silent correction from outside history. His sequence for Michael’s usurpation is treated the same way. Warnings about later material absent from a partial excerpt are legitimate at that stage. They become false if carried into a synthesis containing the continuation.

No completed-final numerical fidelity score is assigned. The observed completion failure and critical source errors already prevent a pass. These findings apply to the tested model, settings, prompts, and pipeline. The reasoning-enabled follow-up is a separate configuration and remains unreviewed.

See [first-section ledger](qwen-first-section.csv) and [later-section ledger](qwen-section-checks.csv).
