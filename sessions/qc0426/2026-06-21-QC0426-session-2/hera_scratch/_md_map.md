## HERA — Step 1: B=0 (n,D) gate map (`gatemap` → `cnp-and-dline-calibration`)

Axis-aligned megasweep in raw gate voltages (cap ratio not yet trusted). **Fast = TG (`dc205_volt`, col `DC_bias`) over [−6, +7] V, 81 pts; slow = BG over [−4.5, +4.5] V, 41 rows**; Si = 0, B = 0. Recipe-canonical orientation: per-row argmax over TG yields the CNP line V_tg(V_bg) directly → slope = −c_bg/c_tg. Reads all four lock-ins (X/P) + `k_bg.curr`/`k_si.curr` (leakage; DC205 has no current monitor). T not fp'd per-point (LS335 Grafana co-master).

**Why this is robust to the 24 dB/oct under-settling:** a constant fast-axis settling lag shifts the CNP ridge by the same amount in every row → biases the *intercept* (offset), not the *slope* (cap ratio). So this runs at fast_delay = 1.0 s for the ratio; SdH acquisition gets proper settling later (Step 3).

**Cost:** 41×81 = 3321 pts at ~1.25 s/pt + 41 TG row-resets (~6.5 s each) ≈ **~1.25 h**. Spans the full CNP line (expect V_tg ≈ −1.3·V_bg + 0.52: from +6.4 V at BG=−4.5 to −5.3 V at BG=+4.5, all in-range).

**Checkpoint (~row 20, ~37 min):** read the live digest — is the CNP ridge forming and continuous row-to-row, and leakage < 1 nA? Continue if yes; abort and reassess (drive/sens, range) if the ridge is absent/discontinuous or leakage climbs.
