# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/159/` (the `# Quantum oscillations discovery
journey` final fan, cell idx 53), the freshest result at the frontier. Used to
score the perception layer (A) independently of the decision layer (B).*

> **Re-grounded 2026-06-05 (ana-notebook audit).** This read was rewritten from
> Aaron's own analysis of `data/159` in **`fans_ana.ipynb` cell 8** (`file = 159`,
> under the `# D = 0.31 V/nm` header), not from the raw TSV + leakage-only
> `plot.png`. There is no `241230_ana.ipynb`; the QO work lives in `fans_ana.ipynb`.
> The prior version was authored from the live-monitor PNG and **drifted**: it
> hedged that "the Landau-fan slope / oscillation period are NOT directly legible"
> and that "a proper 2D colormap is needed" — but Aaron's cell 8 **is** exactly
> that 2D `Rxx(n, B)` fan, plus an FFT in 1/B and a B = 0 linecut. It also said the
> oscillatory feature is uniform "across the swept density window"; his FFT shows
> the fan power is **localized** (strongest near n ≈ −2.2), not flat. The
> `Rxx = sr830_4`-as-current insight in the old read was correct and is kept.
> Figures: `../figures/ana_159_landau-fan_sr830_3.png` (and `_sr830_1`),
> `../figures/ana_159_hall-fan_sr830_7.png`; the immediate in-section predecessor
> (the single-density resolution check, `data/157`) is
> `../figures/ana_157_resolution-check_sr830_1.png`.

> **Re-grounded 2026-06-09 (Aaron, expert-review card).** Aaron rejected the
> "FFT power is localized" framing the 6-05 rewrite introduced: *"I have no idea
> what you are saying about FFT power being localized. This linecut likely goes
> through a number of different phases, so the QO should not necessarily be
> localized like you suggest."* Where fan power concentrates along this density
> line is **not** a single-pocket "where the oscillations live" claim — the line
> crosses multiple phases, each with its own oscillation content. Localization
> is dropped from the floor below; the clean-fan / SdH-confirmed read stands
> (and the next-move capture on this card was confirmed "Correct").

## What the sweep is

`s.multimegasweep([mag.field], [np.linspace(1.0, 0, 351)], [k_tg.volt,
k_bg.volt], [vtgs, vbgs], slow_delay=10, fast_delay=1)`

- **Slow axis:** perpendicular magnetic field (AMI430), `mag.field` from
  **1.0 → 0 T, 351 points**.
- **Fast axis:** a line in (n, D) space — `(k_tg, k_bg)` driven so that
  **n sweeps −2.9 → −2.1 (×10¹² cm⁻²) at fixed D = 0.31 V/nm, 251 points**
  (`calculate_gate_voltages(np.linspace(-2.9,-2.1,251), 0.31)`).
- So this is a **Landau fan**: transport vs (carrier density, B⊥) at fixed D.
- **How Aaron reads it (cell 8):** `I = sr830_4_X` (the AC current, `I_{7-20}`),
  `Vxx = sr830_{ind}_X` for the longitudinal pairs, **`Rxx = Vxx / I`**, plotted
  as a 3-panel stack per channel: (1) 2D `pcolormesh` of `Rxx(n, B)` (the fan),
  (2) an **FFT of background-removed Rxx in 1/B** → fan-frequency `f_ν`, and
  (3) the `Rxx` linecut at B = 0. Hall indices `{7,8}` are plotted as `Ryx` in
  `h/e²`.
- **Channels:** current on `sr830_4` (`I_{7-20}`, gain −1e6); longitudinal voltage
  on `sr830_1/2/3/5/6` (`28-25, 11-13, 13-14, 14-15, 15-17`); Hall on `sr830_7`
  (`29-13`) and `sr830_8` (`28-14`).
- **Config:** `mc_4`, `V_si = −20 V`. `interrupted: false`. Temperature: base
  (heater not driven this section); the `T` column records it.

## What it shows (floor — the must-see findings)

- **`sr830_4` is the current, not transport.** It is the **denominator** in
  `Rxx = Vxx/I`. Reading a "signal" *out of* `sr830_4` would be the mistake; using
  it as `I` is correct (and is what Aaron does).
