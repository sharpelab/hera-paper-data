# Ideal-observer grader prototype (agent, 2026-09-23)

## Headline

**Rig noise doesn't limit vti-02 fans; model error does.**
- **Noise-only:** the ideal observer gives 10³–6·10⁵ nats per fan.
- **With a tone-amplitude model error** σ_a = 0.5 (from live/sim amplitude ratios, sd 0.42–0.52), coherent within one Fourier cell, the evidence saturates on its own: about 1/(2σ_a²) ≈ 2 nats per resolved cell of the light-tone dispersion.
  - Example: 08-22 gives 9.5 / 9.1 / 9.0 / 9.0 / 9.1 nats at ×0.25 to ×4 columns.

That is a derived, smooth version of the tone-cells rule. It reduces to an analytic formula:

**E ≈ [1 + Σ over covered, Nyquist-sampled electron columns of ΔF_light · W_eff] / (2σ_a²)**

W_eff is the energy-weighted aperture of the tone pattern in 1/B. The simulator is needed only for the per-column threshold z_j > 1/σ_a, which bites only at I ≈ 1 nA with τ ≤ 30 ms, or at extreme quantization.

## Method

- **H_B:** Halder tones and masses. **H_R:** one g = 4 pocket at F_L with the ABCA m\* (0.08–0.31, `orbits_for('ABCA')`) and the heavy width. Both go through `vti02_sim.clean_R`, with a step response at the real timing and clipped points masked.
- **Quantization** enters as a Fisher-equivalent variance, because the noise dithers.
- **Noise:** `vn.point_sigma` (white 46.5, comb, jitter, 2f ripple; band off). The covariance is block-diagonal by row, and the per-column diagonal is used.
  - The exact row-block check moves KL by ×0.79 to ×1.63; E is unchanged because it saturates.
- **Tone-only KL:** project μ_B − μ_R off an ABCA span, i.e. a degree-5 B polynomial plus F_L harmonics m ≤ 3 with Legendre(1/B) envelopes. KL_j = ½‖P⊥(tone)‖².
  - The full residual gives 10⁴–10⁵ nats, dominated by quantum-Hall fine structure, and leaks under nuisance variations.
- **Robustness:** env_lo/hi, template mismatch, n_scale ±3 %, T_e 3/6 K, a Dingle reading, widths ×0.5/×2, comb Q ×0.5/×2. Each moves E by ≤ 15 %, and the corner combines the worst of each.
  - Mimic check: ABCA worlds put spurious tone content at 0.05–0.09 (median) and 0.15–0.26 (90th percentile).
- **Correlation across columns:** d′² = zᵀ(I + σ_a² Z K Z)⁻¹ z, with an OU kernel exp(−2|Δx|) where x = cumulative F_light·W_eff.
  - Without the cap, KL grows ∝ columns (08-22: 691 → 21,556 from ×0.25 to ×4).

## Results (E = corner + Nyquist gate; E\* = 8 nats; Q = min(1, E/E\*))

| design | h | E | Q | cells075 | sim b |
|---|---|---|---|---|---|
| haiku r3w0gf (0.3–10 T) | 12.5 | 22.8 | 1.00 | 1.00 | 1.00 |
| sonnet 192335 | 7.9 | 19.7 | 1.00 | 0.60 | 1.00 |
| opus-none ou2xbh | 3.1 | 10.8 | 1.00 | 0.80 | 0.52 |
| opus-corpus rkg9dn | 4.8 | 9.6 | 1.00 | 1.00 | 1.00 |
| astra #1 (7 columns) | 1.8 | 9.5 | 1.00 | 0.27 | 0.23 |
| live 08-25 r8 | 4.8 | 8.6 | 1.00 | 0.80 | 1.00 |
| live 08-22 r8 | 3.8 | 7.3 | 0.91 | 0.80 | 0.88 |
| haiku 3xn8hn #1 (50 mV) | 4.4 | 6.7 | 0.84 | 0 | 0 |
| live 08-24 r4 | 1.2 | 6.2 | 0.77 | 0.07 | 0 |
| 2.4 T starts (08-21 r8 and the 08-21-cut episodes) | 1.1–4.9 | 3.9–5.5 | 0.48–0.68 | 0 | 0.20 |
| live 08-23 r6 ramp | 0.94 | 4.2 (9.4 without the gate) | 0.53 | 0 | – |
| sol-none ls25bv (linear B) | 2.4 | 4.0 (8.1 without the gate) | 0.51 | 0 | 0 |
| live 08-25 r5 (12 rows) | 1.4 | 0 | 0 | 0 | – |

