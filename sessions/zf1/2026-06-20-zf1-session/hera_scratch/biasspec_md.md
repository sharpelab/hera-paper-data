## HERA — Step 2: bias spectroscopy point check at the lowest-Rxx point

Step-1 map (run 2+3) found **no SC candidate** — metallic Rxx everywhere, lowest 3×3-smoothed 4.4 Ω at (Vtg 0.02, Vbg 2.70 ; n≈+2.2e12 cm⁻², D≈−0.20 V/nm), nothing below 2 Ω. Per the constellation discipline I won't call not-SC from Rxx alone: this tests whether even the **best** (lowest-Rxx) point carries a supercurrent.

**What:** 1D dV/dI vs I_dc at the lowest-Rxx operating point. DC bias via `dc205_1` through the 100 MΩ resistor → I_dc = V_dc/1e8; sweep V_dc −1→+1 V = **I_dc −10→+10 nA** (101 pts, 0.2 nA steps). AC excitation stays 0.5 nA. **dV/dI = sr3 (4T) / I_ac** — read directly as the 4T Rxx channel (recipe's `sr830_1/sr830_4` ratio assumes a voltage-bias rig with a separate current monitor; on current-bias zf1 the AC current is constant and sr4 is dead → dV/dI ∝ sr830_3; logging this as a RECIPE FIX).

**Expected forks:** SC → dV/dI ≈ 0 below an Ic, rising sharply (a supercurrent lobe). Good normal metal → flat ohmic dV/dI ~4–5 Ω across all I_dc (the expected null here). If anything nonlinear appears, follow up with a round-trip (hysteresis) + reduced AC + a 2D bias-vs-n dome map.

**Price ~5 min.** `dc205_1.volt.step` raised to 0.02 V (bias through 100 MΩ is current-limited — large steps safe; keeps each move <0.1 V to avoid the DC205 10 s settle). `dc205_1.volt → 0` and gates parked in `finally` (device-card rule). **Preconditions** (asserted): T base; |B|<5 mT; drive 0.5 nA; gates/dc205 printed.
