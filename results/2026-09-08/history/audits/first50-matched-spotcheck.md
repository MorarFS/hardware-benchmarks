# Matched first 50-page spot-check

All three outputs summarize physical PDF pages 1–50 of Charles Oman’s *The Byzantine Empire*. Qwen and Gemma received that group directly. Flash used three source subchunks, then synthesized them. This comparison assesses the resulting summaries, including that extra synthesis step.

This is a targeted source check, not an exhaustive first-section audit or full-book ranking.

| Matched issue | Qwen3.6, reasoning off | Gemma4, reasoning off | Flash, reasoning off |
|---|---|---|---|
| Violence and Gothic raids, PDF 36 | Incorrectly assigns near-extermination of the Megarian population to Gothic raids. | Mentions Goths and usurping emperors without that conflation. | Mentions Gothic incursions without that conflation. |
| Capital selection, PDF 42–43 | Gives the practical location rationale. | Gives the practical location rationale. | Incorrectly says selection remains incomplete, then describes the completed selection. |
| Nicomedia and personal memory, PDF 43 | Omits this detail. | Omits this detail. | Reverses whose memory would overshadow whose. |
| Legendary boundary marking, PDF 44 | Presents seven-hill boundary marking without the source’s legend qualification; cites PDF 43. | Mentions the separately supported solemn processions. | Explicitly identifies the spear-tracing account as a later legend. |
| Episcopal independence, PDF 47–48 | Omits this detail. | Attributes constrained independence to the imperial palace’s proximity. | Adds a deliberate intention to control religious authority, beyond the stated consequence. |
| Excerpt ending, PDF 50 | Notes that the supplied excerpt does not cover later imperial history. | Notes the partial excerpt’s unresolved wider history. | Its PDF 43 gap warning survives after the relevant continuation arrives. |

## Decisive source checks

**Qwen conflates perpetrators.** PDF 36 distinguishes Gothic damage to Black Sea commerce from Gallienus’s soldiers’ sack in 263. Oman qualifies the reported extermination with “it is said.” Qwen assigns near-extermination to Gothic raids and drops that qualification.

**Flash preserves a stale boundary warning.** Its accepted synthesis says the capital selection remains incomplete at PDF 43. That page explicitly explains the choice of Byzantium. The synthesis immediately supplies those explanations itself. A limitation appropriate to the earlier subchunk ending at PDF 42 becomes false after merging pages 43–50.

**Flash reverses the Nicomedia explanation.** The source says Constantine feared his own memory would be eclipsed by Diocletian’s. Flash says Constantine wished to avoid eclipsing Diocletian’s memory. This changes the stated motive.

**Flash overstates intention.** PDF 48 connects palace proximity with constrained patriarchal independence. Flash recasts this as evidence of Constantine’s desire to control religious authority. The cited passage supports a consequence, not that explicit intention.

## Fairness qualifications

Qwen’s and Gemma’s warnings about later history are legitimate for this partial excerpt. They become errors only if repeated as claims about the complete supplied book.

Flash’s publication sentence also overreaches. Copyright does not confirm publication dates for both editions. However, the extracted title-page text omits the visually legible 1908 imprint. The inspected request records and benchmark script contain no 1908 date. Flash should not be accused of ignoring a date it was not supplied.

Flash’s description of Oman as dismissing Byzantine luxury stories is slightly too strong. PDF 33 says those stories were probably hostile neighbors’ scandals. This loses qualification, but does not invent Oman’s skepticism.

Gemma handles these sampled passages most faithfully. That finding does not establish full-book fidelity. Its separate completed-book audit already identifies serious causal and coverage errors.

## Speed context

First-section direct generation rates were approximately 59.62 tokens/s for Qwen and 38.67 for Gemma. Flash’s completed source outputs ranged around 22.16–22.66 tokens/s; its accepted synthesis reached 23.73. These are generation rates, not end-to-end reading speed. Flash also incurred extra subchunk, synthesis, and retry work.

No model earns a combined pass from this spot-check. The same configuration must meet both the speed threshold and the full research-fidelity requirement.

## Saved evidence

Remote root: `<BENCHMARK_ROOT>`.

Source: `source/pages.json`, especially PDF 11–14, 36, and 42–50.

Outputs: `runs/evo-qwen36/book-chunk01-part01.md`; `runs/evo-gemma26/book-chunk01-part01.md`; `runs/evo-flash/book-chunk01-summary-completion-retry.md`.

Book: [Internet Archive scan](https://archive.org/details/byzantineempire00omanrich).
