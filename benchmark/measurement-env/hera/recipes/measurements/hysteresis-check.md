# Hysteresis check

## What
Forward + backward sweep of the same axis (gate, n, or field) at the same operating point, to detect history dependence. The "axis" is whichever one the suspected hysteretic feature lives on. Two structurally distinct flavors that the analysis side consumes differently:
- **Two-file paired sweeps** — forward `s.sweep(...)` then backward `s.sweep(...)` produce two consecutive files. Consumed by `sharpelab_nb.plotting.plot_hysteresis(file_path, file)`, which auto-loads `file` and `file + 1` and overlays them via `plot_sweep`.
- **Single-file hstack** — `axis = np.hstack((forward_vec, forward_vec[::-1]))` and a single sweep call. Consumed by post-processing that splits the trace at midpoint (cf. RPL_19 ana cells 192–194 "Tracking first order Lifshitz" — `zs[:n//2] - zs[n//2:][::-1]`).

Both are valid; pick by what the downstream analysis needs.

## When
Whenever a feature in a `gatemap`, `nD-map`, `gatemap-in-field`, or `field-sweep-1d` *might* be hysteretic — bubbles, AHC switches, flavor transitions, SC dome edges. Hysteresis is the difference between "we have a real ground state" and "we have multiple metastable states selected by sweep history," and the only way to tell from a 2D map is to run the same line forward and backward and compare. Often interleaved with the survey it's testing — Aaron runs `hysteresis-check` cells inside the same notebook section that produced the suspect gatemap, not as a separate later step.

Hysteresis-check is also the natural way to study time-constant artefacts: re-run the same hysteresis at different lock-in time constants (30 ms / 100 ms / 300 ms) and see whether the loop area shrinks. If yes, the loop was instrument response, not physics; cf. RPL_19/20260217 cells 105–116 ("D = 1.04, n = 0.5 to 1, 30/100/300ms time constant").

## Why
Forward-only sweeps silently pick one branch of a multi-state region. A real ferromagnetic AHC, a charge-density-wave, or a first-order phase transition shows up only when you sweep in both directions. Conversely, a clean non-hysteretic sweep is positive evidence that the measurement is in equilibrium — the absence of a loop is also useful information.

The cost is small: one extra cell per pair (or one extra `np.hstack` call), and ~2× the wall-clock of a single-direction sweep.

