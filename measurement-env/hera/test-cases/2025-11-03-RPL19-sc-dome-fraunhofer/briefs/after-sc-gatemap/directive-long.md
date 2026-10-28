<!-- variant: directive-long | autonomy: LOW (full 5-field brief) | length: LONG
     The fully-specified strategic→tactical handoff. Tier-3 fixes the experiment,
     observable, operating point, and stop criteria; Tier-2 owns the execution
     details (ranges, magnet handling, refinement). Replaces the campaign-goal
     framing. Encodes the operator's actual next move (the field-response map).
     See hera/docs/tactical-brief.md for the contract shape. -->

# Brief — perpendicular-field response of the candidate supercurrent

- **Objective.** Establish whether the gate-tunable low-dissipation feature at
  the RPL_19 SC dome optimum is a superconducting critical current, and probe its
  junction character, via its out-of-plane magnetic-field response.

- **Target observable.** The transport response (longitudinal voltage / dV/dI)
  vs (DC bias, B⊥) — how the low-bias supercurrent and its critical-current peaks
  evolve with perpendicular field. Looking for: suppression of Ic toward a
  critical field Bc (superconductivity), and/or Fraunhofer-like lobe modulation of
  Ic with field (a Josephson/proximity junction geometry → lobe spacing sets the
  junction area). Field-independence would argue *against* superconductivity.

- **Operating point.** Hold gates at the SC dome optimum (TG ≈ 0.47 V, BG ≈ −5.2
  V, V_Si = −48 V) identified in the gate-map section. Base temperature.

- **Approach (you own the details).** B⊥ on the slow axis, DC bias on the fast
  axis. **Respect the perpendicular null:** the data/145 field cut hinted the
  null sits a few mT off the magnet's raw zero — define the field axis relative
  to the true null and sweep symmetric about it to catch a Fraunhofer node if
  present. Pick the field range and step count yourself (the dome's low-field
  behavior suggests Bc/lobe scales of order ~10 mT — a first pass can span ±15 mT,
  then refine). It may help to read Ic at B = 0 with a 1D bias cut before
  committing to the 2D map.

- **Success / escalate criteria.** Done when Ic(B⊥) is mapped clearly enough to
  read suppression toward a Bc or a Fraunhofer lobe pattern. **Escalate to
  strategic if:** the feature shows no field dependence over the swept range (it
  may not be SC — re-examine), the operating point has drifted off the dome, the
  field null can't be confirmed, or the base temperature isn't cold enough to see
  a clean supercurrent.

- **Depth.** Deep investigation — map Ic(B⊥) well enough to support a defensible
  conclusion about the SC nature and a rough Bc / lobe scale; not a quick yes/no,
  not yet a paper-grade dataset (no exhaustive repeats/controls at this stage).

- **Constraints.** Stay within the gate ranges the gate checks exercised. Read
  transport from the TSVs (the embedded plots show only gate leakage). Scope the
  sweep to roughly the cost of the other campaign sweeps. The human runs every
  cell; you do not touch the magnet directly.

Land the sweep.
