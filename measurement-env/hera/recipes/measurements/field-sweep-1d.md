# Field sweep 1D

## What
Sweep the magnetic field from one setpoint to another at fixed (V_tg, V_bg) (and fixed V_si, fixed bias), reading every lock-in channel along the way. The simplest measurement in the toploader pipeline that varies field, and the natural follow-up when a `gatemap` or `nD-map` reveals a feature you want to characterize as a function of B. Plots via `sharpelab_nb.plotting.plot_sweep(file_path, [file], ...)`. Two distinct usage modes:
- **"Linecut in field" mode** (Aaron) — pick an (n, D) point that looked interesting in a gatemap, ramp the gates, run a tight sweep over a small B range to look for AHC switching, SC critical fields, etc.
- **"Full-range MR" mode** (Bingcheng) — no gates, fixed angle/orientation, sweep B over the full ±10/±12 T range to characterize the magnetoresistance landscape.

## When
After the validators are blessed and after at least one `gatemap` / `nD-map` / `gatemap-in-field` has revealed a feature worth probing. For Bingcheng's gateless rotator workflow, the dependency simplifies to "instruments are initialized, rotator is at the desired angle." Often run repeatedly inside one session, sweeping the same gate point over progressively wider B ranges (cf. RPL_19 "AH Spot Checks"): the same `Station` is reused across many cells.

## Why
Cheap (10–60 minutes per sweep), highly informative, and the only measurement that resolves SC critical fields, hysteresis-switching fields, weak-localization peaks, and other field-axis features with full B-axis density. A 2D `gatemap-in-field` sees one B value; a 1D field sweep sees the whole axis at one (n, D) point. The two modes are complementary.

