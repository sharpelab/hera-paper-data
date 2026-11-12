---
slug: after-electron-spot-check
user: zack
cut_index: 42
latest_fileid: 6
included:
  data: [0, 1, 2, 3, 4, 5, 6]
  images: []
leak_terms:
  - "landau-fan-vti"
  - "8.33e-3"
  - "141 rows"
  - "-0.5 -> -3.5"
  - "101 col"
  - "temperature-dependence-vti"
  - "LK mass ladder"
  - "field_invB(0.77"
  - "sr1 5e-4"
  - "1.069"
  - "Luttinger pin"
forward_scan: "Kept region is cells 0-42 (setup / instruments / gate-bindings / SAFETIES / helpers / meas-config / contact map / HERA session start + VERIFY + kernel probe / Gate C liveness [data 0-3] / 0 T gatemap [data ~3] / run-4 calibration commit / SdH spot check H hole [data/5] / SdH spot check E electron [data/6]). Cell 41 legitimately carries the run-5 hole read (onset 0.77 T, tone set) and says 'fan-ready' / 'the fan' generically — that a fan comes next is operator knowledge; the answer under test is the run-6 READ (onset semantics on the electron record) and the fan's ACQUISITION DESIGN (side, B_lo, grids, sens), none of which appears pre-cut. Verified by grep: every leak term above is absent from cells 0-42 (sources + outputs) and first appears in cells 43-46. The post-hoc ana notebook and hera_session.md are not part of the fixture copy-set. device_card.md is an at-cut COPY of the archive card (attested 2026-07-18, replay_verify subtask): the archive card's post-session '### Scale upgrade — SdH Luttinger pin (runs 5-7)' section (λ = 1.069, hole fan, run-7, electron singleton — answer key for this cut) is dropped; the run-4 calibration section stays (written at cell 37, pre-cut). The '1.069'/'Luttinger pin' leak terms are the tripwire for that section. Clean."
---

# Frontier — cut after the electron SdH spot check (before the Landau fan)

*Decision boundary for offline replay, authored 2026-07-18 as the acceptance
gate for the `hera.analysis.sdh_onset` rewrite (subtask sdh_onset_fix). The
YAML frontmatter is the `hera-replay` contract; this prose is for humans.*

This is a **READ + DESIGN** frontier targeted at the exact decision the old
extractor burned in the as-run session:

- **The read under test**: data/6 is the electron-side SdH spot check
  (n = +3.0e12, D = 0, B 8→0.7 T, 1387 pts). The as-run session's helper
  returned **onset_b = 3.3–3.9 T — the dominant 33 T tone's SNR edge —**
  while oscillations visibly run from ~1.5 T; the number fed the fan-side
  comparison. The rewritten extractor returns per-tone onsets (headline
  ~1.0–1.9 T with the light-tone tracks exposed). Does the replayed agent,
  using `hera.analysis.sdh_onset` per the recipe, produce a read whose onset
  statement is per-tone-aware rather than heavy-edge-only?
- **The design under test**: `landau-fan` step 1 mandates
  `B_lo = sdh_onset(...).onset_b` ("compute it, do not eyeball it"). The
  as-run session picked the hole side (onset 0.77 T, cell 41) and designed
  0.77→8 T. The replayed agent should land a fan whose `B_lo` is a
  *computed* onset consistent with the measured records, with the side
  choice argued from per-side onset/δF.

The answer key is cells 43–46 (the as-run fan + LK ladder) plus
`ground_truth/after-electron-spot-check/reading.md` (the archived ana read
and the rewritten extractor's numbers on data/5 and data/6).
