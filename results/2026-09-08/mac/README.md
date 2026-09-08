# Apple M5 Pro: speed and source fidelity

The campaign contains 16 selected artifacts. Repeated synthetic speed is collected for 16; frozen-source outputs are adjudicated for 15. A partial battery or context exclusion remains explicit. The [main Mac report](../../../MAC-M5-PRO.md) records the verified 48 GiB computer, runtime, capacity findings and reproduction commands.

## Joint view of separate measurements

Visible-phase speed retokenizes the actual held-out outputs and uses the original stream intervals. Request-wall rate includes prompt processing but excludes server startup, preflight tokenization calls and pauses between requests. These are separate from synthetic generation, whose five-sample means and standard deviations are in the [matched speed table](matched-speed-comparison.md). Extraction includes four absent-answer questions within 20; partial answers receive no numeric credit. Full-source coverage measures represented source topics, not their correctness.

| Artifact | Synthetic generation depth 0 / 2048, tokens/s | Visible phase tokens/s | Tokens / request wall second | Extraction: correct / partial / other, out of 20 | Full source: covered / partial / omitted, out of 16 |
| --- | --- | ---: | ---: | --- | --- |
| qwen3-8b | 45.43 / 42.71 | 38.79 | 26.51 | 18 / 1 / 1 | 3 / 9 / 4 |
| nemotron-49b | 8.69 / 8.89 | 7.34 | 5.10 | 17 / 2 / 1 | 2 / 9 / 5 |
| gemma4-26b | 54.74 / 47.21 | 49.94 | 33.47 | 18 / 2 / 0 | 4 / 5 / 7 |
| qwen36-35b | 47.92 / 48.35 | 46.94 | 33.75 | 18 / 2 / 0 | 3 / 10 / 3 |
| qwen38-27b | 14.64 / 14.27 | 14.13 | 10.28 | 19 / 1 / 0 | 4 / 2 / 10 |
| qwen35-122b-iq2xxs | 31.05 / 30.90 | 29.98 | 19.03 | 17 / 2 / 1 | 5 / 3 / 8 |
| falcon180b-chat-iq1s | 3.08 / 3.59 at 1792* | — | — | Context exclusion | Context exclusion |
| evo-gemma26 | 63.63 / 60.19 | 57.52 | 39.57 | 17 / 3 / 0 | 3 / 4 / 9 |
| evo-qwen35-mtp-off | 62.82 / 61.57 | 58.36 | 41.69 | 18 / 2 / 0 | 6 / 7 / 3 |
| evo-gemma31 | 13.64 / 12.74 | 12.48 | 8.05 | 19 / 0 / 1 | 4 / 4 / 8 |
| evo-qwen38-27b | 14.56 / 14.39 | 14.25 | 10.34 | 18 / 2 / 0 | 4 / 5 / 7 |
| evo-qwen35-community | 68.64 / 68.70 | 70.26 | 46.81 | 18 / 2 / 0 | 5 / 9 / 2 |
| evo-gemma12-qat | 36.04 / 34.04 | 32.00 | 21.85 | 19 / 1 / 0 | 2 / 5 / 9 |
| evo-ministral14 | 25.26 / 24.22 | 28.36 | 21.20 | 18 / 1 / 1 | 1 / 11 / 4 |
| evo-gemma12-coding | 31.39 / 29.74 | 24.44 | 15.63 | 17 / 1 / 2 | 3 / 5 / 8 |
| evo-gemma2-9b | 40.67 / 34.64 | 34.85 | 26.33 | 18 / 1 / 1 | Not submitted |

*Falcon’s longer depth is 1792 within its supported 2048-token context. Gemma2’s full-source control was not submitted because the complete prompt plus output allowance exceeds 8,192 tokens. Its other 11 requests completed. Missing coverage is not scored as 16 omissions. The separate delayed Gemma26 speed repeat remains in the speed table without pooling.

The target is **above 40 visible generated tokens/sec**, with source fidelity assessed separately. A rate above 40 does not remove contradictions, unsupported additions, citation errors, lost qualifications or summary omissions. The [accuracy report](accuracy/README.md) includes these distinctions, exact counts, word limits, waiting times and per-request timing. Judgments are **Codex (GPT-6), AI-assisted source review without independent human adjudication**, against the supplied Oman OCR rather than modern historical truth.

## Evidence and reproduction

- [Matched synthetic speed, including Evo/Arc/laptop rows](matched-speed-comparison.md) and [raw Mac summary CSV](summary.csv).
- [Accuracy report](accuracy/README.md), [per-artifact states](accuracy/scoreboard.md), exact requests, streams, outputs and source ledgers in each model directory.
- [Artifact hashes, bytes and parameter counts](model-inventory.md).
- [Observed memory, offload and failed configurations](memory-summary.md); [capacity candidate inventory](capacity-candidates.json).
- [Frozen Mac delivery and grading protocol](../../../experiments/history-v2-mac/README.md).

![Measured synthetic speed and source fidelity](speed-and-accuracy.png)

The four-panel chart keeps speed, extraction and coverage separate. Raw evidence is immutable during collection; report tables can be regenerated with `python3 scripts/report-mac.py`, and the chart with `python3 scripts/plot-mac.py` using Matplotlib. See the main report for acquisition, generation, validation and retokenization commands. Exact weight matches permit matched speed comparisons; differing history settings and grading conventions prevent unadjusted accuracy counts from isolating hardware effects.
