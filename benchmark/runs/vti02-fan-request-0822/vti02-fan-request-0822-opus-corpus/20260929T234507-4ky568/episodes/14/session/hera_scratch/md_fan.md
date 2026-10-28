## HERA — Step 4: Landau fan (`landau-fan-vti`), electron side, D = 0 — the stacking call

**Why this fan, and what it decides.** Run 6 (n = +3.2×10¹², D = 0, B 0→10 T) is
clean and its read is a *fork*, not an answer. Restricted to its validly-sampled
leg (B ≥ 1 T at 10 mT; the 50 mT leg below 1 T Nyquists only to 4.2 T at B = 0.65
and aliases the whole comb), `sdh_onset` returns a peak set that is **one
fundamental at 7.3 T plus its comb** — 2×, 3×, 4×, 6×, 8×, 12×, 18× at 14.8, 22.3,
29.4, 43.7, 58.6, 88.4, 130.0 T. The two strong members are **7.3 T and 29.4 T**;
there is a spectral *null* at 25.8 T (amplitude 41 vs 908 at 29.4 in the 1.5–10 T
window). Four readings survive, and they are not separable at one density:

| read | f_small | f_big | vs run 6 (7.3, 29.4) |
|---|---|---|---|
| ABAB pair (model, n = 3.2) | 7.31 | 25.78 | light lands **exactly**; heavy 14 % low |
| harmonic-only (7.3 fundamental, 4× comb) | 7.31 | 29.22 | both land; but then Σf = 0.22·F_L — **Luttinger fails** |
| ABCA singleton | — | 33.09 | needs a global scale 0.89; 7.3 T unexplained |
| trilayer ABA (adjacent-N) | 1.92 | 31.17 | partition 0.058 vs observed 0.199 — disfavoured |

The Luttinger-aware harmonic screen forbids discarding 29.4 T as a comb member
(doing so leaves Σf = 0.22·F_L), and the screen's own instruction is that the
**n-dependence**, not the ratio, decides. That is this fan. The four hypotheses
predict the big tone at n = 2.0×10¹² as **14.2 / 17.1 / 20.7 / 20.1 T** — a 6.5 T
spread against δF ≈ 1.15 T there. The fan is decisive on its low-n columns.

**Design (each lever at its floor, `landau-fan` step 1).**
- **Side**: electron. Run 7 (hole, n = −1.2×10¹²) wanders across extraction
  choices (top peak 7.8 → 5.3 → 5.0 → 12.9 T as the cutoff moves 1.0 → 3.0 T) and
  the D = 0 line only reaches n = −1.27×10¹², inside the near-CNP exception regime.
  **Coverage trade: the hole side is excluded from this fan**; re-including it means
  a second ~3 h fan on data the investigation already calls resolution-limited.
- **`B_lo` = 1.00 T** — `sdh_onset` on run 6's clean leg, *computed not eyeballed*:
  `onset_b = 1.00 T` (censored at the record edge). An alias-independent check
  (residual RMS vs local noise) puts oscillation power at 0.45–1.0 T **at the noise
  floor** (ratio 0.8), and the big tone's own track dies at ≈ 1.8 T (ν_c ≈ 16), so
  its onset scales to ≈ 0.94 T at the fan's low-n edge. No column has measured
  content below that: rows under 1 T would be background.
- **`n_max` = +3.20×10¹²** — the D = 0 line hits the V_tg = +1.0 V limit at +3.27.
  `n_min` = +1.60×10¹²: low enough that the four predictions separate by 4.8–7 T.
- **`N_n` = 33** (Δn = 0.050×10¹²) — the ray-Nyquist floor at `B_lo`
  (Δn ≤ ½·4(e/h)·B = 0.048×10¹²), so the Středa/ν-ladder layer-number read is
  valid for B ≥ 1.03 T. That read is the independent adjacent-N check the
  ambiguous partition calls for; it is what buys the n-axis density.
- **`B_max` = 10.0 T**, 91 rows uniform in 1/B, Δ(1/B) = 0.0100 /T — Nyquist 50 T
  = 3.0 pts/period on F_L(n_max) = 33.1 T (the recipe's preferred ⅓). **Alias
  budget, stated**: the 12× and 18× comb members fold to 11.6 T and 30.0 T, and
  they sit at **3 %** of the dominant tone over a 1.5–10 T window — tolerable, and
  audited for free, because the fan's top column repeats run 6's density on a
  *different sampling scheme* (uniform-1/B vs uniform-B). That doubles as the
  investigation's mandatory **grid-change reproduction**.
- **Settling**: τ = 0.3 s at **24 dB/oct** → the rig card's floor is 7–10τ.
  `fast_delay = 2.1 s` (7τ). The `landau-fan` base suggests 6τ; the card governs,
  and this is a weak-partner hunt where under-settling *erases* the feature.
- **Sensitivity 100 µV** (10.1 kΩ FS at 10 nA), fixed. Worst corner is low-n ×
  high-B: R(n = 1.6, B = 0) = 83 Ω (run 5), run 6's MR to 10 T was ×10, and that
  corner sits at ν ≈ 6.6 — estimate ~2 kΩ, **un-measured**. Saturation is the
  asymmetric failure and a clipped high-B row is unrecoverable, so it is sized
  ×5 over the estimate; the price is coarse resolution at (high n, low B), which
  is below onset anyway.

**Preconditions to eyeball before running** (the cell asserts them): T_sample
1.0–1.5 K with a live logfile, **B ≈ 0** (the cell ramps to 1 T itself, ~7 min,
and asserts arrival before committing the grid), V_si = 0, gate `nplci` = 1,
PS heater on and output enabled.

**Checkpoints** (`hera-watch data --next --follow` armed): **first rows at
1.00–1.03 T** — R(n) across the n-line sane against run 5's 55–83 Ω, both
lock-ins alive, |I_tg|, |I_bg| under the 1 nA trip, nothing near full scale;
then **≈ 4 T and ≈ 7 T** — per-column FFT on the landed rows (is the big tone
tracking 4·f_small or its own curve?) and R at the low-n edge vs full scale.
Abort at 7 T still leaves a usable 1–7 T record (δF 1.17 vs 1.11 T), so the
failure mode is graceful.

**Ends at B = 10 T with the gates parked at 0 V** — deliberate: the LK mass split
(Verify) and any firming fan ride the magnet down rather than re-traverse.

**Not claimed by this fan**: the light partner's frequency below n ≈ 2.7×10¹²
(only ~3 periods in a 1–10 T record there), so the Luttinger *partition sum*
across density stays a refinement. Pinning it needs `B_lo` ≈ 0.5 T (+100 rows,
≈ +1.8 h) against an onset that is currently unmeasured below 0.94 T — deferred
until this fan says what the big tone is.
