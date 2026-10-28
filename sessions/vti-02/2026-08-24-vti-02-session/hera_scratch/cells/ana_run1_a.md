## Run 1 — `bg-cut`: same cut, `sr1` re-ranged to 1 mV

**Why / what we're testing:** run 0 clipped the only channel that measures the channel.
This repeats the identical cut with `sr1` at 1 mV (100 kΩ of Rxx headroom at 10 nA) and
τ dropped 0.3 → 0.1 s on both `sr0` and `sr1`, to (a) measure the CNP peak height without
clipping and (b) set the Rxx scale for the gate map. Swept in **reverse** (+2.00 →
−1.30 V), which starts where run 0 parked the gate and buys a hysteresis check for free.

τ = 0.1 s at 24 dB/oct still puts 2f (27.6 Hz) ~99 dB down at the 13.777 Hz drive, and the
compliant dwell falls 2.1 s → 0.7 s per point — the reason the map costs ~34 min and not
~1.9 h.
