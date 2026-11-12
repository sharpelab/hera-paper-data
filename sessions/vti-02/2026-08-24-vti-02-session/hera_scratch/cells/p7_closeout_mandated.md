## HERA — mandated close-out: `close_out(restore=state0)`

Run at the operator's explicit instruction, superseding the hand-written close-out at
idx 49. `close_out()` is the canonical helper: it replays `state0` param-by-param in capture
order, steps the named excitation/heater/gate stages, lands the field at an **explicit**
endpoint (never defaulted), and prints a full readback with validator suffixes.

**Field endpoint: 0.0 T**, stated explicitly rather than `"hold"`. The magnet is already at
+0.006 T from the previous close-out, so this is a no-op guarded by a real set.

**What `restore=state0` puts back, and one consequence worth naming.** `state0` (idx 27) was
captured at bring-up, before the acquisition was re-ranged. Replaying it returns **`sr1`
sensitivity to 2 µV and `sr0`/`sr1` τ to 0.3 s** — the configuration in which `sr1` was
*railed* (fs = 1.01 at the zero-gate operating point) and which made the compliant dwell
2.1 s/pt. That is genuinely what "restore the initial state" means, and it is not a safety
matter: an SR830 input overload is a normal operating condition, and the gates and field are
already at zero. But the next session should know that 2 µV is a known-bad starting
sensitivity for this device at 10 nA bias, not a considered default — see `session_notes.md`.

**Si:** `state0` restores `V_si` through `dc205.smart_voltage(0.0)`, which is a DC205 ramp
call. Si has sat at 0.000 V all session, so this is a zero-length ramp; the DC205 ramp is
consent-gated and the operator's instruction to run `close_out(restore=state0)` is that
consent.

Heaters and both Keithley gates are listed as explicit stages as well as being in `state0`
— `close_out` dedupes by parameter identity, so each appears once in the readback.
