## HERA — Gate C: liveness check (`gate-current-sanity-check`)

First-session branch — no designated references, so this is a liveness-and-gross-safety pass judged on its own terms, per `device-init/gate-current-sanity-check.md`. Four legs, each its own run/file: TG 0→+3 V, TG 0→−3 V, BG 0→+4.5 V, BG 0→−4.5 V (endpoints = the committed SAFETIES limits; other gate parked at 0). `nplci=10` on both Keithleys for pA-resolution gate-current readback; the reset cell below undoes it.

**Si gate is excluded**: the DC205 has no current readback so a Si leg has no leakage watch; Si stays at 0 V for the D ≈ 0 campaign (it is a contact-doping gate only, screened from the channel by the graphite BG).

**What to watch, per leg (live plots):** lock-in X nonzero and smoothly varying = alive; swept gate current stays in pA on the capacitive charging slope = safe; parked gate current at floor = no cross-gate path. A gross turn-up off the charging slope → interrupt the cell (the `finally` parks the gate) and we stop-and-report.

**Cost:** 251 pts × 1 s delay ≈ 5–6 min/leg incl. readback overhead + ~1 min gate ramp-back each → **~25–30 min total**. VERIFY note: sr0 sits at ~99% of its 5 mV sensitivity at gates 0 (full 5 nA flowing); if it rails during the legs that is a sensitivity artifact, not a device problem — the current channel railing high is the healthy direction.

Preconditions asserted in-cell: T_sample < 2 K, |B| < 0.05 T, all gates at 0.
