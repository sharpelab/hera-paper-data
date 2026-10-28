## HERA — 0 T gate map, coarse-BG (CNP-line calibration) — `gatemap`

Investigation step 1 (`trilayer-stacking-fs-count`) via `device-init/cnp-and-dline-calibration`: fit the CNP ridge in (V_tg, V_bg) → c_bg/c_tg from the slope, n_offset from the intercept. Gate C found the CNP near the origin at BG = 0 (runs 0–1: sr1 peak ≈ 1.6 kΩ at V_tg ≈ 0) plus a shoulder at V_tg ≈ +0.55 V to track on the map.

**Coverage trade (stated):** geometry prior slope −c_bg/c_tg ≈ −1.3 (15.6/12 nm hBN) puts the ridge outside the TG window for |V_bg| ≳ 2.3 V, and the D = 0 line exits the validator box there too — so BG spans **±2.4 V**, not the full ±4.5: the excluded range cannot contribute unclipped ridge rows. BG rows are **coarse (25 rows, 0.2 V)** — sized for a robust linear ridge fit (~20+ surviving rows), not for feature-hunting; the price of a full 201×201 canonical map at the card's 1.2 s dwell floor is ~17 h, deferred unless this fit is inadequate (curvature / cross-channel disagreement / mosaic → escalate to a denser map over the disputed window). High-|n| clean-region ID along D = 0 comes next from a designed D = 0 line cut, which this calibration enables.

**Design:** TG fast, −3 → +3 V, 151 pts (40 mV; ridge width ~0.5 V from gate C — well resolved); BG slow −2.4 → +2.4 V, 25 rows; `fast_delay=1.2` (4τ card floor, τ = 0.3 s), `slow_delay=3`. sr1/sr2 sensitivity raised 2e-5 → **2e-4** for this map (ridge at finite D can exceed the 4 kΩ ceiling of 2e-5 at 5 nA; 2e-4 → 40 kΩ ceiling, ~1 Ω quantization keeps the metallic corners readable). Drive 5 nA @ 13 Hz unchanged.

**Wall-clock:** per-point ≈ 1.2 + 0.25 s reads (NPLC 1; reads calibrated from gate C runs 0–3: 2.2 s/pt − 1.0 delay − ~1.1 NPLC-10 Keithley term) ≈ 1.45 s → 151 × 1.45 + 7 s flyback + 3 s ≈ 230 s/row × 25 ≈ **1.6 h; realistic 1.7–1.9 h** (session actuals run over estimates). ETA stamped at launch.

**Checkpoints:** first rows (leakage, railing, dead channel — kill inside minute one) then per-row digests via the armed watch; ridge should march linearly across TG with BG. Abort call: leakage > 1 nA, a channel flat across a full row, or ridge clipped in most rows.
