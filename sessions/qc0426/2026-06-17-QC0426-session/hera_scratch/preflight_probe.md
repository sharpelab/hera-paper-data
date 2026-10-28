## HERA — E1 preflight probe (read-only; my designated first-E1 execute)

Bring-up is verified from the setup-section outputs (Gate A: all instruments
connected, sample T 1.17 K, magnet 0 T / PS heater on; Gate B: SAFETIES exec
[10], validators = device-card limits exactly, B cap 8.0 T). This cell is the
VERIFY-item-5 kernel-binding probe — **read-only, no gate/field/mux writes** —
and it snapshots the remaining VERIFY reads (magnet set-vs-read, sample T,
gate setpoints + committed validators, lock-in tau/filter-slope for the
settling record) in one place.

Per the brief this probe is my **first E1 execute**: I run it once you give
"go for autonomy" to confirm the kernel binding before any hardware move.
Staging it now so you can see exactly what that first autonomous action is.
~2 s, no instrument state changes. Awaiting the grant.
