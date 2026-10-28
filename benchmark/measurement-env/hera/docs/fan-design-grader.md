# Fan-design grader for vti-02

Plan of record (Zack and Aaron's scheme). It grades the Landau fan an agent designs at the
vti-02 replay cuts and the vti-02 live fans. The cuts: the 08-22 state (both spot checks done,
nothing read or drafted), as `vti02-fan-request-0822`, whose brief asks for the fan, and
`vti02-pre-fan-0822`, whose brief does not; and the 08-24 state (before any spot check),
`vti02-pre-fan-0824`. The development frontiers `vti02-fan-design` and `vti02-probe-first` hold
the same states and grade identically. The pre-registration is
`hera/campaigns/vti02-fan-design/prereg.md`; its analysis set is the episodes of
`vti02-fan-request-0822`. It replaces the four scores in `fan-design-grading-review.md`
(side, field resolution, density range, field reach) for the vti-02 cases only: the tones and
onsets are vti-02's, so the QC0426 and vti-01 cases keep the four scores. It is implemented in `hera/graders/fan-design/box.py`
(case `scheme = "box"`); the dev-set rescore is `$HERA_DATA/vti02-fan-scoring-v2/box-rescore/`.
The evidence lives outside git in `$HERA_DATA/vti02-fan-scoring-v2/` (start
at `SYNTHESIS.md`; each topic dir has a `REPORT.md`) and `$HERA_DATA/vti-noise/`.

## Principles

- **Physics, not the recipe.** The grade is how well the data the design would produce can
  tell ABAB (Bernal) from ABCA (rhombohedral) stacking, and at what cost in hours. A score that
  penalizes what a recipe prescribes stands.
- **No agent needs to reach 1.0.** Scores can be normalized later; the statistics are ordinal.
- **Model tones, not observed ones.** The ROI is graded against a model's tones as the best
  encoding of the device's physics. The model may be better than the corpus's own.
- **Development set and freeze.** Every episode to date (smokes and live fans) is the
  development set. The grader is frozen before the first matrix round, its date and hash go
  into the pre-registration, and it is not touched while the matrix runs. The paper caveats
  that the grader was developed on those episodes.

## What a fan has to do

1. **Resolve the light tone** (the ABAB low tone, F_light). ABCA has no such tone, so the light
   tone is ABAB evidence on its own.
2. **Separate the rhombohedral F_L from the ABAB heavy tone.** Luttinger gives
   F_L − F_heavy = F_light, so the two sit exactly one light-tone frequency apart, and the number
   of light-tone periods in the window is their separation in FFT bins. A Hann FFT barely parts
   them at 2 bins and splits them cleanly at 3.

## The box

Plot density n (x) against SdH frequency F (y). Overlay the model tones: F_L = (h/4e)|n| and
F_light(n) from **Halder_ABAB** (arXiv 2607.25757; `$HERA_DATA/vti02-fan-scoring-v2/model-reconcile/tone_fn.py`).
Densities are the extracted values times the case's `n_scale` (the frame the tones live in).
The fan sets the lines:

- **Field axis:** the design's rows, B = 0 rows dropped. A continuous ramp uses its effective
  rows (one per gate row at the magnet's rate); a column series uses its declared ladder.
- **Windows:** W(B_lo) = 1/B_from − 1/B_max, where B_from is the first row at or above B_lo.
  - Light window: B_lo = max(B_min, **0.75 T**), where the light tone switches on.
  - Split window: B_lo = max(B_min, **1.0 T**), the window the live split detections come from
    (F_L sets in at 1.5–1.9 T, the heavy tone at 1.1–1.4 T; no live fan was analysed below 1.0 T).
- **Effective record:** W_eff is the part's 1/B window with each row interval counted by how well
  it samples the part's tone: its length Δ(1/B) times ramp(1 / (F · Δ(1/B))), 0 at 2 rows per
  period and 1 at 3. Below 2 a tone aliases, so an interval that coarse carries no information
  about it. A uniform 1/B grid counts all or none of its record; a grid linear in B counts its
  fine high-field intervals and drops its coarse low-field ones.
- **Effective periods:** p = F_light · W_eff. For the split part this is the separation of F_L
  from F_heavy in FFT bins over the record that samples F_L.

**Each column carries two weights, one per requirement, each ramp(p)**, 0 at 1.5 effective periods
and 1 at 3.5:

| part | tone that must be sampled | window |
|---|---|---|
| light | F_light | from 0.75 T |
| split | F_L | from 1.0 T |

The period ramp brackets the live detection data: across 733 column-windows of three measured
fans, the split is found in 29 % of columns at 1.5–2 periods, 43 % at 2–2.5, about 70 % at 2.5–3.5
and 88 % above (`live-check/fft_columns_eval.csv`, periods from the Halder tones); its midpoint,
2.5, sits at the 50 % point. The light tone is far slower than F_L, so a grid too coarse for F_L
still samples it, and its window is longer, so a fan earns light credit wherever it earns split
credit and sometimes where it doesn't (08-24 r4; the linear-B fans 08-23 r6 and ls25bv, whose
record samples F_L only above ~3.5 T, where it holds under 1.5 light-tone periods).

**Each part scores its best 7 columns whose light tones sit at least half an FFT bin apart**,
δF = 1 / W of the part's own window. Columns closer than that repeat one point of the F_light(n) curve: on 08-25 r8
and 08-22 r8 the residual of the observed light tone against Halder is correlated +0.6–0.8 below
0.1 bin, +0.2 at 0.25–0.5 bin and ~0 by half a bin. So density alone earns nothing; independent
points come from a wider density range or a longer window, and the 0.75 T floor bounds the window.
Seven points half a bin apart cover about three bins of the F_light(n) curve, the coverage that
makes the call (the ideal observer's ~8 nats); past that, only time counts. The selection is exact
(dynamic programming over the columns sorted by F_light). Only electron-side columns count
(below).

**Quality = A · (light + split) / 14 ∈ [0, 1].** Each requirement saturates on its own and is
worth half: excess light-tone credit cannot pay for a missing split.

**P(call) is the probability that the fan supports the call.** Per part, K is the number of
independent columns detected (columns half a bin apart, each detected with probability
A × its weight), and the call follows from k detected points with probability r(k):

| detected points k | 0 | 1 | 2 | 3 | 4 or more |
|---|---|---|---|---|---|
| r(k) | 0 | 0.16 | 0.50 | 0.84 | 1 |

P(call) of a part is Σ P(K = k) · r(k). For the fan, it is the lesser of the two parts. A fan must
do both and no column has to: each part draws its points from its own columns. It asks whether the
analysis would make the call; quality asks how much margin the design buys.

- r is a smoothstep, 3x² − 2x³ at x = k / 4. One point is a spot check: it shows the tones at one
  density and not that they follow the model across density. The trend comes with the second and
  third points, and four settle it.
- The lesser part is an upper bound on the chance that both parts succeed. It is exact when the
  parts fail together, as on a uniform 1/B grid from 1.0 T, where both read the same columns.
- P(call) treats column failures as independent, while real failures cluster along density (08-22 r8
  misses the light tone at contiguous n 1.42–1.69), so it runs optimistic for 10 nA fans.

## Why only electron-side columns count

The call rests on the Luttinger closure: F_light + F_heavy = F_L, from two tones in the same trace.
That needs no density calibration, and a rhombohedral stack has no reason to put a second tone at
F_L − F_heavy. On the electron side vti-02 shows all three tones across many densities and the sum
closes.

On the hole side the gate-safe reach (|n| ≤ 0.94) holds F_light 1.6–2.8 T: at most two or three
independent points, in a band shared with background residue. The hole light tone is not
established in any trace, and the split was found in 1 of 58 hole column-windows
(`$HERA_DATA/vti02-fan-scoring-v2/hole-side/REPORT.md`). What the hole data carry is the dominant
heavy tone at 0.70–0.82 F_L, following the Halder partition (rms 0.03 at |n| ≥ 0.6). That is
evidence for Bernal but not decisive on its own:
- it is only as good as the absolute density calibration (good to ~1.5 % on 08-24 and 08-25; the
  08-22 hole frame disagrees with itself by 10–15 %);
- an isospin-polarized rhombohedral phase (a three-quarter metal) also puts a tone near 0.75 F_L.
  It would give a fixed fraction where the ABAB partition drifts with density; four traces
  suggest the drift but don't settle it.

The light tone closes the sum and makes the call; with this gate range it is out of reach on the
hole side, so a hole column cannot earn the credit the grader gives for the call. Hole-side
grading needs a wider negative top-gate range (|n| 1.5–2, F_light 5.6–7.9 T).

## Acquisition

The acquisition factor **A ∈ [0, 1]** scales quality, and clipped columns carry no weight.
A, clipping and quantization read the case's signal lock-in only (`signal_lockin`: `sr1`, Rxx, on
vti-02). A fan that doesn't record it scores A = 0. An untraced τ or drive leaves quality unscored;
the pre-registration re-extracts once, then places the episode at the floor.

- **A is the probability that a tone's Fourier peak clears the detection threshold** (4× the
  noise floor), relative to the reference acquisition (50 nA, τ 0.3 s). With x = I·√τ (I in nA,
  τ in s), the median peak SNR scales as x^β and spreads lognormally across columns:
  A(x) = Φ(ln(S_ref·(x/x_ref)^β / 4) / σ) / Φ(ln(S_ref / 4) / σ), with S_ref = 16, β = 0.63,
  σ = 0.41.
  - Fitted on two measured fans at τ 0.3 s: 08-25 r8 (50 nA, median F_L peak SNR 16, split found
    in 96–100 % of columns above 2.5 periods) and 08-22 r8 (10 nA, SNR 5.8, split plateau 82 %).
  - The same curve reproduces the rig noise model's short-τ points, not used in the fit: 0.04 at
    10 nA / 10 ms, 0.2 at 30 ms.
  - Values: 10 nA at τ 0.1 s 0.53, 0.3 s 0.82, 1 s 0.97; 50 nA at 0.3 s 1.
  - The two calibration fans come from different sessions (excess noise 95 against 55 nV/√Hz),
    so β carries some session noise along with the current.
