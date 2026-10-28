# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/84/` (the `# Idc vs n` sweep, cell idx 31),
which is the freshest result at the frontier. Used to score the perception
layer (A) independently of the decision layer (B).*

> **Re-grounded 2026-06-05 (ana-notebook audit).** This read was rewritten from
> Isaac's own analysis convention in `20260415_ana.ipynb` (current = `sr830_1`,
> `Rxx = (sr830_4_X/100)/Ixx`), applied to `data/84`, **not** from the raw
> measure-notebook inline overlay. The prior version was authored from
> `images/cell274_out53.png` + `metadata.json` and **drifted** the same way as
> the other audited fixtures: it called raw **`sr830_4_X` the "clearest signal"**
> and **`sr830_1_X` a "featureless / railed" dead contact** — but `sr830_1` is
> the **current** (the denominator of Rxx) and `sr830_4` is the longitudinal
> **voltage** (the numerator); the quantity to read is `Rxx = (sr830_4_X/100)/Ixx`.
> It also placed the critical-current peaks at "±8 in dc205" (≈ **±80 nA**, not
> ±8 nA — the bias resistor gives 10 nA/V), and said the density dependence was
> "not directly legible" when the 2D `Rxx(Idc, n)` map makes the **density-tuned
> critical-current dome** plainly visible. The qualitative conclusion (candidate
> SC, zero-bias dissipationless region, critical-current peaks) was right; the
> channel/units/legibility were wrong. Figures:
> `../figures/ana_84_idc-vs-n_Rxx_sr830_4.png` (2D map) and
> `../figures/ana_84_idc-vs-n_Rxx-traces_sr830_4.png` (trace overlay).

## What the sweep is

`s.multimegasweep([k_tg.volt, k_bg.volt], [vtg_new_vec, vbg_new_vec], [dc205_1.volt], [np.linspace(-15, 15, 301)], slow_delay=5, fast_delay=1.2)`

- **Slow axis:** a line in (n, D) space — gates (k_tg, k_bg) driven together along
  a density line at **fixed D**, 51 frames (n ≈ −0.6 → −0.4 ×10¹⁶ cm⁻², from the
  reading.md context). So this is a **DC-bias × carrier-density** map at fixed
  displacement field.
- **Fast axis:** `dc205_1` DC bias, −15 → 15 V, 301 points. Through
  `bias_resistor = 1e8 Ω` this is a **current bias of −150 → +150 nA**
  (`Idc[nA] = dc205[V]·10`).
- **Channels (this cooldown, `bottom device`):** mc has `sr1 = sr2 = 28-4`,
  `sr3 = 5-30`, `sr4 = 30-31`. Isaac's convention: **`sr830_1` is the current**
  (`Ixx = sr830_1_X / sr1_gain`, gain −1e6, Ixx ≈ 1.0 nA — flat, as a current
  bias should be); `sr830_4` is the four-probe longitudinal voltage. Plus T.
- Base temperature: T ≈ 0.0293–0.0299 K (~29 mK) — base, consistent with the
  Beff = 0 / low-T characterization context.

## What it shows (floor — the must-see findings)

- **`sr830_1` is the current, not a dead contact.** It is the ~flat ≈ 1 nA AC
  current bias — the **denominator** of `Rxx = Vxx/I`. Reading a "signal" *out
  of* sr830_1 (or dismissing it as railed) is the mistake; using it as I is
  correct. Symmetrically, raw `sr830_4_X` is the Rxx **voltage** — read
  `Rxx = (sr830_4_X/100)/Ixx`, not raw sr830_4.
- **A density-tuned superconducting-like critical current.** The 2D `Rxx(Idc, n)`
  map shows a sharp **low-Rxx (~0–1 Ω, dissipationless) diamond centered at
  Idc = 0**, surrounded by a high-Rxx (~40–75 Ω) normal region. The diamond is
  **widest in the middle of the density window (frames ≈ 15–30)** and narrows
  toward both ends — i.e. the **critical current is density-dependent**, peaking
  near the center of this n-line.
- **Critical-current peaks at ±40…±90 nA.** In the `Rxx` vs `Idc` traces, the
  central frames show Rxx ≈ 0 at low bias then sharp Ic peaks (up to ~250 Ω) at
  ±40…±90 nA depending on density; the outer frames stay normal/flat (~30–60 Ω).
  This is the differential signature of a critical current that scales with n.

## Correct read (one or two sentences)

There is a **candidate superconducting feature**: along a density line at fixed
D and base T, `Rxx = (sr830_4_X/100)/Ixx` shows a dissipationless (~0–1 Ω)
zero-bias region with a **density-dependent critical current** (Ic peaks at
±40…±90 nA, maximal mid-window). This establishes *that* there is an SC-like
state to characterize, *where* it sits (this n–D window), and *that its Ic tunes
with density* — it does **not** yet establish true superconductivity (field /
temperature response is the discriminator, untested in this sweep).

## Honest limitations / open questions (don't penalize the agent for these)

- **The disk `plot.png` / inline overlay shows raw lock-in channels, not Rxx.**
  `data/84/plot.png` and the measure-notebook inline overlay
  (`images/cell274_out53.png`) plot raw `sr830_{1..4}_X` vs dc205. The SC read
  requires forming `Rxx = sr830_4_X / sr830_1_X` (with gains) — reconstructing it
  is a reasonable sub-step; flag, don't penalize. A correct read can also be had
  qualitatively from raw sr830_4_X (zero-bias dip + Ic peaks), but the **channel
  attribution and the nA bias scale** must be right.
- **Field discriminator untested here.** This sweep is at the trapped-flux null
  only; whether the Ic is suppressed by perpendicular field (the SC test) is the
  open question — and is exactly the next move (`# B vs Idc`, data/85).
- **Cooldown drift.** `device_card.md` describes the *current* (post-2026-05-04)
  cooldown; `data/75–84` are from the *prior* cooldown (2026-04-23 → 04-25). A
  genuine confound — note whether the agent catches it.
- **Out of `hera-classify` scope.** The classifier targets true (Vtg,Vbg)/(n,D)
  gate maps; this is bias × density, so the classifier should refuse it. The
  perception read here is the human rubric, not a classifier target.
