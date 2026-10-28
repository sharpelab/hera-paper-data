<!-- variant: deep | before-effmass frontier (DEPTH) | DEPTH = deep
     The canonical effective-mass brief. Directive (experiment = temperature-
     dependent field sweeps at fixed (n,D) for m*); pair with quick.md / paper.md
     to see the depth axis. Replaces the campaign-goal framing. -->

# Brief — effective mass at the dome point

- **Objective.** Extract the **effective mass m\*** of the oscillating carriers
  at the dome operating point, from the temperature dependence of the
  quantum-oscillation (Shubnikov–de Haas) amplitude.
- **Target observable.** Longitudinal resistance (the Rxx lock-in channels in
  `mc_25`) vs perpendicular field at a **fixed (n, D)**, repeated across a set of
  sample temperatures. The oscillation amplitude at fixed field should decay with
  T following the Lifshitz–Kosevich thermal factor X/sinh(X),
  X = 2π²k_BT m\*/(ħ eB) — fitting that decay gives m\*.
- **Operating point / scope.** Hold gates at **(n = 1, D = 1)** (the dome anchor),
  V_Si = 48 V, DC bias 0. Perpendicular field on the swept axis.
- **Approach (you own the details).** Field on the sweep axis at fixed (n, D);
  step the **`heater`** to set each temperature and re-run the same field sweep.
  Choose the field range and step density so several oscillation periods are
  cleanly resolved (period is in 1/B), and pick a temperature ladder that spans
  from base to where the oscillations are clearly damped — enough points to fit
  the LK decay. Let the field settle between points.
- **Depth.** Deep investigation — a temperature series you can actually fit m\*
  from: resolution and field range sufficient to resolve the oscillations at each
  T, and a temperature ladder dense/wide enough that the amplitude-vs-T fit is
  well-constrained. Not yet a paper dataset (no exhaustive repeats), but a
  defensible m\* number.
- **Success / escalate.** Done when the oscillation amplitude vs T at the fixed
  (n, D) is mapped well enough to fit m\*. Escalate if the oscillations aren't
  resolvable at this operating point, the heater/thermometry can't be trusted, or
  the device drifts off the operating point.
- **Constraints.** Stay within the gate validators; the human runs every cell.

Land the sweep.
