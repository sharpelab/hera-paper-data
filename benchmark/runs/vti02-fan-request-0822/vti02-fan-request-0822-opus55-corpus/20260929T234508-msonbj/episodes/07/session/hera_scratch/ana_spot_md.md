## Runs 6 / 7 — SdH spot checks (`sdh-spot-check`), D = 0: electron n_cal = +3.2×10¹², hole n_cal = −1.2×10¹²

Raw first (Rxx = (sr1_X/1)/(sr0_X/−1e6)), then the B-space poly5 background, FFT in 1/B, and `sdh_onset`. Both records are clean: T 1.17–1.29 K, gate currents ≤ 0.22 nA, no rail (R max 0.53–0.59 kΩ of the 5 kΩ full scale).

**Electron (run 6).** Above ~4 T the device is in the QH regime: Rxx minima at 4.29 / 4.98 / 6.00 T fall at ν_cal = 30.8 / 26.6 / 22.1. Read as the 4-fold ladder ν = 28 / 24 / 20, they give **density scale S = n_true/n_cal = 0.906** (spread 0.903–0.908). This is a model-independent lever-arm check, −9 % against the geometry prior, inside its 10–15 % band. So **F_L,true = 30.0 T** at this spot. FFT tones (B ≥ 1 T):
- **≈ 30 T**, strongest in the high-B windows, onset 1.76 T.
- **22.2 T**, onset 1.40 T.
- **14.8 T**.
- **7.3 T**, censored at the 1 T edge and flagged near-residual.

Two readings sit on this spectrum, and neither is dropped yet:
- *Harmonic screen:* 14.8 ≈ 2 × 7.3, and 22.3 ≈ 3 × 7.3 (ratio 3.05).
- *Luttinger-aware:* 7.3 + 22.3 = 29.6 T ≈ F_L,true. The model ABAB pair at n_true = 2.9 is 6.3 / 23.6 T.

The 30 T tone sits at F_L,true, which has three candidate origins: an ABCA singleton, an ABAB breakdown sum, or the total-filling QH ladder (present whatever the FS count). **One density cannot decide between them; the n-dependence does.** A harmonic tracks 3 × f exactly, while a real heavy pocket follows its own Onsager curve (at n_cal = 2.0 the model puts 3 × light at 8.9 T but heavy at 15.8 T). On top of that come the F_L-tone origin tests (B-window split, LK).

**Hole (run 7).** F_L,cal = 12.4 T. Tones: 6.6 T (onset 0.71 T), 12.3 T, 4.7 T, 8.5 T, plus 9.4 / 14.8 T at 2 × and 3 × 4.7 T. This is the near-CNP exception regime (model ABAB pair close and balanced, 5.3 / 7.1 T; ABCA m* ≈ 1 mₑ, so LK-dead), and at low |n| the offset uncertainty dominates. **It is a preview, not a decisive read.**

**What the fan inherits.**
- **Cleaner side: electron.** It is the only side that reaches the design density |n| ≳ 2–3×10¹² at D = 0; the hole side is TG-capped at −1.27×10¹².
- **Onset: 1.00 T.** This is `sdh_onset` on the 10 mT section. It is censored, so the true onset is ≤ 1 T. Run 6's 50 mT grid below 1 T was under Nyquist for F_L, so the sub-1 T onset was not measured.
- **Sampling:** 10 mT at 1 T, i.e. Δ(1/B) = 0.010 = 1/(3·F_L,cal).
- **Sensitivity and settling:** sr1 at 50 µV, τ = 0.3 s at 24 dB/oct.

**Carried confound:** region B (run 5), a parallel ridge at +0.43×10¹² relative to region A, sits in series between B_1 and B_2. Expect possible extra tones at about ×1.13.
