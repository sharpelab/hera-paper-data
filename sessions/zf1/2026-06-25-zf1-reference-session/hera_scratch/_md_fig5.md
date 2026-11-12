## HERA — Figure 5: dV/dI vs (I_dc, T) at the optimum, B=B_eff0

Verify passed (run 11): clean supercurrent, **Ic≈36 nA** switching, non-hysteretic, symmetric, field at B_eff0. Now the 2D — the supercurrent vs temperature.

**Shape:** heater the **1τ-settled slow axis** (same method as Fig 3: 80 steps, 34→350 mK cap — Ic→0 by Tc≈235 mK, so 350 mK is ample), DC bias the **fast axis** (±80 nA = ±8 V, 161 pts ~1 nA, one-way — verify showed non-hysteretic so no round-trip needed). Optimum n=−5.0, D=−0.64; AC 0.5 nA; 4T 0.1 mV. Field already at B_eff0 (held). Includes the **1-hour base dwell** + R-settle before the ladder (your thermalization standard).

Gives **Ic(T)** — the switching peaks marching inward to 0 as T→Tc, i.e. the supercurrent dome in the (I_dc, T) plane (the arXiv 2504.06972 Fig-5 move). **~9.2 h** (1 h dwell + 80 × (210 s + ~161 s)). Preconditions asserted (gates at optimum, heater off, B=B_eff0 — if B drifted off, it tells you to re-run the verify). dc205 + heater return to 0 at the end. Checkpoints: first steps, then ~hourly. Watch the fridge MC. Run when ready.
