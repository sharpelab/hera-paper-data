## HERA — post-interrupt state read

Operator instruction mid-close-out: **interrupt, go to high field, run the fan
ramping down.** Good call — it saves roughly half an hour of magnet time. The
previous plan let close-out land at 0 T, ramped back up to 1 T, swept up to 8 T,
and would then have needed a 58 min ramp home; going straight up and sweeping
*down* ends the fan near zero, which is the rig card's "plan the direction so the
fan ends where the next measurement needs it".

The close-out cell above was interrupted mid field-ramp and is therefore
**incomplete**: its stages run restore → excitation → heaters → gates → mux →
field, so everything except the field endpoint completed. The rack is at bring-up
values and the gates are parked, but no close-out readback was printed, so there
is no handoff record from it and **this session is not closed out**.

**The rig-card fact this turns on:** interrupting the cell does *not* stop the
supply — it keeps ramping to its last setpoint (0 T). There is no abort or
ramp-to-zero method; recovery is calling `field()` again with a new target, which
the fan cell does when it positions to 8 T. This cell is read-only and only
establishes where we actually are, including a two-point field read to confirm
the magnet is still moving and in which direction.
