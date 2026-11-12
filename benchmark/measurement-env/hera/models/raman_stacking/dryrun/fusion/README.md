# Mechanics dry run — stacking-raman-transport-fusion on a synthetic device (2026-07-17)

First execution record of
`recipes/investigations/stacking-raman-transport-fusion.md`. A fresh agent
received the recipe plus a synthetic fixture (`device.md`,
`transport_contract.md`, `raman_contract.md` — fictional device Y, designed
to exercise all four mechanism classes) and nothing else.

Result (`result.md` + `registration.png`): all four classes correctly
assigned — ch_A concordant, ch_B reconciled-by-conversion (named risky
step), ch_C unreconciled fork (directionality rule enforced; ABA→ABC never
invoked), ch_D uncovered with no interpolation; per-device headline
correctly refused; all four Verify audits executed. The registration
stress test additionally caught an unplanned fixture feature — ch_C's
boundary 1.0 µm from the map edge, inside the ±1.5 µm registration
uncertainty — and handled it per the recipe (coverage registration-limited,
mechanism class retained with reasoning).

No recipe amendments came out of this run. The fixture is re-runnable
as-is for regression after any recipe edit.
