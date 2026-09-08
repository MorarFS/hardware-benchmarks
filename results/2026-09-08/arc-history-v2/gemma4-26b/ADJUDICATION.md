# Gemma 4 26B-A4B source review

Codex/AI-assisted source review against the complete frozen passages and references; not independent human adjudication or certification of modern historical truth.

## Held-out extraction

**16 correct, 3 partial, 1 contradiction, out of 20.** All four source-absent questions are correctly recognized. Three add a final period to the exact requested absence phrase; this is a punctuation difference, not a factual error. All question IDs are correct.

| Question | Judgment | Source check |
|---|---|---|
| H1-Q1 | Correct | Fritigern, p.61 |
| H1-Q2 | Correct | Conditions and bribery, p.63; exceeds the two-sentence format |
| H1-Q3 | Partial | Food withholding and prices identified, but hunger/desperation leading to revolt omitted, pp.63–64 |
| H1-Q4 | Correct | Indecisive result, p.64 |
| H1-Q5 | Correct absence | No exact Ad Salices casualty count in pp.61–67 |
| H2-Q1 | Correct | Telemachus, 404, death, p.171 |
| H2-Q2 | Correct | Valentinian I, 374, p.173 |
| H2-Q3 | Correct | Both persistence and mitigation retained in quotation, p.173 |
| H2-Q4 | Partial | Large-scale civic withdrawal present; effect on resistance to invasions omitted, pp.174–175 |
| H2-Q5 | Correct absence | No monastery count in pp.169–176 |
| H3-Q1 | Correct | Purple Chamber, p.241 |
| H3-Q2 | Correct | Thessalonica and transient occupation, p.242 |
| H3-Q3 | Contradiction with a correct component | Falsely states the passage does not name Romanus's removers. His sons force his abdication on p.243; the answer correctly names mob/guards as removers of the sons. Primary classification is contradiction rather than mere omission. |
| H3-Q4 | Correct | Franks and Lombards, p.245 |
| H3-Q5 | Correct absence | No annual cavalry pay in pp.241–247 |
| H4-Q1 | Correct | Mohammed, p.362 |
| H4-Q2 | Partial | Rival claimants/retaliation present; uncle and brother relationships omitted, p.363 |
| H4-Q3 | Correct | Mustapha's trouble in Asia Minor prompted withdrawal, p.365 |
| H4-Q4 | Correct | Encouragement with report marker, p.365 |
| H4-Q5 | Correct absence | No siege casualty count in pp.358–367 |

All 16 stated-question responses include supporting quotations and citations. Fifteen support the response's stated content; H3-Q3's quotation supports its second component but contradicts its absence claim. Quotes do not repair missing answer components, and several are longer than the requested short quotations.

## Development observations (excluded from held-out score)

D-Q1 is correct, D-Q2 incorrectly abstains despite p.106 attributing the reported 35,000 deaths to six days, and D-Q3 correctly abstains. The development summary connects 35,000 deaths to the final assault without preserving the six-day scope. It also puts the initial January rioting after the execution order, whereas p.101 says the order followed rioting. These are separate scope and chronology errors.

## Summary and synthesis claim ledger

Complete outputs were compared with the supplied passages. This ledger records reviewed flags; it is not a quantitative claim-accuracy percentage. Other reviewed narrative content is supported at the level stated. Coverage omissions remain separate.

