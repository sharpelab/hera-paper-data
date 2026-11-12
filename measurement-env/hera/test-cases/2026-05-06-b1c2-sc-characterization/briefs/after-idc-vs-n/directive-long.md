<!-- variant: directive-long | autonomy: LOW (full 5-field brief) | length: LONG
     The fully-specified strategic→tactical handoff. Tier-3 fixes the experiment,
     observable, operating point, and stop criteria; Tier-2 owns the execution
     details (ranges, magnet handling, refinement). Replaces the campaign-goal
     framing. This is the reference shape for the brief contract — see
     hera/docs/tactical-brief.md. -->

# Brief — field-suppression test of the candidate supercurrent

- **Objective.** Confirm or refute that the zero-bias feature in data/84 is a
  superconducting critical current, via its out-of-plane magnetic-field
  response.

- **Target observable.** dV/dI vs (DC bias, B⊥) — i.e. how the zero-bias
  suppression and the critical-current peaks evolve with perpendicular field.
  Looking for: suppression of Ic toward a critical field Bc (SC), or Fraunhofer-
  like modulation (Josephson/proximity geometry). Field-independence would argue
  *against* superconductivity.

- **Operating point.** Hold gates at the SC optimum identified in data/84
  (the density line at fixed D = −0.685e9, near the center of n ∈
  [−0.6, −0.4]×10¹⁶ where the feature is strongest). Base temperature.

- **Approach (you own the details).** B⊥ on the slow axis, DC bias on the fast
  axis. Respect the rotator's calibrated **Beff = 0 setpoint** when defining the
  field axis — the magnet's raw zero is offset from the perpendicular null;
  sweep relative to the null, ideally symmetric about it to catch a Fraunhofer
  node if present. Pick the field range and step count yourself; first pass can
  be coarse (Tc and Ic scales suggest Bc is small — tens of mT), then refine.

- **Success / escalate criteria.** Done when Ic(B⊥) is mapped clearly enough to
  read suppression toward a Bc (or a Fraunhofer pattern). **Escalate to strategic
  if:** the feature shows no field suppression over the swept range (it may not
  be SC — re-examine the hypothesis), the operating point has drifted off the
  feature, or the magnet/rotator handle or units can't be confirmed.

- **Depth.** Deep investigation — map Ic(B⊥) well enough to support a defensible
  conclusion about the SC nature and a rough Bc; not a quick yes/no, not yet a
  paper-grade dataset (no exhaustive repeats/controls needed at this stage).
- **Constraints.** Stay within the gate validators. Scope the sweep to roughly
  the cost of the other campaign sweeps. The human runs every cell; you do not
  touch the magnet directly.

Land the sweep.
