## HERA — Gate C: gate-current sanity check (liveness + gross safety)

Recipe: `device-init/gate-current-sanity-check.md` (first-session branch — no
designated references exist; `reentry-baseline` explicitly defers to the
device-init path here). Four legs, each Keithley gate 0 → each card limit
(TG +7/−6 V, BG ±4.5 V), other gates parked at 0, **Si held at 0 V** — the
DC205 has no current readback, so a Si leg would be blind on leakage; leakage
watch lives on the Keithley `curr` channels. Geometry ceiling check passes:
±0.5 V/nm × hBN gives TG ±7.8 V, BG ±6.0 V — both card limits sit inside.

Read per leg: lock-in X nonzero and smooth = device alive on that pair; swept
gate current in pA riding the charging slope to the limit = safe; parked gate
current at floor = no cross-gate path. Voltage-channel sensitivity expectation
near CNP-ish kΩ scale is ~2e-5 (device card) — a railed X is a sensitivity
flag, not a device verdict. Drive: card default 0.5 V through 100 MΩ (5 nA)
at ~13 Hz.

Preconditions printed up top (T ≈ 1.1–1.3 K, B ≈ 0, V_si = 0); cell stops on
mismatch. **Cell A ≈ 25–35 min** (4 × 251 pts at 1.2 s settling floor — rig-card
~1.2 s/pt rule; no in-dir calibrating run yet). Run Cell B (nplci reset) only
if every leg looked safe. On any gross current turn-up: interrupt — the
`finally` parks the gate — and stop.
