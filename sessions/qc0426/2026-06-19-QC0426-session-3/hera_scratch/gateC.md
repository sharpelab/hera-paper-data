## HERA — Gate C: contact liveness on the provided config (E1 auto)

First-session re-entry baseline, first-session branch: no reference run to compare against,
so this is a liveness check, not a quantitative reproduction. Routes the device-card
**provided contact configuration** through the QSwitch (source T2 / drain B7 / sr1 T3-T4 /
sr2 B4-B5 / sr3 T5-B6 (Rxy)) and reads the lock-ins at the resting gate point (TG/BG/Si all
~0 V, B=0) to confirm source-drain carries current and each four-terminal pair reads a sane
resistance. All eight pads are in the device card's Alive set.

Preconditions asserted (cell assumes, does not set): sample_T < 5 K, |B| < 0.05 T, all three
gates inside their validators. `mux.select` is the Auto-bucket routing op (Si standing closures
16/11 excluded from the managed set; no `qsw.reset()`). No sweep, so no run dir — output is
inline. **Pass:** I_meas is finite (a few nA into the 100 MOhm-limited drive) and each Rxx reads
a finite, non-railed resistance. **Read-only on hardware apart from the relay routing.**
