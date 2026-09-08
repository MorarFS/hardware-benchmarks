# Qwen3.8 27B source review

Codex/AI-assisted source checks against the complete supplied passages and frozen references. This is not independent human adjudication or certification of modern historical truth.

## Held-out extraction

**19 correct, 1 partial, 0 contradictions, 0 unsupported answers, out of 20.** All four source-absent questions use the requested absence phrase and correct IDs. The one partial answer is H4-Q2: it says support for the Mustaphas provoked war, but omits their roles as rival claimants and their uncle/brother relationships. Its wording largely repeats the question rather than explaining the political mechanism on p.363.

| Question | Judgment | Source check |
|---|---|---|
| H1-Q1 | Correct | Fritigern, p.61 |
| H1-Q2 | Correct | Both entry conditions and bribery, p.63 |
| H1-Q3 | Correct | Food extortion, desperation and revolt, p.63 |
| H1-Q4 | Correct | No decisive result, p.64 |
| H1-Q5 | Correct absence | No Ad Salices casualty total in pp.61–67 |
| H2-Q1 | Correct | Telemachus, 404, death, p.171 |
| H2-Q2 | Correct | Valentinian I, 374, p.173 |
| H2-Q3 | Correct | Persistence plus mitigation in quotation, p.173 |
| H2-Q4 | Correct content; incomplete citation | Connects civic withdrawal and weakened resistance, pp.174–175; quotes a sentence spanning the page boundary while citing only p.174 |
| H2-Q5 | Correct absence | No monastery count in pp.169–176 |
| H3-Q1 | Correct | Purple Chamber, p.241 |
| H3-Q2 | Correct | Thessalonica and departure, p.242 |
| H3-Q3 | Correct | Both removal stages retained, p.243 |
| H3-Q4 | Correct | Franks and Lombards, p.245 |
| H3-Q5 | Correct absence | No annual cavalry pay in pp.241–247 |
| H4-Q1 | Correct | Mohammed, p.362 |
| H4-Q2 | Partial | Omits claimant roles and relationships, p.363 |
| H4-Q3 | Correct | Mustapha's trouble in Asia Minor caused withdrawal, p.365 |
| H4-Q4 | Correct | Encouragement and report marker, p.365 |
| H4-Q5 | Correct absence | No siege casualty figure in pp.358–367 |

All 16 stated-question responses contain quotations and page citations. Fifteen citations support the stated content; H2-Q4 is incomplete across a page boundary. H1-Q2 exceeds the two-sentence constraint when its quoted sentence is counted. These formatting/citation issues are separate from factual-answer classifications.

## Development (excluded from held-out scores)

All three extraction answers correctly preserve execution survivors, the six-day scope of the reported death toll and the absence of an exact assault duration. The development summary does not explicitly preserve the six-day death-toll scope, but also does not explicitly say all 35,000 died solely in the assault; record qualification loss/ambiguous scope rather than a direct contradictory count. Its Belisarius command citation points to p.102, while assignment of overall command occurs on p.103.

## Direct-summary claim ledger

The complete summaries were compared to the supplied passages. The ledger records flagged claims, with other reviewed narrative claims supported at the level stated. It does not calculate a claim-accuracy percentage.

| Output | Flag | Source judgment | Family |
|---|---|---|---|
| H1 summary | Huns invaded the Balkans around 372 | Geographic conflation: p.61 places this initial Hunnic invasion north of the Euxine; the fleeing Goths later cross into imperial territory. | invasion-location |
| H1 summary | Asylum petition cited p.61 | Petition is p.62; p.61 establishes retreat. | petition-citation |
| H1 summary | Valens's conditions cited p.62 | Conditions appear p.63. | conditions-citation |
| H2 summary | Latin proportion from a quarter to a tenth | Qualification loss: p.170 says probably a quarter in 400 and not a tenth in 620. | Latin-proportion |
| H3 summary | Capture could have been prevented with better timing | Vague causal substitution: p.242 specifically says relief forces could rescue the city if its fall had been delayed a few weeks. | relief-qualification |
| H3 summary | Constantine gained power near forty | OCR ambiguity: supplied p.243 reads nearly i^y.; exact age cannot be verified from this fixture alone. Do not label a modern historical age false or import outside correction. | OCR-age |
| H3 summary | Modern-like organization, uniformity and wounded care cited p.244 | Detailed uniformity and wounded care are p.245, so the citation is incomplete. | military-citation |
| H3 summary | Court ceremonies compensated for lack of power, cited p.246 | Explanation appears p.247. | ceremonies-citation |
| H3 summary | Intellectual decline persisted since Heraclian dynasty | Over-compression loses p.247's gradual recovery from Leo the Isaurian onward. | literary-recovery |

