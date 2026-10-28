## Run 4 — first 0 T gate map (V_tg × V_bg), the CNP-line calibration substrate

`recipe: measurements/gatemap.md`, feeding `device-init/cnp-and-dline-calibration.md`.
V_tg fast [−0.3, +1.0] × 101 (13 mV) at V_bg ∈ [−1.3, +1.3] × 37 (72 mV),
3737 points, B = 0, V_si = 0, T = 1.175 K, I_bias = 49.2 nA, dwell 0.70 s.
Complete, not interrupted, 52 min, no railing (max sr1 load 0.34).

Excluded by design: V_bg ∈ (1.3, 2.0], where Gate C run 2 showed R falling
smoothly with no new ridge, and which is high-D electron side, off the D ≈ 0
operating point the investigation requires.
