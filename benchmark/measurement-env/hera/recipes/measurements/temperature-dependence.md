# Temperature dependence

## What
Temperature as a measurement axis. On the toploader the "temperature knob" is a raw heater voltage — a Keithley 2400 named `heater` on the RPL devices (GPIB4::12, ±6 V validator on RPL_10) or an SRS DC205 (`dc205_1.volt`) on TD48 — **not** a fridge-controller setpoint. There is no closed loop and no calibrated heater-V→T map: the actual temperature must be read back from the `T` column that `s.fp(temperature)` writes into every sweep. Two structurally distinct flavors in the corpus:
- **Flavor A — heater-stepped 2D map** (tMoTe₂ TD48 idiom): the heater drive is the slow axis of a `multimegasweep` over a paired-(k_tg, k_bg) n-linecut at fixed D ⇒ one file containing the whole R(T, n) map. The dome-mapping shape.
- **Flavor B — T-ladder of 1D sweeps at a fixed point** (RPL_19 effective-mass idiom): a Python `for` loop over heater setpoints; at each step, ramp the heater, thermalize, and repeat the *same* 1D sweep (usually `mag.field`) ⇒ one file per T. The amplitude-vs-T / T_onset shape.

A third corpus form — full gatemaps repeated at a manually-tuned T ladder (RPL_10 `# Gate maps at temp`, T = 300/200/115/50 mK) — is just `gatemap`/`nD-map` re-run per temperature; use those recipes with the heater discipline from here.

## When
After a feature exists that T can discriminate:
- **Dome mapping** — a vanishing-ρxx region needs its T extent: ρxx(T, n) at fixed D is the arXiv 2504.06972 Fig. 3 move (SC dome: T_onset ≈ 1.2 K, zero resistance < 300 mK). Flavor A.
- **T_onset / gap extraction** — where does ρxx(T) at one point deviate from the projected normal-state trend? Flavor B at the dome/dip center.
- **Effective mass** — quantum oscillations confirmed by a `landau-fan`; LK amplitude-vs-T needs the same field sweep at 5–9 temperatures. Flavor B.
- **Quantization development** — does a plateau/dip sharpen below some T? Decides whether base-T time is worth committing.
- **Artifact discrimination** — a hysteresis loop or oscillation that survives warming is physics; one that doesn't may be instrumental (pairs with `hysteresis-check`'s time-constant ladder).