## Recipe
**Common setup (all flavors):**
1. Build `s = sweep.AsyncStation(mc)` (or `sweep.Station(mc)` for Bingcheng's mode).
2. `s.add_comment('hysteresis-check')` then a structured tag identifying the axis and operating point: `s.add_comment(f'axis: n at D = {D}, n_range = ({n_lo}, {n_hi})')` or `f'axis: field at (n, D) = ({n}, {D})'`. RPL_19 idiom: also `s.add_comment(grab_metadata())`.
3. `s.ramp` gates and field to the start of the sweep. `time.sleep(10)` (or 30 s for cross-zero magnet moves).
4. `fp` temperature(s) and (lock-in X / P, gate currents). `plot` the swept axis vs each lock-in X plus `'time'` vs gate currents.

**Flavor A — two-file paired sweeps (gate axis or field axis):**
```python
# Field-axis: a pair of opposite-direction `s.sweep` calls
s.sweep(mag.field, np.linspace(0.8, -0.8, 201), delay=1)
s.sweep(mag.field, np.linspace(-0.8, 0.8, 201), delay=1)
```
Two files, file numbers N and N+1. Consumed by `plot_hysteresis(file_path, N)`.

For a gate-axis hysteresis on a 2D line in (n, D), the canonical RPL_10 form is a pair of `s.megasweep` calls with reversed slow axis:
```python
vtgs, vbgs = calculate_gate_voltages(np.linspace(n_lo, n_hi, 51), np.linspace(D_lo, D_hi, 51))
s.megasweep(k_tg.volt, vtgs, k_bg.volt, vbgs, slow_delay=3, fast_delay=1)
# (rebuild Station)
vtgs_rev, vbgs_rev = calculate_gate_voltages(np.linspace(n_lo, n_hi, 51), np.linspace(D_hi, D_lo, 51))
s.megasweep(k_tg.volt, vtgs_rev, k_bg.volt, vbgs_rev, slow_delay=3, fast_delay=1)
```
The reversal is in the slow axis only — a 2D forward/backward of the same (n, D) line. **Watch out** — the second call must be a fresh `AsyncStation` to keep file numbering adjacent for `plot_hysteresis`.

**Flavor B — single-file hstack (Aaron's RPL_19 mature form):**
```python
ns1 = np.linspace(0.3, 1, 401)
ns2 = ns1[::-1]
ns = np.hstack((ns1, ns2))
Ds = (1.0) * np.ones(len(ns))
Vtgs, Vbgs = calculate_gate_voltages(ns, Ds, dtg=17.25, dbg=25.5)
s.multisweep([k_tg.volt, k_bg.volt], [Vtgs, Vbgs], delay=1)
```
Single file, both directions concatenated. Cannot be consumed by `plot_hysteresis` directly — must be split at midpoint by the analysis.

**Flavor C — campaign loop (multiple gate points, paired sweeps each):**
The RPL_10 "Checking hysteresis in the bubble" idiom — for each of N points along a line in (n, D), ramp gates, then run a forward+backward pair of field sweeps. `for` loop with per-iteration `add_comment` tagging the index/(Vtg, Vbg):
```python
ni = -0.75
vtgs, vbgs = calculate_gate_voltages(np.ones(11)*ni, np.linspace(-0.045, 0.07, 11))
for i, (Vtg, Vbg) in enumerate(zip(vtgs, vbgs)):
    s.add_comment(f'{i}: ({Vtg}, {Vbg})')
    s.ramp(k_tg.volt, Vtg)
    s.ramp(k_bg.volt, Vbg)
    time.sleep(10)
    s.sweep(mag.field, np.linspace(0.8, -0.8, 201), delay=1)
    s.sweep(mag.field, np.linspace(-0.8, 0.8, 201), delay=1)
```
Produces 2N files. Each per-iteration `add_comment` is in `comment_to_gates`-parseable form (`'{i}: ({Vtg}, {Vbg})'` ↔ `comment_to_gates` returns the floats), so the analysis can reconstruct the (i, n, D) grid from sweep metadata.

**Choice of flavor:**
- Field-axis hysteresis at one gate point: Flavor A, paired sweeps. Smallest wall-clock, most legible to `plot_hysteresis`.
- 2D gate-line hysteresis (a megasweep run forward+backward): Flavor A, paired megasweeps.
- n-axis hysteresis at fixed D (an n-line, single-direction): Flavor B (hstack) is faster than rebuilding the Station; analysis splits at midpoint.
- Campaign of many gate points each with field hysteresis: Flavor C with structured per-iteration comments.

If you suspect time-constant artefacts: repeat at `sr830.time_constant ∈ {30 ms, 100 ms, 300 ms}` and compare loop areas.

## Examples
- `aaron/RPL_10/241207_measure.ipynb` cells 107–124 — Flavor C (campaign loop with paired field sweeps) and Flavor A (paired megasweeps with reversed slow axis). **Cell-range adjustment vs. index** ("cells 107–124"): the natural section actually splits cleanly. Cells 107–110 are Flavor C: three runs of the for-loop pattern at n_e ∈ {−0.75, −0.62, −0.53} along an 11-point D-line, each producing 22 field-sweep files (forward+backward pairs at each D). Cells 111–116 are Flavor A: a section "Changing sweep direction across bubble" running paired megasweeps over the same (n, D) line in opposite directions — cells 112/113 are the forward-direction runs and 114/115/116 are the reverse-direction counterparts. Cells 117–122 are setup/scratch (defining `nus = np.matlib.repmat(...)` for a 2D bubble grid, helper `vtgs.flatten()` calls); cells 123–124 are 2D bubble megasweeps using the gridded vectors. The 117–124 sub-section is structurally distinct from the 107–116 hysteresis pairs and could arguably belong with `gatemap` (a denser bubble re-mapping rather than a hysteresis check). Recipe consumer: read 107–116 carefully, treat 117–124 as supplementary.
- `aaron/RPL_19/20260217_measure.ipynb` cells 97–142 — extensive multi-D campaign in Flavor B (single-file hstack), with time-constant comparison. **Cell-range adjustment vs. index**: the index says 97–142 but the natural section ends at 121 (the last "D = 1.04 ... 30 ms time constant run3" cell). Cells 117–121 introduce a `D_list = [0.9, 0.92, 0.95, 0.98, 1.0, 1.02]` Python loop wrapping the same hstack pattern across multiple D values at decreasing time constants (300 ms / 100 ms / 30 ms). Cells 123–125 ("Fan at D = 0.2, valence side") pivot to a different feature; cells 127–142 ("Going back to hysteresis checks across flavor transitions") are more hstack hysteresis at D ∈ {0.2, 0.5, 0.75} but with broader scope. Crop captures cells 97–121 as the canonical Flavor B campaign. Notable: cells 100, 102, 104, 107, 110, 113, 116 are all near-identical hstack runs at D = 1.0, 1.02, 1.04 with `ns1 = np.linspace(0.5, 0.9, 201); ns2 = ns1[::-1]; ns = np.hstack((ns1, ns2))`, varying only D and time constant — the most explicit time-constant-dependence study in the corpus. No `add_comment` calls in these cells (Aaron has stopped tagging individual hysteresis runs in this notebook — a regression vs. RPL_10 discipline). Recipe asks for `add_comment` going forward.
- `bingcheng/NF02B1_dev00/NF02B1_dev00_measurement.ipynb` cells 41–55 — Flavor B (single-file hstack) for field axis. **Cell-range adjustment vs. index**: kept as is. Cell 41 is the markdown header; cells 42–48 are the 1.5 → 4.5 → 1.5 T loops at theta = 0; cells 49–55 add a wide (1 → −1 → 0 T) hysteresis loop and a tail sweep at low field. Two distinct hysteresis runs of the same gate-free orientation, with cell 46 being a `sleep(4000)` between them (4000 s = 67 min — Bingcheng is checking whether the hysteresis is time-dependent over 1+ hour timescales). Cell 45 hstack: `np.concatenate((spoints(1.5, 4.5, 301), spoints(4.5, 1.5, 301)))` — direct equivalent to Aaron's `np.hstack((ns1, ns1[::-1]))`. No gate ramps (Bingcheng's gateless mode), no `add_comment` calls. The hysteresis check is the science question here, not a side-test — the 1.5–4.5 T loop is what the angular survey is *for* (looking at the full ±10 T elsewhere puts this in context).

## Next
- **Loop closes**: feature is non-hysteretic at this time constant. Move on.
- **Loop is open**: feature is hysteretic. Tag the (n, D, B) point and note the loop area for the writeup. Optional: re-run at narrower time constant to see if the loop is real or instrumental.
- **Loop closes only at slow time constant**: the apparent hysteresis is sweep-rate artefact; not real physics. Stop.
- **Loop is open *and* survives the time-constant ladder**: physics. Next steps are `temperature-dependence` (does the loop close above some T?) and (deferred) `bias-spectroscopy` to map the gap.
- **Field-axis hysteresis showed an AHC switch**: follow-ups are `landau-fan` (does the switch evolve continuously into LL physics?) and `temperature-dependence`.
- **Saw an SC critical-current hysteresis (forward and backward Ic differ)**: deferred `idc-vs-T` and (deferred) `fraunhofer` are the natural follow-ups.
- Hysteresis-check is terminal in Block 1 — the "if you also see X" pointers above lead to Block 2 (`landau-fan`, `temperature-dependence`) or to deferred recipes (`bias-spectroscopy`, `idc-vs-T`, `fraunhofer`).
