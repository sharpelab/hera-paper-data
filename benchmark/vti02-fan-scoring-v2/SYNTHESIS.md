# Fan scoring v2: overnight investigation synthesis (2026-09-23)

Opus agents ran for fan scoring (8) and VTI noise (7, in `../vti-noise/`). Their reports are the `*/REPORT.md` files in this directory. The frozen
proposal is `hera/docs/fan-design-scoring-v2.md` (uncommitted, not edited overnight). Nothing
touched the repo, the graders or git, and no replay episodes ran.

| dir | question | one-line answer |
|---|---|---|
| `live-check/` | Do the metric's premises hold on live fans? | k ≈ 2 per tone; the light tone is present at the 1 T edge; model tone low; clipping and quantization as design flags |
| `onset-clip/` | Where does the light tone switch on? | ≈ 0.75 T at reference acquisition, ≈ 0.85–1.0 T at 10 nA; the mass-scaled 0.45–0.6 T is refuted |
| `model-fit/` | Refit the tone model to vti-02 | refit B (γ2 −0.0145, γ3 0.3) fixes electrons and holes; n_scale corrections |
| `model-literature/` | Literature prior | Halder / Shi ABAB sets match vti-02 at rms 0.006, unfitted |
| `model-reconcile/` | Which grader model? | **Halder_ABAB**, fallback refit B, corpus as a secondary; `tone_fn.py` |
| `synth-calibrate/` | Simulator | `vti02_sim.py`, a Landau-level model; the floor is mostly signal harmonics; noise 55–165 nV/√Hz by session |
| `synth-score/` | Does the component score track simulated detection? | yes: ρ 0.85–0.94 (clip, 87 nV); the I·√τ multiplier overstates acquisition ~4× |
| `noise-diag/` + `../vti-noise/` | Why does noise vary by session? | a 4.998 Hz pulse comb (instrument timer, ground loop), seen at \|3f0 − f_ref\|; setup explains 70–75 % of the variation; `vti_noise.py` generator |
| `prereg-stats/` | Pre-registration statistics | D_pool stratified by model, floor placement; fixed N; draft `PREREG_DRAFT.md` |

## Recommended grader, to freeze after Zack's and Aaron's rulings

1. **Tones:** Halder_ABAB (published Bernal-tetralayer set, γ3 on, D = 0), through
   `model-reconcile/tone_fn.py`. Nothing in it is fitted to vti-02.
   - Held-out rmse: 08-21 electrons 0.040, holes 0.022. The corpus model gives 0.063 and
     0.114.
   - Uncertainty band `env_lo` / `env_hi` is ±0.01 in fraction at n ≥ 1.5.
   - Fallback: refit B. Report the corpus model as a secondary score.
2. **ROI:** capped tone cells.
   - k = 3 periods of the light tone; the joint light-AND-split detection has its 50 % point at
     p ≈ 3.3.
   - Cell width = bare δF (2δF lowers agreement).
   - At most 3 columns per cell; 1.0 = 5 cells.
   - B_lo clip 0.75 T, applied to the analysis window as well.
3. **High line:** m = 3 at the worst step is conservative. Columns at 2.5 rows per period are
   detected 34–71 % of the time, and the worst-step rule is harsh on linear-B grids. Keep m = 3
   unless there is a ruling; the candidate change is a local rows-per-period rule.
