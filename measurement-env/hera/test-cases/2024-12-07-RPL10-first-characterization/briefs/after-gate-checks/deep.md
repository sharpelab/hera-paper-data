<!-- variant: deep | after-gate-checks frontier (DEPTH probe) | DEPTH = deep
     The canonical anchor. Directive (experiment = the first (n,D) gate map);
     pair with quick.md and paper.md to isolate the depth/rigor axis. Replaces
     the campaign-goal framing. -->

# Brief — first (n, D) gate map

- **Objective.** Gates are validated and the device is alive (gate checks
  data/0–8: no breakdown to the working window, device responds in transport).
  Establish the device's baseline **(n, D) transport landscape** — where it
  conducts, where the charge-neutrality point sits, and where any correlated /
  superconducting-candidate features show up.
- **Target observable.** Lock-in resistance / current over the (Vbg, Vtg) plane
  (read in terms of (n, D)), `sr830_4` being the current channel.
- **Operating point / scope.** Base T, no field. Cover the validated window
  (`k_tg ∈ (−5.5, 2.5)`, `k_bg ∈ (−9, 5)`); pick a Si-back-gate setting (the
  operator scanned a few — V_Si = +10 / −10 / +20 V).
- **Depth.** Deep investigation — a map you can actually read the phase
  structure off: resolution fine enough to locate the CNP and feature edges,
  `slow_delay` / `fast_delay` long enough for the gate-line RC to settle (the
  rig's gate ramps are slow). Not a paper figure yet, but a map you'd trust to
  pick where to look next.
- **Success / escalate.** Done when the (n, D) landscape is mapped well enough to
  choose regions worth following up. Escalate if a gate leaks, the validators
  look wrong, the device appears dead, or the map can't be read (e.g. the plot
  registered only gate currents — register the lock-in channels).
- **Constraints.** Stay within the working validators; the human runs every cell.

Land the sweep.
