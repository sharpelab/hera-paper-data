## HERA — Landau fan, hole side, D = 0 (`landau-fan-vti`)

Investigation step 4: the dense version of run 6. **n = −1.5 → −6.0e12** (hole side per SC verdict), D = 0 paired n-line fast axis; **B slow, uniform-1/B** (`field_invB`), 1.6 → 8 T ascending — magnet sits at 1 T (SC2 endpoint), fan starts where it is and **ends at 8 T** for a ride-down grid-change cut (Verify: alias screen).

**Design (recipe step-1 checks, stated):**
- **N_B = 101** rows, Δ(1/B) = 5.0e-3 /T = ⅓-Nyquist at the *measured* partition sum 66.4 T (tightened from the 62 T nominal). B_lo = 1.6 T: onset measured 1.41 T (run 7 sr2, `sdh_onset`) / ~1.8 T eye (run 6); 1.6 splits the band — low-B rows are the fan's cheapest (14 mT steps).
- **N_n = 87** (Δn = 0.052e12): ray-Nyquist 3.0 rows/period at the 1.6 T, n = −6e12 corner (≥2 floor, at the prefer-3 mark). δF = 1/(1/1.6 − 1/8) = 2.0 T → partition claims trusted for |n| ≳ 2.5e12 (f_ML ≥ 2·δF); low-n columns are shape/onset data, stated floor.
- **Overlay validity**: Onsager model clamp |n| ≤ 3.5e12 — overlay runs on that sub-window only; the Luttinger partition check (algebraic) uses the full window.
- **Dynamic range (worst corner −1.5e12 × 8 T, R₀ = 127 Ω × MR ~×20–30 ≈ 2.5–3.8 kΩ)**: split sensitivities — **sr1 2e-4** (10 kΩ, no-clip channel, owns low-|n| columns), **sr2 5e-5** (fine digitization, owns high-|n| columns; its low-n × high-B corner will clip → excluded from sr2 reads), **sr3 2e-4** (Rxy → 3.3 kΩ at corner). Every corner has one clean channel.
- **Dwell**: fast_delay = 1.8 s (6τ — n-axis feeds per-column FFT, recipe step 7); slow_delay = 1; `magnet.settle_s` 1.2 for the fan (restored after).

**Wall-clock**: 101 × (87 × ~2.05 s + ~5 s turnaround) ≈ 5.1 h + B traverse 6.4 T ≈ 47 min + positioning ≈ **6.0 h; realistic 6.3–6.6 h** (session-calibrated rates: 3.7 s/pt SC runs, 1.45 s/pt gate sweeps). Overnight run, ETA ~03:00.

**Checkpoints**: first rows (clip/drain/leakage), then every ~90 min: re-formed partial fan + per-column FFT on landed rows — continue/abort on: sensitivity railing beyond plan, drain sag, T excursion, or frequency content collapsing (acquisition fault). Ends parked: gates 0, B = 8 T.
