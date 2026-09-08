# Qwen3.6 35B A3B, UD-Q4_K_M, MTP enabled, reasoning on: completed full-book review

**Fidelity result: fail.** The completed final was checked against the supplied source.
The ledger contains 113 final claim units. Each unit records its evidence and verdict.
Section checks sample all eight source groups. They are not an estimated error rate.
Completion means generation ended normally; it does not mean the content passed review.

| Dimension | Score, 0–4 |
|---|---:|
| Factual accuracy | 1 |
| Chronology and causation | 1 |
| Attribution | 2 |
| Citations | 0 |
| Coverage | 1 |
| Uncertainty | 0 |

Passing requires at least 3 in every dimension and no disqualifying material error.
Scores are reviewer judgments under the approved rubric, not statistical accuracy estimates.

The final repeats AD 196 as 1996 and merges the two Heraclius figures.
It cites preface claims to library markings and later events to unrelated pages.
Several printed page numbers become incorrect physical PDF references.
It describes the 1453 fall, then says the source ends before 1204.
This false limitation was copied from the sixth intermediate source group.
The final also merges Basil's reign length with the duration of Bulgarian warfare.

The final contains 1,404 whitespace-delimited words after removing bracketed citations.
Its 900-word instruction was not met. More space did not preserve reliable coverage.
The later narrative includes many events, but its contradictory ending defeats the synthesis.

Source errors are distinguished from errors introduced by the model.
Oman's historical dates and judgments are not silently corrected using outside knowledge.
Library markings, printed pagination, physical PDF pages, and image-only pages remain distinct.
A legitimate partial-section warning becomes erroneous when retained after full-book synthesis.

All 396 physical PDF pages entered completed source-summary requests.
The run made 13 book requests, including 4 capped attempts.
Every recorded request showed actual reasoning tokens and reasoning stream events.
1 capped attempt(s) produced no visible answer.

| Timing measure | Result |
|---|---:|
| All-attempt native generation, weighted | 72.68 tokens/s |
| Native generation range | 69.85–81.08 tokens/s |
| Visible answer phase, range | 80.29–87.76 tokens/s |
| Visible tokens / all request wall time | 7.07 tokens/s |
| Request wall time, including retries | 1709.90 s |
| Full book phase, including loading and preflight | 1729.87 s |
| Total generated tokens | 105,173 |
| Reasoning tokens | 93,047 |
| Retokenized visible text tokens | 12,093 |
| Final request: first visible token | 125.08 s |
| Final request: full wall time | 157.23 s |
| Final request: visible answer phase | 87.76 tokens/s |

Native generation includes reasoning and answer tokens.
Visible-phase timing includes final response overhead and is conservative.
Retokenized visible counts can differ slightly from native total minus reasoning counts.
Book phase excludes model acquisition and human source review.
These measurements do not turn a fidelity failure into a combined pass.

- [Final claim ledger](qwen-thinking-final-claims.csv)
- [Section checks](qwen-thinking-section-checks.csv)
- [Unedited model final](qwen-thinking-final-summary.md)
