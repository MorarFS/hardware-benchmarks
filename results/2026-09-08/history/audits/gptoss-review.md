# GPT-OSS 120 B source-fidelity review

**FAIL.** Speed exceeds 35 visible tokens/s; source fidelity does not pass.

The complete final audit covers 151 citation-linked claim units. It records 17 critical,29 major and 29 moderate flags. Twenty-one additional units have minor issues;55 units are supported. Units may contain several related assertions. Counts are manifestations, not independent mistakes or accuracy percentages.

All eight source groups completed, covering 396 physical PDF pages. The final synthesis required one retry after a 12,288-token cap. The accepted retry finished normally with 8,400 native output tokens:407 reasoning tokens and 7,983 retokenized visible tokens. The native total-minus-reasoning count includes 10 additional formatting/control tokens; it is not substituted for visible text.

Final visible decode measured 44.2403 tokens/s. First visible text arrived after 13.0509 seconds; total request time was 193.4972 seconds. This was a retry with a reused input prefix. Its native first-token latency was 0.1172 seconds, which does not measure first visible text.

The successful book phase took 1,486.1271 seconds (24.77 minutes), including loading and preflight. Its ten requests consumed 1,264.9457 seconds,36,843 native output tokens and 15,471 reasoning tokens. Retokenized visible output totalled 21,272 tokens, or 16.8165 per total request second. Earlier API failures and model-download costs remain separate records.

The accepted final contains 5,288 whitespace-delimited words, including citations, against a 900-word request. It reproduces extensive intermediate notes instead of delivering the requested concise synthesis. It does not substantively cover the final century or the 1453 fall. Its final citation to 368–370 supports a generic uncertainty claim, not a narrative of the ending.

## Decisive findings

- The Black Sea’s Axeinos/Euxeinos names become the colony’s name (PDF 28–29).
- Philip’s failed siege becomes his capture of Byzantium (PDF 33–34).
- TheodosiusI and Arcadius merge into a ruler who dies in 408 (PDF 70/80).
- Justinian’s reign ends in 532, confusing a Persian treaty with his death (PDF 101/131).
- StSophia is rebuilt in 40 days; the source says preparations began then (PDF 133).
- The African exarch and his son Heraclius become one person (PDF 156–157).
- Burtzes’s capture of Antioch is attributed to Phocas (PDF 257).
- Zimisces is assigned Russian campaigns predating his reign (PDF 260–261).
- A statistic about Janissary-born Grand Viziers becomes territorial loss (PDF 350–351).

These errors often propagate from source summaries into the final. They are not new independent errors at each stage. Citation drift also affects multiple neighboring claims.

## Rubric judgments

| Dimension | Score,0–4 |
|---|---:|
| Factual fidelity |1|
| Chronology |1|
| Attribution |1|
| Citation reliability |1|
| Beginning/middle/end coverage |0|
| Uncertainty handling |1|

Passing requires at least 3 in every dimension and no disqualifying critical error. Scores are reviewer judgments, not measured accuracy percentages.

The separate 43-unit source sample covers all eight groups. It records 13 critical,16 major and 6 moderate flags. It deliberately follows suspicious claims, so its error prevalence must not be generalized. Source and final counts must not be added.

The one-word API validation returned exactly Ready in 1.9662 seconds. It confirms the repaired request format and observed reasoning. It is excluded from history throughput and fidelity scores.

[Final claim ledger](gptoss-final-claims.csv) · [Source checks](gptoss-section-checks.csv) · [Raw accepted final](gptoss-final-summary.md)
