# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/1776/` (the cell-176 small fan → file_id 1776),
the freshest result at the `after-qo-confirmed` frontier. Used to score the
perception layer (A) independently of the decision layer (B).*

> **Re-grounded 2026-06-05 (ana-notebook audit).** This read was rewritten from
> Aaron's own analysis of `data/1776` in `20260124_ana.ipynb` **cell 78**
> (`files= [1776]`), not from the raw TSV. The prior version was authored from
> `metadata.json` + TSV channel statistics and **drifted**: it called `sr830_5`
> the strongest *Rxx* channel — but in Aaron's analysis `sr830_5/6` are the
> **Hall (Rᵧₓ) channels** (`realhall`, `28-10`/`25-11`); the longitudinal Rxx
> channels are `sr830_1/2/3` (`long1`, `29-28`/`28-25`/`25-24`). It also under-
> described the result: Aaron's 2D map shows **explicit Landau-fan oscillation
> fringes** (clean diagonal stripes in the high-n / high-B corner), directly
> visualizing "the oscillations are real." Figures:
> `../figures/ana_1776_qo-fan-D1_sr830_{1,2,3}.png` (Rxx) and
> `../figures/ana_1776_qo-fan-D1_ryx_sr830_5.png` (Rᵧₓ); the preceding
> effective-mass temperature series is
> `../figures/ana_1639_effmass-tdep_sr830_1.png`.

> **Expert-confirmed 2026-06-09 (Aaron, review card).** *"Your read is right!"*
> — the small-fan-at-D=1 / fringes-in-the-high-n-high-B-corner read and the
> channel-role assignment (Rxx on `sr830_1/2/3`, Hall on `sr830_5/6`) stand as
> written.

## What the sweep is

`s.multimegasweep([mag.field], [np.linspace(0.9, 2.5, 161)], [k_tg.volt,
k_bg.volt], [Vtgs, Vbgs], slow_delay=1, fast_delay=0.6)` at **D = 1**,
n = 0.9 → 0.5 (151 fast points).

- **Slow axis:** perpendicular field `mag.field`, 0.9 → 2.5 T, 161 points — a
  moderate field window chosen to capture a few oscillation periods.
- **Fast axis:** the (Vtg, Vbg) gate pair along an (n, D) line — n = 0.9 → 0.5 at
  fixed D = 1 (151 points; stored as 302 interleaved gate columns).
- **How Aaron reads it (cell 78):** converts gates to density with
  `xs, _ = calculate_n_D(vtg, vbg, dtg=17.25, dbg=25.5)`, forms `I = sr830_4_X`
  and `Rxx = Vxx/I`, plots a 2D `pcolormesh` of **Rxx(n, B)** (SymLog). So this
  is a **small Landau fan: density × perpendicular-field map at D = 1**, taken
  specifically to verify the field-periodic structure is a genuine quantum
  oscillation, not noise.
- **Channels (config from `mc_0`):** current on `sr830_4` (`I_{30-21}`, ~1 nA AC);
  **longitudinal Rxx on `sr830_1` (`29-28`), `sr830_2` (`28-25`), `sr830_3`
  (`25-24`)** (`long1`); **Hall Rᵧₓ on `sr830_5` (`28-10`), `sr830_6` (`25-11`)**
  (`realhall`).
- Base temperature, V_Si = 48 V, ~24k rows, not interrupted.

So this is the **oscillation-confirmation fan** — a deliberately small,
moderate-resolution density × field map whose purpose is the go/no-go ("are the
oscillations real?"), not a frequency extraction.

## What it shows (floor — the must-see findings)

- **`sr830_4` is the current, not transport** — flat at ~1 nA (the AC current
  bias), the **denominator** in `Rxx = Vxx/I`. (In `curr` Aaron even normalizes
  `I/np.nanmax(I)` to show its flatness.)
- **Visible Landau-fan oscillation fringes.** On the longitudinal channels
  `Rxx(n, B)` shows clear **diagonal oscillation stripes** concentrated in the
  high-n / high-field corner (n ≳ 0.8, B ≳ 2 T) — the field- and density-periodic
  modulation that **directly confirms the oscillations are genuine
  Shubnikov–de Haas / Landau-fan structure, not noise.** Consistent across
  `sr830_1/2/3` (see the three `ana_1776_qo-fan-D1_*` figures).
- **`sr830_5/6` are the Hall channels** (Rᵧₓ, diverging scale), showing the
  smooth Hall background over the same window — distinct from the longitudinal
  fan. See `ana_1776_qo-fan-D1_ryx_sr830_5.png`.
- This is a **confirmation-grade** map: small and moderate-resolution by design.
  It establishes *that* the oscillations are real but is too coarse/narrow to pin
  the oscillation frequency B_F or carrier density.

## Correct read (one or two sentences)

`data/1776` is a **small Landau fan at D = 1** (n = 0.9 → 0.5, B = 0.9 → 2.5 T)
at base temperature: the current channel (`sr830_4`) is the flat ~1 nA AC bias,
the **longitudinal Rxx channels (`sr830_1/2/3`) show explicit Landau-fan
oscillation fringes** in the high-n/high-field corner, and the **Hall channels
(`sr830_5/6`) carry the smooth Rᵧₓ background**. It **confirms the oscillations
are genuine** but is too coarse/narrow to pin the oscillation frequency or
carrier density — that needs the higher-resolution fixed-(n, D) cuts that come
next.

## Honest limitations / open questions (don't penalize the agent for these)

- **`plot.png` is blank.** Only gate-leakage monitors are registered in
  `s.plot(...)`; the transport signal lives **only** in `data/1776/data.tsv`.
  "The PNG is the leakage monitor, load the TSV and form Rxx" is the correct
  sub-step — flag, don't penalize.
- **Rxx vs Hall channel identity is from his `contact_pairs` dict.** `long1` =
  `sr830_1/2/3` (Rxx), `realhall` = `sr830_5/6` (Rᵧₓ). An agent that guesses
  "sr830_5 is large ⇒ it's the Rxx" is making a defensible-but-wrong call; the
  channel roles are the answer key. Per Aaron (2026-06-05) there is **no single
  canonical Rxx channel** — all of `sr830_1/2/3` are valid longitudinal pairs.
- **"These are quantum oscillations" is well-supported here but should still be
  qualified.** The fringes are visible in 2D, which is strong evidence; a
  *quantitative* SdH claim ("frequency B_F = X, pocket density Y") would over-read
  this coarse fan. **[VERIFY: a proper 1/B FFT / fan-index read on the dense
  fixed-(n,D) cuts is what nails the frequency — flag for Aaron.]**
- The two small fans differ in D (1774/1775 at D = 0.2, 1776 at D = 1); 1774 has
  a narrow gate range (likely a first/aborted attempt). `data/1776` is the
  canonical D = 1 confirmation fan.