## Recipe
**Common shape — single Station built once, reused across many sweeps:**
1. Build `s = sweep.AsyncStation(mc)` (or `sweep.Station(mc)` for Bingcheng's synchronous workflow).
2. Compute the target (V_tg, V_bg): `Vtg, Vbg = calculate_gate_voltages(n, D, dtg=..., dbg=...)`. Skip if you're in Bingcheng's gateless mode.
3. `s.ramp(sr830_1.amplitude, A)` to set excitation; `s.ramp(k_tg.volt, Vtg); s.ramp(k_bg.volt, Vbg)`; `s.ramp(k_si.volt, V_si)`; `s.ramp(bias_voltage.volt, 0)` if a DC bias source is present. `s.ramp(mag.field, B_start)` to position the magnet at the start of the first sweep. `time.sleep(10)` (or longer for high field).
4. `s.add_comment('field-sweep-1d')` then optional structured tag identifying the gate point: `s.add_comment(f'(Vtg, Vbg) = ({Vtg}, {Vbg}), n = {n}, D = {D}')` (parseable by `comment_to_gates` if you use the `'label: (Vtg, Vbg)'` form). For RPL_19 idioms, also `s.add_comment(grab_metadata())`.
5. `fp` temperature(s), all three gate currents (or just gate voltages if Isaac's idiom), and every lock-in X / P. `plot` `mag.field` vs each lock-in X (the live magnetoresistance trace) plus `'time'` vs each gate current (live leakage).
6. (Optional, recommended for high-bandwidth runs) `s.register_run_before(autorange_sr830s_v2, (sr830_4, sr830s_2_autorange,))` so sensitivity tracks the trace.
7. **The sweep — multiple cells, same Station**: `s.sweep(mag.field, np.linspace(B_start, B_end, N), delay=0.5)`. Each subsequent cell is just another `s.sweep(...)` call — Aaron's idiom is to escalate the range on each cell ("`np.linspace(0, 0.1, 101)`", "`np.linspace(0.1, -0.1, 101)`", "`np.linspace(-0.1, 0.2, 201)`", etc.), bumping the bounds outward as features appear. Each `s.sweep` produces one file. The Station is *not* rebuilt between cells — the comments accumulate, the fp/plot list persists.
8. **End**: `mag.field(0)` (or wherever the next section needs it), `k_bg.volt(0); k_tg.volt(0)` if done with this gate point.

**Notes on cadence:**
- Aaron uses `delay=0.5` for fast field sweeps (101 points × 0.5 s = ~1 minute), `delay=1` for slower scans where Hall channel needs more averaging.
- Bingcheng uses `delay = 3 * time_constant` (with `time_constant = 1` s, that's 3 s/point × 4801 points × ±12 T × 5 mT step = ~4 hours per sweep). The slower cadence is justified by the 5 mT B-step resolution he wants for hysteresis-feature visibility.
- For paired forward/backward at the same gate (a hysteresis check by another name), see `hysteresis-check`.

**Notes on field source plumbing:**
- AMI430-controlled magnet: `mag.field` is the canonical parameter; `mag.field(B)` sets, `mag.field()` reads. Ramps respect the AMI430's internal ramp rate.
- Yokogawa-controlled magnet (`yoko_mag` in RPL_19/20251220+): same parameter surface, but the Yoko has a write-only software cache (see `sharpelab_nb.drivers.Yokogawa7651`). After a kernel restart, seed the cache via `set_voltage_cache()` / `set_current_cache()` or pass `start=` to ramp methods, or the ramp will raise.
- Aaron sometimes ramps to one field, then rebuilds the Station and ramps to a different field to start the next sweep (RPL_19/20260124 cell 53 — bidirectional ±1 T pair using the same Station). Bingcheng ramps the field once and stays there for an entire-axis traversal in a single `s.sweep`.

## Examples
- `bingcheng/NF02B1_dev00/NF02B1_dev00_measurement.ipynb` cells 21–26 — full-range MR mode, gateless. **Cell-range adjustment vs. index** ("cells 25–26"): the actual sweep is at cell 26 but the recipe consumer needs the upstream `meas_config` (cell 21) and `smagneto = sweep.Station(meas_config)` + `fp`/`plot` block (cell 22) to understand the surface. Cells 23–25 set helper `lia_vec`, the `delay = 3` constant, and `B_max, B_min, B_step = 12, -12, 0.005` with `field_vec = calc_field_vec2(...)` building a full ±12 T traversal in 5 mT steps. Cell 26 is the actual `smagneto.sweep(mag.field, field_vec, delay=delay)`. Distinctive: uses `sweep.Station` (synchronous) rather than `AsyncStation`, no `add_comment` calls (Bingcheng's idiom), `meas_config["comment"]` carries the recipe-tag in the static config instead. The gateless meas_config explicitly enumerates `lia1` ("current"), `lia2` ("B - D (28 - 22)"), `lia3` ("D - E (6 - 21)"), `lia4` ("E - F (7 - 10)") and three contact pairs by physical channel.
- `aaron/RPL_10/241230_measure.ipynb` cells 49–53 — "linecut in field" mode, but with a strict-1D-vs-2D nuance. **Cell-range adjustment vs. index**: the brief cited 49–53 as "n vs B scans" — only **cell 51** is a strict 1D field sweep at fixed (V_tg, V_bg). Cells 50, 52, 53 are 2D `multimegasweep` calls that pair `mag.field` (slow axis, 101–351 points) with a paired (V_tg, V_bg) (n-line, fixed D) fast axis — these are landau-fan-shaped (see `landau-fan`). Crop captures cell 51 in full as the canonical strict-1D example: `vtg, vbg = calculate_gate_voltages(-2.6, 0.31)` then `s.ramp(k_bg.volt, vbg); s.ramp(k_tg.volt, vtg); s.ramp(mag.field, 0)` then `s.sweep(mag.field, np.linspace(0, 1, 1001), delay=1)`. The `add_comment` carries the (Vtg, Vbg) tuple in `comment_to_gates`-parseable form: `f'..., (Vtg, Vbg) = ({vtg}, {vbg})'` — Aaron-style structured tagging at its best.
- `aaron/RPL_19/20260124_measure.ipynb` cells 41–53 — mature linecut-in-field mode, ±B escalating sweeps. Cell 42 is the canonical full setup cell: AsyncStation, `s.ramp` to (n=0.465, D=1.000), `s.add_comment('MC6, Vsi = 48V, gate map in -100 mT')` (stale text — actual setpoint is 0 T at cell start, ramping to 0.1 T mid-cell), `fp`/`plot` block, autorange callback installed (`s.register_run_before(autorange_sr830s_v2, (sr830_4, sr830s_2_autorange,))`), then `s.sweep(mag.field, np.linspace(0, 0.1, 101), delay=0.5)`. Cells 43–52 are each a one-line `s.sweep(mag.field, np.linspace(B_start, B_end, N), delay=0.5)` reusing the same Station, escalating ranges: 0.1 → −0.1, −0.1 → 0.1, 0.1 → 0.2, 0.2 → −0.2, ..., 0.7 → −0.7. Cell 53 is the widest pair: `s.sweep(mag.field, np.linspace(-1, 1, 501), delay=0.5)` then `s.sweep(mag.field, np.linspace(1, -1, 501), delay=0.5)` — both directions in one cell, two files. This is exactly the idiom the recipe is recommending: build the Station once, run many sweeps off it. The escalation pattern (each sweep starts where the previous ended) means the magnet never has to re-traverse — efficient with wall-clock.

## Next
- **Saw a hysteresis loop or AHC switch**: that pair of files is *already* a hysteresis-check (forward + backward at the same gate). Annotate it as such and feed it to `plot_hysteresis(file_id)`. If the switch isn't clean, dedicated `hysteresis-check` recipe to take a tighter pair.
- **Found an SC critical field**: build a 2D map at finer resolution near B_c — a `gatemap-in-field` at ±B_c, or (deferred) a `fraunhofer` at fixed gate.
- **Saw quantum oscillations**: extend the range to higher field and run a `landau-fan`. The 1D `field-sweep-1d` is the warmup.
- **Found a temperature-sensitive feature**: `temperature-dependence` of the same field sweep.
- **Bingcheng's full-range MR**: typically followed by a rotator step + repeat, building up an angular survey (deferred `angular-magnetoresistance-survey`).
