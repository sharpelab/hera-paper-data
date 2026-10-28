## HERA — Gate C: liveness pass (`gate-current-sanity-check`)

First-session branch (no designated references — device-init path per the
brief's data isolation). Four legs, each its own run + slug: TG 0→+3 V,
TG 0→−3 V, BG 0→+4.5 V, BG 0→−4.5 V — endpoints are the committed SAFETIES
limits, other gate parked at 0, Si at 0 V. `nplci=10` on both Keithley `curr`
channels for pA readback (follow-up cell resets to 1); liveness drive
0.1 V / 100 MΩ ≈ 1 nA at 13 Hz per the recipe (not the 0.5 V mapping default).

**Read per leg**: swept-gate current stays pA on the capacitive charging
slope → safe; parked-gate current at floor → no cross-gate path; lock-in X
nonzero and smoothly varying → alive. Any gross turn-up → interrupt (the
`try/finally` parks the gate), stop-and-report; a leaking gate is
blocklisted-`gate-leakage-survey` territory → operator call.

**Coverage trade**: the Si gate (DC205) is **not** swept — no current
readback on the DC205, graphite BG screens it from the channel, and the near
arc (CNP calibration → fan at D=0) never moves it. If a later step needs Si,
a Si leg (watched via cross-gate Keithley currents only) lands first — flagged
here so the omission is on the page.

**Cost**: 251 pts/leg at ~1.1–1.4 s/pt (rig-card NPLC=10 calibration,
20260714.2 runs 0–3) → ~5–6 min/leg, **~25 min total** incl. flybacks.
Checkpoints: first rows of leg 1 (railing / dead channels / wrong sens),
then per-leg completion — monitored via `hera-watch`.

E1 auto bucket: in-envelope (endpoints = validator limits), preconditions
asserted in-cell (B ≈ 0, T ≈ base).
