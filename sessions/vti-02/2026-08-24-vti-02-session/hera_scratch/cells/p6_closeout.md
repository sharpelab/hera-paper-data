## HERA — close-out: return-to-initial

The brief's close-out step. Order matters: **heaters off first**, so the sample begins
cooling from 40 K while the gates and field ramp; then both Keithley gates to 0 V at their
committed 5 mV/step pacing; then the field to zero (it is already at +0.006 T, where the
ladder left it, so this is a no-op guarded by a read). Finally a full readback of field,
gates, leakage, temperatures and heater ranges for the session log.

**Si is not touched.** It sat at 0.000 V all session — the graphite back gate screens it
from the channel, so it was never needed — and the DC205 ramp is consent-gated. The cell
reads it and flags it for the operator rather than ramping it.

**Lock-in settings are deliberately NOT restored to `state0`.** `sr1` sensitivity
(2 µV → 1 mV) and `sr0`/`sr1` τ (0.3 → 0.1 s) were changed with operator authorisation
because the session-start values were wrong for this device — `sr1` was railed at 2 µV
before the first sweep. Restoring them would hand the next session a known-bad
configuration. The readback records what they actually are.
