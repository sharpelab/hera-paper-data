# Live-fan check for fan scoring v2 (2026-09-23)

Read-only analysis of the live vti-02 fans (08-21 r8, 08-22 r8, 08-24 r4, 08-25 r8, 08-23 r6),
with QC0426 06-19 r4 as the clipping positive control. Proposal doc:
`hera/docs/fan-design-scoring-v2.md`. Densities are in the actual frame. R = sr1_X / I_meas,
where I_meas = sr0_X / −1e6. sr1 has no preamp. Every fan steps its fast axis in one
direction only.

| fan | B (rows) | n actual | I | sr1 sens | τ, slope | delay/τ |
|---|---|---|---|---|---|---|
| 0821 | 10→2.4 T (36, 1/B) | 3.13→1.38 (41) | 9.9 nA | 50 µV | 0.1 s, 24 dB | 7.0 |
| 0822 | 1→10 T (101, 1/B) | 2.88→1.42 (61) | 9.9 nA | 100 µV | 0.3 s, 24 dB | 4.0 |
| 0825 | 8→1 T (101, 1/B) | 1.20→3.05 (57) | 49.5 nA | 100 µV | 0.3 s, 24 dB | 7.0 |
| 0824 | 0.75→6 T (40, 1/B) | −0.94→1.89 (46) | 9.9 nA | 1 mV | 0.1 s, 24 dB | 7.0 |
| QC0426 r4 | 0.4→4 T (451, B) | 1.0→4.5 (41) | 20 nA | 10 µV | 0.3 s, 24 dB | 3.3 |

## FFT method (`fft_q1.py`, `q1_eval.py`)

- Mirrors the `sdh_fft` in the session analysis cells (`log=False`).
- Background: a polynomial in B (degree 3 below 30 rows, otherwise 5).
- FFT: direct in 1/B, Hann window, zero-padded to 2048.
- Peak search bands, in units of F_L = 10.34·n: light 0.08–0.33, heavy 0.66–0.895,
  F_L 0.925–1.08.
- Noise floor: the median |FFT| over [1.12 F_L, 0.95 Nyquist]. A peak counts as present at
  SNR ≥ 4.
- light_true: the peak lies within max(0.5 δF, 0.75 T) of the observed light curve and at
  or above 0.75 δF.
- split: heavy and F_L both present, with a dip below 0.8 between them and a separation of
  at least 0.5 δF.

## Tone frequencies

- Observed light fraction, F_light/F_L = 0.0394·n + 0.1235, fitted on 0825 over [1, 8] T.
- Observed / model: 1.29 at n 1.4, 1.11 at 2.0, 1.08 at 3.0.
- The Luttinger sum closes within 0.3 T.
- The F_L tone over 10.34·n is 1.007 (0821), 1.02 (0822) and 0.95 (0825), so 08-25's
  n_scale is ≈ 0.95.

## Detection vs window

In the k columns, "mod" counts columns passing on the model tone and "obs" on the observed
tone.

| fan, window | δF (T) | columns | light_true | F_L present | split | k ≥ 1 mod / obs | k ≥ 2 mod / obs |
|---|---|---|---|---|---|---|---|
| 0821 [2.4, 10] | 3.16 | 41 | 17 | 30 | 3 | 29 / 35 | 6 / 11 |
| 0822 onset 2.0 | 2.50 | 61 | 31 | 60 | 15 | 51 / 61 | 17 / 25 |
| 0822 onset 1.53 | 1.81 | 61 | 27 | 60 | 43 | 60 / 61 | 36 / 45 |
| 0822 [1, 10] | 1.11 | 61 | 50 | 60 | 60 | 61 | 55 / 61 |
| 0825 onset 2.0 | 2.67 | 57 | 26 | 43 | 18 | 41 / 49 | 15 / 21 |
| 0825 onset 1.53 | 1.89 | 57 | 49 | 54 | 40 | 49 / 57 | 30 / 37 |
| 0825 [1, 8] | 1.14 | 57 | 56 | 57 | 54 | 57 | 45 / 54 |
| 0824 electron side [2, 6] | 3.0 | 26 | 5 | 0 | 0 | 2 | 0 |

Detection rate against model k, pooled over all windows of 0821, 0822 and 0825
(10 nA / 50 nA):