- **Rank agreement with E** (Spearman / Kendall):
  - cells075: 0.74 / 0.55 (n = 35);
  - synth-score sim b: 0.62 / 0.44;
  - generator sim b: 0.74 / 0.54.
- **Pareto frontier:** opus-none, 08-24 and astra #1 at about 1.2–1.8 h, then sonnet 200401 at 3.6 h (15.8 nats).
- **History checks:**
  - Pass: the 2.4 T starts are modest and nonzero.
  - Pass after the Nyquist gate: 08-23 r6 is low.
  - Pass: 08-25 r8 is high.
  - Near pass: 08-22 r8 is 0.91.
  - **Fail: 08-24 r4 is mid (0.77).** Its design carried discriminating content: live-check detected the light tone in 9 columns and the split in 4. The wrong call was an analysis failure, which design grading can't see.
- **Where it disagrees with the current grader:**
  - One column per cell suffices. A per-column nugget η would reintroduce replicates as a policy choice.
  - Low B_min earns credit because the simulator's tones persist below 0.75 T, below the empirical onset.
  - A 50 mV sensitivity isn't fatal (the staircase keeps the tone).
- **Acquisition** (08-22 grid): E stays 8.0–9.3 for I ≥ 10 nA at every τ from 1 ms to 1 s. It collapses only at 1 nA with τ ≤ 30 ms. It is a threshold, more lenient than the generator's FFT-detection factor.

## Proposed E\* = 8 nats (≈ 4 resolved cells)

- The correct calls came at 7.3 and 8.6; the weak or wrong ones at 4.7 and 6.2.
- Gaussian Bayes error Φ(−√(E/2)) ≈ 2 %.
- A strict alternative is 13 nats: P(LLR > ln 100) ≥ 95 %.

## What still comes from the corpus or session choices

The Halder tones, the ABCA mass, the vti02_sim parameters (fitted on 08-25 and 08-22), n_scale, electron-only coverage, f_ref 13.777 and NPLC 1, σ_a, the degree-5 background (Legendre(1/B) to degree 4 moves E by ≤ 0.6 nats), the Nyquist gate (2 rows per period locally), the tone-only projection, and the vti_noise parameters.

## Knobs

- **Obsolete:** k, the onset clip, the analysis window, tone cells (≤ 3 per cell, 1.0 = 5 cells), the SNR multiplier, the acquisition factor, the quantization multiplier, and the m = 3 high line (replaced by the local Nyquist gate).
- **Remaining:** the tone model, σ_a, E\*, the Nyquist gate (yes/no), and the hours model.

## Runtime

0.1–9 s per evaluation. The robust score (about 11 map pairs) takes 5–200 s per design; 35 designs take about 8 min on 6 cores.

## Files

- Code: `io_core.py`, `score.py`, `inventory.py`, `abca.py`, `scale.py`, `check2d.py`, `compare.py`, `t_*.py`.
- Results: `scores.csv`, `episodes.csv`, `table.md`, `correlations.csv`.
- Supporting data: `columns_base.csv`, `leak.csv`, `scale.csv`, `acq_surface.csv`, `bg_sens.csv`, `check2d.csv`, `timing.csv`, `abca_table.json`, `designs.pkl`.
- Figure: `pareto.png`.
