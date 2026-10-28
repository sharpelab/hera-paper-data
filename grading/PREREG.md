# Tier-1 scoring — preregistration record

**Locked before any card was scored.** Rubric text: `hera-paper` `notes/quality-rubric.md` @ `a205ab8`. Pool, maps and scripts: this repo @ tag `t1-scoring-locked`. Wiki mirror: *HERA — Run quality rubric*.

## What is scored

151 cards / 561 items from 6 tier-1 archives (keys T1A–T1F, sealed in `blind-map.yaml`): 90 inference, 54 decision, 7 verdict. Aaron scores every item blind (correct / partial / wrong / unverifiable); card value = mean of items; S_claim per run = weighted mean of card values (verdict 2, else 1). Item-level and per-type accuracy reported alongside.

## What was stripped, and where the record lives

Starting from 215 extracted claims (116 inference, 74 decision, 16 observation, 9 verdict; `raw/<KEY>.claims.jsonl`):

1. **Excluded at extraction, never emitted** (v2 prompt, `extract-prompt.md`): gate-leakage claims (instrument offsets make them unjudgeable); claims whose only check is the device/rig card; time re-pricing, checklist authoring, cost boilerplate. Not counted; the v1 calibration run (`raw/CAL.claims.jsonl` vs `raw/CAL2.exclude.json`) shows what this filter removes on one run.
2. **Observations (16): extracted, not scored.** Folded into the inference cards that cite the same read cell as "supporting readings". Ruling from the calibration walk-through: reads are graded through the inferences they feed. The taxonomy row exists for extraction only; Methods should state this.
3. **Recipe-default decisions (5)** — `raw/<KEY>.exclude.json`, reason per id.
4. **Merges (28)** — fork→resolution and near-duplicate folds, `raw/<KEY>.merges.json`; the folded claim appears in its target card as context and is not scored separately.
5. **Instrument/tooling decisions (15)** — hidden from the page after the consequential-only filter (`raw/T1.decision-exclude.json`, reason per id; two of the pass's 17 proposals, T1-062 and T1-086, restored by Aaron). Logged as rig-card gaps in `corpus-gaps.md`. Ids remain in the sealed map; ingest excludes them.
6. **Identifier scrubbing** — device names, dates, session names, corpus hashes, people's names removed from claim/context/evidence/verbatim (`SCRUB` in `hera_cards.py`); contact labels and sweep ordinals retained. Figures are the agent's own notebook outputs or regenerated from archived data (`hera_plot.py`).

Arithmetic: 215 − 5 − 28 − 16 = 166 pooled → 151 visible after (5).

## Calibration

Extraction rules were calibrated on one undisclosed run outside tier 1 (`CAL`, `CAL2`), not in tier 1; rulings in `calibration-notes.md`. That run is not scored.

## Known departures from blinding

Aaron saw a screenshot from Zack listing which archive is which arm before scoring began; the per-card `recognized` flag records how often a card was identifiable. Reported, not corrected.

Pass B (the collaborator debrief, `passb/`) is device-unblinded by construction: the scorer recognized the device from the gatemap in every run (`know_adjudicated = yes` on all six exports; `know_text` records it). Arm identity within the vti-02 series is not stated in the knowledge text. Reported, not corrected.

## Process changes after the first lock

`f8d0c41` (hide 15 decisions), `b5c10d3` (per-item scoring) — both before any score existed. Anything after `t1-scoring-locked` is a visible diff.

## Second rater, Pass A subset (Sandesh) — pre-registration

**Locked before delivery of the pages to the rater.** Sample, page, script, and this text at tag `passa-sandesh-locked`.

1. **Sample.** 56 cards / 212 items from the tier-1 pool: every visible verdict card, plus 30 % (ceiling) of the inference and decision cards from each of the six runs, drawn with seed 20260904 and shuffled fresh (`hera_subset.py`). Ids in `raters/sandesh/manifest.json`. Pooled ids are preserved; the rater's scores join the scores of record card for card. The sample does not change after delivery.
2. **Instrument.** Identical to Pass A: rubric `a205ab8`, the same page mechanics, the same four item verdicts, the standard of correctness printed on the page. Six practice cards from the burned calibration run precede it and are not data. The rater scores every item alone; any model assistance is logistics only, and the rater attests to this on return.
3. **Knowledge state.** Logged verbatim before the first card (`raters/sandesh/knowledge.md`), plus the per-card `recognized` flag. Reported, not corrected.
4. **Scores of record.** Aaron's Pass A scores remain the scores of record for every reported quantity. The second rater's scores are never averaged into them, never used to revise them, and never substitute for any run's S_claim.
5. **Main-text quantities, exactly two.** On items both raters scored correct / partial / wrong (items either rater marked unverifiable are excluded and the count stated): (a) exact agreement, the fraction of items given the same verdict; (b) quadratic-weighted Cohen's κ on item values 1 / 0.5 / 0. One sentence in the paper, both numbers, whatever they are. No adjective labels for κ.
6. **Grading supplement, content floor.** The supplement includes at least: agreement and κ by claim type and by run; card-level κ on card values; S_claim per run recomputed from each rater's items on the subset, with one yes/no test — does every corpus arm outscore every no-corpus arm under the second rater; disagreement characterized from the notes, both raters quoted. Format is not constrained.
7. **No post-hoc exclusion.** The result is reported whatever it is. The only pre-stated departures: incomplete scoring is reported on the items scored with the fraction stated; contamination the rater discloses (having seen or discussed the scores of record) is reported as a departure, and the numbers are still reported.
8. **Computation.** `hera_agree.py`, committed at the lock tag, computes 5 and 6 from `scores/T1.scores.json` and `raters/sandesh/T1.sandesh.scores.json`. Nothing in the analysis is decided after the export arrives.
9. **Sealed predictions.** Two, in a file outside the repo, committed here as its hash — `sha256 a32810d693a6dc1089c71d8620fe278f18e863d7f4a7f69cfd7d23fad3402bcc` — revealed after the export is committed.

**Jordan (Pass B second rater) is not covered by this section.** His pass was pre-registered only as scope, order, and knowledge state (`passb/ANALYSIS-PLAN.md` decision (a); `passb/RATER-JORDAN.md`); no agreement metric or reporting rule preceded his data. His result is recorded post hoc in `passb/RATER-JORDAN-RESULT.md`, labeled as such, under the same rule 4: reported beside the expert's, never averaged.
