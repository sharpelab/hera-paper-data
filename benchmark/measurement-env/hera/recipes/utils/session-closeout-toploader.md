# Session close-out — toploader variant

**Base**: `utils/session-closeout.md`. This file carries only the deltas
(STYLE rule 13); read the base first.

**Overridden decisions and the rig facts that force them:**

- **Heaters off (base decision 4)** — open-loop sample heater: a plain
  `(heater.volt, 0.0)` in `heaters=`. No equilibration holds on descent —
  holds are ascent-only; the `volt.step` pacing covers the
  dilution-circuit perturbation the stepping guards against (rig card,
  Thermometry; Aaron, 2026-07-20).

## Obsolescence

Delete when the base goes instrument-class-conditional on open- vs
closed-loop heater shutdown — the remaining content is card-resolved.
