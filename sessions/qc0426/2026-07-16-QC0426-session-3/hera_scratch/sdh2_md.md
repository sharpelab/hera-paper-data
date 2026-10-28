## HERA — SdH spot check 2/2: electron side, n = +6e12, D = 0 (`sdh-spot-check`)

Mirror of SC1 on the electron side, riding the magnet **down 8 → 1 T** from where SC1 left it (no re-traverse). Same design: F_L(nominal) = 62.0 T, ΔB = 5.38 mT uniform-B (Nyquist held at the 1 T end), 1303 pts descending; gates (V_tg, V_bg) = (+2.8342, +2.2075) — run-4 calibration, D = 0. Drive 20 nA @ 13 Hz, sens sr1/sr2/sr3 5e-5, `magnet.settle_s` 1.2 (restored after). SC1 interim already shows the {12, 55, 67≈sum} T set on the hole side; SC2 asks (a) does the electron side show the matching combinatorics, (b) which side is cleaner for the fan (investigation step 3 decision).

**Ends at 1 T** — the fan (step 4) starts near the measured onset, so the magnet parks exactly where the next measurement needs it.

**Wall-clock**: 1303 × ~3.7 s ≈ 80 min (SC1-calibrated rate; no positioning ramp needed).

**Checkpoints**: first rows (drain/clip/Hall sign flip), mid-run FFT. Abort on rail/sag/leakage.
