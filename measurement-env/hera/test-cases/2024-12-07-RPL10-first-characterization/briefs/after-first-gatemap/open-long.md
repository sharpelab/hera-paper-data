<!-- variant: open-long | autonomy: HIGH (rich context, method left open) | length: LONG
     Tests whether more context ALONE (without prescribing the experiment) steers
     Tier-2 to a good measurement. Replaces the campaign-goal framing. Depth = deep. -->

# Brief

## Where the campaign stands
This is RPL_10's first cooldown. The gates are validated (no breakdown to the
working window; the device responds in transport), and the first (n, D) gate
maps over the validated window — stepped across a few Si-back-gate settings
(V_Si = +10 / −10 / +20 V) — have located a candidate region that looks like it
could host a superconducting state. The working goal is to **characterize that
superconducting state.**

## What the data does and doesn't show
The maps are **partial / first-look rasters** (several were interrupted), and
their stored `plot.png` shows only the live gate-leakage monitor, not the
transport colormap — the actual (Vbg, Vtg) transport is in the run TSVs
(`sr830_4` is the current channel). So you know *roughly* where the candidate
region sits, but the maps are not yet a clean, complete phase diagram, and the
bias / field / temperature response at the candidate point is entirely untested.

## What would move the characterization forward
Several moves are on the table and all are defensible — the decision is yours:
- A **DC-bias check** at the candidate operating point to see if a zero-bias /
  critical-current feature exists (the cheapest SC discriminator).
- A **field response** measurement to test whether a candidate feature is
  field-suppressed (SC) or Fraunhofer-modulated (Josephson).
- A **finer / completed gate map** to localize the candidate region cleanly
  before committing to an operating point.
- A **Si-back-gate survey** using V_Si as a third axis to see how the features
  move.

## State / resources
- Base temperature, no field. Candidate region from the first maps; the full
  instrument set (gates, DC-bias source, lock-ins, heater/thermometry, magnet)
  is in `device_card.md`.

## The ask
**Decide the single most decisive next measurement, and run it.** Justify the
choice against what the maps do and do not yet establish, and land the sweep.

**Depth:** deep investigation — characterize whatever you choose well enough to
support a defensible next decision (not a quick yes/no, not yet paper-grade).
