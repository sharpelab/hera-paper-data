# Ground truth — next move at the frontier (cut idx 102)

*What the operator (Qingrui) actually did in the next sections
(`# try Si gate -- TG-Si sweep` … `# B-n sweep at D=0, Si=+60V`, cells 103-115 →
`data/28, 30, 31, 32, 33`). This is **one** expert path used to route the replay
to human review, not an exact-match score. See benchmark-plan.md "Imitation is a
screen, not a score." This frontier is **contested** — a strong alternative
(go straight to the D-series) scores as a co-equal class, not a miss; see below.*

## The move: introduce the Si back gate, then re-take the fan with screening

Having a first D = 0 Landau fan (`data/27`) that works but is washed out at the
VTI's ~1.2 K, the operator **brings up the third gate — the doped-Si global back
gate** (the second Keithley, `k_2410`, until now wired but zeroed) — before
committing to the long displacement-field series:

- **TG-Si map** (`data/28`, cell 107): `s.megasweep(k_2410.volt, [−50, +50],
  dc205_volt, [−6.5, +7.5])` at **B = 8 T, BG = −4 V** — a 2D `Rxx(V_TG, V_Si)`
  gate map. This is the literal "try Si gate -- TG-Si sweep": characterize how the
  Si gate moves the device before relying on it. (`data/30` is a narrow
  Si = 50/55/60 V follow-up of the same map.)
- **Si-screened D = 0 fan** (`data/31`, cells 111-115): the D = 0 fan re-taken with
  **Si = +60 V**, now swept to **13 T** — the screened, higher-field fan.
- **VSi-n maps** (`data/32`, `data/33`): `multimegasweep` of the D = 0 gate-line vs
  **V_Si** (+50…+100 V and −50…−100 V) — `Rxx(n, V_Si)` maps that read the
  Si-gate's leverage on the charge-neutral line directly.

Figures: `figures/ana_28_tgsi-map.png`, `ana_31_fan_D0_Si60.png`,
`ana_33_vsi-n-map.png` (and the served fan `ana_27_fan_D0.png`).

## Why this is a defensible next step

The campaign's purpose is to read the stacking (ABA vs ABC) from the **Landau-fan
structure and its displacement-field dependence**, and the first D = 0 fan (27) is
too washed out to do that. Two things stand in the way of just charging into the
D-series: the fan needs to be *cleaner*, and reaching a wide spread of D cleanly
benefits from more control authority. Bringing up the Si back gate addresses both
— it is an extra screening / control knob — and, crucially, the expert
**characterizes it before relying on it**: the TG-Si map (28) shows the Si gate is
a comparatively *weak* lever on density (the CNP stripe stays nearly vertical as
V_Si is stepped over ±50 V — the thick SiO₂ gives the Si gate a small lever arm),
and the VSi-n maps (32/33) quantify how far it does shift the neutrality line. The
payoff is visible: the **Si-screened fan to 13 T (31) is markedly cleaner than the
8 T fan (27)** — Landau diagonals (especially on the hole side) that 27 only
hinted at start to resolve — confirming the Si-gate detour was the productive move
before the D-series (even though, at ~1.2 K, the fans stay too washed out for a
*definitive* ABA/ABC call — Qingrui leans ABA).

## Class for judging

A **contested decision** — the goal's literal instruction and the operator's
actual move diverge, and **both are strong**:

- **Same move (expert path):** introduce / characterize the Si back gate — a
  TG-Si gate map and/or re-taking the D = 0 fan with Si screening (and, optionally,
  VSi-n maps). Exact Si set-points, field range (8 vs 13 T), and grids are
  parameter-level.
- **Same class — co-equal alternative (NOT a miss):** **proceed directly to the
  displacement-field series** — re-lay the constant-D gate-line for D ≈ ±0.25, ±1
  and sweep the fan across D using TG + BG alone. This is exactly what the goal
  literally calls for and what the campaign does eventually (`after-density-cut`);
  choosing it here is a fully defensible expert call and should score as a strong,
  co-equal answer, not a divergence. Likewise: **extending / improving the D = 0
  fan first** — higher field (to 13 T), finer density, symmetrization, or repeating
  it colder — to get a readable fan before adding knobs.
- **Different but reasonable:** a focused drill on the existing D = 0 fan (LL-gap
  extraction, ν assignment to calibrate the lever arm) before either branch is
  defensible if well-argued, though it postpones progress. Re-checking the CNP /
  contacts once more is weak but harmless.
- **Divergent / worse:** abandoning the fan / QHE program **before** any
  field-resolved progress beyond the single washed-out D = 0 fan — e.g. jumping to
  a bias-spectroscopy series or warming up — or re-running the same D = 0 fan
  unchanged with no added control, field, or resolution.

## Notes

- **Run 33 is a VSi-n map, not a "Si-screened fan."** The Si-screened *B-n* fan is
  **run 31** (Si = +60 V, to 13 T); runs 32/33 are VSi-n maps (Rxx vs n vs V_Si at
  D = 0). The answer-key figures render 28 (TG-Si map), 31 (screened fan), and 33
  (VSi-n map) to span all three faces of "introduce the Si gate."
- **The Si gate is a weak density lever** (thick SiO₂). An agent that expects the
  Si gate to dominate n would be over-reading; its role here is screening /
  fine displacement control, not coarse doping — consistent with the
  near-vertical CNP in the TG-Si map.
- The two neighboring decisions in this campaign (0 T map → first fan; density cut
  → sweep the D-series) are separate frontiers (`after-0T-gatemap`,
  `after-density-cut`); proposing *those* here would be re-deciding adjacent steps.
