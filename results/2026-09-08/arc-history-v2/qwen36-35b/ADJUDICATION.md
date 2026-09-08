# Qwen3.6 35B-A3B source review

Codex/AI-assisted review against the complete supplied passages and frozen reference ledger. No independent human adjudication. This measures fidelity to Oman, including the source's dated judgments and OCR, not modern historical truth.

## Held-out extraction

**16 correct, 4 partial, 0 contradictory, 0 unsupported, 0 unanswered, out of 20 questions.** Partial answers remain a separate category. All four source-absent questions were recognized semantically. Only three used the exact requested absence response with the correct question ID. H1's fifth answer repeats `H1-Q4`; it is mapped to H1-Q5 by position and explicit reference to exact casualties. Under strict ID matching H1-Q5 is missing/ambiguous instead of correct.

| Question | Judgment | Source check |
|---|---|---|
| H1-Q1 | Correct | Fritigern, p.61 |
| H1-Q2 | Correct | Both conditions and bribery, p.63 |
| H1-Q3 | Correct | Withholding, extortion and desperation, p.63 |
| H1-Q4 | Correct | Indecisive result, p.64 |
| H1-Q5 | Correct content; ID/format failure | No exact Ad Salices casualty number anywhere in pp.61–67; answer mislabeled H1-Q4 |
| H2-Q1 | Correct | Telemachus, 404, death, p.171 |
| H2-Q2 | Correct | Valentinian I, 374, p.173 |
| H2-Q3 | Partial | Preserves centuries of persistence, omits the requested mitigation qualification, pp.173–174 |
| H2-Q4 | Partial | Civic withdrawal present; connection to hampered resistance to invasions omitted, pp.174–175 |
| H2-Q5 | Correct absence | No monastery count in pp.169–176 |
| H3-Q1 | Correct | Purple Chamber, p.241 |
| H3-Q2 | Correct | Thessalonica, 904, transient occupation, p.242 |
| H3-Q3 | Partial | Gives removal of sons by mob/guards but omits sons forcing Romanus to abdicate, p.243 |
| H3-Q4 | Correct | Franks and Lombards, p.245 |
| H3-Q5 | Correct absence | No annual cavalry pay in pp.241–247 |
| H4-Q1 | Correct | Mohammed, p.362 |
| H4-Q2 | Partial | Rival claimants and retaliation present; uncle/brother relationships omitted, p.363 |
| H4-Q3 | Correct | Mustapha's trouble in Asia Minor caused withdrawal, p.365 |
| H4-Q4 | Correct | Encouragement and report marker retained across the two sentences, p.365 |
| H4-Q5 | Correct absence | No siege casualty count in pp.358–367 |

The 16 stated answers cite pages supporting the content they actually include; this does not repair partial answers. Only seven of those 16 include an explicit supporting quotation (H1-Q1/Q3/Q4 and H4-Q1–Q4). Missing quotes are instruction failures, not fabricated citations.

## Summary and synthesis claim ledger

The complete outputs were compared with all four passages. The following ledger records flagged claims; other reviewed narrative claims have source support at the level stated. Coverage omissions are reported separately below. These are reviewed flags, not an exhaustive quantitative claim-accuracy percentage.

| Output | Claim or issue | Judgment and evidence | Family / propagation |
|---|---|---|---|
| Development summary | Hippodrome massacre killed 35,000 | Contradiction/qualification loss: p.106 says it is reported that 35,000 died over six days. Extraction D-Q2 was correct, but answers were not supplied to this summary. | D-death-scope; development only |
| H1 summary | Visigoths numbered nearly 200,000 | Qualification loss: p.62 quotes no less than 200,000 fighting men, besides dependants. Direction, population scope and report marker are lost. | population |
| H2 summary | Paganism disappeared by the fifth century | Qualification loss: p.176 says practically disappeared as an active force by the end of that century, while philosophers still professed it. | paganism |
| H3 summary | Emperors lacked strength had times been harder | Qualification loss: p.241–242 expresses doubt, not certainty. | counterfactual |
| H4 summary | Earlier fall could delay the Renaissance | Unsupported change: p.359 says reduced brilliance if dispersion preceded Italy's readiness; it does not state delayed onset. | renaissance |
| H4 summary | Murad II unified the Ottoman realm | Contradiction: Mohammed is the reunifier on p.362; Murad is his successor on p.363. | reunifier |
| H4 summary | John VIII traveled to Italy | Source mismatch: p.365–367 calls this ruler John VI. A historically motivated correction is outside this source-only task. | regnal-number |
| Merged synthesis | Copies the H1 population, H2 paganism and H3 counterfactual formulations | Same qualifications lost as in direct summaries. | Three propagated manifestations |
| Merged synthesis | Omits the entire fourth excerpt | Coverage omission, not a factual contradiction; also 762 whitespace words rather than 350–450. | H4 omission |
| Full-source control | Nearly 200,000 Visigoths | Same population qualification problem, independently repeated from original-source input. | population; repeated independent |
| Full-source control | Murad II unified the Turkish realm | Contradiction, pp.362–363. | reunifier; repeated independent |
| Full-source control | Unreliable mercenaries | Unsupported adjective: p.366 describes mercenaries, origins and number, not unreliability. | mercenaries; new |
| Full-source control | John VIII and aid cited to p.371 | Source regnal-number mismatch plus fabricated out-of-input citation; the relevant supplied page is 367. Both final-paragraph citations to 371 fail. | regnal-number repeated; citation new |
| Full-source control | Narrative bridges and eventual collapse | Goes beyond four discontinuous excerpts, which end before the fall; the final generic trajectory is not source-cited. | synthesis-bridging; new |

There are six distinct held-out direct-summary flag families (population, paganism, counterfactual, renaissance, reunifier, regnal-number), three propagated manifestations in merged synthesis, and additional independent-control flags. Development death-scope is excluded from held-out counts. Repetitions are not extra unique error families.

## Predeclared coverage ledger

Order is C1/C2/C3/C4 within each passage. C = covered, P = partial, O = omitted. Compound units require all material components for C. A coverage mark does not excuse a factual error.

| Passage | Direct summary | Merged synthesis | Full-source control |
|---|---|---|---|
| H1 | P/P/P/C | P/P/P/C | C/P/P/C |
| H2 | C/P/P/P | C/P/P/P | P/P/P/O |
| H3 | C/P/P/C | C/P/P/C | P/O/P/P |
| H4 | C/C/P/C | O/O/O/O | P/C/P/C |

Main omitted components: H1 Fritigern/entry conditions/Ad Salices; H2 explicit slavery persistence, later learned monasticism and Orosius; H3 temporary occupation, two succession stages, tactical caution and naval limits; H4 direct-summary vision and rebellion as the distinct withdrawal cause. Merged synthesis drops H4 completely. The full-source control supplies wider breadth but introduces its own unsupported claims and citations.
