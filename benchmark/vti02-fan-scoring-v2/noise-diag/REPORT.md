# Inter-session noise on vti-02: diagnosis (agent, 2026-09-23)

## Headline

The missing variable is an interference line at **14.9935 Hz**. It is the 3rd harmonic of a
source at about 4.998 Hz; a 4.998 Hz line is also present in the 1-PLC gate currents. It enters
the lock-in at |f_ref − 14.9935|:
- +1.216 Hz at f_ref 13.777 (vti-02);
- +1.9935 Hz at f_ref 13.000 (QC0426 in June). This is Zack's "~2 Hz".

The 1-PLC / 10-PLC amplitude ratio is 5–10× observed. A 15 Hz line predicts 7.1×; a real 1.2 Hz
line would give 1.02×.

- **Amplitude:** about 95 pA, an additive current, in every session at base temperature
  (96 / 80 / 118 / 94 pA). It falls to about 33 pA above 9 K.
- **Sources carrying it:** both gate currents (15–30 pA), which points to a ground loop.
- **Filter:** it follows H(f0; τ) exactly. Input-referred it is the same at τ = 0.1 and 0.3,
  with a raw ratio of 17× against a predicted 15.6×.
- **Second component:** a broadband band about 0.7 Hz (w ≈ 0.3 Hz) from the reference. Its
  amplitude g(B) grows with field: 7 nV at 1 T, 110 at 3 T, 159 at 5 T, 54 at 10.5 T, with a
  peak near 5–5.5 T. It is random: it doesn't repeat between runs, and it shows equally in X
  and Y.
- **Correction:** the earlier "fast axis white, excess only along B" pattern was an artifact of
  aliasing and the window. With f0·dt mod 1 ≈ 0.99 (0821) or 0.01 (0824), the line lands only
  between rows.

## Model (`model2.py`, `fit2.json`)

V = white 46 nV/√Hz + line + band.
- **Line:** H(1.21628 Hz; τ) · i_n · Z_t(B) · sin(2π f0 tᵢ + φ), evaluated at each point's
  real timestamp tᵢ, with i_n ≈ 95 pA and Z_t = 10 Ω + 470 Ω/T·|B|.
- **Band:** g(B) · ∫L(f)|H(f; τ)|² df, where L is Gaussian at ±0.71 Hz with w 0.29 Hz.
- **Fit:** 13 parameters, 66 statistics, 14 runs. RMS log error is 0.32 on the fitted runs and
  0.42 held out (15 % low).

Session metric, live / full model, in nV/√Hz:

| session | live | model | low-field window, live / model |
|---|---|---|---|
| 0825 | 54 | 53 | 52 / 50 |
| 0822 | 98 | 56 | 85 / 50 |
| 0821 | 173 | 106 | 90 / 97 |
| 0824 | 180 | 105 | 148 / 96 |

Unexplained:
- The gap above 5 T, which is row-to-row structure. Real slow quadrature signal at large row
  spacing may be counted as noise here.
- A 0822 episode between 109 and 130 min, where sr0 rises 42 → 156 pA.
- The 0824 figure has no leak correction.

## τ and delay predictions (`taugrid.txt`)

Per-point rms at 5 T (at 10 nA the equivalent in Ω is shown):

| τ | 1 ms | 10 ms | 0.1 s | 0.3 s | 1 s |
|---|---|---|---|---|---|
| per-point rms | 462 nV | 255 nV | 130 nV | 45 nV | 15 nV |
| at 10 nA | 46 Ω | 26 Ω | 13 Ω | 4.5 Ω | 1.5 Ω |

- The line passes the filter almost fully at τ ≤ 10 ms and is gone by 0.3 s.
- Row-to-row noise reaches up to 2× per-point where the line aliases near DC.
- The 24 dB step residual is 0.98 at delay/τ 1, 0.65 at 3 and 0.08 at 7.

## Settings

Lock-in reserve, sync, notch, coupling, shield and harmonic are never recorded. Gate sweeps use
1 PLC, and the sanity checks use 10 PLC. Point period: 0.812 s (0821), 1.300 s (0822),
0.832 s (0824), 2.224 s (0825). The overhead is 0.11 s.

## A rig measurement to settle what's left

Park at 5 T and at 0 T, with the drive on and then off. Record sr1, sr0 and a 1-PLC gate
current for 10 minutes each, at f_ref 13.777 Hz and at 17.3 Hz (≥ 2 Hz from every 5 Hz
harmonic).
- **Line:** it should vanish at 17.3 Hz.
- **Band:** if it also vanishes, it belongs to the 5 Hz family. If it stays, it comes from the
  field.
- **Source:** power-cycle the candidate 5 Hz sources while watching the gate current.

## Contradicts earlier reports

- The fast-axis-white pattern is an artifact.
- Noise is not a session constant. It is set by B, τ and the point timing.
- The simulator should drop `e_excess` and use `model2.simulate` with each design's own timing.
