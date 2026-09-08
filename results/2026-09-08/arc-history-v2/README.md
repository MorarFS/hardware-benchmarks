# History source-fidelity benchmark on Intel Arc Pro B70

**All 36 requests completed. Qwen3.6 35B-A3B was fastest. Qwen35 and Qwen27 tie on supported-answer content under the published Evo grading convention, while Qwen27 leads under the stricter completeness review. None produced consistently reliable summaries.** This small pilot does not establish overall model accuracy.

The [frozen history-v2 suite](../../../experiments/history-v2/README.md) was found in this repository and run on the three models already downloaded for the Arc speed comparison. It uses Charles Oman's public-domain *The Byzantine Empire*: four passages, 20 held-out questions (including four source-absent questions), direct summaries, summary synthesis, and a full-source control, plus two development requests per model.

This reuses the Evo prompts and passages exactly, but **is not an exact Evo hardware/configuration reproduction**. Arc uses SYCL and existing weights; Evo's Gemma quantizer and Qwen MTP weights differ, and GPT-OSS 120B was not run. See [method and deviations](METHOD.md). The [completed Evo audit](../history-v2/README.md) was published while this run was underway, in commit `18eb5aa`. Its judgments are now available for a scoring crosswalk; differences must not be attributed to hardware alone.

## Extraction results

Codex/AI-assisted judgments compare answers to the supplied source, including its qualifications. They are not independent human adjudication. Partial answers remain separate rather than being assigned arbitrary half credit. The four absence questions are included in the 20-question denominator and shown separately as a diagnostic. This first table retains the initial **strict completeness review**; the Evo-aligned content review follows it.

| Model / Arc configuration | Correct | Partial | Contradiction | Correct source-absent answers | Server decode tokens/s |
|---|---:|---:|---:|---:|---:|
| Qwen3.6 35B-A3B UD-Q4_K_M, MTP off | 16/20 | 4 | 0 | 4/4 | 68.39 |
| Gemma 4 26B-A4B Instruct bartowski Q4_K_M | 16/20 | 3 | 1 | 4/4 | 52.20 |
| Qwen3.8 27B UD-Q4_K_M | 19/20 | 1 | 0 | 4/4 | 19.94 |

Qwen35's fifth H1 answer repeats the H1-Q4 label. It is mapped to H1-Q5 by position and explicit question content. Strict ID matching would classify H1-Q5 as missing/ambiguous, yielding 15 correct, four partial and one ambiguous item. Gemma falsely states that the passage does not identify who removed Romanus, although his sons are named as the actors on p.243. All three omit some requested detail about the two Mustaphas; Qwen27's other nineteen answers are complete under this rubric.

Per-question judgments and citation checks: [Qwen35](qwen36-35b/ADJUDICATION.md), [Gemma](gemma4-26b/ADJUDICATION.md), [Qwen27](qwen38-27b/ADJUDICATION.md). Correct content does not imply that every quote, citation, question ID or sentence limit passed.

### Crosswalk to the published Evo content convention

The Evo ledger accepts explaining civic withdrawal without separately naming invasions (H2-Q4), and support for rival claimants without spelling out both kinships (H4-Q2). Applying that convention changes Qwen35 H2-Q4/H4-Q2 and Gemma H2-Q4/H4-Q2 to supported content. Qwen35 H2-Q3 also preserves the central requested qualification, centuries of continued slavery, although it omits mitigation. Its strict detail penalty is retained above but removed for this content-level view. Qwen27 H4-Q2 remains partial because it does not identify rival claimants and mostly restates the question.

| Configuration | Supported answer content / 20 | Partial | Contradictory answer containing false absence | Correct absence / 4 |
|---|---:|---:|---:|---:|
| Arc Qwen35, MTP off | 19 | 1 | 0 | 4 |
| Arc Gemma, bartowski weights | 18 | 1 | 1 | 4 |
| Arc Qwen27 | 19 | 1 | 0 | 4 |
| Evo Qwen35, MTP on (published) | 19 | 1 | 0 | 4 |
| Evo Gemma, Unsloth weights (published) | 18 | 2 | 0 | 4 |
| Evo GPT-OSS120 (published) | 19 | 0 | 1 false abstention | 4 |

