# vti-02 stacking campaign — working plan

## State at handoff

E1 grant and printed `VERIFY: ALL GREEN` are recorded in `session_notes.md`; measure cells 44 and 46 show the rig returned to 0 T / 0 V and kernel binding. Gate A/B passed in this kernel. The only wired longitudinal pair is B_1–B_2 (source T_0, drain B_3), so the region-resolved output can cover this measured pair only; the 0 T two-ridge structure may represent more than one region in series.

## Steps and decision gates

1. **Liveness (done, data/0–3):** compare gate-current scale, drain current and longitudinal response in the hardwired path. Stop for dead contacts or sustained leakage above 1 nA. Passed: current ~10 nA, gate currents ~0.1 nA, features move with both gates.
2. **CNP and D-line calibration (done, data/5):** extract two CNP ridges and slope near D=0. Use ridge A c_bg/c_tg = 0.773 and offsets n0 = −0.0894×10¹² cm⁻², D0 = −0.013 V/nm. Absolute n/D scale retains the 9.5 nm TG geometry prior; check against fan slopes before treating it as measured. The B ridge is shifted ~−0.426×10¹² cm⁻² in this convention.
3. **SdH feasibility (done, data/6–7):** fixed-density traces on both signs at D≈0, 0–10 T and 10–0.3 T. They show strong oscillations and Rxx <0.6 kΩ; electron FFT has ~7, 14, 23, 30 T structure with possible harmonics, hole ~5 and 12.5 T. These motivate a density fan; do not assign stacking from one trace.
4. **D≈0 Landau fan (next):** field slow, 1–10 T in 0.2 T steps from the parked 0 T, density fast −1.0…+3.2×10¹² cm⁻² in 0.05×10¹² steps, both TG/BG co-swept along the run-5 D≈0 line, Si=0, base T. This covers both carrier signs and the two ridges' expected offset, with ~20 density points per fourfold Landau spacing at 10 T. Plot raw |Rxx| and current/gate-current maps first; then track extrema in (n,B), branch intercepts and sequences. Distinct density-moving branches support distinct pockets; same-density integer multiples in single-trace FFT may be harmonics. The fan alone may yield only `cannot tell` because the two ridges can mix regions in series.
5. **Decision after fan:** compare slopes/intercepts and degeneracy/level crossings against ABAB, ABCA, ABCB predictions using this session's calibration. If clean branches distinguish one order, state it with numerical uncertainty; if mixed, use a short targeted cut at selected D/field only if the fan identifies a resolving feature and it stays in the committed box. If there is no discriminating feature, make a calibrated `cannot tell` call rather than invent a stacking assignment. Record every acquired run raw→analysis→take in the ana notebook as it completes.
6. **Close-out:** on operator `return-to-initial`, run the close-out cell to 0 T, TG/BG/Si=0 at committed pacing, both heater ranges off, and record field/gate/T readback in `session_notes.md`.

## Fan checkpoint/price

At the first complete rows, inspect gain-divided R, gate currents, drain-current continuity, clipping and measured field. Continue only if the path remains healthy. Revisit near 3, 6, and 8 T: form a partial fan and ask whether branches advance the stacking distinction; abort a washed-out or unsafe sweep using `nb-collab interrupt` (never interrupt a magnet ramp as a way to stop the supply). Price from data/6: 10 T traverse and 921 fixed-gate points completed in 2h00m. The fan's 9 T ramp floor is ~66 min; 46×85 points at 2.4 s dwell plus reads/turnaround are ~3 h, so budget ~4h30m. This estimate excludes large unexpected gate-settle overhead; read `hera-watch` ETA and actual rows to update.
