# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/79/` (the 0-field density cut along the D = 0.25
gate-line, cell 180 of the served notebook), the freshest result at the frontier.
Used to score the perception layer (A) independently of the decision layer (B).
Rendered from the data via the device's own convention — see
`figures/ana_79_density-cut_D0p25.png` and `analysis/render_fans.py`.*

## What the sweep is

`s.multisweep([dc205_volt, k_bg.volt], [vtg_vec, vbg_vec])` along the **D = 0.25
gate-line** (`vtg ∈ [1, 5]`, `vbg = vtg/1.3 − 2`, 101 points), at **zero field**,
base T ≈ 1.25 K (VTI). Comment: *"n sweep at fixed D, DC205 for TG, K2400 for BG,
Si = 95 V, float other contacts."*

- **What it maps:** a **1D carrier-density cut** at fixed displacement field
  (D ≈ 0.25 V/nm) — `Rxx` vs `n` as the top/back gates are co-swept along the
  constant-D line. Density `n` is computed from the gate-line via
  `calc_nD(Vtg=DC_bias, Vbg=k_bg_volt, c_tg, c_bg)`, `n_12cm = n·1e-16`.
- **Channels (this config):** current on **`sr0`** ("drain current on 42",
  gain −1E6); voltages on `sr1 = 09-01`, `sr2 = 12-20`, `sr3 = 09-12`.
  `I = sr0_X / sr0_gain`, `Rxx = sr{1,2,3}_X / I`.
- **Field:** nominally zero. **Temperature:** ~1.25 K.

So this is a **0-field density scan along the D = 0.25 line** — the operator
checking that the freshly-reconfigured contacts give a clean `Rxx(n)` before
committing the line to a long Landau-fan field sweep.

## What it shows (floor — the must-see findings)

(Read directly from the re-formed `Rxx(n)` — see `ana_79_density-cut_D0p25.png`.)

- **A sharp charge-neutrality peak at n ≈ 0.** `sr1` and `sr2` rise to a tall
  insulating peak (~**78 kΩ** on `sr1`, ~**67 kΩ** on `sr2`) right at charge
  neutrality, confirming the gate-line crosses the CNP and the device gaps out at
  neutrality.
- **Metallic away from neutrality.** Both longitudinal channels fall steeply to a
  low-Rxx metallic background (→ few hundred Ω, then ~0 on this scale) by
  **n ≳ 2 ×10¹²**, out to the n ≈ 8 ×10¹² edge of the cut — the device conducts
  well across the doping range.
- **`sr3` is transverse / mixed (Hall pickup).** `sr3` is **antisymmetric across
  the CNP** — it dips to ≈ −20 kΩ just below neutrality and swings to ≈ +30 kΩ
  just above, crossing zero near n = 0. That sign-change signature means `sr3`
  carries a Hall-like (`Rxy`) component (consistent with the analysis treating
  `sr3` as `r_xy` in the fans), **not** a clean longitudinal `Rxx`.
- **Good contacts / no obvious leakage.** Smooth, single-valued traces with a
  well-defined CNP — the reconfigured contact set (`sr0` on 42, `sr1 = 09-01`) is
  working; the line is ready to be swept vs field.

## Correct read (one or two sentences)

A clean **0-field density cut at D ≈ 0.25** (Rxx = Vxx/I, sr0 = current) shows a
sharp charge-neutrality peak at n ≈ 0 (~70-80 kΩ) and a metallic background away
from neutrality, with `sr3` carrying a Hall-like antisymmetric component — the
reconfigured contacts give a good `Rxx(n)` and the D = 0.25 gate-line is
well-placed. It is a single 0-field line, so it shows *that* the line is clean and
where the CNP sits, but **no field / Landau-level information** — turning it into a
B-n Landau fan (and repeating across D) is the obvious next step.

## Honest limitations / open questions (don't penalize the agent for these)

- **The disk `plot.png` shows the live monitor, not transport.** `data/79/plot.png`
  is the registered live-monitor view; the `Rxx(n)` trace requires forming
  `sr{1,2,3}_X / (sr0_X / sr0_gain)` from the TSV (exactly what the device's
  analysis does). An agent that only looks at the PNG sees no CNP — reconstructing
  Rxx is the correct sub-step; flag, don't penalize.
- **1D, single D-line — out of `hera-classify` scope.** This is a density cut, not
  a 2D gate map, so the 2D-map classifier doesn't apply to it directly.
- **`sr3` sign / channel role.** Calling `sr3` a longitudinal `Rxx` would be the
  mistake; its antisymmetric-across-CNP shape marks it as the transverse/Hall
  channel. Reading `sr1`/`sr2` as `Rxx` and `sr3` as `Rxy` is correct.
- **Absolute D value is calibration-dependent.** D ≈ 0.25 V/nm comes from the
  capacitance lever arms (`t_tg = 1.3·t_bg`, `t_bg = 12 nm`); the lever arm is
  approximate until cross-checked against Landau-level filling factors. Don't
  over-index on the exact D.
- **Field zero is the magnet set-point, not an absolute B.** As on the toploader,
  treat "0 T" as the current null.
- **Classification context.** This cooldown exists to classify the stacking
  (ABA vs ABC), which is read from the *field-resolved* fan, not this 0-field
  line — so the density cut is a setup/QC step, not itself the discriminator.
  Don't over-read stacking from `data/79`; and note the VTI's ~1.2 K base left
  even the fans too warm for a definitive call (Qingrui leans ABA).
