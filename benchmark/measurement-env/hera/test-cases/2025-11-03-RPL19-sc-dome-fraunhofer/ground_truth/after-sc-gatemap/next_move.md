# Ground truth — next move at the frontier (cut idx 83)

*What Aaron actually did in the next section (`# Fraunhofer`, cells 84–102 →
`data/146–158`). This is **one** expert path, not **the** answer — used to route
the replay to human review, never as an exact-match score. See benchmark-plan.md
"Imitation is a screen, not a score." This frontier is **CONTESTED**: several
moves below are legitimate; the buckets reflect that.*

> **Expert-confirmed 2026-06-09 (Aaron, review card).** The captured next move
> (Fraunhofer) is "Correct"; the contested framing stands ("All of these are
> fine"), with the Beff = 0 null re-check "perhaps the most pressing".

## The move: `# Fraunhofer` — Ic vs perpendicular field at the dome optimum

Having mapped the SC dome, Aaron pinned a single operating point at its center
(TG = 0.47 V, BG = −5.2 V, V_Si = −48 V) and characterized the candidate
supercurrent against perpendicular magnetic field:

1. **`## Determine Ic at zero field TG=0.47, BG=-5.2`** (cell 87) —
   `s.sweep(dc205_1.volt, np.linspace(-2.5, 2.5, 101), delay=1.0)` at B = 0
   → **`data/146/`**. A 1D DC-bias (Idc) cut to read the zero-field critical
   current at the fixed dome point. Repeated at B = 8 mT (cells 90/93/95
   → `data/147–149`) to see the field response of Ic by hand first.
2. **`## 2D fraunhofer at TG=0.47V, BG=-5.2V`** (cell 100) —
   `s.megasweep(mag.field, np.linspace(0.015, -0.015, 61), dc205_1.volt,
   np.linspace(-3, 3, 101), fast_delay=1, slow_delay=3)` → **`data/150/`**.
   Slow axis: perpendicular field, +15 mT → −15 mT, 61 points. Fast axis: DC bias
   (dc205), −3→3, 101 points. Gates held at the dome optimum. Then repeated with
   the field swept the other direction (cell 102 → `data/151`) to check
   hysteresis / sweep-direction artifacts.

This is the canonical **Fraunhofer / Ic-vs-B⊥** measurement: map dV/dI (or the
voltage channel) vs (Idc, B⊥) and look for the supercurrent lobe pattern.

## Why this is a good next step

The SC-gatemap section established *that* there is a candidate superconducting
dome and *where* it sits (TG ≈ 0.47, BG ≈ −5.2, V_Si = −48 V). The open question
for an SC campaign is then: **is it actually superconducting, and what is its
junction character?** The decisive discriminator is field response — a true SC
critical current is suppressed by an out-of-plane field, and a
Josephson/proximity-junction geometry shows Fraunhofer-like lobe modulation of
Ic with B. Fixing the operating point at the dome optimum and mapping Ic(B⊥)
both (a) tests the SC nature and (b) reveals junction physics (single-junction
Fraunhofer vs SQUID-like, lobe spacing → junction area).

## Class for judging (CONTESTED frontier — several moves are legitimate)

- **Same experiment:** propose Ic vs perpendicular field at the SC dome optimum —
  a field × DC-bias map (Fraunhofer) or an equivalent Ic(B⊥) extraction. Pinning
  to the dome center first and reading Ic at B = 0 before the 2D map is part of
  the same move (exact field range / step count is parameter-level).
- **Same class, different params:** field dependence by another cut — a 1D
  zero-bias-voltage vs B at fixed Idc, Ic(B) extracted from a different slicing,
  or a coarser/finer field window.
- **Different but reasonable (this frontier is genuinely contested — rate these
  equivalent-or-better on their merits):**
  - **Temperature dependence across / at the dome** — heat the sample and watch
    Ic → 0 at Tc (the other canonical SC confirmation). Aaron in fact did this in
    later cooldowns; it is a defensible *first* interrogation too.
  - **Looking for oscillations** — quantum-oscillation / SC-oscillation structure
    at the dome (a field or density fan), to characterize the underlying state.
  - **Check SC properties at Beff = 0** — find the perpendicular null (here a
    *trapped-flux* null of the AMI430 field, not a rotator angle — it is cooldown-
    and field-history-dependent) and characterize the dome there before committing
    to field work. **Aaron (2026-06-05) rates this the *best* of the valid moves**
    — finding the true null is itself nontrivial given trapped flux, and SC
    properties are cleanest there. (Re-affirmed 2026-06-09: "perhaps the most
    pressing" — all the more so given the dome turned out to be centered at
    finite nominal field; see `reading.md`.)
  - **Finer Idc-vs-n / Idc-vs-(n,D) at the dome** — localize the feature and
    confirm the zero-bias supercurrent signature before field work.
  A reviewer may rate any of these as good-or-better than the Fraunhofer move; do
  not penalize a well-argued choice among them.
- **Divergent / worse:** abandoning SC characterization entirely, re-running an
  already-completed gate map with no new axis, jumping to an unrelated device
  region, or a move that never interrogates the dome it just mapped.

## Notes

- The operating point (TG=0.47, BG=−5.2) is the same dome center the SC-gatemap
  section's `draw_line_through_point((-5.2, 0.47), slope=0.3)` line was built
  around — the agent can recover it from the kept cells (65/79) without leakage.
- Aaron interleaves a `mag.field(0)` park and several base-temperature retries
  (down to 27–41 mK) around the Fraunhofer work; getting the fridge cold is part
  of executing the field test well, not a separate experiment.