- **A real Landau fan.** `Rxx(n, B)` shows **field- and density-dependent
  oscillatory structure that strengthens / develops as B rises toward 1 T** — the
  qualitative signature of Shubnikov–de Haas / quantum oscillations. Consistent
  across the longitudinal channels (see `ana_159_landau-fan_sr830_3.png` =
  contacts `13-14`, and `_sr830_1` = `28-25`). The B = 0 linecut shows clear
  density-dependent resistance structure (steps / a broad peak between
  n ≈ −2.7 and −2.2).
- **FFT power varies along the density line — do not over-read where it
  concentrates.** In Aaron's figure the 1/B-FFT happens to be strongest near
  n ≈ −2.2 (near the guide lines he drew: n = −2.72, −2.675, −2.51, −2.2), but
  per Aaron (2026-06-09) this density line **likely crosses several phases**, so
  concentration of fan power is *not* evidence of a single localized oscillatory
  pocket — different fillings can carry different (or no) oscillation content.
  The floor finding is "oscillations exist and develop toward 1 T"; *which*
  fillings carry *which* frequencies needs finer, targeted fans.
- **Gates well-behaved.** No runaway leakage in the gate-current monitors; a few
  transient spikes only.

## Correct read (one or two sentences)

`data/159` is a **clean Landau fan** at D = 0.31 V/nm over n = −2.9…−2.1, B = 0→1 T
at base temperature: `Rxx = sr830_{1,2,3,5,6}_X / sr830_4_X` shows quantum /
SdH oscillations that develop with field, confirming an oscillatory regime (the
1/B FFT giving a first handle on fan frequency). It establishes *that*
oscillations exist; the density line likely crosses several phases, so *which*
fillings carry which frequencies — and the Fermi-surface frequency / degeneracy
— still wants finer/longer fans, and **effective mass needs a temperature
series** (the T-damping of the oscillation amplitude).

## Honest limitations / open questions (don't penalize the agent for these)

- **The disk `plot.png` shows only the live monitor, not the fan.** `data/159/
  plot.png` is the live sweep monitor — each panel overlays all 351 field frames
  of a channel vs `k_tg.volt`, so the **fan slope, oscillation period (1/B), and
  fan-diagram structure are NOT legible from that PNG**. The fan is only legible
  once you form `Rxx = sr830_{1,2,3,5,6}_X / sr830_4_X` and reshape to `Rxx(n, B)`
  (Aaron's cell 8). An agent that looks only at the embedded PNG sees overlaid
  traces; reconstructing the 2D fan is the reasonable sub-step — flag, don't
  penalize. (The `../figures/*` here are Aaron's reconstruction, answer-key side.)
- **Density-axis units / sign.** The live plot's fast axis is labelled
  `k_tg.volt`; the physical density (n = −2.9…−2.1 ×10¹²) comes from
  `calculate_gate_voltages` / `n = (Vbg/dbg + Vtg/dtg)·ep·5.5263`. Don't penalize
  reading the axis as gate voltage. (Minor: cell 8 uses the global `dbg = 40` while
  the device card / `calculate_gate_voltages` use `dbg = 40.5` — ~1.25% n-axis
  shift; see `analysis/README.md`.)
- **Physics interpretation is reviewable — flag for expert check.** Calling the
  structure "quantum oscillations / SdH" follows Aaron's own framing, his fan, and
  the 1/B-FFT having structure; but a *quantitative* claim (true periodicity in
  1/B, the fan frequency → carrier density / Fermi-surface degeneracy,
  distinguishing SdH from other gate-dependent features) should be read off the
  FFT carefully and confirmed with cleaner fans. Better an honest "oscillatory
  feature consistent with QO, FFT power localized near n ≈ −2.2, needs finer fans +
  a T-series for period/mass" than a confident frequency claim.
- **Companion files give context.** The B = ±1 T gate maps (153–155) located the
  window; the single-density resolution check (157, cell 9 → `ana_157_*`) confirmed
  oscillations are resolvable; 156/158/159 are the fans, with 159 the densest/last.
