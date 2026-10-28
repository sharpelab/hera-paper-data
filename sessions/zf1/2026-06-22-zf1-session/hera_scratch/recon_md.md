## HERA — Step-1 reconnaissance: 3-row gatemap (de-risk before the full survey)

Gate C passed cleanly: device alive (I = 1.006 nA steady), contacts conduct (2T 5-4 = 21.7 kΩ; 4T 30-31 live and gate-responsive), leakage **38 pA / 31 pA** (TG/BG) — far below threshold. Magnet still pristine (B ≈ 0), so this stays pre-field per Step 1.

Before I commit ~2 hr to the full-box survey map, this **~4 min** reconnaissance de-risks it — a coarse 3-row megasweep (TG slow = {−3, 0, +3} V, BG fast = −4 → +4.2 V, 83 pts). It answers four things the full map can't afford to get wrong:

1. **CNP peak magnitude** → sizes the full map's lock-in sensitivity so the CNP ridge doesn't clip (autorange is unusable here — it no-ops below 160° phase, and our voltage channels sit at ~0°). Sensitivity set **generously (0.5 V)** here precisely so nothing clips and I can read the true peak.
2. **CNP-vs-TG slope from 3 points** → a cap-ratio *preview* and a slow/fast-axis sanity check (the geometry prior is flagged-uncalibrated; the real extraction comes off the full map via `cnp-and-dline-calibration`).
3. **Per-point timing** → honest wall-clock pricing for the full map (rig default 1.2 s/pt is a starting guess; I'll calibrate from this run's actual rate).
4. **Leakage + clipping across the box corners** at TG = ±3.

**Preconditions** (asserted at top): base T, B ≈ 0, gates parked — and I print the live lock-in tc/sensitivity (snapshot didn't capture them). I also refresh `meas_config["bias_voltage_1"]` from the live amplitude so this run's metadata is correct (the Gate C run recorded a stale 0.05 V — see session_notes).

**Cost:** ~4 min (249 pts). **Read after:** CNP magnitude → map sensitivity; 3-pt slope → cap-ratio preview; rate → map pricing. Then I commit the full survey map with settings it can't get wrong.
