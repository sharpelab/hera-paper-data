## HERA — 0 T TG-BG gate map (substrate for CNP / (n,D) calibration)

Foundational map (`gatemap.md`): axis-aligned raw-gate-voltage megasweep at B=0,
Si=0, provided contacts. BG[-4.5,4.5] x25 (slow) x TG[-6,6] x61 (fast) = 1525 pts.
TG fast range catches the CNP line (geometry slope ~-1.3, intercept ~0) at every
BG row. sens 0.5 mV (headroom over the ~1.4k liveness CNP peak). NO LS335 per-point
poll (contention fix). Stays inside validators; TG leakage is not directly
monitorable (DC205 has no current readback) so I watch the lock-ins + BG/Si current.

**Cost ~50-60 min** (1525 pts at ~1.7-2.3 s/pt incl. measure overhead + ~3 min row
turnaround; rig-card 2D rate is 2.0-2.5 s/pt). **Checkpoint at ~row 12** (BG~0,
~25 min): confirm the CNP ridge tracks diagonally and sens is not overloading at the
peak; continue / adjust sens / abort. E1 auto (in-envelope, B=0, gates within
validators). Output feeds the per-channel CNP-line fit and the (n,D) conversion.
