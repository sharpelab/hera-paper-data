## HERA — Figure 3: R(T,n) map at the widest-D line (D=−0.64), B=B_eff0

Warm-up landed: heater→T re-confirmed, and the **R(T) at the optimum previews Tc≈280 mK** (R→0 below ~150 mK, normal ~43 Ω by ~360 mK) — the SC is healthy. Settle times (τ≈2 min) say the dense ladder's 4.4 mK steps thermalize in ~100 s.

**This cell** — the headline T-map. Flavor A `multimegasweep`: heater the **dense slow axis stepping DOWN** (480→34 mK, **100 steps, uniform 4.4 mK** built from the warm-up's measured heater→T), n the **fast axis** at D=−0.64 (n∈[−4.0,−6.5]×10¹¹, 0.02 step, 126 pts — into normal both sides). B held at B_eff0. AC 1 nA, 4T sens 0.1 mV, DC 0. **Measure-while-cooling** (recipe-preferred: the mixture's cooling power settles each descending step). `init_delay=False` (heater already at the 6.5 V ceiling). **slow_delay 90 s** (≳ the calibrated ~100 s settle; per-row T-drift ~2 mK ≪ the 4.4 mK step).

**~7 h** (100 steps × (90 s settle + 126 pts × ~1.3 s) ≈ 7.0 h). Ends with **heater OFF at base** — positioned for Fig 4a, which will ascend from base at B_eff0+1 mT (alternating ladder direction to avoid re-warming between the four field-maps).

**Preconditions (asserted):** heater at the ceiling & drawing (run cell 40 first if not), B=B_eff0. Cell `fp`'s T / fridge-T / heater V & I and plots heater.curr + T live. **Watch the fridge MC for runaway — interrupt (`nb-collab interrupt`) if T spikes.** **Checkpoints:** first ~2 steps (heater drawing, T descending, dome appears on the n-line); then ~hourly (T ladder monotonic, dome suppressing with T). I'll read the map at completion (R(T,n), Tc(n), the dome's T-extent) and propose Fig 4.