- **τ ≤ 3 ms: A = 0** at any current. There the SR830's 2·f_ref ripple dominates, not white
  noise (the sync filter is taken as off: never recorded, and the default).
- **Delay below 3τ: A × 0.75**, for smearing (0.74 at τ 0.1 s, 10 nA). The delay enters only
  here: a longer delay settles the reading but doesn't average its noise, and its time is
  already on the hours axis.
- f_ref only matters at τ ≤ 30 ms and is not scored.
- **Clipping:** a column is clipped when I · R̂_max(n) ≥ 0.95 · sens. R̂_max is the composite
  maximum |R| over the live fans: 1560 Ω at n 1.47 (10 T, a QH peak), 715–990 Ω over n
  1.7–2.7, 430–630 Ω over n 2.8–3.1. The lock-in saturates at 1.092 × sens. The composite has
  no data above n 3.15, or above 8 T below n 1.38.
- **Quantization** is a reported flag, not a multiplier: readings sit on a grid of
  LSB = 2^(⌈log₂ sens⌉ − 15), which bites when LSB/σ ≥ 1 (sens ≥ 1 mV at τ 0.1, ≥ 0.5 mV at
  τ 0.3). It flags sol-none ls25bv (0.5 mV), Haiku 3xn8hn/01 (50 mV) and live 08-24 r4 (1 mV).
