## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n −1.25 → +3.25×10¹², B 1.25 → 10 T

**Why (plan step 4).** Runs 6 and 7 (ana) show strong SdH on both carrier sides. One trace can't tell a 7.4 T fundamental with harmonics apart from independent pockets (the ABAB model pair is 7.5 + 25.6 T at n = +3.2×10¹²). The stacking discriminators are:
- how each tone scales with n: an independent pocket has its own dF/dn, while a harmonic has k·dF₁/dn;
- the sum rule ΣF_i = F_L(n);
- the Landau-level crossing pattern.

The fan also gives two more things:
- the **absolute density scale** from quantum-Hall-minimum slopes — c_tg is still the geometry prior, and the sum rule needs the real scale;
- the region-B series family, whose lines converge on n_A ≈ −0.43×10¹², so it can be identified and excluded.

**Design.**
- **Fast axis:** (V_tg, V_bg) co-swept along the region-A D = 0 line (run-5 calibration, the same one runs 6/7 used). n runs −1.25 … +3.25×10¹², which is the whole D = 0 window inside the validators (V_tg tops out at 0.998 V). Δn = 0.03×10¹², 151 points, which is 4 points per Luttinger Landau-level period at 1.25 T.
- **Slow axis:** B, uniform in 1/B (0.007 T⁻¹; Nyquist 71 T, above the maximum F_L of 33.6 T) from 1.25 T to 5 T. Then 0.2 T steps to 10 T for the high-field Landau-level pattern. 112 rows in total.
- **Field window:** starts at 1.25 T because the heavy tones in runs 6/7 set in at 1.3–1.9 T. FFT resolution is about 1.4 T, which separates 25.6 T from 33 T.
- **Start and end:** the magnet is at 0 T, so the fan starts there. It ends at 10 T with the gates parked at 0; step 5 (D-dependence, chosen from this result) rides the field down.
- **Delays:** fast_delay 1.0 s at τ 0.3 s / 24 dB (as in run 5). That leaves a lag of about one point toward +n, the same on every row, so it doesn't bias the per-column 1/B FFT. slow_delay 3 s after the flyback, plus the magnet's 3 s settle.
- **Readout:** sr1 fixed at 100 µV = 10 kΩ full scale (runs 6/7 peaked at 590 Ω). Field readback is recorded at every point.
- **Guards:** an interrupt fires if either gate current exceeds 1 nA or T_sample exceeds 3 K.

**Coverage trade.** Holes stop at −1.25×10¹² (the TG −0.3 V limit). D ≠ 0 is not covered here; it is step 5. The CNP columns may rail at high B; that is accepted, since the tone read doesn't use them.

**Price.** 112 rows × (151 × 1.17 s/pt + ~10 s flyback/settle) ≈ 5.8 h, plus 73 min of 0 → 10 T ramps, gives 7.0 h. Adding the ~7 % realistic overrun gives **7 h 30 m**. The 1.17 s/pt is from run 5: 4158 points in 81.2 min at the same delay and τ. The fan reaches 2 T at about 2.7 h, 2.5 T at 3.6 h and 5 T at 5.5 h.

**Checkpoints.**
- **First rows at 1.25 T:** sr1 not railing, drain current flat, gate currents at the pA floor, field readback equal to the setpoint, and R(n) at +3.2 and −1.2 matching runs 6/7 at 1.25 T.
- **At ~2.5 T** (row ~58, ~3.6 h): a partial per-column FFT on the 1.25–2.5 T record (ΔF ≈ 2.5 T). Continue if the tone structure resolves. Cut the high-B segment only if the columns are featureless.