| k | ≤ 1.0 | 1.0–1.25 | 1.25–1.5 | 1.5–2.0 | 2.0–2.5 | 2.5–3.0 | 3.0–4.0 |
|---|---|---|---|---|---|---|---|
| light_true | 0.07 / 0.10 | 0.35 / 0.41 | 0.18 / 0.35 | 0.42 / 0.64 | 0.68 / 0.96 | 0.76 / 0.81 | 0.91 / 1.00 |
| split | 0.00 / 0.08 | 0.09 / 0.19 | 0.16 / 0.27 | 0.36 / 0.51 | 0.45 / 0.71 | 0.56 / 1.00 | 0.85 / 0.97 |

On the observed tones, the 50 % points are k ≈ 1.7 (light) and ≈ 2.2 (split).

## Per-tone onsets (`onsets.py`, `tone_onsets.csv`; `hera.analysis.sdh_onset`)

- F_L tone median: 1.53 T (0825), 1.86 T (0822).
- Heavy tone: 1.1–1.4 T.
- Light tone: present at the 1.0 T record edge in 14/14 tracked columns in 0825 and 18/18
  in 0822.
- 0825 over [1, 1.53] T: heavy present in 55/57 columns; light in 58–100 % of columns
  wherever n ≥ 2.4.

## Clipping and quantization (`quant2.py`, `quantization.csv`, `clip_quant_noise.csv`)

The reading grid is LSB = 2^(⌈log₂ sens⌉ − 15). Over-range readings pin at 1.092 × sens.

| run | max\|X\|/FS | ≥ 0.95 FS | LSB/noise | oscillation rms / LSB (median / min) |
|---|---|---|---|---|
| 0821 | 0.31 | 0 | 0.055 | 363 / 194 |
| 0822 | 0.097 | 0 | 0.17 | 165 / 81 |
| 0825 | 0.34 | 0 | 0.15 | 504 / 305 |
| 0824 | 1.092 | 0.65 % (only near charge neutrality) | 1.61 | 6.5 / 2.1 |
| QC0426 sr1 | 1.092 | 17.35 % | 0.025 | 392 / 100 |

- Clipped point: |X| ≥ 0.95 sens.
- Quantized channel: LSB/σ_V ≥ 1, i.e. sens ≥ 1 mV at τ 0.1 s or ≥ 2 mV at 0.3 s.
- No per-point quantization definition fires on any run.

## Noise (`noise_q.py`, `ynoise.py`, `tau_pair.py`)

Measured on the quadrature channel at low field.

| run | τ | I | σ_V | σ_R | input-referred |
|---|---|---|---|---|---|
| 0821 | 0.1 s | 9.9 nA | 34 nV | 3.4 Ω | 38 nV/√Hz |
| 0824 | 0.1 s | 9.9 nA | 37 nV | 3.7 Ω | 42 nV/√Hz |
| 0822 | 0.3 s | 9.9 nA | 22 nV | 2.2 Ω | 43 nV/√Hz |
| 0825 | 0.3 s | 49.5 nA | 21–26 nV | 0.5 Ω | 45 nV/√Hz |
| QC0426 | 0.3 s | 20 nA | 19 nV | 0.95 Ω | 37 nV/√Hz |

- Voltage noise doesn't depend on current.
- It scales about as 1/√τ (a factor of 1.55 for 3× τ).
- The FFT floor is 2.5–12× the white-noise level. Going from 10 to 50 nA and 4τ to 7τ lifted
  the light-peak SNR only 3.2× (10.6 → 33.4).

## Settling (`settle.py`, `settle.json`)

- 24 dB on every channel.
- Unsettled step fraction: 0.43 at 4τ, 0.08 at 7τ.
- No row-start lag in any fan: the regression slopes sit within the interior-point control.
- In-row lag can't be measured because no fan sweeps the fast axis in reverse.

## Composite R(n, B) (`composite.py`, `composite_*.csv`)

- Coverage: n 1.4–3.0 over 0–10 T with 3–5 sources per bin; above 3.15 there is none; below
  1.38 only up to 8 T.
- Worst point: 1558 Ω (n 1.47, 10 T, a quantum-Hall peak). The 99.9th percentile over the
  window is 915–962 Ω.
- Minimum safe sens: 20 µV at 10 nA, 100 µV at 50 nA.
- Every live fan had at least 3× headroom.
