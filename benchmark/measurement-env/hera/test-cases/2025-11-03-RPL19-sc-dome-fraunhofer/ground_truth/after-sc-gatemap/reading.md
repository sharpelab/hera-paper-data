# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/145/` (the last SC-gatemap-section sweep, cell
83), the freshest result at the frontier. Used to score the perception layer (A)
independently of the decision layer (B).*

> **Re-grounded 2026-06-05 (ana-notebook audit).** This read was rewritten from
> Aaron's own analysis of `data/145` in `20251103_ana.ipynb` **cell 17**
> (`files = [145]`), not from the raw TSV. The prior version was authored from
> `metadata.json` + the TSV and **drifted** — it called reading `sr830_4` "a
> mistake" (it is the *current* in his `Rxx = Vxx/I`) and asserted a "weak,
> non-monotonic field dependence with a minimum at 6–8 mT," which was an artifact
> of field-averaging the voltage into 1D. Aaron's 2D map shows a clean SC dome.
> Figures: `../figures/ana_145_dome-vs-field_sr830_3.png` (and `_sr830_5`); the
> preceding dome gate-map is `../figures/ana_134_sc-dome-gatemap_sr830_3.png`.

> **Re-grounded 2026-06-09 (Aaron, expert-review card).** Aaron rejected the
> field-scale claim: *"Your read on the numbers is wrong because the dome is
> centered around finite field."* The dome's field maximum sits at finite
> *nominal* B (the trapped-flux null, ≈ +7 mT at this point in the run), so this
> positive-only sweep cuts through one flank of the dome — the earlier "suppressed
> by field and closes by ~8–10 mT" floor read mistook a one-sided cut through an
> off-center dome for a B = 0-centered dome with an ~8–10 mT closing field. The
> floor below was rewritten accordingly. (Same card: the next-move capture —
> Fraunhofer — was confirmed "Correct", and re-finding the true null re-affirmed
> as "perhaps the most pressing" alternative.)

## What the sweep is

`s.multimegasweep([mag.field], [np.linspace(0, 0.020, 201)], [k_tg.volt,
k_bg.volt], [ys, xs], slow_delay=3, fast_delay=1)`

- **Slow axis:** perpendicular magnetic field (AMI430), 0 → 20 mT planned, 201
  points. **Interrupted at ≈ 11.6 mT** (117 field frames of 201 actually landed;
  23,490 of ~40k rows). Note the swept range is **field ≥ 0 only** — this run
  cannot show symmetry about B = 0 by itself.
- **Fast axis:** a *line in gate space* — `draw_line_through_point(point=(-5.2,
  0.47), slope=0.3, extent=0.2, npoints=101)`, i.e. (Vbg, Vtg) swept together
  along a 101-point line centred on the dome optimum (BG = −5.2, TG = 0.47). The
  ana plot's horizontal axis is labelled `V_tg` (0.41 → 0.53), the gate-line
  coordinate.
- **How Aaron reads it (cell 17):** `I = sr830_4_X` (the AC current bias),
  `Vxx = sr830_3_X` / `sr830_5_X`, **`Rxx = Vxx / I`**, plotted as a 2D
  `pcolormesh` of `Rxx(V_tg, B)` (SymLog, ~10–70 Ω) plus the lock-in phase.
- **Channels:** current on `sr830_4` (`I_{6-22}`, gain −1e6); longitudinal
  voltage on `sr830_3` (`25-24`) and `sr830_5` (`13-14`).
- **Base temperature:** T ≈ 0.044–0.060 K over the run. (`metadata.json` also
  carries a `T_m ≈ 4.69` field of unclear meaning — possibly a different
  thermometer channel; do not over-read it.)
- AC excitation 0.5 nA at 7.78 Hz; V_Si = −48 V; config MC4 (gate map was MC3).

So this is a **gate-line cut through the SC dome × small perpendicular field** —
how the dome region responds to field up to ~12 mT.

## What it shows (floor — the must-see findings)

- **`sr830_4` is the current, not transport.** It is ~flat at ≈ 0.5 nA because it
  is the AC current bias; it is the **denominator** in `Rxx = Vxx/I`. Reading a
  "signal" *out of* sr830_4 would be the mistake — using it as I is correct.
- **A clean SC dome.** `Rxx(V_tg, B)` shows a sharp **low-Rxx region (~10 Ω, dark)
  centred near V_tg ≈ 0.45–0.475**, surrounded by a high-Rxx ring (~70 Ω). This
  is a gate-tunable low-dissipation (candidate superconducting) dome sitting on
  the SC-gatemap optimum. **Consistent on both voltage channels** (sr830_3 `25-24`
  and sr830_5 `13-14`) — see both `ana_145_dome-vs-field_*` figures.
- **The dome is suppressed by perpendicular field — but it is centered at finite
  nominal B, so this cut sees only one flank.** Within the swept window the
  low-Rxx region narrows with increasing nominal field and Rxx recovers toward
  the ~70 Ω background. Per Aaron (2026-06-09) **the dome is centered around
  finite field** (the trapped-flux null, ≈ +7 mT here), so the apparent
  "closes by ~8–10 mT" is NOT a closing-field number — it is where a one-sided
  cut through an off-center dome exits the dome. Reading a field scale for the
  SC suppression from this sweep alone is the mistake.

## Correct read (one or two sentences)

A candidate SC dome located by the SC-gatemap section (optimum near TG ≈ 0.47,
BG ≈ −5.2, V_Si = −48 V) shows, in `Rxx = Vxx/I` along the dome gate-line, a sharp
low-Rxx (~10 Ω) dome that is **suppressed by perpendicular field**, consistent
across both longitudinal voltage channels — but the dome is **centered at finite
nominal field** (the trapped-flux null), so this positive-only cut shows one
flank and gives **no closing-field number**. The run establishes a
field-suppressible low-dissipation dome; re-finding the true null and a proper
Ic-vs-(Idc, B) map are the natural way to confirm it is superconducting and read
its junction character.

## Honest limitations / open questions (don't penalize the agent for these)

- **The disk `plot.png` shows only gate leakage, not transport.** `data/145/
  plot.png` (and every sweep cell's inline PNG) plots the registered live-monitor
  channels (`k_*.curr`), all ~1e−11–1e−10 A — a gate-health plot with no
  transport. An agent that only looks at `plot.png` legitimately sees "no
  feature"; the SC signal requires forming `Rxx = sr830_{3,5}_X / sr830_4_X` from
  the TSV. Reconstructing it is a reasonable sub-step — flag, don't penalize.
- **The run is interrupted** (~12 mT of 20 mT). Field behaviour beyond ~12 mT is
  simply absent.
- **Field center is set by trapped flux — do NOT read an absolute B from this
  run.** Because only B ≥ 0 was swept, this sweep alone cannot place the dome's
  field maximum. Per Aaron (2026-06-05) the perpendicular null is **trapped flux:
  cooldown-dependent and shifts after large-field excursions** — a moving offset,
  not a fixed instrument zero (the post-cut Fraunhofer shows ~+7 mT *at that point
  in the run*). So "the dome sits near B = 0" should be read as "near the current
  trapped-flux null," and the clean characterization is an Ic-vs-B map about the
  *re-found* null, not this positive-only cut.
- **Mixed axes.** Field and the gate line move together (field slow, gate line
  fast), so a single map does not separate "dome shape in gate" from "pure field
  response." Proposing a cleaner reshape / a fixed-gate Ic(B) cut is fine.