4. **Per-column credit:** the simulated joint detection is about 0.2 at p 1.5–3. So credit of
   about 0.2–0.25 below 3 periods (the doc's a = 0.25 variant) matches the physics better
   than 0.
5. **Acquisition: a simulated factor, capped at 1, from the VTI noise model**
   (`$HERA_DATA/vti-noise/generator/`).
   - The factor is simulated detection at the design's own settings ÷ detection at the
     reference (50 nA, τ 0.3 s, delay 4τ, f_ref 13.777). It uses `vti_noise.py`: white floor,
     the 4.998 Hz pulse comb seen at |k·f0 − f_ref| through the lock-in filter at the real
     timestamps, gate-step jitter, and the SR830 2·f_ref ripple. `vti02_sim_vn.acquire_design`
     computes it.
   - **Shape** (surface figure): about 1 for τ ≥ 0.3 at 3–7τ.
     - τ 0.1 at 10 nA: 0.3–0.9.
     - τ 30 ms: ≤ 0.5.
     - τ ≤ 10 ms at 10 nA: about 0; τ 1 ms: 0 at any current.
     - Delay = 1τ smears: 0.14–0.34.
     - f_ref matters only at short τ.
     - Cap at 1: at 24 dB the 4τ reference is only 57 % settled, so delay 7τ would otherwise
       score 1.2.
   - **On the dev set** the factor is 0.85–1.08 for τ 0.3 designs and 0.33–0.64 for τ 0.1.
     I·√τ overstates the loss about 5×.
   - The factor doesn't change dev-set ranks (Kendall 0.73 → 0.71), because every dev design
     already runs at τ ≥ 0.1. Its job is to guard the part of design space the agents haven't
     explored (short τ, delay ≈ τ), which is Zack's requirement.
   - **The B-dependent band is excluded by default.** It's session-specific: absent in QC0426
     B-sweeps and broadband on SF109A. Treat it as a sensitivity.
   - Use ≥ 5 seeds: the seed spread is about ±0.1 per cell.
   - Quantization: multiplier 0 when the oscillation is about 1 LSB. Clipping never fires on the
     dev set.
6. **Time and statistics:**
   - Primary: **D_pool**, the mean over models of P(corpus ≻ none) − P(none ≻ corpus) on
     (quality, hours), with non-fan endings and Q = 0 fans placed at the floor. Stratifying by
     model is required: arm-pooled D flips sign (Simpson's paradox, driven by astra).
   - Secondary: ΔHV1, the per-episode quality·(1 − h/8 h), with 6 h and 12 h as sensitivities.
   - Fix N before launch, with a within-model permutation test for the decision. The planned
     precision-based stopping inflates D̂ and false positives (0.12–0.21 under the null).
   - Power: N = 10 gives half-width 0.16, P(CI lower bound > 0) 0.72, about $530 per cut.
     N = 20 gives 0.11, 0.95, about $1070 per cut. The 2×2 doubles the cost.
7. **Multiverse (pre-registered):**
   - Tone model: corpus / B / Halder / env band. This moves the opus corpus − none gap from
     0.33 to 0.20.
   - k, onset clip, 2-period credit, acquisition form (noise-model ratio vs I·√τ vs none).
   - On the dev set D_pool > 0 in all 72 knob combinations, but that is mostly fan vs no fan.

## Corrections to record (data hygiene)

- `cases.toml` n_scale: 08-25 is set to **0.95** (uncommitted). 08-24 stays at 0.90 per Zack's
  ruling, and its note flags the Luttinger points (0.837 / 0.860) as "possibly 0.85". The review
  doc's numbers are rescored; the saved scores.json files are left as historical.
- **Dev-set model labels:** most "fable-corpus" episodes are Sonnet or Haiku smokes, and 2 of 4
  "sol-corpus" are luna. The doc's "Scores now" table is mislabelled. Label by
  `run.model.observed`.
- Four fans at the 08-22 cut were never graded (r3w0gf, 005529, tayua3 #00/#01). They were
  hand-extracted in `prereg-stats/common.py`.
- The case ran two cuts (08-21 `45433bea`, then 08-22 `3a4cf818`), and there are four early
  episodes at another frontier.
- `band.py` reads `sys.argv[1]` when imported. That's a scratch-script wart; fix it if it's promoted.

## Physics findings worth keeping, beyond grading

- The corpus model's light tone is low because its effective γ2 is too strong for ABAB, and it
  omits the D = 0 screening. γ3 = 0 is not the cause on the electron side, but γ3 is what fixes
  the hole side. The corpus hole-side partition is refuted at about 4σ. This goes to the HERA
  TODO as a corpus finding.
- **The dominant F_L tone doesn't need magnetic breakdown.** Quantum-Hall pinning at fixed
  total density reproduces it in the simulator. That weakens the sessions' breakdown reading at
  the model level; it doesn't disprove it.
- Measured heavy/light mass ratio is 1.2–1.5, and every model gives 1.84–2.34.
- **Damping, unresolved:**
  - The simulator fits thermal damping, T_e ≈ 4.9 K, with negligible level broadening.
  - The onset agent assumed T_e 1.2 K and found per-tone τ_q.
  - Both give an exp(−α/B) envelope, and the ~0.75 T onset projection is an empirical
    extrapolation of that envelope. So the clip value stands whichever reading is right.
  - With thermal damping, the light/heavy slope ratio is the mass ratio: 0.67–0.83 with
    measured masses, against 0.93 [0.85, 1.04] fitted. That is closer than mass scaling from the
    corpus model, but still not a clean match.
- **Session excess noise:** 55 / 95 / 165 / 146 nV/√Hz for 08-25 / 08-22 / 08-21 / 08-24,
  against a 40 nV/√Hz instrument floor. Worth a rig-side look.

## For Aaron (once Zack has ruled)

- The onset-clip one-pager, `onset-clip/onepager.md`, with the figure `dingle_onset.png`.
- Optional: one slow 1D sweep at n ≈ 2.8, 50 nA, τ 0.3 s, 1.2 → 0.4 T in ≤ 5 mT steps, about
  1 h. It measures the light onset directly and would settle the clip.
- Confirm the Halder middle-pair couplings (Γ1/Γ3/Γ4 = 0.32/0.25/0.032, quoted secondhand from
  Klanurak 2024).

## Next (proposed, not started): a noise model of the VTI rig from its full run history

The source is `~/sharpelab/dgglab-measurements/vti`: 2,750 runs from 2024-06 to 2026-08. Each
has point timestamps and full instrument snapshots. 418 are `watch` time series, and many
record unconnected lock-in channels.

1. **Metadata index:** per run, the point period (from timestamps), lock-in τ, slope, sens,
   reserve and f_ref, NPLC, and state.
2. **Signal-free segments:** watch runs, unconnected channels, NPLC 1 gate currents,
   quadratures.
3. **Joint spectral fit across runs:** white + 1/f + a mechanical line f0 with harmonics.
   Include each run's filter transfer (lock-in |H|², NPLC window) and its own sampling
   aliasing, plus a per-run amplitude. The variety of τ and sampling periods breaks the
   aliasing ambiguity.
4. **What drives the variation:** track line amplitude and frequency against time and state,
   including the InfluxDB VTI He level, pressure and L218 channels.
5. **Coupling path:** compare unconnected channels, gate current, device quadrature, and
   scaling with B·|dR/dB| (vibration in field).
6. **Generator:** `vti_noise.py` samples the fitted spectrum, filters it at the design's τ and
   slope, and samples it at the design's actual timestamps. It replaces the hand-set excess
   noise in `vti02_sim.py`.
7. **Held-out validation:** predict the four vti-02 fans' excess (55 / 95 / 146 / 165
   nV/√Hz) and the QC0426 VTI runs from their settings and timing.

`noise-diag/` is a pilot of steps 3–5 on about 10 runs. Decide whether to scale up after it
lands. Question for the rig expert: which mechanical systems run on the VTI (pumps, needle-valve
drive, compressor or recirculator), and at what cycle periods.

## Ideal-observer grader (`ideal-observer/REPORT.md`)

- **Noise doesn't limit vti-02 fans:** noise alone gives 10³–10⁵ nats. Model error does.
- **With σ_a = 0.5** (tone amplitude, coherent within one Fourier cell) the evidence saturates at
  about 2 nats per resolved cell of the light-tone dispersion. The analytic form is
  **E ≈ [1 + Σ ΔF_light·W_eff] / (2σ_a²)**, over covered, Nyquist-sampled columns. That is the
  tone-cells rule, derived.
- **Acquisition only matters at extremes** (1 nA with τ ≤ 30 ms, heavy quantization) for an
  ideal observer. It matters more for a real FFT analysis.
- **E\* = 8 nats** (about 4 cells). The correct live calls came at 7.3 and 8.6; the weak or wrong
  ones at 4.7 and 6.2.
- **08-24 scores mid (0.77).** Its design carried the content, and the wrong call was an
  analysis failure.
- **Knobs made obsolete:** k, the onset clip, the analysis window, tone cells, the SNR and
  acquisition multipliers, quantization, and the m = 3 line (replaced by a local Nyquist gate).
- **Knobs remaining:** the tone model, σ_a, E\*, the Nyquist gate, and hours.
- NPLC enters only as time: gate-current reads add about 1 s per point at NPLC 10 against about
  0.1 s at NPLC 1.
- **Next:** a high-level review, a cleanup pass, and an explicit cut-down pass toward the simplest
  grader that's still defensible.
