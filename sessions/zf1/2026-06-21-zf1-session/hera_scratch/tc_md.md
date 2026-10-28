## HERA — I_c(T) / Tc ladder (final constellation piece; the heat-up, last)

Base-T characterization is complete: Rxx→0, supercurrent I_c≈8–10 nA, B_c⊥≈2.5 mT (ξ~360 nm), central supercurrent lobe (field null ≈ −1 mT). The last hallmark is the **I_c collapse at Tc** (`temperature-dependence.md`, Flavor B). At the arc min (B=0), I warm to the heater top and step **down** through the ladder (measure while cooling), taking dV/dI vs I_dc at each T. The SC signature: the zero-bias dip / I_c shrinks and vanishes at Tc; Rxx(0) rises to the ~40 Ω normal value.

**Heater** per device card (≤6.5 V → ~480 mK sustained): steps 6.5→0 V (T read back from data, never the setpoint; the cell prints heater current as the open-line check). **~8 min thermalization/step, 8 steps → ~80 min**, producing one run per T; then heater→0 to re-cool (~1 h, not part of the cell). I'll read each T-run as it lands and call Tc once bracketed (and can stop early if the collapse is clear).

**⚠️ This is the thermal-cycle step** — the expensive one, hence last. If Tc > ~480 mK (heater ceiling), the SC may not fully close at the top; I'll then report Tc as a **lower bound** (comparing Rxx(T) to the field-kill normal value ~40 Ω). B stays at 0. **After this: the full five-part SC call.** Monitor armed.