Nine flagged direct-summary families appear in H1–H3 above, including one unresolved OCR ambiguity rather than a factual contradiction. Coverage omissions remain separate.

H4 adds substantial errors despite mostly correct extraction from that same passage:

| Claim | Judgment | Evidence / family |
|---|---|---|
| Earlier fall would affect Renaissance timing | Source speaks of reduced brilliance and Italy's readiness, not a changed Renaissance start date | p.359; renaissance |
| Mohammed II reunified the Ottoman realm | Unsupported regnal number for the source's Mohammed/Mahomet; source then names his successor Murad II | pp.362–363; regnal-number |
| Retained territories until reunification in 1421 | Misleading endpoint: Mohammed let Manuel retain them; cession follows Murad's war in 1422 | pp.362–365; territorial-chronology |
| Siege failed due to walls and a reported vision, resulting in peace | Conflates encouragement/resistance with the withdrawal cause; Mustapha's revolt in Asia Minor is the stated immediate reason | p.365; siege-cause |
| His son John VI sold Thessalonica | Contradiction: John's brother Andronicus sold it | p.367; seller-identity |

That gives fourteen reviewed direct-summary flag families, including citation defects, qualification losses and one unresolved OCR ambiguity. This count is not fourteen equally severe factual errors.

## Merged synthesis and coverage

The merged synthesis closely copies all four parent summaries. It propagates all fourteen flagged direct-summary families above, including the geographic conflation, uncertain age, wrong seller and misleading siege cause. These are fourteen propagated manifestations, not fourteen additional unique families. All four passages are present, but the result greatly exceeds the requested 350–450 words.

C = covered, P = partial, O = omitted; order C1/C2/C3/C4. All material components of compound units are needed for C, and coverage does not imply accuracy.

| Passage | Direct summary | Merged synthesis |
|---|---|---|
| H1 | C/C/P/C | C/C/P/C |
| H2 | C/P/C/P | C/P/C/P |
| H3 | C/P/P/C | C/P/P/C |
| H4 | C/C/P/C | C/C/P/C |

Omitted components include Ad Salices; explicit persistence of slavery; Orosius; temporary occupation and the two succession stages in H3; naval limits; and the rival-claimant/rebellion causal sequence in H4. The presence of the vision without the withdrawal cause does not fulfill that compound unit.

## Independent full-source control

The control ends normally, below the 2,048-token cap, but omits H4 entirely and most of the later material in H1–H3. Its four paragraphs do not correspond to four excerpts: two cover early H1, one covers only Latin decline in H2, and one covers early H3. It exceeds the 350–450-word target and uses prose page announcements rather than factual-sentence bracket citations.

| Flag | Source check | Relationship |
|---|---|---|
| Huns invaded the Balkans in 372 | Initial invasion is north of the Euxine, p.61 | invasion-location repeated independently |
| Page63 announcement includes seizure of Fritigern | Banquet action is p.64 | new citation manifestation |
| A quarter spoke Latin in 400 | Drops probably on p.170 | Latin-proportion repeated independently |
| Only Dalmatian seaports retained Latin | Omits the few scattered survivors in the Balkans on p.170 | new Latin-survival qualification loss |
| Entire H4 and later parts of H1–H3 absent | Omission, not a factual contradiction or transport/output-cap failure | control coverage failure |

Other stated claims were reviewed against their source pages. Independent full-source input means these are new or repeated manifestations, not established propagation from direct summaries. Full-source coverage: H1 C/C/P/O; H2 C/O/O/O; H3 C/P/O/O; H4 O/O/O/O. A strong extraction score therefore does not establish reliable summarization.
