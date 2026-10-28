# Session close-out — VTI variant

**Base**: `utils/session-closeout.md`. This file carries only the
deltas (STYLE rule 13); read the base first.

**Overridden decisions and the rig facts that force them:**

- **Heaters off (base decision 4)** — closed-loop LS335: pass the labeled
  callable `("LS335 ranges off", lambda: heater.off("both"))`; the
  readback's `T_sample` line confirms nothing is lifting.
- **Si gate park** — through the ramped parameter (`k_si` /
  `smart_voltage`): the driver paces the set at `ramp_rate` (Si
  dielectric pacing) and its get reads back `VOLT?`, so it belongs in
  `gates=` like any other gate. Never park via raw `voltage`.
- **Persistent switch / output** — operator-only (rig card, Magnet);
  close-out never touches them.

## Obsolescence

Delete when the base goes instrument-class-conditional on closed-loop vs
open-loop heater shutdown and managed-mux presence — the remaining deltas
are already card-resolved.
