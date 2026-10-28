## HERA — Step 4: D = 0 Landau fan (`landau-fan`), n_A −1.25 → +3.23×10¹², B 0 → 10 T

**Plan step 4** (`hera_scratch/plan.md`), requested by the operator as the stacking measurement.
- **Why this measurement:** runs 6–7 show strong SdH/QH on both sides, but a single density cannot tell apart the readings in play:
  - an ABAB-like pair (7.1 + 22.2 ≈ 29.5 T at n = +3.2×10¹²);
  - a single band with a harmonic ladder;
  - region-B tones (region B is ≈ 0.43×10¹² more electron-doped than A).
- **What decides it:** F(n) across density plus the fan-line families.
  - ABAB: two branches with F₁ + F₂ = F_L, ratio ≈ 0.2–0.3, and crossings between the two families.
  - ABCA: one branch at F ≈ F_L and no crossings at D = 0.
  - Region B: shows up as a second fan whose lines converge at n_A ≈ −0.43.
- The fan also fixes the absolute n scale from the QH minima (n = ν·eB/h). The run-5 scale is still the geometry prior.

**Geometry:**
- **Fast axis:** co-swept (V_tg, V_bg) along the region-A D = 0 line (run-5 cal). 151 pts at δn = 0.030×10¹², covering the full in-validator window (5 mV margin).
  - The hole side stops at −1.25×10¹² because of the TG −0.3 V limit. That limit is the operating box; extending it is banned.
  - Direction: hole → electron.
- **Slow axis:** B, ascending from where the magnet sits (0 T). ~146 rows:
  - one row at 0 T (the MR/background reference, aligned to the fan columns);
  - uniform in 1/B from 0.7 to 3.6 T, δ(1/B) = 0.0115 T⁻¹. Nyquist is 43 T, above F_L max ≈ 39 T including region B, and dF ≈ 0.8 T;
  - uniform 0.15 T from 3.6 to 10 T, for the QH fan and crossings.
  - Below 0.7 T only the light tone lives. Uniform-1/B rows there cost ~2.5 h for 0.5–0.7 T alone, so they're excluded.
- **Readout settings:**
  - `fast_delay` 0.8 s at τ = 0.3 s / 24 dB. This is a constant ~1-pt lag in the fixed sweep direction, which folds into n_offset. Attenuation is ≲ 30 % at 1 T.
  - `slow_delay` 5 s after each flyback.
  - sr1 at **100 µV = 10 kΩ FS** (0.37 Ω quantization). Trade: a gapped ν = 0 CNP at high B may rail on a few columns; the stacking read doesn't use its magnitude.
- **Ends at 10 T with gates parked at 0 V.** Step 5 (finite-D fan) rides the magnet down from there.

**Price:** calibrated on run 5 (1.10 s/pt at 1.0 s delay, i.e. 0.10 s read overhead + ~0.03 s for the second gate) and run 6 (3.1 s per field set beyond the ramp).
- Per row: 151 × 0.93 s + 5 s slow_delay + ~6 s flyback + 3.1 s ≈ 155 s.
- Total: 146 rows ≈ 6.3 h + the 10 T ramp floor of 73 min ≈ 7.5 h. **Headline 7 h 45 m.**

**Guards:**
- Auto-abort if |I_gate| > 1 nA or T_sample > 2.0 K.
- Preconditions printed and asserted: T, B, V_si, heaters, nplci, drive, and τ (the pricing assumes τ).

**Checkpoints:**
1. **First rows (0 T and 0.7 T):** R(n) matches run 5's D = 0 cut (≈ 50–500 Ω, CNP near n_A = 0, ridge B near −0.43), no rail, gate currents at the pA floor. Abort on any failure.
2. **B ≈ 2 T (~2 h 20 m in):** partial fan. Fan lines visible and converging? Light tone in the per-column FFT?
3. **B = 3.6 T (end of the 1/B block, ~4 h 15 m in):** per-column F(n) on 0.7–3.6 T. This is the main discriminator.
   - If F(n) is already unambiguous, continuing to 10 T buys the n calibration and the QH crossings (~3.5 h).
   - If F(n) is washed out, abandon the top and re-plan.
