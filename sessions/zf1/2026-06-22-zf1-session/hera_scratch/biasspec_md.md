## HERA — Run 5: bias spectroscopy at the optimum — the critical-current test

Run 4 confirmed **Rxx → ~0** (min 0.52 Ω, X-offset-limited) at **n≈−4.65×10¹¹, D≈−0.65 V/nm** (Vtg=−5.444, Vbg=+4.053) — first SC hallmark in hand. This is the decisive nonlinear test (`bias-spectroscopy`): does the zero-resistance state carry a **supercurrent** (dV/dI≈0 below a critical current Ic, rising at Ic), or is it just a good low-R metal (ohmic dV/dI, no lobe)?

**Design:**
- Gates fixed at the optimum; **DC bias swept −15 → +15 V** via `dc205_1` through the 100 MΩ resistor → **Idc −150 → +150 nA**, symmetric across 0 (captures Ic⁻ and Ic⁺). This is the wide bracket the investigation asks for (reference Ic ~20 nA [s41586-022-05446-x]; real devices run several× higher; ±150 nA is the full dc205 range).
- **Step 0.0987 V (≈1 nA), 305 pts — deliberately ≤0.1 V** to avoid the DC205's mandatory 10 s settle (rig card); ~13 min total.
- AC sense **1 nA** (≪ expected Ic), sr830_3 @ 200 µV, tc 0.3 s, delay 1.5 s (≥5×tc). dV/dI = (sr830_3_X/100)/(sr830_1_X/−1e6).
- Magnet untouched (B≈0).

**Preconditions** asserted: base T, B≈0; gates ramped to optimum then verified. dc205 parked to 0 in `finally` (device-card rule), gates parked after.

**Read after:** a flat dV/dI≈0 plateau below |Ic| rising to the normal value = **supercurrent → SC** (then field-kill + T-dependence to complete the constellation). Ohmic dV/dI with no lobe = good metal, not SC. A smooth/smeared onset → reduce AC drive or check heating. Note the QAH confound needs an Rxy read (no transverse pair in the current config — a follow-up); the field-kill test is the cleaner B=0 discriminator next.