| Output | Claim or issue | Source judgment | Family / propagation |
|---|---|---|---|
| H1 summary | Marcianopolis affray and revolt cited to p.63 | Narrative is supported on p.64; p.63 only begins the lead-in. Citation is incomplete. | H1-citation |
| H1 summary | Valens's campaign in 378 cited to p.64 | Year and personal campaign appear on p.65, not p.64. | H1-citation |
| H2 summary | Roman element vanished by the seventh century | Qualification loss: p.169 says rapidly vanishing, with survivals described on p.170. | Latin-survival |
| H2 summary | Individual-soul explanation cited to pp.172–173 | P.172 is illustration OCR; the explicit causal explanation for vulnerable classes is p.174. P.173 only partly supports the combined statement. | soul-citation |
| H2 summary | Paganism disappeared by the end of the fifth century | Qualification loss: p.176 says practically disappeared as an active force, with surviving philosophers. | paganism |
| H3 summary | Most monotonous era asserted as opening fact | Omits immediate attribution of Oman's evaluative judgment; next sentence does attribute his characterization. | judgment-attribution |
| H4 summary | Era began with John's reign | Unsupported chronology: p.358 starts the last 75 years around 1370; p.359 says John's reign had lasted over half a century when he died in 1391. | reign-start |
| H4 summary | Mohammed's reunification forced Manuel's 1422 cession | Causal conflation: p.362 says Mohammed let Manuel retain his gains; pp.363–365 connect renewed war and cession to Murad and Manuel's rival claimants. | reunification-cause |
| H4 summary | Empire's population shrank | Scope generalization: p.366 specifically describes Constantinople's population, not an empire-wide population series. | population-scope |
| Merged synthesis | Repeats H1 citation errors, Latin vanished, soul citations, paganism disappeared, opening H3 judgment, reign-start and reunification-cause | Inherited from the direct summaries; not separate unique families. | propagated |
| Merged synthesis | In A.D.372 instead of around A.D.372 | Drops the approximation in p.61 and its parent summary. | dating-precision; new |
| Merged synthesis | Far above 350–450 words | Length failure; all four passages are present. | formatting, not factual error |

Direct-summary flags have eight unique families, with two manifestations of H1-citation. Merged synthesis propagates seven families (eight manifestations, counting both H1 citations); it softens the population-scope statement to an unspecified population and adds one date-precision family. Development errors are excluded from those counts.

## Predeclared coverage

C = covered, P = partial, O = omitted; order C1/C2/C3/C4. Compound components must all be represented for C. Coverage does not imply correctness.

| Passage | Direct summary | Merged synthesis |
|---|---|---|
| H1 | C/C/P/P | C/C/P/P |
| H2 | C/P/P/O | C/P/P/O |
| H3 | C/P/P/C | C/P/P/C |
| H4 | C/C/O/P | C/C/O/P |

H1 omits Ad Salices and the defenses as the explicit deterrent. H2 omits slavery persistence, later learned monasticism, Orosius and statecraft. H3 omits transient occupation, the two removal stages, tactical caution and naval limits. H4 omits the rival-claimant/vision/rebellion sequence and the loss of Thessalonica. Merged synthesis largely preserves these omissions.

## Independent full-source control

The control covers all four excerpts but devotes two paragraphs to H1, one to H2 and one combined paragraph to H3/H4, failing the requested one paragraph per excerpt. It also exceeds the length target. Citations use `(61)` rather than `[PDF p. 61]`; page numbers can still be assessed.

| Flagged claim | Judgment | Evidence |
|---|---|---|
| Visigoths' more civilized status | Author's evaluative framing is repeated without local attribution | pp.61–62; attribution issue, independently repeated type |
| Children bartered for bread | Over-specific compression: p.63 says a slave for a loaf, then selling their own children as slaves to avoid starvation | p.63; new trade-scope flag |
| Constantine compensated for lack of real power, cited p.246 | Supporting explanation appears on p.247 | pp.246–247; new citation manifestation |
| Unredeemed gloom by late fourteenth century | Chronology error: p.365 applies that phrase to the last thirty years after Manuel's death in 1425 | p.365; new chronology family |

Other narrative claims were checked against the supplied pages. This control avoids the direct-summary false causal connection from Mohammed's reunification to the cession. Independent inputs mean these are repeated or new observations, not proof of propagation from summaries.

Control coverage: H1 C/C/P/O; H2 C/P/P/O; H3 P/O/P/P; H4 P/P/O/P. In particular it omits Constantinople's defensive deterrence, Ad Salices, later monastic learning/Orosius/statecraft, Thessalonica and succession details in H3, and the claimant/vision/rebellion causal sequence in H4.
