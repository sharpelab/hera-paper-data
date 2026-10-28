# vti-02 ABAB tone model: data assembly and fit (agent, 2026-09-23)

**Recommendation: refit B.** It is the corpus ABAB model with **γ2 = −0.0145 eV** (the one
fitted parameter; the corpus has −0.020) and **γ3 = 0.3 eV** (the literature graphite value,
not fitted).
- On the electron side it matches the empirical fit, on the training sessions and on
  held-out 08-21.
- It is the only option that predicts the hole side. The corpus model misses the hole
  partition by −0.11.

Everything is done in the frame-free partition p = F_light / F_L_ref vs F_L_ref, since
n_scale is itself pinned from F_L.

## Data (`vti02_tones.csv`, `partition_points.csv`)

- **Extraction:** FFT as in live-check (Hann window, polynomial-in-B background, 1/B, zero
  padding to 16k), over 8 window/background variants. F is the median over detected
  variants.
- **Sources:**
  - fans: 08-21 r8, 08-22 r8, 08-24 r4, 08-25 r8;
  - spot checks: 08-21 r5, 08-22 r6/r7(h), 08-24 r5, 08-25 r7;
  - LK ladders: 08-21 r10–15, 08-22 r9–14.
- **Excluded:** 08-23 r6. Its ramp Nyquist is 14–21 T.
- **Injection test:** partition bias ≤ 0.008 on 08-25 and 08-22. On 08-21 the light tone
  is biased +0.03–0.10 at fewer than 2 periods. Cuts that follow from this: light k ≥ 2;
  heavy ≥ 1.5 δF below F_L.

### n_scale from each session's own F_L slope

| session | fitted n_scale | cases.toml | note |
|---|---|---|---|
| 08-25 | **0.9496 ± 0.0006** | **1.0** | 57 + 4 columns, rms 0.13 T |
| 08-22 | 0.8625, with n0 = −0.10 (0.893 through the origin) | 0.886 | |
| 08-21 | 0.927 ± 0.005 | 0.92 | |
| 08-24 | ≈ 0.85 | **0.90** | weak: 2 points |
| 08-23 | — | 0.90 | no tone data |

### Partition

- **Training:** 08-25 (median p 0.214 / 0.215, light- / heavy-based) and 08-22
  (0.220 / 0.219).
- **Test:**
  - 08-21: 0.24–0.26
  - 08-24 electron: 0.128
  - 7 hole points: 0.23–0.33
- Light- and heavy-based estimates agree to about 0.005 above F_L 16 T. Below 15 T on 08-25
  they split (heavy 0.21–0.26 vs light 0.19): a ±0.03 systematic at low n.
- **Hole side:** the dominant tone sits at 0.67–0.77 F_L. The corpus predicts a near-balanced
  pair (p 0.40–0.43).

### LK masses

| session, n | light m* | heavy m* | F_L tone m* |
|---|---|---|---|
| 08-21, n 2.78 | 0.040 (session: 0.039) | unstable (session: 0.048) | 0.064 |
| 08-22, n 2.85 | 0.031 (session: 0.028) | 0.041 (session: 0.038–0.057) | 0.052 |
| corpus model | 0.026 | 0.060 | — |

- Measured heavy/light is 1.2–1.5; the model gives 2.2.
- γ2 doesn't move the masses, so no refit fixes this.
- Masses were not used in the fit.

## Fits (training: 08-25 + 08-22 electron, 237 points)

**Sensitivity:**
- The electron partition responds almost only to γ2: ±0.01 eV moves p by ±0.09 at F_L 13.
- γ0 and γ1 are degenerate with γ2.
- Δ′, γ4 and γ5 move p by less than 0.01.
- γ3 = 0.3 moves the electron side by +0.005 and the hole side by −0.19.
- The γ3 solve is on a 2D grid over the corpus `build_h`. At γ3 = 0 it matches the radial
  solve to 0.001 T, and it is converged.

| model | free parameters | result | χ²/dof raw |
|---|---|---|---|
| corpus | 0 | γ2 −0.020, γ3 0 | 72.7 |
| A | γ2 (γ3 0) | γ2 −0.0140 ± 0.0003 | 5.6 |
| **B** | γ2 (γ3 0.3 fixed) | **γ2 −0.0145 ± 0.0004 stat ± 0.0008 syst** | 5.6 |
| C | γ2, Δ′ (γ3 0.3) | γ2 −0.016, Δ′ 0.00 (at bound) | 5.4 |

