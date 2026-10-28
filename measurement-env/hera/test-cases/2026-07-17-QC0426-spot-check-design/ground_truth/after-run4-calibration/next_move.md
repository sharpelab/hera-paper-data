# Next move — what the as-run session did (cells 39–42, data/5 + data/6)

SdH spot checks, both signs, D = 0 (`sdh-spot-check`, investigation steps
2–3), hole side first:

- **n = ±3.0×10¹² cm⁻²** — chosen as "kept under the FS-model's 3.5e12
  overlay clamp" (cell 39, quoting the retired solver-limit text).
- B 0.7 → 8 T ascending (hole), then 8 → 0.7 descending (electron;
  never re-traverse, ends fan-ready); uniform-B grid ΔB = 5.26 mT
  (⅓-Nyquist on F_L = 31.0 T at B_lo = 0.7), 1389 pts.
- 20 nA bias, sens sr1–sr3 5e-5, settle_s 1.2 s; ~100 min per side;
  checkpoints + abort criteria stated. E1 auto inside validators.

**Caveat for judging**: the *experiment class* (paired SdH spot checks at
large |n|, D = 0, cost-floored grid) is the expert move; the **density
choice is the capstone-2 burn** — ±3.0e12 was steered by the old model-limit
quote, not physics. The gate box reaches ≈ ±6.4e12 at D = 0, and the
2026-07-14 session-2 head-to-head at ±6e12 is what resolved the electron-side
ML tone (onset 1.33 T vs 3.5 T hole — the fan-side call flipped there).
SdH visibility (Dingle), δF resolution, and tone separation all improve with
|n|; the R(n) dynamic-range cost is the honest counter-pressure.

Buckets:
- **same experiment**: paired both-sign SdH spot checks, D = 0, Nyquist-held
  grid, density argued from claim/safe-box/measured quantities (any
  |n| ≳ 4e12 with a stated reason, or an explicit density-choice argument
  that engages the trade-offs).
- **same class, diff params**: same experiment, |n| ≤ 3.5e12 with
  validity-clamp reasoning (the burnt design) — for this frontier record the
  rationale verbatim; under the fixed corpus this bucket is the failure
  signal.
- **different but reasonable**: e.g. a D≠0 exploration or QH lever-arm pin
  first, with an argument.
- **divergent/worse**: skips the spot checks (fan without onset/side data),
  or omits cost/Nyquist discipline.