**T-ladder ordering**: survey warm, refine cold. Everything is faster and more robust warm (features are broad, lock-in scales tame, no fragile states to heat); base-T time is the scarce resource, so spend it only on what the warm survey proved interesting (arXiv 2504.06972's own (ν_h, D) maps descend 2 K → 900 mK → 100 mK). Mechanically the corpus often *measures while cooling* — warm up first, then step the heater **down** through the ladder (TD48: `np.linspace(7, 0, 15)`) — because stepping down approaches each setpoint from above with the mixture's own cooling power doing the settling.

**Honest caveat (lab input required)**: all corpus examples drive a resistive heater against the mixture and read a probe/MC thermometer. Whether that plumbing — which heater, which thermometer governs, achievable range and stability, base *electron* temperature — carries over to the next cooldown's sample-in-mixture setup is an open lab question (campaign-readiness report §4.0 item 4). This recipe documents the corpus idioms; confirm the T-control mechanics with Aaron before promising a T-campaign on the new device.

## Why
Temperature is the cheapest discriminating axis after field: no new wiring, no new configs, and the warm part of the ladder is *faster* than base-T work. A completed Flavor-A map answers "is there a dome and where" in one ~3 h file (TD48 files 12/20: 2.92 h each, verified). A Flavor-B ladder turns a qualitative "dip" into numbers (T_onset, m*, gap) that anchor the writeup. The corpus uses it constantly — RPL_10's qo-discovery fixture's *answer* is `# Temperature dependence`; RPL_19 spent whole sessions on effective-mass ladders.

The costs are thermalization time (5–15 min per step, 1 h to recover base) and risk: heating can pop the fridge into an unstable regime (RPL_10/241230 records an accidental 1 K trip mid-campaign), and on fragile-state devices the measurement excitation itself is part of the thermal budget.

## Recipe
**Common to both flavors:**
1. `s.fp(temperature)` — non-negotiable; the heater voltage is meaningless without the readback. Add `s.fp(fridge_temperature)` where the second sensor exists (RPL_19). The columns land as `T` (TD48), `T`+`T` (20260124-era RPL_19 — duplicate name), or `T_probe`/`T_fridge` (later RPL_19).
2. `s.add_comment('temperature-dependence')` plus a structured tag (`f'axis: heater {h_lo}-{h_hi} V, n-line at D = {D0}'` or the fixed-point form), and `s.add_comment(grab_metadata())` where available (RPL_19/20260124 cell 353 does this; the TD48 cells reuse a single `'D=0 linecut vs temp'` string for everything including the later DC-bias runs — stale-comment trap).
3. Confirm the heater is actually drawing current after every ramp: `s.ramp(heater.volt, sp); time.sleep(1); s.read(heater.curr)` — the corpus does this religiously (RPL_10 reads it twice). A heater at setpoint with zero current is an open line and your "ladder" is all base-T.
4. Settle/cooldown gates are **stability criteria, never absolute targets**: gate on |dT/dt| below a floor, or on settling within a band of the running asymptote — not "wait until T < X". Base T is a property of the *current* fridge config (needle-valve flow, heating history), and an absolute threshold remembered from before the heated period can sit below the new equilibrium, timing out a queue that has in fact settled. Design the fallback in: proceed at the new equilibrium when the physics tolerates it — escalate to the operator, don't die at a timeout.
   - The per-step dwell *duration* is a rig fact, not a recipe constant: the rig card's heater discipline is the override, and it applies for all changes in heater voltage (up or down).
   - Guards must be **direction-aware** when a ladder descends: an up-leg overshoot assert (T > c·target) fires on legitimate cooling from the rung above. Fault on true runaway — T rising above *both* its rung-start value and the target — never on approach from above. [our-measurement: VTI LK ladder v1 abort, 2026-07-15]

**Flavor A — heater-stepped R(T, n) map (TD48):**
5. Take a base-T reference linecut first — same n-line, plain `multisweep`, before any heating (TD48 cell 66 → file 9: 301 pts, `delay=1`).
6. Warm up *manually* to the ladder top and let the fridge find equilibrium (TD48 cells 56–62: single `s.ramp(dc205_1.volt, V)` cells stepping 1→6 V over a stretch of wall-clock; RPL_19's loop form sleeps 5 min per volt-step).
7. The map, stepping the heater **down**:
   ```python
   ns = np.linspace(-0.8E13, -0.33E13, 501)
   Ds = 0.005 * np.ones(len(ns))
   Vts, Vbs = nD_to_VbVt(ns, Ds)
   s.multimegasweep([dc205_1.volt], [np.linspace(7, 0, 15)],
                    [k_tg.volt, k_bg.volt], [Vts, Vbs],
                    slow_delay=5*60, fast_delay=1)
   ```
   `slow_delay=5*60` is the per-step thermalization (the only place in the corpus a multi-minute slow_delay appears). `init_delay=False` skips the first settle when the heater is already at the start value (TD48 cells 76/105). 13–15 steps × (300 s + 501 s) ≈ 3 h.
8. Hold every other knob fixed and re-assert the ones that matter inside the cell — TD48 re-ramps `k_cg2.volt` to −3.2 V (the contact-gate operating point) in *every* sweep cell, because a map with the contact gate off is garbage (it happened: cell 110's "contact gate wasn't on" rerun).
9. **Gotchas from the source session**: TD48's first two map attempts (cells 71/72 → files 10/11) were both **interrupted** (0.01 h and 0.56 h); the completed canonical runs are cell 76 → file 12 (6→0 V) and cell 105 → file 20 (0→6 V). And the adjacent `## Change config` cluster records the canonical source-output blunder — cell 99 markdown: *"we didn't have the output on. rerunning but in a finite field"* — a botched run (file 15, source output off) caught only by looking at the data, then deliberately re-run at −0.2 T (cell 98/100 → file 16) rather than just repeated. Verify your slow-axis source is *on* (step 3's `s.read` is exactly this check for the heater), and treat a rerun as a chance to also vary what you wished you had.

**Flavor B — T-ladder of 1D sweeps at a fixed point (RPL_19):**

**Ladder-top design from the mass prior (LK).** For an effective-mass ladder,
size the top rung from the expected mass, not from precedent: the LK argument
is X = 14.69·(m*/mₑ)·T/B (amplitude ∝ X/sinh X), evaluated at the FFT window's
effective field (1/B_eff = window midpoint in 1/B) and at the **lightest**
expected mass — the light tone needs the hottest rung. Put the top at X ≳ 3
(amplitude ≲ 0.15) with 5+ rungs spanning X ≈ 0.5–3; a top that leaves the
light tone above ~50% amplitude ill-conditions the fit. At m* = 0.02 mₑ and
B_eff ≈ 4 T that is ~40–55 K [our-measurement: QC0426/VTI 2026-07-16, 32 K top
left m_ML ≈ 0.02 barely suppressed; AS ruling: m* ~ 0.03 mₑ ⇒ T range toward
~100 K]. The rig card's T ceiling authorizes; X designs — do not inherit a
ladder top from an earlier session's ceiling. Re-fit as the hot rungs land and
extend the top *while hot* if X coverage falls short — lifting further is
cheap, re-heating later is not.

5. Ramp gates to the (n, D) point; build one AsyncStation; then loop:
   ```python
   h_sps = [0, 1, 2, 3, 4, 5, 6, 7]
   for i, h_sp in enumerate(h_sps):
       s.ramp(heater.volt, h_sp)
       time.sleep(1)
       s.read(heater.curr)
       mag.field(1.25)                      # reposition for a same-direction sweep
       interruptible_sleep(10*60)           # thermalize (10-15 min in the corpus)
       s.sweep(mag.field, np.linspace(1.25, 0.75, 501), delay=0.9)
   alerts.discord(f'🐍{ind} done 🐍')
   ```
   (20260124 cells 147–172 — one such cell per density, n = 0.95 → 0.55.) One file per (T, sweep); ~20 min per 501-pt sweep including ramps (file 1684: 0.33 h, verified). Per-point ladder ≈ 6 × (10 + 20) min ≈ 3 h.
6. Between ladder points (new density / new gate point): `heater.volt(0)` then `interruptible_sleep(60*60)` — the corpus allows a full hour to recover base. **Watch out** for the cell-188 typo: `interruptible_sleep(5^60)` is XOR — 57 seconds, not 5 minutes; the thermalization silently never happened. Write `5*60`.
7. Variants, both real: alternate the sweep direction each ladder step so the field never re-traverses (`# Heating at CSC`, cell 186: a `flag` flips between 1→4 T and 4→1 T sweeps, 15-min thermalization); or take a forward+backward *pair* per T when the observable is a hysteresis loop (`# Temp dependence at the Hot spot`, cell 353: 9 heater steps × ±0.6 T pair at 1201 pts — Aaron's own wall-clock note, cell 351: "+/- 350 mT @ 700 steps takes 40 mins").
8. The same heater discipline drives map-ladders: RPL_10's `# Gate maps at temp` walks the heater manually (1→2→3→4→5→4.5→4.7 V, cells 212–218) *hunting* for a target readback before each `## T = 300 mK`-style map — the heater-V↔T relation is found empirically, expect to iterate.

## Verify
The defining check is that **T actually moved and settled** — read back from the data, never trusted from the setpoint. A flat T has two causes that must be separated: the sample didn't heat (heater off / open line / wrong sensor), **or the readback is frozen** — a dead thermometry worker pins the logfile at a stale value. Discriminator: if `heater.curr` is drawing **and** an independent signal (R, dV/dI) shows the sample heated while T stays flat, the logfile is stale — re-check worker liveness; don't trust the T column or read a Tc off it.

```python
from hera.analysis import open_run, summarize_run
import numpy as np

run = open_run("<notebook_dir>/data/<file_id>")
print(summarize_run(run))

assert not run.interrupted, "interrupted — TD48's first two T-maps both were; investigate"

# 1. Locate the temperature column. Names vary by era: 'T' (TD48; RPL_19
#    20260124 has probe + fridge both named T — col() takes the first),
#    'T_probe'/'T_fridge' (later).
T = run.col("T_probe") if "T_probe" in run.cols else run.col("T")
print(f"T span: {np.nanmin(T):.4g} → {np.nanmax(T):.4g}")
assert np.ptp(T[~np.isnan(T)]) > 0, "T never moved — heater off / open line / wrong sensor"

# 2. Flavor A: per-heater-step T plateaus, monotonic ladder.
#    Group rows by the slow column and check each step settled.
if "dc205_voltage" in run.cols:           # heater slow axis (TD48 idiom)
    h = run.col("dc205_voltage")
    t_means = [np.nanmean(T[h == sp]) for sp in np.unique(h)]
    print("T per heater step:", np.round(t_means, 4))
    d = np.diff(t_means)
    assert (d >= 0).all() or (d <= 0).all(), "T ladder not monotonic — thermalization too short"
    for sp in np.unique(h):
        Ts = T[h == sp]
        if np.nanstd(Ts) > 0.05 * abs(np.nanmean(Ts)):
            print(f"⚠️  heater={sp} V: T drifted {np.nanstd(Ts):.4g} during the row — still settling")

# 3. Flavor B: one file per T — check intra-file drift, and build the
#    ladder by reading T from each file in the series (NOT from h_sps).
#    A drifting T within one field sweep smears the LK amplitude.
if run.swept_axis == "magnet_field":
    drift = np.nanmax(T) - np.nanmin(T)
    print(f"intra-sweep T drift: {drift:.4g}")

# 4. Usual completeness/liveness: lock-ins not flat/NaN; gate-current
#    columns checked when present (TD48 fp's them out — comment block).
for name in set(run.cols):
    if name.startswith("sr830_") and name.endswith("_X"):
        x = run.col(name)
        if np.allclose(x, x[0]) or np.isnan(x).any():
            print(f"⚠️  {name} flat or NaN")
```

For Flavor B series, also confirm the ladder *covers the question*: a T_onset extraction needs points straddling the deviation; an LK fit wants ≥5 temperatures with the amplitude visibly suppressed at the top of the ladder — if the highest-T sweep still shows full-strength oscillations, extend the ladder up before burning base-T time.

## Examples
- `aaron/tmote2/td48/TD48_measure1.ipynb` cells 66–76 and 105 — Flavor A, the only moiré-TMD T-maps in the corpus. **Cell-range adjustment vs. index**: the tmote2 index names cell 71 → file 10 as the canonical example, but files 10 *and* 11 (cells 71/72) were both interrupted (0.01 h / 0.56 h, verified from metadata); the completed canonical runs are **cell 76 → file 12** (heater 6→0 V, 13 steps, `init_delay=False`, 2.92 h) and **cell 105 → file 20** (0→6 V ascending, 2.92 h). Cell 66 → file 9 is the base-T reference `multisweep` (301 pts); cell 63 defines `nD_to_VbVt` (t_bg = 6.7 nm, t_tg = 7.9 nm, eps = 3); cells 54–62 are the manual warm-up ramps; CG2 re-asserted to −3.2 V in every cell. The `# Heating up` header sits at cell 53, well before the actual sweeps. Heater column in data: `dc205_voltage`; T column: `T`.
- `aaron/RPL_19/20260124_measure.ipynb` cells 101–112, 146–172, 185–190, 350–354 — Flavor B across its whole maturity arc. Cells 105–112 are the early form (separate ladder cells `for sp in np.linspace(1, 7, 7): ... interruptible_sleep(5*60)` between repeated 751-pt field sweeps at (n=1, D=1)); cells 147–172 are the mature one-cell-per-density loop form (`h_sps = [0, 1.5, 3, 4.5, 6, 7]`, 10-min thermalization, 1-h base recool, B 1.25→0.75 then 1.4→0.9 in the `## Continuing but with higher field range` cells 168–172); cell 186 (`# Heating at CSC`) adds the alternating-direction `flag` trick (3001-pt sweeps 1↔4 T, 15-min settles) and cell 188 carries the `5^60` typo flagged in the Recipe; cell 353 (`# Temp dependence at the Hot spot`) is the hysteresis-pair-per-T variant with `add_comment(grab_metadata())` and the v2 autorange. The `before-effmass` fixture (`hera/test-cases/2026-01-24-RPL19-qo-effmass`) freezes this notebook at cell 100, where the ladder's *depth* is the open decision. Data gotcha: this session's files carry two columns both named `T`.
- `aaron/RPL_10/241230_measure.ipynb` cells 55–69 (and 211–278) — the qo-discovery fixture's answer key. The post-fan move is `# Temperature dependence` (cell 55): manual heater steps (Keithley `heater`, cells 57–59/61/65/67–68, always with the double `s.read(heater.curr)` check) interleaved with repeated n-linecuts at D = 0.35/0.365 (cells 60/63/64) — Flavor-B-shaped but with an n-line, not a field sweep, as the repeated unit. Two oddities worth knowing: cell 62 wraps its multisweep in `while True:` + `KeyboardInterrupt` (sweep continuously while the fridge drifts, operator stops it by hand), and cells 67/69 sweep a *constant* 4000/13000-pt n-vector — a fixed-point time trace recording R while T evolves. Cells 211–278 (`# Gate maps at temp`) are the map-ladder form: heater hunting (212–218) then full polygon maps tagged `'MC5, Vsi = -30V, 300 mK'` at T = 300/200/115/50 mK, descending.

## Next
- **Dome found in a Flavor-A map**: pick the dome center and interrogate — `field-sweep-1d` fine B-scans (critical field), `hysteresis-check`, and dV/dI vs I_dc once `bias-spectroscopy` exists (deferred). For the (T, B) plane → B_c(T) (the GL move, cf. arXiv 2504.06972 Fig. 4), repeat the field sweep per T — Flavor B with the dome center as the fixed point.
- **Feature sharpens cold**: commit base-T time — denser `nD-map` around it, `landau-fan` if it might disperse, quantization-accuracy spot checks. The warm survey has done its job.
- **Feature unchanged or gone warm→cold**: deprioritize; it was either trivial or instrumental.
- **Amplitude-vs-T ladder in hand (QO)**: Lifshitz-Kosevich fit is ana-side. The corpus workflow is the semilogy-overlay in `RPL_19/20260124_ana.ipynb` cells 41–43 and the `# Returning to effective mass` batches (cells 57–70, files 1684–1741 in 6-file chunks — one chunk per `h_sps` ladder); note **no automated LK fit exists in the corpus** — the extraction is visual/manual, flag the fit itself for expert review.
- **ρxx(T) deviates from the normal-state trend at one point**: that's your T_onset candidate; verify it reproduces on a second contact pair before claiming it (arXiv 2504.06972 reports T_onset from exactly this deviation criterion).
- **T won't settle / ladder not monotonic**: if T has *stopped moving* but sits above an absolute threshold, the threshold is stale, not the fridge — re-reference to the current equilibrium (common rule 4). Otherwise: thermalization too short — lengthen `slow_delay`/`interruptible_sleep`, or the heater range is fighting the fridge's cooling power; escalate to the fridge owner. If the new device's T-control plumbing is unconfirmed, this is the §4.0-item-4 conversation with Aaron, not a recipe fix.