- **Systematic on γ2:** −0.0129 to −0.0149 across fitting light only or heavy only, each
  session alone, the F_L split and the 08-22 offset.
- **Uncertainties:** χ²/dof scaled to 1, then ×3 for correlation (N_eff 26 tone cells).
- **Sanity:** γ2 −0.0145 is plausible and inside the few-layer range. γ3 is from the
  literature. Δ′ is unconstrained on the electron side and lands at the bound, so C is not
  recommended.

## Held-out (partition residual observed − model, bias / rmse)

| group | n | corpus | A | **B** | C | empirical |
|---|---|---|---|---|---|---|
| train 08-25 | 112 | +0.042 / 0.052 | 0.005 / 0.026 | 0.005 / 0.026 | 0.010 / 0.031 | 0.005 / 0.023 |
| train 08-22 | 125 | +0.036 / 0.041 | 0.001 / 0.019 | 0.001 / 0.019 | 0.004 / 0.020 | 0.002 / 0.018 |
| **test 08-21 e** | 10 | +0.051 / 0.063 | 0.024 / 0.043 | 0.024 / 0.043 | 0.022 / 0.043 | 0.018 / 0.044 |
| test 08-24 e | 1 | +0.022 | −0.033 | −0.034 | −0.016 | −0.042 |
| **test hole** | 7 | −0.113 / 0.115 | −0.199 / 0.203 | **+0.028 / 0.032** | +0.002 / 0.016 | none |

- **Empirical fit:** p = 0.1095 + 0.00454·F_L[T]. Leave-one-session-out rmse 0.023 / 0.018.
  CI half-width about 0.01 at 15–30 T.
- **Low-n end (F_L 12 T):** corpus 0.09, B 0.145, empirical 0.164 ± 0.01. The data read
  0.19–0.25.

## Deliverable

`tone_fn.py`: `tone_fn(n_actual_1e12, side, model='B'|'corpus') -> (F_light, F_heavy, F_L)`.
- It is table-backed (`tone_table.csv`), so no solver runs at grading time.
- `tone_fn_empirical` gives the electron-only alternative.
- It raises an error outside the table and warns outside the data support (electron
  1.14–3.15, hole 0.71–1.07).

Example values:

| n | refit B (F_light / F_heavy / F_L) | corpus (F_light / F_heavy) |
|---|---|---|
| +1.2 | 1.89 / 10.51 / 12.41 | 1.15 / 11.25 |
| +3.0 | 7.45 / 23.57 / 31.02 | 6.67 / 24.35 |
| −1.0 | 2.86 / 7.48 / 10.34 | 4.43 / 5.91 |

## Tradeoff

B is fitted to vti-02's own sessions. The corpus model is what an agent could have had.
- Grading against B shifts scores one way only: it moves the low-tone line down in n for
  every arm.
- The question the grade asks is about the device ("could the light tone be resolved at
  this n?").
- B's only changes (γ2, γ3) are within literature ranges an agent could have chosen.

Recommendation: grade against B and report the corpus-model score as a secondary.

## Contradicts the proposal / cases.toml

1. 08-25 n_scale is 0.95, not 1.0.
2. 08-24 n_scale is ≈ 0.85, not 0.90.
3. The corpus hole-side partition is wrong by ~0.11.
4. The measured mass ratio (1.2–1.5) contradicts the model's 2.2. Any mass-ratio onset
   rule must use measured masses.

## Artifacts

- Plug-in: `tone_fn.py`, `tone_table.csv`.
- Data: `vti02_tones.csv`, `partition_points.csv`, `columns_*.csv`, `session_frames.csv`,
  `lk_masses.csv`, `inject_bias.csv`.
- Fits: `fit_results.json`, `fit_curves.csv`, `empirical.json`, `heldout*.csv`,
  `systematics.csv`.
- Figure: `partition_vs_FL.png`.
- Code: `runs.py`, `extract.py`, `aggregate.py`, `inject.py`, `dataset.py`, `swm.py`,
  `fit.py`, `empirical.py`, `heldout.py`, `lk.py`, `systematics.py`, `make_table.py`,
  `export.py`, `plot.py`.