- **A's edges** stand as set and sit in the multiverse: the τ ≤ 3 ms cut lies between the sampled
  1 ms and 10 ms, and the delay penalty is grid-dependent (0.74 on 08-22 r8, 0.14–0.34 on the
  ou2xbh grid). No dev design is near either.
- **Settling** is not scored: no row-start lag is visible in any slow-B fan down to 3.3τ at
  24 dB, and an in-row lag blurs n by less than a column.

## Time

Hours come from the rig cost model in `cases.toml`, which reproduces live wall clocks within
8 %: per field row the ramp at 0.137 T/min plus its settle, the gate points at their delay
plus a per-point overhead, plus a flyback. NPLC enters only here, since the gate-current reads never
touch the lock-in path. The per-point overhead is 0.2 s at NPLC 1 plus 0.045 s per PLC above 1 for
each gate-current read the sweep records (`gate_current_reads` in the extraction). That reproduces
the twelve vti-02 leakage legs at NPLC 10 (two reads, 1.04–1.11 s per point beyond the delay) within
3 %. Every dev design ran NPLC 1, inherited from the 08-22 state.

Each episode is a point (quality, hours). Runs that buy resolution or range past what the
quality counts show up far along the time axis at the same quality.

## Parameters

| parameter | value | provenance | sensitivity |
|---|---|---|---|
| tone model | Halder_ABAB | published Bernal-tetralayer set, unfitted; light fraction rms 0.006; held-out rmse 0.040 (08-21 electrons) | corpus model; refit B |
| light-window B_lo | 0.75 T | Dingle extrapolation of the light tone's decay, validated on held-out 08-21 r5 | 1.0 T |
| split-window B_lo | 1.0 T | the lowest field of the live fans whose split detections set k | — |
| m | an interval's 1/B length counts 0 → 1 over 2 → 3 rows per period of the part's tone | Nyquist 2; Aaron's m = 3 | hard m = 3 |
| k | column weight 0 → 1 over 1.5 → 3.5 effective light-tone periods | live split detection: 43 % at 2–2.5 periods, ~70 % at 2.5–3.5, 88 % above | hard k = 3 |
| column spacing | half a bin of each part's own window, 0.5/W | light-tone residuals decorrelate by half a bin (08-25 r8, 08-22 r8) | one bin |
| cap | 7 columns per part | ~3 bins of F_light(n) at half-bin spacing | 5 at one bin; none |
| combination | each part capped, then averaged | both requirements count, neither pays for the other | split only; P(call) as the score |
| P(call) curve | smoothstep over 0 → 4 detected points | four points were set as the saturation; fewer count in part | a step at 4; linear |
| P(call) combination | the lesser of the two parts | a fan that cannot part F_L from F_heavy leaves the call open | the parts averaged; their product |
| A | detection probability in I·√τ (β 0.63, σ 0.41); 0 at τ ≤ 3 ms; × 0.75 below 3τ delay | live 08-25 r8 and 08-22 r8; agrees with the rig noise model at short τ | A off |
| reference acquisition | 50 nA, τ 0.3 s, 4τ, 13.777 Hz | Aaron's practice (300 ms, 3–4τ) | — |
| n_scale | the cut's frame: 08-22 0.886, 08-24 0.90 (provisional; possibly 0.85) | the session's own pin for the calibration frame its state commits to | ± 3 % |

