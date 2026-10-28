## HERA — bias spectroscopy at the arc minimum (decisive SC test)

The zoom (run 10) confirmed a **contiguous low-Rxx arc** — Rxx → **0.6 Ω** (from ~28 Ω) at **n=−5.02×10¹¹, D=−0.673 V/nm**, the s41586 proximity-SC location, leakage clean. Rxx→0 is hallmark 1. Now the decisive test (`bias-spectroscopy.md`): **dV/dI vs I_dc** at that point. A **supercurrent lobe** — dV/dI ≈ 0 for |I_dc| < I_c, rising at a critical current — is the SC tell; a flat ohmic dV/dI would mean "just a good metal."

**Setup:** gate to the arc minimum (TG=−5.64, BG=4.20); **drop AC to 0.5 nA** (≪ expected I_c, avoids smearing/heating a fragile state); DC bias via dc205_1 through 100 MΩ, **±20 nA round-trip** (±2 V, ~0.5 nA step, fwd+bwd to check hysteresis), tc=300 ms, sr3 ranged for 0–400 Ω. The cell prints the zero-bias dV/dI before sweeping. ~8–12 min. **B stays 0** — this establishes I_c at zero field first; field response (B_c⊥, Fraunhofer) comes next if a lobe is found.

**Reads:** a clean zero-bias dip rising at ±I_c → supercurrent, hallmark 2 (then I map I_c(n,D), and the field/T ladder). dV/dI flat/ohmic → not a supercurrent, candidate downgrades toward "good metal / low-Rxx correlated phase." A shift of the lobe is instrumental; a magnitude asymmetry I_c⁺≠I_c⁻ would be physical (worth noting). Cell zeroes the DC bias at the end (device-card rule). I'm arming a monitor.
