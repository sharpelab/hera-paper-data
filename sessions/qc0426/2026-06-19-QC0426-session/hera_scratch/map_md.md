## HERA [E1] — 0 T TG–BG gate map (CNP-line calibration + clean-region survey)

Full-box megasweep: **BG slow rows** `linspace(-4.5,4.5,37)` (Δ0.25 V) × **TG fast**
`linspace(-6,7,131)` (Δ0.10 V), Si=0, B=0. BG-slow/TG-fast so the fitted ridge
position is V_tg vs V_bg rows → slope = −c_bg/c_tg directly (cnp-and-dline recipe).
Box brackets the recon CNP at (0,0) with geometry slope −1.3 → CNP line runs
V_tg≈+5.85 (BG −4.5) → −5.85 (BG +4.5), fully inside the TG window.

**Settling:** `fast_delay=1.0` — recon validated the ridge at delay 2.0; sr1 (τ=0.03)
is fully settled, sr2/sr3 (τ=0.3) lag ≈0.03 V (< Δ_TG), negligible for ridge *position*
(I fit sr1 primary). `slow_delay=2.0`. **~1.5 h** (37 rows × 131 pts × ~1.05 s + retrace).

**Checkpoint @ ~28 min (≈row 11, BG≈−1.75 V):** confirm the ridge is tracking
diagonally at slope ≈−1.3 (CNP should sit near V_tg≈+2.3 there), BG leakage < few
hundred pA, lock-ins not flat/railed. Fork: continue / adjust extent / abort. Leakage
via Keithley `curr` (DC205 has no monitor); NO per-point Lakeshore poll (rig quirk).
Auto: all gates inside committed validators, reversible. Tag 'gatemap'.
