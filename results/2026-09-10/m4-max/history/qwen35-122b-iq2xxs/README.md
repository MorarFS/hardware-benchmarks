# Qwen122 IQ2_XXS research-source observations on M4 Max

All 12 frozen requests passed independent payload/stream validation at 32K context, FP16 KV, Metal, greedy seed 42, cache 1024 and reasoning/speculation off. The full-source prompt used 13,916 tokens without truncation. All model downloads had finished naturally before this battery; no transfers were paused.

Ten held-out requests produced 4,574 visible tokens in 260.107 request-wall seconds: **33.624 visible tokens/s** and **17.585 tokens per request-wall second**. Peak sampled RSS was 40.108 GB (37.35 GiB), with system swap zero. The short synthetic suite reached 42.248 tokens/s at depth zero and 41.683 at depth 2,048; those rates do not predict sustained source-workload performance.

## Source fidelity

Codex-assisted review found **17 correct extraction answers, two partial and one unsupported**. All four truly source-absent answers abstained correctly. H3-Q3 omits the sons forcing Romanus to abdicate; H4-Q2 omits claimant kinship. H2-Q1 gives the correct monk, date and death, but adds a crowd as killer where the supplied account only describes an angry scuffle. This category records the added unsupported agency, rather than treating the core event as absent.

The full-source control represents **4 compound units completely, 2 partially and omits 10**. The entire literary-emperors excerpt is absent. It wrongly makes Ad Salices decisive, contradicting its own correct extraction answer; changes a lower bound of 200,000 fighting men plus families into nearly 200,000 Visigoths; overstates complete Latin disappearance and army annihilation; and adds a claim of inevitable fate. Coverage records representation separately from truth, so the falsely described Ad Salices outcome remains in the claim ledger even though that episode is represented.

The merged synthesis exactly concatenates all four direct summaries after whitespace normalization. It repeats the direct Latin chronology and disappearance errors, lost qualifications, Valens’s unsupported expectation, and H4’s reported-vision/exclusive-cause distortion, ruined-wall assertion and unsupported Florence arrival date. Unlike the older M5 output, it adds no spurious H3 page 169 citations: all current H3 direct and merged prose has no citations. Current outputs and changed passages were reviewed rather than inheriting old flags indiscriminately.

`adjudication.json` preserves 20 extraction rows, 48 coverage judgments and 174 grouped claim annotations. Thirteen factual/qualification families have 23 manifestations; these are not standardized claim precision. Citation support, ambiguous readings, quotations, coverage and correctness remain separate. No independent human adjudication.

Normalized prose counts are 205, 204, 228 and 259 for H1–H4 against 180–220 requested; merged 896 and full-source 464 against 350–450. The configuration misses the requested 40-token research target on both observed rates.

## Evidence

Requests, exact outputs, observed settings, memory samples and retokenization receipts are retained. Stream events and large offload excerpts are losslessly gzip-compressed for GitHub; decompress before running the existing collector/retokenizer. Model weights and private runtime logs remain local.
