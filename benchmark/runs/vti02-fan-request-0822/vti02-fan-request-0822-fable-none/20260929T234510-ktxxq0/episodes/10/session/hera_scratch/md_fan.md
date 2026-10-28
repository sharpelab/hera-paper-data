## HERA — Step 4: Landau fan along D = 0 (`landau-fan`), n = −1.24 → +3.24×10¹², B = 0.5 → 8 T

**Plan step 4** (hera_scratch/plan.md; ana runs 6–7 take). The spot checks proved oscillations resolve from ≤ 0.3 T (electron) / 0.7 T (hole) and showed two incommensurate fundamentals at n = +3.2×10¹² — the stacking call now needs F(n) branch structure and the LL fan, which is exactly this map. Design:

- **Fast axis:** n along the run-5-calibrated D = 0 line, −1.24 → +3.24×10¹² in Δn = 0.04 steps (113 pts) — the full validator-reachable D = 0 span with ~10 mV margin at both TG corners (V_tg −0.288 → +0.995 V, V_bg −0.480 → +1.181 V). **Coverage trade:** hole side ends at −1.24×10¹² because the TG −0.3 V limit does — deeper hole coverage does not exist inside the committed box.
- **Slow axis:** B 0.5 → 8 T ascending, **190 rows uniform in 1/B** (direct FFT per column, points weighted to low B where the light tones live). F_Nyquist = 50.7 T: fundamentals (≤ ~33–37 T) unaliased; the 2×F_heavy ≈ 60 T harmonic folds to ~41 T, clear of all fundamentals. **Trade:** top capped at 8 T, not the 10 T session cap — the extra 1/B span 8 → 10 T is 1% more frequency resolution for ~45 min + coarser top rows; the deep-QH regime at 10 T is already sampled by runs 6/7.
- **Sensitivity:** sr1 at **200 µV = 20 kΩ FS** (run-4 rail lesson: the field-gapped CNP, not the 0 T peak ≤ 330 Ω, sets R_max; run 7 hit 590 Ω at 10 T at n = −1.2, and the CNP column itself will exceed that — headroom over resolution). sr0 unchanged (20 mV).
- **Dwell:** fast_delay 1 s (≈ 3.3 τ at τ = 0.3 s — position-reading of LL features, not LK amplitudes; same as the run-5 gatemap), slow_delay 0 (the magnet set blocks through ramp + 3 s settle).
- **Guards:** leak trip 1 nA on either Keithley; T trip at 2 K (unattended overnight-scale run).

**Price** (run-5 per-point 1.23 s/pt, runs-6/7 ramp overhead): 113 pts × 1.25 s + flyback ~4 s + mean 40 mT B-step (17 s ramp + 3 s settle) ≈ 165 s/row × 190 rows + initial 0 → 0.5 T ramp ≈ 8.8 h; with the session's 5–10% overrun history the realistic figure is the headline. Ends at **8 T, gates at the electron end** — the next step starts from there (rig-card: never re-traverse).

**Checkpoints:** first 3 rows (~12 min: rail / leakage / signal / field-readback tracking); then periodic reads of the armed `hera-watch` digest (~every 2–3 h): partial-fan re-form, LL lines visible, fs fraction sane — continue / abort with ~3 h steps priced. Abort = kernel interrupt (partial fan keeps its rows; magnet holds).
