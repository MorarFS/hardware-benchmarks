# Separated source-fidelity pilot, version 2.0

This bounded experiment follows the original book-summary benchmark. It does not replace it.

Four held-out passages span PDF pages 61–67, 169–176, 241–247, and 358–367. Each passage has five fixed questions, including one source-absent question. The canonical text preserves OCR noise and source judgments. Development uses pages 101–106, including previously identified execution and casualty errors. Held-out means excluded from prompt development, not absent from training or earlier whole-book inputs.

The runner sends only `inputs/`, `questions.json`, and `prompts.json`. Files in `gold/` contain evaluator references and never enter a request. A SHA-256 freeze manifest records the entire suite before held-out inference. Exact payloads are retained for inspection.

Stages run as independent requests: factual extraction, a direct summary for each passage, synthesis of the four summaries, and a full-source synthesis control. The control uses all four original passages, not the entire book. Summaries do not receive the question answers. Synthesis does not receive the gold ledger.

The initial pilot uses Gemma4 26B A4B UD-Q4_K_M, Vulkan, reasoning OFF. Qwen35 OFF with bundled MTP and GPT-OSS120 with template-medium reasoning can use the same frozen suite. Each is a configuration-level observation. Temperature, reasoning, and MTP differ, so this is not a controlled test of model architecture alone.

Evaluator judgments are source-grounded and manually checked. Extraction reports correct, partial, contradiction, unsupported, qualification loss, ambiguous, or no answer, out of 20 matched questions. Citation support is a separate judgment. Source-absent questions have their own four-question denominator. Partial answers are not silently converted to binary accuracy. Direct summaries and synthesis use claim ledgers plus four predeclared coverage units per passage. Synthesis errors are marked new, propagated, or repeated; omissions are separate. Unique error families and repeated manifestations are reported separately.

The source is Oman’s historical narrative, not an authoritative modern gold standard. Matching it does not certify historical truth. A small, deliberately selected battery does not establish whole-model research accuracy. Better prompting may help; one pilot cannot establish a general improvement. Baseline and revised development outputs are not held-out scores.

Performance reports visible decode, actual first-visible delay, reasoning tokens and time when observable, total wall time, and memory separately. RAM, VRAM, GTT, RSS, and PSS overlap on AMD UMA. The current speed preference is above 40 visible tokens/s; the original threshold was at least 35. Research usefulness is not reduced to a zero-error gate.

The passage boundaries were expanded before freezing, to provide roughly 2–4K tokens per passage. Exact model-token counts are recorded during preflight. Sixteen predeclared coverage units span the beginnings, middles, and endings. Compound units can receive partial coverage judgments. No prompt changes follow development or held-out outputs in this frozen run.
