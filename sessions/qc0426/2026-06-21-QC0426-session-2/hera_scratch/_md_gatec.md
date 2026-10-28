## HERA — Gate C (2/2): 1D BG liveness sweep (`reentry-baseline`)

First-session liveness check on the provided contacts (no reference to compare — judged on its own terms: gate response, smoothness, leakage floor). Sweep **BG ∈ [−4.5, +4.5] V** (full validator range, inclusive edges) at **TG = 0, Si = 0, B = 0**, 91 pts, dwell 1.2 s (4τ at τ = 0.3 s). Read all four lock-ins (X/P) + `k_bg.curr` / `k_si.curr` for live gate leakage. The static read-back already showed alive contacts (Rxx ~1.2–1.4 kΩ); this confirms they *respond* to gating and bounds leakage before the Step-1 map.

**VTI note:** temperature is **not** fp'd per-point (rig card: LS335 has a Grafana co-master, per-point polling has killed a run) — T is captured once in `meas_config`. Leakage watched on `k_bg.curr`; DC205 (TG) has no current monitor. ~2–3 min, writes a run dir. Sweeps at the current lock-in drive — if a CNP peak rails the sens I'll flag a drive/sens change rather than change it silently.
