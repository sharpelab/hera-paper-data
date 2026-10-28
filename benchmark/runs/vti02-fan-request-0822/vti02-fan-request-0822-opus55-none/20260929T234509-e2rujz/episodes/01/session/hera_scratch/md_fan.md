## HERA — Step 4: Landau fan at D = 0 over the full density window (`landau-fan`)

**Why (plan step 4, `hera_scratch/plan.md`).** The spot checks at D = 0 (analysis in `hera_scratch/ana_sdh67.py`, promoted to ana while this runs) give, on both carrier sides, **two tones plus a third near their sum**:
- **Run 6** (n = +3.2×10¹²): 7.2 + 22.2 ≈ 29.5 T.
- **Run 7** (n = −1.2×10¹²): 3.5 + 8.5 ≈ 12.3 T.

That is the ABAB signature: a light and a heavy bilayer-like band, which my coarse TB model puts at ≈0.26 / 0.73 of n (electron side) and ≈0.31 / 0.68 (hole side). ABCA or ABCB would instead show one dominant surface at ≈0.9 F_L. **What these two points cannot rule out:** on the electron side 22.2 ≈ 3 × 7.2, so "one band plus harmonics" still fits run 6.

The fan settles that across n. **Two independent line families** — tones that scale with n, keep a non-integer ratio (≈2.7 electron side, ≈2.2 hole side) and sum to F_total at every column, with LL crossings visible in the 2D image — would mean ABAB. **One dominant family** at ≈F_total would send the call to ABCA vs ABCB (step 5). The fan also **calibrates the absolute density scale** from the QH-minimum slopes (dn/dB = νe/h, independent of the gate calibration). c_tg is still the 9.5 nm prior, and the spot-check totals suggest it is ~8 % high.

**Design.**
- **Fast axis:** n along the run-5 D = 0 line, −1.20 → +3.20×10¹² in 0.04 steps (111 pts). V_tg and V_bg are co-swept; both ends are TG-limited, the electron end 16 mV under +1.0 V. The step resolves the heavy-band LL spacing (≈0.14×10¹² per T) down to ~1 T.
- **Slow axis:** B from 0.8 → 8 T, uniform in 1/B at Δ(1/B) = 0.010 T⁻¹ (113 rows). That gives ≥3 samples per period of the ~30 T total-filling tone at every B, so the per-column FFT runs without resampling. The rows are dense at 1–2 T, where the LL crossings live.
- **Dwell and sensitivity:** fast_delay 1 s, as in run 5 (τ = 0.3 s, 24 dB). The resulting lag is a uniform one-point n-shift and is identical on every row. sr1 is fixed at 100 µV (10 kΩ FS), 17× over the largest D = 0 value seen.
- **Guards:** the leak guard (1 nA, either gate) stays on. hera-watch's per-row "⚠ LEAK k_2400_tg" is the known flyback transient (session_notes).

**Coverage trade.**
- **Only D = 0** (run-5 calibration). Finite-D behaviour — the ABCA gap and a possible ABCB ±D asymmetry or hysteresis — is step 5, measured from where this fan ends.
- **Below 0.8 T** is excluded: only the light tone lives there, and 1/B-uniform rows would add ~1.7 h for 0.6 T.
- **Above 8 T** is excluded: 2 rows for +15 min of ramp, with the QH scale already fixed by 4–8 T.
- **Electron side** stops at +3.2×10¹² (TG limit).
- The **CNP column may rail at high B**. I accept that: the rail itself says the ν ≈ 0 state is insulating.

**Price.** Calibrated on run 5 (1.10 s per in-row point, 5.8 s turnaround) and run 6 (field step 437.6 s/T + 3.1 s):
- 113 rows × (111 × 1.11 s + 8 s): 4.1 h
- field 0 → 8 T at 0.137 T/min: 58 min
- per-row settles: 6 min
- **floor ≈ 5.2 h; realistic ≈ 5 h 40 m.**

**End state:** field **stays at 8 T** (step 5 starts there; never re-traverse). Gates are parked at 0 V, also on an interrupt.

**Checkpoints** (read from `hera-watch`):
- **Rows 0–3 (~10 min):** signal level, rails, gate currents, and the (V_tg, V_bg) path reading back the D = 0 line.
- **Row ~20 (0.95 T, ~50 min):** light-band LL lines visible in n?
- **Row ~58 (1.5 T, ~2 h 20 m):** partial per-column FFT — light/heavy tones and their ratio vs n. Abandon if the record is featureless.
- **Row ~100 (4 T, ~4 h 15 m):** QH minima → density scale.
