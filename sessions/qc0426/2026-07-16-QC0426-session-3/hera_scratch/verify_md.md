## HERA — session-start VERIFY (read-only)

Brief's VERIFY checklist as one cell: magnet at zero (measured readback + status), base T with logfile-freshness guard (a frozen worker reads a plausible value — rig card), DC205 on RNGE 2 / output on / 0 V, PS heater + output enabled, gate readbacks, committed validators echoed against the card numbers (TG ±3.0, BG ±4.5, Si ±50 V, |B| ≤ 8 T, T ≤ 50 K), and the lock-in τ / filter-slope / sensitivity record (operator-set, not in run snapshots — this is the bring-up record). No instrument writes. ~10 s.

If all asserts pass it prints **VERIFY: all green** — then your "go for autonomy" engages E1 (first E1 execute will be the read-only kernel-binding probe, then gate C liveness).
