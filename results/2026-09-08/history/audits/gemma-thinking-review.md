# Gemma4 26B A4B IT, UD-Q4_K_M, reasoning on: completed full-book review

**Fidelity result: fail.** The completed final was checked against the supplied source.
The ledger contains 87 final claim units. Each unit records its evidence and verdict.
Section checks sample all eight source groups. They are not an estimated error rate.
Completion means generation ended normally; it does not mean the content passed review.

| Dimension | Score, 0–4 |
|---|---:|
| Factual accuracy | 2 |
| Chronology and causation | 2 |
| Attribution | 2 |
| Citations | 2 |
| Coverage | 2 |
| Uncertainty | 2 |

Passing requires at least 3 in every dimension and no disqualifying material error.
Scores are reviewer judgments under the approved rubric, not statistical accuracy estimates.

The final moves a reported six-day Nika death toll into one massacre.
It fixes an explicitly uncertain capital-selection date at 328.
It changes officials' extortion of wealth into extortion of food.
It dates Theodoric's completed conquest to the year of his commission and departure.
It transfers a comparison of senate institutions to the Senate House's design.
Its statement about missing Theme origins erases a supplied explanation and qualified date.

The final contains 786 whitespace-delimited words after removing bracketed citations.
Coverage favors early Constantinople and Justinian over later institutional and economic developments.
The social-history discussion of Christianity, slavery, and monasticism largely disappears.
Later centuries receive a sequence of events with little causal explanation.

Source errors are distinguished from errors introduced by the model.
Oman's historical dates and judgments are not silently corrected using outside knowledge.
Library markings, printed pagination, physical PDF pages, and image-only pages remain distinct.
A legitimate partial-section warning becomes erroneous when retained after full-book synthesis.

All 396 physical PDF pages entered completed source-summary requests.
The run made 13 book requests, including 4 capped attempts.
Every recorded request showed actual reasoning tokens and reasoning stream events.
2 capped attempt(s) produced no visible answer.

| Timing measure | Result |
|---|---:|
| All-attempt native generation, weighted | 39.85 tokens/s |
| Native generation range | 38.81–41.79 tokens/s |
| Visible answer phase, range | 38.16–40.80 tokens/s |
| Visible tokens / all request wall time | 2.59 tokens/s |
| Request wall time, including retries | 3413.58 s |
| Full book phase, including loading and preflight | 3444.26 s |
| Total generated tokens | 125,779 |
| Reasoning tokens | 116,874 |
| Retokenized visible text tokens | 8,846 |
| Final request: first visible token | 558.38 s |
| Final request: full wall time | 594.36 s |
| Final request: visible answer phase | 38.77 tokens/s |

Native generation includes reasoning and answer tokens.
Visible-phase timing includes final response overhead and is conservative.
Retokenized visible counts can differ slightly from native total minus reasoning counts.
Book phase excludes model acquisition and human source review.
These measurements do not turn a fidelity failure into a combined pass.

- [Final claim ledger](gemma-thinking-final-claims.csv)
- [Section checks](gemma-thinking-section-checks.csv)
- [Unedited model final](gemma-thinking-final-summary.md)
