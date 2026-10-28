<!-- Source: https://wiki.sharpelab.science/doc/qc-run5-NIKkda05a8 (QC-run5 live log, operator notes by Zack) — archived 2026-06-19 -->

tooling: need nb --outputs-only

wasted a bunch of time verifying instrument behavior- this should be device or rig card.  each time it reads a code file in this and previous sessions we should see if we can provide a fix or cheaper alternative

it was in the qingrui directory for some reason \[ blinding leak?\]

it didn't push anything to the ana notebook after the recon, which is real data worth having in the ana nb

sr1 tc is 0.03 \[did it set it to that or is this just held over from previous stuff run on the rig?\]

it dropped out of autonomy with a bunch of things it could do, including the primary arc of the investigation.  very bad

it seems overly fixated on details like  ● BG set is only partially blocking (returns at \~1.9 s but keeps ramping \~3–4 s for a 1.5 V move) — so the fan's n-line retrace each B-row wouldn't settle within a short fast_delay

it used tau=0.1s for the fan for speed (not a terrible choice if it has classified that as ok)

Cells HERA executes don't always show in the nb until they are completed, the live plot does but the intermediate prints and progress bar doesn not.  Perhaps we pop a widget for the progress bar, could fix both the wasteful output and this disconnection issue.


## Token Usage

* 174k running gate map
* \~500k pre laundau fan