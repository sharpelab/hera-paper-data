## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n −1.25 … +3.25×10¹² × B 1 → 10 T

Plan step 4 (`hera_scratch/plan.md`); the operator asked for the fan. The spot checks (runs 6–7, ana) show QH by 1.8 T and a two-band signature at n_e = +3.2×10¹²: tones 7.1 / 22.2 / 29.5 T with 7.1 + 22.2 ≈ 29.5 = F_L. The minima form a ν = 4k ladder only after scaling the density prior by ×0.894, and ν = 40, 52, 56, 68–76 are missing. That leans ABAB, but it is one point. The fan decides:
- **(a)** absolute n scale from the ν-line slopes
- **(b)** per-n tone count, the sum rule, and the **light-tone fraction vs n**: ABAB ≈ 0.25–0.3 and flat; ABCB's Dirac band starts small and grows with n; ABCA has none
- **(c)** the missing-minima / LL-crossing pattern
- **(d)** the hole side and CNP

**Design:**
- **Fast axis:** n along the run-5 D = 0 line, co-sweeping V_tg / V_bg, −1.25 → +3.25×10¹² (prior scale), 151 pts at 0.03×10¹².
- **Slow axis:** B, 82 rows **uniform in 1/B** from 1 to 10 T. Δ(1/B) = 0.0111 gives Nyquist 45 T (≥ 1.5 × F_L(true) ≈ 30 T, room for region-B tones at ×1.13) and ΔF = 1.1 T.
- **Settling:** fast_delay 1 s = 3.3 τ at τ = 0.3 s / 24 dB. This is a uniform ~1-point lag in the sweep direction, harmless for per-column 1/B FFTs, and gives timing parity with run 5. slow_delay 3 s after each flyback + field step.
- **Sensitivity:** sr1 fixed at 100 µV = 10 kΩ FS. A rail at the high-B ν = 0 core near n = 0 is accepted.
- **Protection and end state:** leak guard at 1 nA. Gates park at 0 at the end; the field stays at 10 T for step 5 to ride down.

**Coverage trade:** the n window is TG-limited at both ends (the D = 0 line leaves [−0.3, +1.0] V at −1.27 / +3.27). The hole side reaches only ≈ −1.1×10¹² true. There is no finite-D coverage here (that is step 5). Starting at 0.7 T instead of 1 T would sharpen ΔF to 0.75 T for about +2 h (39 more rows); not bought, since the light tone is already resolved at 1.1 T.

**Price:** from run 5 (1.10 s/pt at fast_delay 1 s) + 0.03 s for the second gate set, 151 pts × 1.13 s + ~10 s turnaround ≈ 180 s/row. 82 rows = 4 h 06 m, plus the field ramps 1 → 10 T at 0.137 T/min (66 m) and the pre-ramp 0 → 1 T (7 m) = 5 h 19 m, quoted with ~8 % overrun.

**Checkpoints:**
- **First rows (≈ 10 min in):** R scale at B ≈ 1 T vs run 6 (≈ 15–20 Ω at +3.2) and near the CNP; rail; I_drain ≈ 9.9 nA; gate currents.
- **Row ~25 (B ≈ 1.4 T, ~1 h 30 m) and row ~50 (B ≈ 2.2 T, ~3 h):** interim per-column FFT on the landed rows, with the light-tone fraction vs n.
- **Row ~70 (B ≈ 4.5 T):** the ν-line scale fit.

Abandon if the channel rails away from the CNP, the leak guard trips, or no oscillations appear by row 50.