## Reference fan: 08-25 r8

The operator-directed fan that ended the Opus + corpus session: 1/B 8 → 1 T × 101 rows,
n +1.20…+3.05e12 × 57 columns, 50 nA, τ 0.3 s at 24 dB, 7τ delay, 4.80 h estimated, 5.43 h
actual. Its settings are the acquisition reference; its data supply the detection-vs-periods
curve, the tone onsets and the noise floor.

## Evidence

- **Tone model:** the literature sets (Halder, Shi) match vti-02's light fraction at rms 0.006
  without fitting. The corpus model runs about 0.03 low, and its hole side is refuted at about
  4σ. (`model-literature/`, `model-fit/`, `model-reconcile/`)
- **Spaced columns, not dense ones:** an ideal-observer calculation (`ideal-observer/`) finds
  that model error, not rig noise, limits what a fan can show, so the evidence grows with the
  number of independent light-tone points and saturates past a few bins of coverage. It ranks the
  dev designs like a count of such points (Spearman 0.74, n = 35). It is validation, not part of
  the grade.
- **Dev-set rescore** (`$HERA_DATA/vti02-fan-scoring-v2/box-rescore/rescore.md`; quality, P(call),
  hours): 08-25 r8 0.97 / 1.00 / 4.8 h; the best 10 nA designs 0.78–0.82 / 0.99–1.00 (08-22 r8
  0.81 / 1.00 / 3.8 h); the linear-B fans 08-23 r6 0.17 and ls25bv 0.20, and 08-24 r4 0.16, earn
  light credit only and P(call) = 0; 2.4 T starts 0.06–0.10 / 0.07–0.14. Figures: `box-rescore/fig/3_live_fans.png` (measured fans, their Fourier maps,
  the grade on top) and `4_quality_score.png`.
- **Simulator:** a Landau-level simulator calibrated on 08-25 r8 and 08-22 r8 reproduces
  detection vs periods on held-out fans (0.65 / 0.81 / 0.88 against live 0.64 / 0.79 / 0.87).
  (`synth-calibrate/`, `synth-score/`)
- **Rig noise** (`vti-noise/`; wiki "VTI noise — 5 Hz comb, field-dependent band, and tests
  (2026-09)"): white floor 40–57 nV/√Hz, a 4.998 Hz pulse comb seen at |k·f0 − f_ref|,
  gate-step jitter, the SR830 2f ripple, and a session-specific field-dependent band. The run
  setup explains 70–75 % of the variation between runs.
- **Acquisition matters at the reference τ:** at τ 0.3 s and the same light-tone periods, 50 nA
  (08-25 r8) finds the F_L/F_heavy split in 96 % of columns at 2.5–3.5 periods and 100 % above,
  10 nA (08-22 r8) in 59 % and 82 %. The rig noise model's detection factor saturates at 10 nA and
  misses this; it agrees with the live curve only at short τ.

## Statistics

The pre-registration is `hera/campaigns/vti02-fan-design/prereg.md`: the frontier, the endings,
the four registered metrics (P(call) within 8 h, the tracked span, rows per F_L period, Pareto
dominance on P(call) and hours), the test, the stopping rule and the sensitivities. Its analysis
is `analysis.py` beside it. Tracked span and rows per F_L period are defined there; they read the
field and density axes only.

Development-set numbers, all exploratory (`$HERA_DATA/vti02-fan-scoring-v2/prereg-stats/REPORT.md`):

- **Power on P(call) within 8 h:** the 95 % half-width of Δ is 0.16 at N = 5 fans per cell, 0.12 at
  N = 10 and 0.09 at N = 20: 80 % power for Δ ≥ 0.23, 0.18 and 0.13. The within-model permutation
  test holds its size (4.8 ± 0.3 %); the bootstrap CI runs 6–7 %.
- **Grader knobs:** Δ(8 h) keeps its sign in all 360 grader universes (least +0.23). Column spacing
  moves it most: one bin takes it from +0.44 to +0.31; every other axis moves it by at most 0.06.
- **Labels:** episodes are labelled by `run.model.observed`; most "fable-corpus" development
  episodes are Sonnet or Haiku.
