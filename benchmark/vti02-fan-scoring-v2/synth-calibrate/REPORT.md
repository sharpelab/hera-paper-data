# synth_fan calibration to vti-02 (agent, 2026-09-23)

The module is `vti02_sim.py` with its parameters in `vti02_sim_params.json`. It is calibrated on
08-25 r8 and 08-22 r8 and validated on 08-21 r8 and 08-24 r4. The scripts and logs are in `work/`.

```python
simulate(B_grid, n_cols, I_A, tau_s, sens_V, rng, tone_fn=None, *, mass_fn=None, params=None,
         slope_db=24, delay_s=None, n_scale=1.0, return_clean=False) -> R[row, col]
```

- `n_cols` is on the F_L = 10.3392·n frame.
- Tone sets: `corpus_tones` (the default) or `observed_tones`, or any `tone_fn` / `mass_fn`
  plug-in.
- Runtime is 3–13 s per fan.

## Model

It is a Landau-level model of two g = 4 pockets (light and heavy) at a fixed total density:
- Gaussian Landau levels with Zeeman splitting, and the chemical potential solved at every
  field point. A small reservoir DOS (`res_dos`) sets the pinning.
- Conductivity is two-band Drude weighted by the thermal-averaged ⟨DOS²⟩, then inverted.
- Harmonics, quantum-Hall zeros, the difference tone and the **F_L tone** all come out of the
  physics. The F_L tone comes from pinning at integer total filling (4k); no breakdown term
  is needed.
- Empirical additions:
  - low-filling enhancement: ×2.4 below ν_tot 12;
  - zero-field negative MR, taken from the 08-25 B = 0 gate map.
- Acquisition effects: the SR830 24 dB response along the fast axis, noise, clipping at
  1.092·sens, and LSB quantization.

## Parameters

| parameter | value | source |
|---|---|---|
| n_scale 08-25 / 08-22 | 0.9505 / 1.0163 | pointwise fit |
| light fraction | 0.2014 + 0.0625 (n − 2) | pointwise fit |
| **T_e** | **4.9 K** | statistics fit |
| level widths | light 0.188, heavy 0.090 meV/√T (T_D ≈ 0.09 / 0.05 K) | statistics fit |
| density spread δn | 1.41 % | statistics fit |
| G / mobility ratio / c_xy | 0.23 / 0.97 / −0.032 | statistics fit |
| res_dos | 0.067 | statistics fit |
| enhancement a / ν_c / w | 1.37 / 2.52 / 0.093 | statistics fit (a); pointwise (ν_c, w) |
| noise | e_n 40 nV/√Hz, excess **87 nV/√Hz** (from 08-22) | measured |

The statistics fit reached a mean squared log-ratio of 0.034.

## What makes the FFT floor

- **Signal content, mostly.** The noise-free model reproduces 70–90 % of the live floor in the
  windows starting at 1.53 and 2 T. That floor is harmonics and combination tones of
  non-sinusoidal quantum-Hall structure, including a bump at 2 F_L. It doesn't scale with I
  or τ.
- **Session-dependent excess noise.** In the quadrature channel it is 55 / 95 / 165 / 146
  nV/√Hz for 08-25 / 08-22 / 08-21 / 08-24. It is heavy-tailed (kurtosis 4.6) and
  uncorrelated between columns.
- **Ruled out:**
  - phase jitter: it moves X by less than 0.3 %;
  - common row offsets;
  - magnet noise: about 5 µT row to row.

## Validation on held-out fans

Observed tones, default noise, 3 seeds (seed spread ±3 columns). Columns detected, live / sim:

| fan, window | columns | light_true | split | F_L | heavy |
|---|---|---|---|---|---|
| 08-21 [2.4, 10] | 41 | 17 / 11.3 | 3 / 2.0 | 29 / 39.3 | 5 / 2.0 |
| 08-24 o2.0 | 26 | 5 / 3.0 | 0 / 0 | 0 / 0 | 3 / 2.3 |
| 08-24 o1.53 | 26 | 8 / 6.7 | 0 / 0.7 | 7 / 5.3 | 8 / 7.0 |
| 08-24 full 0.75 | 26 | 9 / 12.7 | 4 / 5.0 | 10 / 8.7 | 13 / 18 |

- **Per-column SNR, sim / live (medians, held-out):** light 0.66–0.85, heavy 0.52–0.66,
  F_L 0.39–1.32.
- **Session noise:** with each session's own noise, 08-21 F_L drops to 34 (live 29).
- **Detection vs k:** light_true in sim is 0.65 / 0.81 / 0.88 at k 2–2.5 / 2.5–3 / 3–4, against
  live 0.64 / 0.79 / 0.87. Below k 2 the sim is low (0.19–0.22 vs 0.29–0.34). This curve
  pools calibration fans with 08-21.
- **Floor shape:** it matches on all four fans, including the 2 F_L bump. The tail above
  2.3 F_L is 30–40 % low.
- **Onsets:** 08-25 F_L 1.53 / 1.53 T, light 1.0 / 1.0 T, heavy 1.13 / 1.40 T.
- **Amplitude tails:** too high on 08-25 (99.9th percentile 901 vs 666 Ω) and too low on 08-21
  (974 vs 1200 Ω).

## Failures

1. **Heavy tone, and the light tone at high field, are under-predicted.** The chemical
   potential is pinned too hard at high field, which pushes heavy weight into F_L.
2. **Corpus tones wreck light_true** (08-25: 11 vs 56). That is a tone-model problem; use
   observed or refined tones.
3. **Too little randomness.** Excess noise is the only real random knob, so the default 87
   penalizes 08-25.
4. **Unvalidated outside n 1.2–3.15.** 08-24's n_scale is assumed to be 1.0.
5. **Two choices were in-sample:** the pick among fitted parameter sets was made with 08-21
   in view, and the noise check used the held-out fans' own quadrature channels.

## Contradicts the proposal

- **Noise isn't a fixed 40 nV/√Hz.** The effective noise is 55–165 nV/√Hz, and part of the
  floor is signal harmonics that don't scale with I or τ. So SNR ∝ I·√τ overstates what extra
  current or τ buys.
- **Damping is thermal** (T_e ≈ 4.9 K) plus density spread. Level broadening comes out
  negligible, so "Dingle calibrated on live fans" isn't the right knob. This conflicts with
  onset-clip's per-tone τ_q fit, which assumed T_e 1.2 K.
- **F_L comes out of quantum-Hall pinning.** No breakdown is needed, which weakens the
  session notes' breakdown reading at the model level.
- **Agrees:** 08-25's n_scale is 0.95.