For Evo, the published 16-answerable and four-absent denominators are combined here; no outputs were regenerated. Arc Gemma's explicit false absence for Romanus coexists with a correct second component, so this review labels it contradiction, while Evo GPT's declined answer is labeled false abstention. These categories are not identical. Qwen35's duplicated H1-Q4 ID remains a format issue in either content convention; strict ID matching subtracts one supported item. The crosswalk is a documented secondary review, not a silently revised frozen rubric or a calibrated cross-machine accuracy test.

## Summaries and synthesis

| Model | Summary/synthesis word limits met, including development | Material findings |
|---|---:|---|
| Qwen35 | 1/7 | Direct H4 summary names Murad as reunifier where the source names Mohammed. Merged synthesis omits H4. Full-source control invents p.371 citations outside the supplied pages. |
| Gemma | 4/7 | Direct H4 summary conflates Mohammed's reunification with the later territorial cession under Murad. Merged synthesis propagates causal and citation errors. |
| Qwen27 | 0/7 | Direct H4 summary attributes Thessalonica's sale to John rather than his brother Andronicus and misses the stated withdrawal cause. Merged synthesis propagates those errors. Full-source control omits H4 entirely. |

Every request finished with a normal stop and no output cap, timeout, or transport error. Missing material is therefore a generation/coverage failure, not a missing source or truncated download. Both synthesis inputs were reconstructed and verified after the run. Direct summaries received no extracted answers; merged synthesis received all four direct summaries; full-source control received all four original passages.

The detailed reviews contain flagged-claim ledgers, separate predeclared coverage assessments, and distinctions between new, propagated and independently repeated errors. Their flag counts include citation/qualification issues and are not interchangeable severity scores or exhaustive claim-accuracy percentages. Word counts remove page-citation markers before whitespace counting; targets are 180–220 words for five direct/development summaries and 350–450 for two syntheses.

## Performance and reproducibility

| Model | Median first-visible delay | Total time for 12 requests, excluding loading |
|---|---:|---:|
| Qwen35 | 4.89 s | 139.00 s |
| Gemma | 4.08 s | 156.11 s |
| Qwen27 | 12.71 s | 490.35 s |

Decode rate is total completion tokens divided by summed server-reported prediction time across all twelve requests. It includes any control tokens in that counter and excludes prompt processing. It is not Evo SDK-retokenized visible-token speed, end-to-end throughput, or the earlier synthetic llama-bench measurement. One battery per configuration was run; these rates have no repeated-battery uncertainty estimate.

All layers were offloaded: Qwen35 41/41, Gemma 31/31, Qwen27 66/66. All used context 65,536, F16 K/V cache, flash attention, one slot, seed42, reasoning off and MTP off. Per-request sampling was temperature0, top-p1, top-k40, min-p0 and repeat penalty1. Server defaults in `server-properties.json` may differ from those request overrides; `observed-request-settings.json` retains observed slot settings. Full layer offload does not mean zero CPU/host-memory use.

The original 17 fixture hashes and all 36 exact payloads were verified. Model hashes were checked before each load. [summary.csv](summary.csv) contains per-request performance, completion status and word counts. Model subdirectories contain requests, raw streams, outputs, weight manifests, configuration evidence and source adjudication. Verbose server logs remain local because they include machine paths; sanitized properties and offload evidence are published.

Runner: [run_arc.py](../../../scripts/history_v2/run_arc.py). It requires the three existing GGUF files and corresponding metadata manifests under `work/`, and the b10852 SYCL runtime under `work/llama-sycl/`; it does not download models. The unmodified portable Evo runner and frozen fixtures remain in their original directories. On Windows, clone with `git -c core.autocrlf=false clone ...` to preserve frozen fixture bytes.

For this workload, Qwen35 offers the highest speed and ties Qwen27 on the Evo-aligned content count. Qwen27 supplies more complete details under the stricter review, but misses the earlier 40 tokens/s preference. All three need source checks for summaries. A broader source-diverse evaluation is needed before drawing a general quality ranking.
