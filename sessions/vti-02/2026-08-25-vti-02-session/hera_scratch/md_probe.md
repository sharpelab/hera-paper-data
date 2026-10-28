## HERA — E1 kernel-binding probe (read-only)

**Session state.** Setup ran clean in one kernel (exec `[1]`–`[15]`, no gaps):
magnet 0.006 T with output + persistent switch on; both temperature logfiles
live (age 2 s, period 5 s), T_sample 1.176 K / T_vaporizer 0.954 K; both
Keithleys state-verified at 0 V, NPLC 1, `rangei` 1.05 µA; DC205 on range code
2 (±100 V), output on, 0 V; four SR830s connected. **Gate A green.** SAFETIES
(cell 18, exec `[10]`) committed TG [−0.3, +1.0], BG [−1.3, +2.0], Si
[−25, +25], `magnet.field` cap 10.0 T, T-setpoint cap 100 K — every number
matches the device card's operating-limits table, and 10.0 T sits inside the
driver's 14.0 T backstop. **Gate B green.** No data on disk; ana notebook is
the fresh template. Gate C (contact liveness) is the first measurement, after
the grant.

**This cell** is the brief's kernel-binding item: a namespace probe that
confirms an `nb-collab execute-cell` lands in *this* kernel — the one the
operator's Setup/SAFETIES cells built — and not a second kernel serving the
same file. It touches no instrument (no `.get()`, no VISA traffic): it prints
the pid, the notebook's `main_dir`, the qcodes instrument registry, `id(magnet)`,
and checks that every global the measure cells depend on is present. Last line
is `PROBE: BOUND` or `PROBE: NOT BOUND`.

Under the brief's conditional grant this is my **first E1 act**, executed before
VERIFY. It is safe for the operator to run by hand instead — the outcome is the
same either way.
