# vti-02 stacking campaign — live plan

## State at handoff (2026-08-23)

- Gate A/B and conditional E1 VERIFY green (measure cells 31–32; session_notes); post-handoff kernel probe BOUND (cell 46), state0 restored: gates 0 V, field 0 T, heater ranges off.
- Gate C complete in runs 0–3 on the only hardwired Rxx pair, B_1–B_2; no contact routing available.
- Step 1: 0 T map run 5 (run 4 interrupted after sensitivity rail). CNP A ridge slope gives c_bg/c_tg = 0.773; c_tg absolute scale remains geometry anchored. D = 0 offset −0.013 V/nm. A second parallel ridge B has a density offset of about −0.43e12 cm^-2 in A coordinates; transport mixes regions along the hardwired path.
- Step 2: spot checks runs 6 (electron, n_A +3.2e12, D_A 0, B 0→10 T) and 7 (hole, n_A −1.2e12, D_A 0, B 10→0.3 T). Both produce oscillations; FFT peaks depend on field window. Current at handoff is back at 0 T / gates 0 V after operator state0 replay, not at run-7 endpoint.

## Next measurements and decision tests

1. **Landau fan, electron side, D_A = 0.** Sweep n_A about +0.5 to +3.1e12 cm^-2 as the fast, co-swept TG/BG line, B slow from the present 0 T to 10 T (record from 0.5 T; the 0→0.5 T ramp is a prerequisite within the cell). Use ~0.04e12 density steps and ~0.1 T field steps. Record Rxx, drain current, both gate currents, temperature, and actual field. First-row leakage/rail check; periodic partial-row checkpoint. Re-form actual Rxx(B,n), identify fan branches and intercept/degeneracy patterns, track frequency vs n. Distinguish multiple Bernal bilayer-like pockets from a rhombohedral single dominant pocket and mixed dispersion; account for the second CNP ridge's offset. If the line rails or has no features by ~3–4 T, adjust sensitivity/coverage before spending the high-field traverse.
2. **Targeted refinement only if the first fan is ambiguous.** Choose a smaller (B,n) window, a second D line or a reverse-field pass to test the origin of overlapping branches. Price it from run 8 throughput and use the magnet's current endpoint; do not traverse field twice gratuitously. Avoid a standalone Si survey and any gate-limit exploration.
3. **Analysis and call.** Raw plot before derived map for every run. Report a per-region verdict for the measured B_1–B_2 path, and calibrate uncertainty from spatial mixing, geometry-anchored density scale, missing Rxy and other pairs. Use `cannot tell` where the evidence does not separate ABAB/ABCA/ABCB. Then execute the requested return-to-initial close-out and record actual readback.

## Conditions changing the plan

- If the fan gives a clear, internally consistent sequence and the region-B ridge does not compromise assignment, skip refinement and close out.
- If the density calibration fails to close on observed fan features, revise the lever arm from the *session's* data before comparing filling slopes.
- If leakage exceeds 1 nA, a channel rails, thermometry freezes, or magnet/readback tracking fails, interrupt the sweep at its safe point and re-read actual state before any move. A field-set interrupt does not stop the VTI supply ramp; enlist the operator for an in-progress ramp concern.
