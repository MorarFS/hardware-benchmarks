# Method and implementation disclosures

The original `history-v2.0` fixtures remain unchanged. Their 17 hashes were frozen before held-out generation. This note clarifies implementation and evaluator identity outside that freeze.

## Evaluator identity

References and subsequent judgments use Codex/AI-assisted source checks. They are not independent human adjudication. The frozen README's phrase “manually checked” means deliberate source comparison by Codex. The user inspected selected earlier examples, not the complete ledger.

A coordinator preflight checked the source support for 16 stated answers. It did not independently validate the four absence cases. Those require review across each complete supplied passage. Payload inspection and software tests separately assess gold exclusion. Neither establishes answer correctness.

## Fixed development and held-out stages

Development uses two probes from the frozen revised prompts: extraction and direct summary. No extra baseline prompt has been invented outside the freeze. Earlier baseline errors informed prompt design before freezing. Development outputs do not change the held-out prompts or references.

“Held-out” means excluded from prompt development. These pages appeared in previous whole-book inputs and some earlier source inspections. They are not claimed unseen during training or all prior inference.

## Seed and load settings

The frozen configuration requests seed 42. The installed LM Studio CLI exposes concurrency and MTP controls but no seed option. The autonomous Evo implementation therefore records the actual SDK seed and explicitly declines to claim seed 42 without verification. This operational deviation was documented before inference. Frozen files were not silently edited.

The portable API runner does not control model loading. Its native API checks verify context 65,536, parallel capacity 1, MTP, flash attention, and GPU KV offload. Full layer placement, F16 cache, backend, seed, and GPT template require separate inspection. Attach operator-reviewed settings and the exact weight hash to distinguish verified facts from intentions.

GPT's native API rejected `top_k=0` and `reasoning=medium` during earlier compatibility checks. Both fields are omitted. Its server-default top-k remains uncontrolled. Medium refers to the verified template default, not an accepted native reasoning parameter. Gemma and Qwen send `reasoning=off`. Samplers and MTP differ across profiles, so comparisons are between configurations, not architectures alone.

## Performance and accuracy

Synthetic speed, native generation speed, visible-phase speed, first-visible latency, and total request time answer different questions. Reasoning may substantially delay visible text. The portable runner uses returned API token differences; the Evo implementation also retokenizes visible text. Those denominators are not interchangeable.

No keyword score is presented as factual accuracy. Extraction needs source-backed judgments for correctness, partial support, contradictions, unsupported detail, qualification loss, ambiguity, and absence. Citation support is separate. The four absence cases retain their own denominator.

Direct summaries and syntheses need claim ledgers and coverage review. Synthesis errors should distinguish new errors, inherited errors, and repeated manifestations. Unique error families are separate from total flagged claims. Coverage omissions do not automatically become factual contradictions.

This small, deliberately selected pilot cannot establish whole-model research accuracy. Source matching does not certify historical truth. Generation completion is not a passing score. Accuracy results and final source adjudication are not included in this initial reusable package.
