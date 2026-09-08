# Gemma errors: evidence and reasoning

These examples concern Gemma 4 26 B with reasoning OFF. They assess fidelity to Oman’s text, not modern historical truth.

## Casualty scope, G-F-033

Model: “This assault killed approximately 35,000 people in the Hippodrome.”

Source, physical PDF 106, printed 80: “It is said that 35,000 men were slain in the six days”.

The model assigns the six-day total to one assault. It also removes the source’s explicit qualification. This is a major scope error.

## Reversed explanation, G-F-038

Model: “Oman interprets this failure as a result of religious and racial tensions.”

The preceding model sentence concerns Belisarius’s conquest failing to endure. Physical PDF 109, printed 83, instead discusses divisions between Germanic rulers and their Roman subjects. Those divisions explain Gothic and Vandal weakness, which aided reconquest. Applying that explanation to reconquest’s failure reverses the causal subject. This is a critical error.

## False missing-source claim, G-F-082

Model: “This synthesis is limited by the absence of information regarding Justinian’s later reign”.

Physical PDF 124, printed 98, opens “THE END OF JUSTINIAN’S REIGN.” The chapter continues through physical PDF 139. It discusses Persia, plague, Belisarius, buildings and law. The summary itself uses several of those passages. Its blanket absence claim is false.

## Withdrawn flag, G-F-085

Model: “It also lacks details on Leo the Isaurian’s administrative reforms”.

Source, physical PDF 220, printed 194: “We should be glad to have the details of Leo’s reforms”.

Oman names broad reforms but laments missing details. The model’s limitation is defensible. This is no longer counted as a material error.

## Ambiguous wording, G-F-040

Model: “Simultaneously, Chosroes of Persia launched an invasion that sacked Antioch”.

Physical PDFs 124–127 place the war’s opening in 540 and the plague in 542. The events overlapped. “Simultaneously” need not assert identical starting dates. This flag is withdrawn from material counts.

The revised final audit records 14 material flags across 86 claim units:2 critical,3 major and 9 moderate. Counts include citation and attribution defects, not only false historical facts. Repeated manifestations must not be treated as independent mistakes.

[Complete ledger](gemma-final-claims.csv) · [Revision history](audit-revisions.json)
