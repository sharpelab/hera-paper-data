<!-- variant: open-long | autonomy: HIGH (rich context, but method left open) | length: LONG
     Tests whether more context ALONE (without prescribing the experiment) steers
     Tier-2 to the right measurement. Replaces the campaign-goal framing. -->

# Brief

## The hypothesis
The campaign has built a case that this device hosts a superconducting state.
The zero-bias differential-resistance suppression with symmetric peaks in the
Idc-vs-n sweep (data/84) reads as a critical current (Ic ~ 80 nA on the clean
channel), and it persists across the measured density line at fixed D, at base
temperature. The working hypothesis is: **this is a genuine supercurrent.**

## Why it matters / what's at stake
A zero-bias dip is suggestive but not proof — normal-state nonlinearities
(Kondo, weak localization, heating, contact effects) can mimic it. Before the
campaign invests in mapping the dome, the phase diagram, or device physics, the
SC nature needs to be established or ruled out. A wrong call here propagates
into everything downstream.

## What would be convincing
The standards of proof for a 2D superconductor are well known: the critical
current should be suppressed by an out-of-plane magnetic field (and, for a
Josephson/proximity geometry, show Fraunhofer-like modulation); it should
vanish at a transition temperature; and the feature should be reproducible and
gate-tunable. You have temperature behavior partially in hand (nT map, Idc-vs-T)
and density behavior (Idc-vs-n). Consider what is genuinely missing and most
decisive.

## State / resources
- Operating in the SC window from data/84: a density line at fixed D, base T
  (~29 mK), zero effective field (Beff = 0 at the rotator's calibrated setpoint).
- The full instrument set for this run is in `device_card.md` (gates, DC bias,
  lock-ins, heater/thermometry, magnet, rotator).

## The ask
**Decide the single most decisive next measurement to test the SC hypothesis,
and run it.** Justify the choice against what the data does and does not yet
show, and land the sweep.

**Depth:** deep investigation — characterize it well enough to support a
defensible physics conclusion (not a quick yes/no, not yet paper-grade).
