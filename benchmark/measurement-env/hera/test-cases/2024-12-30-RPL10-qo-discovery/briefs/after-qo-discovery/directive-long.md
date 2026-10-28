<!-- variant: directive-long | autonomy: LOW (full 5-field brief) | length: LONG
     The fully-specified strategic→tactical handoff. Tier-3 fixes the experiment,
     observable, operating point, and stop criteria; Tier-2 owns execution
     details (T-range, step count, settle time, operating point refinement).
     Replaces the campaign-goal framing. Encodes Aaron's actual next move. -->

# Brief — temperature dependence at the quantum-oscillation operating point

- **Objective.** Now that quantum oscillations are confirmed at D = 0.31 V/nm
  (data/159), measure how the device's transport evolves with **temperature** at
  this operating point — to extract the carrier **effective mass** from the
  thermal damping of the oscillation amplitude, and to pin the **transition
  temperature** of the SC1 feature in this density window via its zero-bias /
  critical-current softening.

- **Target observable.** Transport vs temperature at the established operating
  point — most directly, a **DC-bias × temperature map** (zero-bias /
  critical-current feature vs T) and/or the oscillation amplitude vs T. Looking
  for: the zero-bias feature weakening and vanishing at a Tc (SC), and the
  oscillation amplitude decaying with T in a Lifshitz–Kosevich-like way (→ m*).

- **Operating point.** Hold the gates near the SC1 / oscillation optimum in this
  n–D window (around D ≈ 0.31–0.35 V/nm, n in the −2.9 to −2.1 ×10¹² range
  established by data/156–159), V_si = −20 V. You will likely want a brief gate
  map first to re-center the spot once the device is warm — gate features drift
  with temperature.

- **Approach (you own the details).** Temperature on the slow axis, your chosen
  fast observable (DC bias, or gate for an amplitude-vs-T fan) on the fast axis.
  Warm the device with the sample heater, ramping it up in steps and letting each
  temperature settle before sweeping (these are slow — generous settle per
  T-point). Pick the temperature range, the number of T-points, and the settle
  time yourself; a sensible first pass spans base up through a few hundred mK.

- **Success / escalate criteria.** Done when the T-evolution is mapped clearly
  enough to read a Tc (or its absence) and/or a clean amplitude-vs-T decay.
  **Escalate to strategic if:** the feature has drifted off the operating point
  and a gate re-map can't recover it, the heater behaves unexpectedly, or the
  device doesn't warm/equilibrate as expected.

- **Depth.** Deep investigation — map the T-dependence well enough to support a
  defensible conclusion (a rough Tc and/or m* trend); not a quick screen, not yet
  a paper-grade dataset with exhaustive repeats.

- **Constraints.** Stay within the gate validators (`device_card.md`) and the
  heater range (−6, +6 V). Scope the sweep to roughly the cost of the other
  campaign sweeps. The human runs every cell.

Land the sweep.
