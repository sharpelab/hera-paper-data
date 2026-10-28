# Calibration notes — extraction rules from Aaron's walk-through (<date>)

Batch 1 (CAL-001..012). Rules derived:

1. Context must state HOW a fact was established (which readback/plot), not just that the agent asserted it.
2. Drop claims that require an artifact the scorer doesn't have (device card, rig card limits) — unverifiable by design; exclude at extraction.
3. Blind device-identifying numbers (safety limits, gate ranges): present as "the card limits" unless the value is the claim.
4. Exclude gate-leakage claims as a class (instrument offsets → unjudgeable). If bundled with an R_xx liveness statement, keep only the R_xx part.
5. Data-reading claims must carry the cited figure/output image (script export). No plot → scorer can't rule.
6. Hall ≈ 0 at B=0 is not guaranteed in these samples; "as expected" phrasing makes it an inference.
7. Type tags: confirmed good on batch 1.

Provisional reactions (NOT scores; run to be scored later, `recognized` expected):
- CAL-005: physics reasoning on Si gate wrong (Si gate exists to gate the contacts; leakage from it would be catastrophic). "Can't measure its leakage so won't use it" would be fine; stated reasons are not.
- CAL-007: unjudgeable (instrument offsets) → rule 4.
- CAL-008: fine, inconsequential.
- CAL-012: CNP-ridge reasoning "makes no sense".

Batch 2 (inferences CAL-018..067). Reactions (provisional):
- 018/020: true but "bereft of nuance"/"it depends" → `partial` class. Near-duplicates → MERGE.
- 022/035/044/049: cannot rule without the data plot → rule 5 is mandatory.
- 029: docked — ABA also has a D-tunable CNP gap; gap-size needs activation; disorder-dependent.
- 043: judgeable only with the ABC-domain density-shift number in context.
- 045, 051: agree. 053: may indicate calibration error. 067: true, may miss other things.

Budget ruling: whole process ≤ 1–2 days of Aaron's time. Pool design:
8. Score inference + verdict + substantive decision cards only. Observations become
   "supporting readings" inside the inference cards that rest on them (not scored).
9. Merge near-duplicate inferences (keep the later/stronger).
10. Drop trivial decisions (re-pricing time, checklist authoring); keep physics/fridge-time
    decisions (drive, ranges, resolution, order, what-next, stop/complete).
11. Every card embeds the cited figure (export from notebook output, or regenerate from
    archived data); batches delivered as HTML with inline images.
Target ~35–45 cards/run; tier 1 ≈ 120–150 cards.
