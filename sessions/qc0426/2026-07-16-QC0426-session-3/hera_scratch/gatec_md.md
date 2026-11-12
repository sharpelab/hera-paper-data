## HERA — Gate C: liveness + gross-safety (`gate-current-sanity-check`)

First-session branch (no designated references — `reentry-baseline` N/A): sweep each metal gate 0 → each card limit, other gates parked at 0, B = 0, watching gate current at pA resolution (`nplci=10`) and all four lock-ins for contact liveness on the provided configuration (source T2, drain B7/sr0, Rxx T3–T4/sr1 + B4–B5/sr2, Rxy T5–B6/sr3). Four legs, one cell each (E1: each leg gets its own armed monitor so a leakage turn-up is killed in-leg): TG→+3.0, TG→−3.0, BG→+4.5, BG→−4.5 V, then a reset cell (nplci back to 1). **Si legs deferred**: the investigation operates at Si = 0 (D ≈ 0 dual-gate work; Si is the contact-doping gate), and the DC205 has no current readback — a ±50 V excursion buys no leakage information and costs ~7 min. If the campaign later needs Si ≠ 0, a liveness leg lands first.

Drive per device card: sr1 sine 0.5 V through 100 MΩ = 5 nA at ≈13 Hz. Dwell: `delay=1` s per the recipe (3.3τ at τ = 0.3 s — liveness-grade, knowingly under the card's 1.2 s classification floor).

**Pass/fail read (per leg)**: lock-in X nonzero and smoothly varying = alive; swept-gate current pA-scale on the capacitive charging slope = safe; parked-gate current at floor = no cross-gate path. Turn-up off the slope → interrupt (try/finally parks the gate), stop, notify.

**Wall-clock**: ~2.1 s/pt (1 s delay + ~1.1 s Keithley NPLC-10 reads, rig-card timing — inherited figure, first in-session calibration comes from leg 1; expect actuals ~5–10% over) × 251 pts ≈ 9 min/leg, ~38 min all four + ramps.
