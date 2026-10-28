## HERA — session close-out, second attempt (`return-to-initial`)

The first close-out (cell 55) was interrupted mid field-ramp on operator
instruction so the fan could run; its restore/heaters/gates stages had completed
but the field endpoint never landed and **no readback was printed**, so the
session has had no handoff record until now.

Re-running it. This time the ramp is short by design: run 8 swept **descending**
8 → 1 T, so the magnet is already at 1.006 T and the trip to zero is ~7 min
rather than the 44 min the ascending plan would have owed. That is the rig card's
"plan the session's last sweep to end at the endpoint" actually paying out.

Same call as before — ask is `return-to-initial` from the brief: field explicitly
to **0.0 T** (the session-start value from VERIFY), `restore=state0` to replay the
bring-up capture (drive back from 5.0 V to 1.0 V, all four lock-ins' sens/τ/slope
to bring-up values, gates to 0), heaters off via the labelled callable
(closed-loop LS335, VTI variant), Si parked through `k_si`/`smart_voltage` so the
driver paces it, and no `mux=` since the breakout is hardwired this cooldown.
Persistent switch and output stay untouched — operator-only.

Note the acquisition settings this restores are the ones run 8 deliberately set
(5 V drive, τ = 300 ms, sr1 at 100 µV). Those are recorded in the run metadata and
in the cells above; `return-to-initial` is about handing the rig back as found,
not about preserving the session's working point.
