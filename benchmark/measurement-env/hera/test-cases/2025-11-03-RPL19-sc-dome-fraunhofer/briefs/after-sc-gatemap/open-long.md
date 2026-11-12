<!-- variant: open-long | autonomy: HIGH (rich context, but method left open) | length: LONG
     Tests whether more context ALONE (without prescribing the experiment) steers
     Tier-2 to the right measurement. Replaces the campaign-goal framing. -->

# Brief

## The state of play
The campaign has located and mapped a candidate superconducting dome on RPL_19.
The SC-gatemap section converged on an optimum near (TG ≈ 0.47 V, BG ≈ −5.2 V) at
V_Si = −48 V, base temperature; along the gate line through the dome there is a
clear gate-tunable low-longitudinal-voltage region (data/134 maps the dome,
data/138–145 cut through it). The latest run (data/145) probed the dome point
versus a small perpendicular field (0→~12 mT, interrupted) and hinted at a weak,
non-monotonic field dependence.

## Why it matters / what's at stake
A gate-tunable low-dissipation dome is suggestive but not proof of
superconductivity — it needs interrogation before the campaign invests in
junction physics, the phase diagram, or device-level conclusions. The standard
discriminators for a 2D superconductor are well known: the supercurrent should be
suppressed by an out-of-plane magnetic field (and, in a junction geometry, show
Fraunhofer-like lobe modulation); it should vanish at a transition temperature;
and it should be reproducible and gate-tunable. You have the gate-space picture
in hand and a first, partial look at field. Temperature behavior is *not* yet
measured at this dome point.

## What you have to work with
- The dome optimum and the gate line through it (recoverable from the kept
  `draw_line_through_point` cells).
- A heater (`heater`, Keithley2400) for temperature-dependence work, an AMI430
  magnet (perpendicular field, Tesla) and a Yokogawa field source — full setup in
  `device_card.md`. Note the perpendicular null may sit a few mT off the magnet's
  raw zero.
- Caution: the embedded plots show only gate leakage, not transport — read the
  TSVs.

## The ask
**Decide the single most informative next measurement to advance the SC
characterization at this dome, and run it.** Justify the choice against what the
data does and does not yet show (gate-space: mapped; field: partial; temperature:
untested), and land the sweep. There is more than one defensible move — commit to
one and say why.

**Depth:** deep investigation — characterize it well enough to support a
defensible physics conclusion (not a quick yes/no, not yet paper-grade).
