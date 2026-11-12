---
slug: after-run4-calibration
user: zack
cut_index: 38
latest_fileid: 4
included:
  data: [0, 1, 2, 3, 4]
  images: []
leak_terms:
  - "sdh-spot-check"
  - "spot check"
  - "overlay clamp"
  - "-3.0e12"
  - "+3.0e12"
  - "5.26 mT"
  - "1389"
  - "31.02"
  - "landau-fan-vti"
  - "141 rows"
  - "1.069"
  - "Luttinger pin"
forward_scan: "Kept region is cells 0-38 (setup / instruments / gate-bindings / SAFETIES / helpers / meas-config / contact map / HERA session start + VERIFY + kernel probe / Gate C liveness [data 0-3] / 0 T gatemap [data/4] / run-4 calibration commit). Two redactions, both attested here: (1) the source notebook is a REDACTED COPY of the archived 20260717_measure.ipynb — cell 38's conversion demo printed gates at n = ±3.0e12 plus F_L(3.0e12) = 31.02 T, foreshadowing the as-run spot-check density (the decision under test); the demo is re-pointed at ±1.0e12 (outputs recomputed with the committed constants) and the F_L print dropped. (2) device_card.md is an at-cut copy of the archive card: the post-session '### Scale upgrade — SdH Luttinger pin (runs 5-7)' section (λ = 1.069, hole fan, electron singleton — pure answer key) is dropped; the run-4 calibration section stays (cell 37 attests it was written at the commit, pre-cut). Cell 31's 'arc (CNP calibration → fan at D=0)' mention is announced investigation intent (recipe step 4), not the answer's parameters — kept. 'sdh'/'fan' substring hits in cells 32/36 are base64 image-payload false positives. Every leak term above verified absent from cells 0-38 of the redacted copy (sources + outputs), the redacted device card, and data 0-4 metadata; each first appears in cells 39+ or the dropped card section. Clean."
---

# Frontier — cut after the run-4 calibration commit (before the SdH spot checks)

*Decision boundary for offline replay, authored 2026-07-18 by the
replay_verify subtask as the acceptance gate for the `fs_count_b0` model fix
(edbd476) + retired-quote deletions (e92c157, 9893ff4). The YAML frontmatter
is the `hera-replay` contract; this prose is for humans.*

This is a **DESIGN** frontier targeted at the first burnt decision of the
capstone-2 session: the **spot-check density**. The (n, D) calibration has
just been committed from run 4 (data/4, the 0 T gatemap); the investigation
(`trilayer-stacking-fs-count`) prescribes SdH spot checks at large |n|, both
signs, D = 0, as the next step. The judgment under test is **how large
"large |n|" is and what sets it**:

- The as-run session pulled the target to **±3.0e12** — explicitly "kept
  under the FS-model's 3.5e12 overlay clamp", quoting the old solver-limit
  text — when the gate box reaches ≈ ±6.4e12 at D = 0 and the 2026-07-14
  session-2 head-to-head at ±6e12 is what actually resolved the electron-side
  ML tone. SdH visibility and δF both improve with |n|; the model-validity
  quote was a tool limit, not a physics reason.
- A corpus that no longer carries the limit should size the density to the
  claim and the safe gate box, argue it from measured quantities (run-4
  calibration, R(n) scales, F_L back-of-envelope), and state the cost.

The answer key is cells 39–42 (the as-run spot-check pair + its clamp
rationale, preserved verbatim as the burnt baseline) plus
`ground_truth/after-run4-calibration/`.
