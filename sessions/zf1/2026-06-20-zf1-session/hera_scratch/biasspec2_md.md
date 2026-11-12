## HERA — bias spectroscopy point check (CORRECTED — supersedes cell 40)

**Do not run cell 40** — it set `dc205_1.volt.step = 0.02`, now under a hard ban. This cell is identical except `volt.step` is left at its setup default (0.005 V). Logged the ban for the toploader card (session_notes).

**What:** 1D dV/dI vs I_dc at the Step-1 lowest-Rxx point (Vtg 0.02, Vbg 2.70; n≈+2.2e12 cm⁻², D≈−0.20 V/nm) — the confound test of whether even the best low-Rxx point carries a supercurrent. DC bias `dc205_1` through 100 MΩ → I_dc = V_dc/1e8; V_dc −1→+1 V = **I_dc −10→+10 nA** (101 pts). AC excitation 0.5 nA. **dV/dI read as `sr830_3` (4T, 30-31) / I_ac** (current-bias rig — sr830_1 is the current, sr830_4 is dead; recipe's sr1/sr4 ratio doesn't apply here).

**Forks:** SC → dV/dI ≈ 0 below an Ic, rising at the lobe edge. Good metal → flat ohmic ~4–5 Ω (expected). Anything nonlinear → round-trip + lower AC + a 2D bias-vs-n dome.

**Timing — note:** with `volt.step` left at 5 mV, the DC205's ~1 s fixed-ramp-per-set means the bias axis ramps slowly (≈ total volts traversed / 0.005 × ~1 s). Wall-clock is **uncertain, ~5–13 min**; I'll re-price from the run's first points. Interrupt if it drags and I'll trim the range. `dc205_1.volt → 0` + gates parked in `finally` (device-card rule). **Preconditions** asserted: T base; |B|<5 mT; drive 0.5 nA; gates/dc205 printed. No `volt.step` writes.
