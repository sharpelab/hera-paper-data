## HERA — VERIFY (read-only): session-start checklist + autonomy verdict

Plan step **P0**. The session brief's `[VERIFY]` list, one check per line, ending in
the machine-readable verdict the E1 grant keys on: `VERIFY: ALL GREEN` or
`VERIFY: FAIL <item>`. **Read-only by construction** — every statement is a get;
nothing is set, ramped, or swept, so this is safe to run at any time.

Checks: magnet at 0 T (measured readback, plus persistent switch + output);
every SAFETIES validator compared **numerically** against the device card's
gate-operating-limits table and the session B / T caps; thermometry worker live
(logfile age + cadence, so a frozen-but-plausible T cannot pass) and sample T
holding 1.2–1.3 K; both heater ranges 0 with the vaporizer tracking base; contacts
hardwired — no QSwitch/ContactMux anywhere in the kernel and `WIRING` equal to the
card's provided configuration; DC205 on RNGE 2, output on, sitting at 0 V.

Below the verdict-bearing checks is an **informational** block (not gating): each
lock-in's sensitivity / tau / slope with its live X, Y, R and full-scale fraction,
the drive amplitude to `I_bias`, the measured drain current, the zero-gate Rxx, and
both gate-leakage currents. Those numbers size the sweep dwell and catch a lock-in
that will rail the moment a gate moves — and the rig card notes tau/slope live
nowhere on disk except the bring-up record, so they are captured here.

**Precondition to running this:** the kernel-binding probe cell above must have
printed `PROBE: BOUND`.
