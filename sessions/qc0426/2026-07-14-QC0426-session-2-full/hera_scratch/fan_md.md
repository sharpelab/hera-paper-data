## HERA — Step 4: D = 0 Landau fan, electron side (`landau-fan-vti`)

Spot checks done (runs 5/6, analysis in ana). **Side choice: electron** — computed onset 1.33 T vs 3.5 T (hole), i.e. twice the 1/B record → δF ≈ 1.6 T per column, which is what the 53 / 67 / 14 T tone separation needs. The fan's job: per-column peak sets vs the Hall-pinned F_L(n), the Luttinger partition f_B(n) + f_s(n) = F_L(n), tone n-tracking (Onsager), and the QH corner for the lever-arm upgrade.

**Design (floored):**
- **Fast axis**: paired n-line at D = 0, n = +2.0 → +6.3×10¹² cm⁻², **51 columns** (δn = 0.086e12; ray-Nyquist ≥2/spacing holds for B ≥ 2.5 T — Středa/ray reads below 2.5 T are out of scope, FFT reads unaffected). Gate vectors from the run-4 calibration; all inside validators.
- **Slow axis**: `field_invB(1.33, 8.0, 126)` — B_lo = the **computed** run-6 onset; Δ(1/B) = 5.0×10⁻³ → unaliased to 100 T: all claim tones (≤ 68 T) at ≥ 1.5× Nyquist; the 2f_B ≈ 104 T harmonic aliases to ~96 T, inside a quarantined 90–100 T band stated per column (checked at n_max = 6.3e12 — not inherited).
- **Sensitivity resize for the worst corner** (low-n × high-B, QH regime ν ≈ 10): sr1/sr2 1e-4 (5 kΩ ceiling vs ~3 kΩ expected LL peaks at n = 2e12, 8 T), sr3 2e-4 (10 kΩ vs R_xy ≈ 2.5 kΩ), sr0 5e-2. Trade: start-corner signal (60 Ω at 6.3e12, 1.33 T) reads at ~1 % of range — grainy in the onset rows, clean where the claims live.
- **Coverage trade stated**: hole side not fanned (weaker window, δF 6.5 T — spot check run 5 is its record); Onsager-overlay claims floored at |n| ≤ 3.5e12 (model validity clamp); n > 3.5e12 carries the algebraic partition + tone-resolution claims and the run-5/6 spot-check cross-check at 6.4e12.

**Cost** (per-point 2.3 s measured, runs 4–6): 126 rows × (51 × 2.3 s + ~15 s turnaround) ≈ 4.6 h + 6.7 T traverse ≈ 49 min + positioning ≈ **5.5–6.5 h** (done ≈ 13:00–14:00). Checkpoints: first 3 rows (~15 min), then interim per-column FFT at ~½ (B ≈ 2.5 T… uniform-1/B front-loads rows), then completion. Ends at 8 T, gates parked at 0.

Preconditions: T < 2 K, magnet at ~0.25 T (parked by run 6), Si = 0. Tag: `landau-fan-vti`.
