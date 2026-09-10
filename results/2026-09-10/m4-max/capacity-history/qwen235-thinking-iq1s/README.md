# Qwen3-235B-A22B-Thinking-2507 IQ1_S: native 16K source experiment

Completed with delivery failures. This is separate from the reasoning-off comparison: 16,384 context, FP16 KV, 1,024 MiB prompt cache, native thinking with 512 tokens per thinking block and 2,048 total output tokens. Eleven requests were submitted (two development, nine held-out); merged synthesis was blocked because H1-summary capped. Full-source prompt was 13,736 tokens without truncation.

Peak sampled server RSS: 53,238,972,416 bytes (49.58 GiB); sampled swap: zero. All layers were on GPU. Budget activated 11 times: seven forced ends, four natural ends.

Identifiable visible extraction statements: 19 correct, one contradiction, plus four semantically correct absent-answer statements included in those 20. Only one of four extraction blocks was clean and complete; two had complete final answers if H1’s preceding leakage is allowed. H3 mixed structured statements with planning and incomplete post-tag answers; H4 ended in planning. Do not present 19/20 as a clean final-answer delivery score.

H1-summary has no identifiable final summary. The full-source summary covered four units, partially covered eight, and omitted four. The complete ledger contains 48 coverage dispositions: 28 assessed, four unassessed due to missing H1 final prose, and 16 unassessed due to unsubmitted synthesis. Major final-prose errors include wrong Manuel death year, recovered-territory and court-attendant units, reversed military conditions, work ownership, and conflation of literary and Ottoman eras.

Nine submitted held-out requests generated 6,182 API-content tokens: 15.757768756 tokens/s over 392.314425708 visible-phase seconds and 6.162382250 tokens/s over 1,003.1834685 request-wall seconds. Content includes leaked planning/repetition, so these are not final-answer rates.

See `adjudication.json` for source-anchored claims and explicit delivery boundaries; `review-boundary-policy.json` preserves the review-policy timing. Raw streaming receipts are retained losslessly as gzip. Review is AI-assisted, without independent human adjudication, and concerns supplied Oman OCR rather than modern historical truth.
