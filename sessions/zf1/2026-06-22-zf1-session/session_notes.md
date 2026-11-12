# Session notes — zf1 / toploader

Operational log (not a science notebook).

**SESSION RESULT (2026-06-22):** zf1 bottom device **SUPERCONDUCTS (decisive)** — proximity SC at
n≈−4.65e11, D≈−0.65 V/nm. Ic≈18–24 nA, B_c⊥≈2.5 mT, Tc≈234 mK, ξ~360 nm (o.o.m.). Full constellation
+ 5-part verdict in `20260622_ana.ipynb`. Runs: 0 liveness, 1 recon, 2 survey(+cap-ratio 1.185),
3 fine linecuts (found candidate), 4 confirm(Rxx→0), 5 bias-spec(Ic), 6 field-kill, 7 Ic(T).

## 2026-06-22

**TOOLING — `meas_config["bias_voltage_1"]` freezes at config-build, stale in run metadata.**
Cell 21 captures `bias_voltage_1 = sr830_1.amplitude()` once, when setup runs.
The Gate C cell set `sr830_1.amplitude(0.1)` (→1 nA) at run time, but metadata still
recorded `bias_voltage_1: 0.05` (the 0.05 V / 500 pA that was set at setup). Consequence:
`hera-watch`'s auto `R = V/I_bias` used 500 pA and reported ~2× the true resistance.
The *measured* current channel (`sr830_1`, 1.006 nA) is authoritative — recompute R from it.
Fix going forward: in each run cell, refresh `meas_config["bias_voltage_1"] = sr830_1.amplitude()`
(and `lockin_freq_1`) after setting the drive, before building the station. (run: data/0)

**TOOLING — two sequential `hera-watch --next` arms race against run start.**
Armed a completion watch (`--next --follow`), then in a *later* message armed a
checkpoint watch (`--next --timeout 2100`). Between the two, the operator started the
survey (run 2), so the checkpoint watch snapshotted known={0,1,2} and waited for run 3,
which never came — timed out at 2 h, missing the 35-min checkpoint entirely. No cost this
time (run was healthy, caught at 91% via `--once`). Fixes: (a) arm checkpoint + completion
watches **back-to-back in one message** before the run can start (both snapshot the same
known-set, both latch the new run); or (b) once the run dir exists, checkpoint with a
**specific-id** watch `hera-watch data/<id> --timeout N`, not `--next`. Prefer (b) for
mid-run checkpoints once the id is known. (run: data/2)

**FEEDBACK/TOOLING — setup pointed `temperature` at a DEAD thermometer (Probe2); live sensor is Probe1.**
The measure setup cell (idx 8) set `temperature = temperature_from_logfile("T", ...Probe2_MixingCh_low.txt)`
with a `# <-- verify probe` comment, trusting the device card's "rotator probe (Probe2) loaded". But
`Probe2_MixingCh_low.txt` **stopped updating at 13:10 (Saturday), ~2.4 days before the session** — frozen
at ~33.7 mK. `Probe1_MixingCh_low.txt` is the **live sample sensor** (tab col[-3] = T in K): it tracked
run 7 exactly — base 31 mK → 433 mK at the 6 V warm-up → cooling through the ladder. Caught at the run-7
checkpoint via the recipe's stale-logfile discriminator (heater drawing 600 µA + dV/dI showing the sample
heated, while `T` stayed frozen). **Impact:** runs 0–6 unaffected (no heating; sample genuinely at base,
which the frozen value happened to match). Run 7's T-axis is reassigned post-hoc from Probe1 by
timestamp cross-ref — no re-run needed. **Fixes:** (1) the [VERIFY] probe-selection check must compare
logfile mtimes/freshness, not just trust the device card; (2) the device card's "rotator probe loaded"
may be stale — Probe1 (straight) appears to be the live one; confirm with operator. (3) Probe2 AVS worker
likely dead — operator to restart for future sessions. (run: data/7)

**RECIPE FIX — `gate-current-sanity-check` cheap-liveness branch: surface the metadata refresh.**
The recipe sets `sr830_1.amplitude(<...>)` in Cell A but doesn't refresh `meas_config`'s
captured bias voltage, so the run metadata (and any V/I_bias auto-analysis) is wrong whenever
the drive differs from setup. Worth a one-line note in the recipe. (run: data/0)
