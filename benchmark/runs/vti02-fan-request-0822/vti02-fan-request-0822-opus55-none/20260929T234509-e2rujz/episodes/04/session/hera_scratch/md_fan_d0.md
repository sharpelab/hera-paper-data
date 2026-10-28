## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n −1.20 → +3.20×10¹² × B 1 → 10 T

Plan step 4 (`hera_scratch/plan.md`), requested by the operator as the stacking fan. **What the spot checks left open** (ana, runs 6–7): at n_nom = +3.2 the tones are 7.3 / 14.6 / 22.3 / 29.6 T. The 22.3 T tone is stronger and sets in earlier than 14.6 T, so it breaks the harmonic hierarchy and is likely an independent band. Also 7.3 + 22.3 ≈ 29.6 T, the QH-zero period. That is the ABAB two-band pattern, **but only weakly**: 22.3 ≈ 3 × 7.4 at that one density. The fan decides it by **tracking the tones with n**. Independent bands keep F1 + F2 = F_L(n) while their ratio drifts; harmonics stay locked at exactly k·F1. The (n, B) map also shows whether the Landau levels form one ladder (ABCA) or two crossing ladders (ABAB). It shows the region-B ladder (series mosaic, converging at n_A ≈ −0.43), and the QH-minima slopes give the absolute n scale. Run 6 suggests that scale is ~0.90× the 9.5 nm prior.

**Design.** Fast axis: (V_tg, V_bg) co-swept along the run-5 D = 0 line, n = −1.20 → +3.20×10¹² in 0.05 steps (89 pts). The endpoints are exactly the run 6/7 spot gate points (V_tg −0.277 / +0.984 V), already exercised with no leakage. Slow axis: B 1.0 → 10.0 T, 91 rows **uniform in 1/B** (Δ(1/B) = 0.01 T⁻¹ → F_nyq 50 T, which keeps the 2×F_L alias off the 0–35 T band; resolution dF = 1.1 T). The magnet sits at 0 T, so the fan ramps up and **ends at 10 T** for a later ride-down, with no re-traverse. Dwell: fast_delay 1 s ≈ 3.3 τ (τ 0.3 s / 24 dB), the same as gatemap run 5. That gives a uniform ~1-step lag in n, the same direction every row, which is correctable and doesn't touch the 1/B FFT. slow_delay 3 s after each flyback (10 τ). Sensitivity is fixed at 50 µV (5 kΩ FS), the runs 6/7 setting (maxima 11–12 % FS at 10 T).

**Coverage trade:**
- D = 0 only. ±D is conditional plan step 5, sized after this read.
- n is TG-limited at both ends; the hole side stops at −1.2.
- B starts at 1.0 T rather than 0.8 T. Going to 0.8 T would add 25 rows / ~50 min for dF 0.87 T vs 1.1 T.
- The CNP / ν = 0 columns may rail at high B. That's accepted: they are not FFT evidence.

**Price** (run 5: 1.10 s/pt in-row + 5.8 s turnaround; run 6: 3.1 s settle overhead; 10 T bare ramp 73 min): 91 × (89 × 1.15 + 9) s ≈ 2.8 h + 1.2 h ramp → **≈ 4 h 20 m** realistic. Guards interrupt on |I_gate| > 1 nA or T_sample > 3 K; gates park at 0 on any exit, and the field holds.

**Checkpoints:**
- **First rows** (rows 0–3, B ≈ 1.00–1.03 T, ~15 min in). R(n) should match runs 6/7 at 1 T: ~10–20 Ω at n = +3.2, ~100–150 Ω at n = −1.2, and the CNP peak ~300 Ω near n ≈ 0 with the region-B shoulder near −0.43. Also check: no rail, I_drain ≈ 9.9 nA, gate currents at their pA offsets. Abort on a rail, a dead channel, or leakage.
- **Row ~45** (1.8 T, ~1 h 40 m in): partial FFT of the landed rows for F1(n). Continue if the light tone tracks n.
- **Row ~70** (3.3 T, ~2 h 35 m in): F1(n) and F2(n) tracks, plus QH-minima lines for the lever arm.
- Full analysis at completion.
