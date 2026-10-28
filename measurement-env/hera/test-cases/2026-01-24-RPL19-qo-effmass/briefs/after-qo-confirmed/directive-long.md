<!-- variant: directive-long | autonomy: LOW (full 5-field brief) | length: LONG
     The fully-specified strategic→tactical handoff. Tier-3 fixes the experiment,
     observable, operating point, and stop criteria; Tier-2 owns execution
     (densities, field range, #points). Encodes Aaron's actual next move. -->

# Brief — fixed-(n, D) field cuts to read the oscillation frequency

- **Objective.** Now that data/1776 confirms the oscillations at D = 1 are real,
  extract the **quantum-oscillation frequency B_F** (and thus the oscillating
  pocket's Fermi-surface area / carrier density) and see how it evolves with
  filling.

- **Target observable.** Longitudinal resistance (the Rxx lock-in channels in
  `mc_25`) vs perpendicular field at a **fixed (n, D)** — periodic in 1/B, with
  B_F set by the period. Cleanly resolving the period over a wide field range is
  what lets a 1/B FFT return B_F.

- **Operating point.** D = 1, base T, V_Si = 48 V. Pick a few densities in the
  region where data/1776 showed the oscillations (around n ≈ 0.5–0.9) — start
  with one or two single (n, D) points, then step through a set if the first
  cuts look clean.

- **Approach (you own the details).** Perpendicular field on the sweep axis at
  each fixed (n, D); choose a **wide field range and high point count** so the
  oscillation period is well sampled in 1/B (the prior fans used ~1–2.5 T; a
  cut wants more periods and finer ΔB). Let the field settle. Sweeping up and
  down (or alternating direction across densities) is fine.

- **Success / escalate criteria.** Done when the field cuts resolve the
  oscillation period cleanly enough to read B_F at the chosen (n, D) points.
  **Escalate to strategic if:** the oscillations don't survive at higher
  resolution (they may have been an artifact after all — re-examine), the period
  is unreadable over the accessible field range, or the operating point drifts.

- **Depth.** Deep investigation — resolve B_F well enough for a defensible
  Fermi-surface read at the chosen points; not yet a paper-grade sweep set
  (no exhaustive density grid or repeats required at this stage).

- **Constraints.** Stay within the gate validators; scope the sweeps to roughly
  the cost of the campaign's other field sweeps; the human runs every cell.

Land the sweep.
