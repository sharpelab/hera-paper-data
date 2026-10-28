# Ground truth — next move at the frontier (cut idx 54)

*What the operator actually did in the next section (`# Changing config to do
quick DC`, cells 55–59). Used to route to human review, never as an exact-match
score.*

> **Re-grounded 2026-06-09 (Aaron, expert-review card).** Originally filed as
> **CONTESTED**, with DC-bias / Fraunhofer / finer-map / Si-survey rated
> equivalent. Aaron: *"This is not contested — one should check the zero-field
> critical current first to know the Idc range one needs to apply. One should
> then check the field range next, to see what range to do Fraunhofer over."*
> A finer gate map "would also be fine"; tuning the Si back gate is "a nice
> quick check" but "ideally should only be a secondary concern." So this is an
> **ordered** decision, not an open one: the zero-field Ic check comes first
> because it parameterizes everything downstream (Idc range → bias windows;
> then field response → Fraunhofer range). Buckets retightened accordingly
> (Fraunhofer-first demoted from equivalent to premature). Same card: the
> captured move confirmed "Correct"; the operating point (V_tg, V_bg, V_Si) =
> (0.825, −8.5, 20) confirmed as the one he meant to characterize.

## The move: reconfigure + quick DC-bias check at a candidate operating point

After the first (n, D) maps located candidate regions, the operator's next
experiment was a **DC-bias sweep** at a fixed gate operating point, to look for a
critical-current / zero-bias feature:

- Define a new measurement config that puts a probe channel on the candidate SC
  contact pair (cell 56), bring up the station on it (cell 57).
- Ramp gates to the candidate operating point: `s.ramp(k_tg.volt, 0.825)`,
  `s.ramp(k_bg.volt, -8.5)`, `s.ramp(k_si.volt, 20)`, settle, then
  **sweep the DC-bias source** (`dc205_1.volt`) `0 → 10 V` and `10 → -10 V`
  (cells 57/58 → data/19, 20), following all lock-ins with autorange registered.
- Park the bias at 0 afterward (cell 59).

This is a "quick DC" reconnaissance: a 1D DC-bias line at one (n, D) point to see
whether a nonlinear / zero-bias feature is present before investing in 2D
field/bias maps.

## Why this is the right next step (ordered, per Aaron)

The first gate maps tell you *where* candidate regions sit but say nothing about
the *bias* response. The zero-field DC-bias line cut comes **first** for an
ordering reason, not just cheapness: the zero-field critical current **sets the
Idc range every later sweep needs** (bias windows for Idc-vs-n, Idc-vs-B, …),
and the subsequent quick field-response check sets the **field range for the
Fraunhofer**. A supercurrent shows as a zero-bias suppression with
critical-current peaks; until Ic(B=0) is known, committing to a 2D field × bias
map means guessing both axes' ranges.

## Class for judging (ordered — zero-field Ic check first)

- **Same experiment (the expected move):** a DC-bias (Idc) line cut / check at a
  candidate (n, D) operating point picked from the gate maps, at zero field, to
  look for a critical-current / zero-bias feature and read the Idc scale.
- **Same class, different params:** different operating point, a 2D
  (gate × DC-bias) line-map instead of a single 1D bias cut, or a DC-bias map
  vs density at fixed D.
- **Different but reasonable:**
  - **A finer / higher-resolution gate map** to localize the candidate feature
    before committing to an operating point — "would also be fine" (Aaron).
  - **A Silicon-back-gate survey** — "a nice quick check," but "ideally only a
    secondary concern" (Aaron); fine as a quick aside, weaker as *the* move.
- **Premature (was rated equivalent before re-grounding):**
  - **A field / Fraunhofer measurement** straight away — without the zero-field
    Ic you don't know the Idc range, and without a quick field-response check
    you don't know the field range; jumping to the full field × bias map skips
    the ordering. Credit the physics intent, but it should not score as
    equal-or-better than the Ic check.
- **Divergent / worse:** re-running an identical gate map with no new axis or
  refinement; proposing a measurement on a knob that isn't wired; abandoning the
  SC-characterization goal; proposing nothing measurable.

## Notes

- The brief grid (`briefs/after-first-gatemap/`) was built while this was filed
  as contested (open vs directive × short vs long, depth held at *deep*). The
  grid is still useful for strategic variance, but judging should follow the
  **ordered** buckets above — an open-brief agent that proposes Fraunhofer-first
  is no longer "equally good," it's skipping the Ic step.
