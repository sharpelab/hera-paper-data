## Runs 6–7 — SdH spot checks (`sdh-spot-check`) at D = 0, both carrier signs

Investigation Step 3. Two fixed-(n, D = 0) field sweeps at base T, from the run-5
calibration: **run 6** electron, n = +3.20×10¹² (the D = 0 line's electron reach —
V_tg = +0.984 V, 16 mV under the limit), B 0 → 10 T; **run 7** hole,
n = −1.20×10¹² (the line's hole reach), riding the magnet back 10 → 0.3 T.
Both `sr1` (B_1 − B_2), 50 µV, I_bias = 10 nA, dwell = the magnet driver's 3 s
settle = 10 τ at τ = 0.3 s / 24 dB.

**Each record carries a coarse low-B leg that is undersampled for its own tones**
— run 6 steps 50 mT below 1 T (Δ(1/B) = 0.55 1/T at 0.3 T, against a Nyquist need
of 0.015), run 7 steps 20 mT throughout (Δ(1/B) = 0.22 1/T at 0.3 T). FFT'ing
through those legs folds aliases into the low-frequency band, which is what a
first pass did: the peak set wandered with the cutoff (7.8 → 8.6 → 33 T on run 6).
Everything below is read on the **Nyquist-valid window only** — B ≥ 1.0 T (run 6)
and B ≥ 0.70 T (run 7), where the grid resolves F_L. Raw first, then the read.
