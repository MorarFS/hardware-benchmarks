# Flash reasoning-off review

The tested Flash configuration fails the speed threshold and does not complete the full-book workflow. Completed source requests generated 22.16–23.36 tokens/s. Its accepted first-group synthesis generated 23.73 tokens/s. No completed-final fidelity score is assigned.

The model completed source notes for physical PDF pages 1–100. It also completed the first 50-page group synthesis. The second group synthesis failed after bounded retries, so pages 101–396 were not processed in this workflow.

## What failed

The initial second-group source request repeatedly hit its output ceiling. An adaptive repair reserved more output room and divided later source groups into smaller batches. That repair completed all second-group source notes.

The subsequent reduction received about 5,300 input tokens in an 8,192-token context. It hit output limits of 1,100, 2,200, and 2,200 tokens. The last retry also requested a shorter finished response. It still reached the ceiling, and the service recorded a bounded completion failure at 05:08 UTC.

This was an output-completion failure under the tested prompts, partitioning, and context. It was not an observed hardware crash or proof that no other Flash configuration could work. Larger full-GPU context requests had been blocked by the loader’s memory guardrail; partial offload at a larger context was not benchmarked.

## Source fidelity

The completed first-group synthesis contains two clear errors. It preserves a stale statement that capital selection remains incomplete, although the continuation explicitly explains the selection. It also reverses whose memory would overshadow whose in the Nicomedia discussion. These findings do not establish a full-book ranking.

The copyright sentence overstates what a copyright notice proves. However, the extracted title-page text omitted the visually legible 1908 imprint. The model is not penalized for ignoring an unsupplied date.

[Matched first-section source check](first50-matched-spotcheck.md)

## Measured cost

Twenty book-related requests generated 24,991 tokens in 1,347.73 seconds of request wall time. Eleven reached their output ceilings. The sum of book-phase wall times was 1,468.22 seconds, including loads, token preflight, and intermediate writes. These are costs of an incomplete workflow, not a completed-book turnaround time.
