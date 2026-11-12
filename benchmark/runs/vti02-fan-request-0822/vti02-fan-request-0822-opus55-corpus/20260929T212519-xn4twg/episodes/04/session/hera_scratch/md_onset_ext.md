## HERA — Step 4a: low-field onset extension at n = +2.0×10¹² (`sdh-spot-check`), B 0.3 → 3 T — pins the fan's B_lo

**Spot-check read (runs 6/7, ana):** electron side (n = +3.2) shows tones at 7.3 / 22.2 / 29.5 T (+ 14.6, 36, 44, 52, 58 T: exact 7.3 T multiples). There are two readings:
- **ABAB pair.** 7.3 + 22.2 = 29.5 = 0.886·F_L. The partition 0.25/0.75 matches the model at scale 0.89.
- **Comb.** A 7.3 T tone plus harmonics/intermodulation, with 22.2 = 29.5 − 7.3.

The hole side (n = −1.2) has clean low-field SdH (onset 0.71 T) led by a **~7 T tone, the same frequency as the electron 7.3 T at 4.4×10¹² more density**. That suggests a density-independent (fixed-density parallel region) tone rather than a gated pocket. Only the F(n) slopes in a fan decide this, so the fan runs on the **electron side**, the only side reaching the design densities |n| ≳ 2×10¹² (the D = 0 line stops at n = −1.27 on the hole side).

**Why this cell first:** the fan's B_lo must come from `sdh_onset` (`landau-fan` step 1, lever 1), but run 6's carrying tone is **censored** at 0.85 T. Below that edge its 50 mT grid is under Nyquist for 7 T, so the onset was never recorded, and the recipe says to pin it with a cheap low-field extension before a long fan. B_lo is the fan's dominant cost lever, because both N_B ∝ 1/B_lo and the ray-Nyquist N_n ∝ 1/B_lo scale with it. Fan price at n ∈ [1.8, 3.2]×10¹², B_lo → 5 T: **≈ 5.6 h at B_lo = 0.6, 4.2 h at 0.7, 3.0 h at 0.85**.

**Why n = +2.0:** this is near the fan's low-density edge, where the ABAB light tone is slowest (the binding case for B_lo; model ≈ 3 T at scale 0.89). It also gives a **third density** for the 7 T question: a fixed-density tone stays at ~7 T, the ABAB light tone drops to ~3 T, and the heavy tone should sit near 15 T.

**Grid:** uniform in 1/B, Δ(1/B) = 0.0125 T⁻¹ (Nyquist 40 T vs F_L(2.0) = 20.7 T), 241 pts. Dwell = the driver's 3 s settle = 10τ, `delay = 0` (inherited from runs 6/7). sr1 is fixed at 50 µV (inherited; state0 restore left it at 2 µV, so it is set explicitly here).

**Checkpoint:** first ~20 points for rail, leakage and field tracking. After that, read `sdh_onset` at the end. The magnet ends at 3 T, and the fan starts at B_lo and ascends to 5 T.
