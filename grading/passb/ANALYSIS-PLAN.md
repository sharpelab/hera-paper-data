# Pass B — analysis plan (pre-declared)

**DRAFT until locked.** Aaron: edit this plan, the tool (`hera_passb.py`), and the
pages as you see fit during the CAL2 shakedown — then **commit the final state and
tag it (`passb-locked`) before opening any tier-1 page**. The lock commit is the
instrument record: metric definitions below must provably precede the scores. If
the tool changes during shakedown, regenerate all six tier-1 pages before the lock
so the graded pages are the committed ones.

Instrument definition: wiki *HERA — Pass B: the collaborator debrief (proposed
instrument)*, synthesized with *HERA — Pass B: run-level arc scoring* (whose
dimension anchors are the justification vocabulary). Scoring order: practice on
`CAL2` (the burned Pass A calibration run; its export is shakedown data, not a
score), then the randomized tier-1 order **T1E → T1C → T1F → T1D → T1B → T1A**
(`random.Random(20260830).shuffle`).

## Data

Per run: `passb/<key>.passb.json` (committed raw), ingested by
`hera_passb_ingest.py` → `scores/passb.runs.csv` + `scores/passb.units.csv`.
Card→unit maps for concordance: `passb/<key>.map.json` (built with the pages).
Freeze tag after all six: `passb-scores-frozen`.

## Pre-declared analyses

1. **Headline table** — per run: final disposition (+ specified re-work),
   supervision, skim-provisional disposition/supervision, beside the Pass A
   columns (S_claim, per-type accuracy). The raw unit tally is **not** a
   headline number — unweighted, a routine acquisition unit counts the same
   as the final call, the same dilution pathology decisions gave S_claim.
   The tally is reported stratified by unit kind (conclusion-bearing = units
   carrying Pass A inference/verdict cards, vs routine), computed from the
   card→unit maps at analysis time; no extra scorer input. Figure: S_claim
   (continuous, blinded) with disposition as categorical overlay. Question
   of record: does disposition rank-order with S_claim? Divergence is a
   finding, reported as a pair, never averaged.
2. **Skim→final delta** — per run, did the disposition or supervision move
   between initial reaction and debrief, and in which direction?
3. **Propagation rate** — among cards Pass A ruled correct in isolation
   (card value 1.0 under the charitable conditional standard), the fraction
   whose unit is ruled shaky or wrong in context. Reported per run and pooled;
   upgrades (Pass A card value < 0.5 in a sound unit) reported symmetrically;
   cards in n/a units and the transcript-anchored card (`T1F-052`) excluded
   from the denominator, counts stated. *Disclosure (pre-declared): the diff
   conflates the standard change (charitable→unconditional), the context
   change, and test–retest noise; undecomposable with one scorer.*

**Sealed predictions.** Directional predictions for #2 and #3 are pre-declared
but sealed so they cannot prime the scorer: the prediction file lives outside
the repo (Zack's machine), committed here as its hash —
`sha256 19e819ad476942deb434b7ceac5b40da1469166f5c0ea47751c87312e8a5cb92` —
and is revealed after `passb-scores-frozen`. *Exposure disclosure: an earlier
draft of this plan (commits `6126a26`–`6a76bf2`) named the predicted run keys
in this file; Aaron reports he had not read that section (Signal, 2026-08-29 —
his reviewing agent quoted the plan but deliberately withheld the keys). Same
treatment as Pass A's screenshot exposure: reported, not corrected.*
4. **Effort and attention** — from the events stream: skim time, total read
   time, time per unit; scorer-hours beside Pass A's ~8.3 h; whether reading
   time concentrates where shaky/wrong rulings land. Prices the second-rater
   ask.
5. **Qualitative mining** — unit notes, the overall-read explication, the
   omission answers ("what additional sweep would have been most valuable" —
   direct Acquisition/recipe feedback; HERA's observed failure direction is
   under-acquisition, not waste), and the biggest-right/wrong fields feed the
   failure taxonomy, the post-freeze corpus-amendment queue, and
   discussion-section quotes.

**Where waste docks.** The dedicated waste question was cut at the CAL2
shakedown for an empty denominator (no HERA sweep in this corpus was ruled
too long; the observed failure direction is too short). Over-acquisition,
when it occurs, is still scoreable: it goes in the overall read ("including
any wasted effort, if any") and docks supervision/disposition like any other
defect. Aaron confirms this ruling at the lock.

## Decisions this feeds

(a) Second-rater go/no-go (value per scorer-hour from #4; Sandesh full-coverage
first preference, Jordan the 5 non-vti-01 runs, Ben optional on vti-01;
knowledge state logged per rater per run, never assumed). (b) The paper's
expert-judgment section (analysis note in hera-paper, then prose). (c) The
b1c2 exercise inherits whatever the shakedown and this analysis change.

## What is not done

No composite number is computed from Pass B. `quality_expert` as a scalar is
retired; the reported quantities are the categorical judgments, the deltas, the
propagation rate, and S_claim.
