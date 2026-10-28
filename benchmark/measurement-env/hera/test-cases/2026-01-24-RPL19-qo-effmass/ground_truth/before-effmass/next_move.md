# Ground truth — next move at the frontier (cut idx 100)

*What Aaron actually did in the next section (`# Effective mass`, cells 101–145,
→ `data/1639`+). One expert path, not the only answer — used to route the replay
to review, never as an exact-match score.*

> **Expert-confirmed 2026-06-09 (Aaron, review card).** Move capture confirmed
> ("yes") and the depth framing confirmed ("Correct") — with one addition: depth
> here is not only rigor but also **coverage**: *"also a question of where we
> want to perform these measurements. Do we want to take more n and D."* An
> agent that raises the at-which-(n, D)-points question alongside
> #temperatures / ΔB / averaging is reading the frontier well. Caveat on the
> `mc_25` config label: Aaron's ana cells note it is mislabeled, and per the
> Device-facts review he *"often messes this up"* — trust the contact map over
> the config label.

## The move: `# Effective mass`

A **temperature-dependent field-sweep series at a fixed (n, D) anchor**, to
extract the effective mass from the temperature damping of the quantum
oscillations:

- Park gates at **(n = 1, D = 1)** (`calculate_gate_voltages(1, 1, dtg=17.25,
  dbg=25.5)`), V_Si = 48 V, DC bias 0, config `mc_25`.
- `s.sweep(mag.field, np.linspace(1.5, 0, 751), delay=0.4)` — a single 1.5 → 0 T
  field sweep at **base temperature** → `data/1639`.
- Then step the sample temperature up via the `heater` (`for sp in
  np.linspace(1, 7, 7): heater.volt(sp); …; interruptable_sleep(5*60)`) and
  **repeat the same 751-point field sweep at each temperature** (cells 105–112 →
  `data/1639`–`1642`, continued and refined in `# Resuming effective mass` out to
  higher field, cells 146–172). Heater steps span ~1–10 V (a ladder of
  mixing-chamber temperatures).
- The oscillation amplitude vs. T at fixed field is then fit to the
  Lifshitz–Kosevich thermal damping factor → m*.
- His own analysis of this series (`20260124_ana.ipynb` cell 42, `files=[1639,
  1640, 1641, 1642, 1646]`) overlays the Rxx(B) traces at each temperature over
  ~0.75–1.25 T — see `figures/ana_1639_effmass-tdep_sr830_1.png` (answer-key
  only; post-cut).

## Why this is the right next step
m* extraction in a 2D metal is, canonically, the **T-dependence of the
Shubnikov–de Haas amplitude**: the LL oscillation amplitude decays as
X/sinh(X) with X = 2π²k_BT m*/(ħ eB), so a set of field sweeps at a fixed
(n, D) over a controlled temperature ladder, fit period-by-period, yields m*.
The prep section established the operating point and that the rig (field range,
heater, lock-ins) is ready; the natural and stated next move is to run the
temperature ladder.

## Class for judging (DEPTH frontier)
Because the experiment is essentially named by the section, judging here is
mostly about **execution / depth**, not experiment choice:
- **Same experiment:** temperature-dependent `mag.field` sweeps at a fixed
  (n, D) to get m* via LK damping. (Exact (n, D), field range, #temperatures,
  step density are depth-level parameters — see the `quick`/`deep`/`paper`
  briefs.)
- **Same class, different params:** m* via a different but equivalent route —
  e.g. amplitude-vs-T extracted from a temperature-series of fans rather than
  single-point sweeps, or a different fixed (n, D) on the dome.
- **Different but reasonable:** finishing/QO-frequency work first (a high-res
  fixed-(n,D) cut to nail B_F before the m* ladder), or a control check that the
  oscillations are real before investing the temperature series — defensible,
  reviewer may rate equivalent.
- **Divergent / worse:** abandoning the m* goal, re-running an already-completed
  AH map with no new axis, or a field sweep at a single temperature with no
  temperature ladder (can't get m* from one T).

## Notes
- Depth is the axis under test here: the *number of temperatures*, the *field
  range and ΔB* (must resolve several oscillation periods), and *averaging* are
  exactly what should move between the quick / deep / paper briefs while the
  sweep shape stays fixed.
