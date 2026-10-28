<!-- variant: directive-long | autonomy: LOW (full 5-field brief) | length: LONG
     The fully-specified strategic→tactical handoff. Tier-3 fixes the experiment,
     observable, operating point, and stop criteria; Tier-2 owns the execution
     details (operating point refinement, bias range, plotting). Replaces the
     campaign-goal framing. Depth held = deep (so the 2x2 isn't confounded). -->

# Brief — DC-bias check of the candidate region

- **Objective.** The first (n, D) maps located a candidate
  superconducting-looking region. Find out whether a **DC-bias / critical-current
  feature** exists there — a zero-bias suppression with symmetric
  critical-current peaks — before investing in field maps.

- **Target observable.** Differential signal vs DC bias at a fixed gate operating
  point: looking for a zero-bias dip flanked by critical-current peaks (SC /
  strongly nonlinear) vs a featureless / ohmic line (nothing there).

- **Operating point.** Reconfigure the measurement so a probe sits on the
  candidate SC contact pair, and hold the gates at the candidate region from the
  maps (a point in the Vbg ≈ −8 to −9, Vtg ≈ +0.8 range at V_Si = +20 V is where
  the operator parked — refine from the maps yourself). Base temperature.

- **Approach (you own the details).** DC bias on the swept axis; first pass can
  be a single 1D bias line cut at the operating point (cheap recon), symmetric
  about zero bias to catch a zero-bias feature. Pick the bias range and step
  count yourself (the DC205 source through its bias resistor — confirm the
  resistor for the current scale). Refine the gate operating point if the first
  cut misses the feature.

- **Success / escalate criteria.** Done when you can say whether a zero-bias /
  critical-current feature is present at this operating point. **Escalate to
  strategic if:** no bias feature anywhere near the candidate region (the maps
  may have mislocated it — go back to finer maps), the operating point has
  drifted, or the bias source / resistor can't be confirmed.

- **Depth.** Deep investigation — characterize the bias response well enough to
  decide whether it's worth a field measurement; not a one-point yes/no, not yet
  a paper-grade dataset.

- **Constraints.** Stay within the gate validators. Keep the bias within the
  source's safe range. The human runs every cell.

Land the sweep.
