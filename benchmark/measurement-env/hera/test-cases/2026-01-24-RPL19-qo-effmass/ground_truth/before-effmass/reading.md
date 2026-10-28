# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/1638/` (the last prep map of `# Preping for
effective mass`, cell 100 → file_id 1638), the freshest result at the
`before-effmass` frontier. Used to score the perception layer (A) independently
of the decision layer (B).*

> **Re-grounded 2026-06-05 (ana-notebook audit).** This read was rewritten from
> Aaron's own analysis of `data/1638` in `20260124_ana.ipynb` **cell 39**
> (`files= [1638]`), not from the raw TSV. The prior version was authored from
> `metadata.json` + the TSV channel statistics and **drifted** in two ways:
> (1) it called `sr830_5` the "largest dynamic range" *Rxx* channel — but in
> Aaron's analysis `sr830_5/6` are the **Hall (Rᵧₓ) channels** (`realhall`,
> contacts `28-10`/`25-11`); the longitudinal Rxx channels are
> `sr830_1/2/3` (`long1`, contacts `29-28`/`28-25`/`25-24`). (2) It described the
> map as merely "field/density-structured Rxx" — Aaron's plot shows a **clean,
> well-developed Landau fan** with radial Landau-level lines, not just generic
> structure. Figures: `../figures/ana_1638_prep-fan-D0.2_sr830_{1,2,3}.png`
> (Rxx) and `../figures/ana_1638_prep-fan-D0.2_ryx_sr830_5.png` (Rᵧₓ); the
> preceding AH (n, D) map is `../figures/ana_1599_ah-nd-map_sr830_1.png`.

> **Re-grounded 2026-06-09 (Aaron, expert-review card).** The perception read
> stands (*"You read the plot right"*) — but the sweep itself was **operator
> error**: *"This plot was actually a mistake... I ran a fan at much lower D on
> accident."* The D = 0.2 setting was not a deliberate survey choice; the m\*
> work was always headed for D = 1. This resolves the old [VERIFY] (same pocket
> at D = 1 vs separate survey — answer: neither; an accident) and means the
> ground truth at this frontier includes a known operator slip: an agent that
> notices the D mismatch between this fan and the stated m\* operating point is
> reading *better* than the frozen record.

## What the sweep is

`s.multimegasweep([mag.field], [np.linspace(0, 1.5, 151)], [k_tg.volt,
k_bg.volt], [Vtgs, Vbgs], slow_delay=1, fast_delay=0.4)` at **D = 0.2**,
n = 0 → 1.5 (301 fast points).

- **Slow axis:** perpendicular field `mag.field` (AMI430), 0 → 1.5 T, 151 points.
- **Fast axis:** the (Vtg, Vbg) gate pair stepped along an (n, D) line — n from 0
  to 1.5 at fixed D = 0.2 (301 points; stored as 602 interleaved gate columns).
- **How Aaron reads it (cell 39):** he converts the swept gate pair to density
  with `xs, _ = calculate_n_D(vtg, vbg, dtg=17.25, dbg=25.5)`, forms
  `I = sr830_4_X` and `Rxx = Vxx / I` for each longitudinal pair, and plots a 2D
  `pcolormesh` of **Rxx(n, B)** (SymLog) — i.e. a **density × perpendicular-field
  Landau fan at D = 0.2**. The x-axis is `n` (10¹² cm⁻²), the y-axis is field.
  (The auto x-label in the figure falls back to the raw gate-column name
  `['k_tg_volt','k_bg_volt']`, but the axis runs 0 → 1.5 = the n range.)
- **Channels (config from `mc_0` in his cell):** current on `sr830_4`
  (`I_{30-21}`, gain −1×10⁶); **longitudinal Rxx on `sr830_1` (`29-28`),
  `sr830_2` (`28-25`), `sr830_3` (`25-24`)** (`long1`); **Hall Rᵧₓ on `sr830_5`
  (`28-10`) and `sr830_6` (`25-11`)** (`realhall`).
- **Base temperature** (~29–32 mK), V_Si = 48 V, ~45k rows, not interrupted.

So this is the **last prep-section Landau fan** (density × field at D = 0.2)
taken before the dedicated effective-mass temperature series begins — though
per Aaron (2026-06-09) the D = 0.2 value was an **accident**, not a chosen
survey point (see the re-grounding note above).

## What it shows (floor — the must-see findings)

- **`sr830_4` is the current, not transport.** It is ~flat at ≈ 1 nA (the AC
  current bias) and is the **denominator** in `Rxx = Vxx/I`. Reading a "signal"
  *out of* `sr830_4` would be the mistake; using it as I is correct.
- **A clean Landau fan.** `Rxx(n, B)` on the three longitudinal channels shows a
  well-developed **Landau-level fan** — radial LL lines emanating from low n,
  fanning out with field, with the densest, cleanest structure on `sr830_2`
  (`28-25`). This is unambiguous quantum-oscillation / Shubnikov–de Haas
  structure across the (n, B) plane (see all three `ana_1638_prep-fan-D0.2_*`
  figures), **not** merely "field-dependent variation."
- **`sr830_5/6` are the Hall channels.** Plotted as Rᵧₓ on a diverging
  (RdBu_r) scale, they show the antisymmetric Hall response (faint AH/quantum-Hall
  features in the same (n, B) window), **distinct** from the longitudinal fan.
  See `ana_1638_prep-fan-D0.2_ryx_sr830_5.png`.
- This is a **prep / survey map at D = 0.2** — it establishes the (n, B)
  landscape and confirms the rig is ready; it is **not** the m* measurement
  (no temperature axis here).

## Correct read (one or two sentences)

`data/1638` is a **density × perpendicular-field Landau fan at D = 0.2**
(n = 0 → 1.5, B = 0 → 1.5 T) at base temperature: the current channel
(`sr830_4`) is the flat ~1 nA AC bias, the **longitudinal Rxx channels
(`sr830_1/2/3`) show a clean Landau-level fan**, and the **Hall channels
(`sr830_5/6`) carry Rᵧₓ**. It is the final survey before the dedicated
effective-mass series — it confirms the operating regime and that quantum
oscillations are present, and does **not** by itself yield m* (no temperature
axis).

## Honest limitations / open questions (don't penalize the agent for these)

- **`plot.png` is blank.** Aaron registered only gate-leakage monitors
  (`k_*.curr`) in `s.plot(...)`, so `data/1638/plot.png` is a gate-health plot
  (all ~0). The transport signal lives **only** in `data/1638/data.tsv.gz`; an
  agent that says "the PNG is the leakage monitor, load the TSV and form
  `Rxx = sr830_{1,2,3}/sr830_4`" is correct — flag, don't penalize.
- **Rxx vs Hall channel identity is from his `contact_pairs` dict, not
  re-derived per sweep.** The longitudinal/Hall split (`long1` = 1/2/3,
  `realhall` = 5/6) is Aaron's wiring choice for config `mc_0` in this cell; an
  agent that, lacking the dict, guesses "sr830_5 is large so it's the Rxx" is
  making a defensible-but-wrong call — the channel roles are the answer key.
- **Which Rxx pair is "canonical."** Per Aaron (2026-06-05) there is **no single
  canonical Rxx channel** — `sr830_1/2/3` are all valid longitudinal pairs;
  `sr830_2` (`28-25`) happens to show the cleanest fan here, but that is a
  per-sweep observation, not a fixed rule.
- **D = 0.2 vs the m* anchor (D = 1) — resolved: the D = 0.2 was an accident.**
  This prep fan is at D = 0.2; the effective-mass work then moves to (n = 1,
  D = 1). Per Aaron (2026-06-09) he *"ran a fan at much lower D on accident"* —
  the D = 0.2 fan is neither the m* operating point nor a deliberate
  density-axis survey. Don't read intent into the D value; do credit an agent
  that flags the mismatch.
- **No quantitative QO frequency / Fermi-surface area is extracted here** — and
  Aaron does not extract one in this cell either. A confident "B_F = X, n_pocket
  = Y" claim would be over-reading; that is downstream (the fixed-(n,D) cuts).
