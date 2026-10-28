## HERA — Figure 1: high-res (n,D) dome zoom (nD-map) at B = B_eff0

Step 0 done: **B_eff0 = −0.366 mT** (ana cell executed). This cell takes the headline dome map at that true zero field.

**Grid:** n ∈ [−6.0, −4.3]×10¹¹ **fast (0.02 step, 86 pts)** × D ∈ [−0.66, −0.56] **slow (0.005 step, 21 rows)** = **1806 pts**, boustrophedon, AC 1 nA, 4T sens 1 mV, DC bias 0. ~2.5× finer than run 8 (0.05×0.01). All points verified inside validators — **no clipping** (rectangular grid). Field held at B_eff0 throughout (`fp`'d for the record).

**Coverage trade (on the page):** the high-|D| edge D=−0.66 rides near the BG +4.2 V cap (max V_bg = 4.163 V) — this is the known validator-limited flank; the dome may continue just beyond reach there. I cap D at −0.66 to stay safe; going further needs the BG validator raised (consent-gated, not proposed). The fast axis brackets the dome core into normal both sides.

**Purpose:** select the **widest-point D-line** (provisionally −0.64) and the **optimal n** (Rxx-min on that line) that Figs 3/4/5 and the Fraunhofer all ride.

**~65–70 min** (1806 pts × ~2.1 s/pt at delay 2 + ramps; priced off run 0's 1.34 s/pt at delay 1.2, +session margin). **Checkpoints** (I'll watch live): **(1) first D-row (~86 pts, ~3 min)** — leakage <1 nA, 4T not railed/flat, dome dip appears as n crosses ~−5.0; abort there if wrong. **(2) periodically (~every ~20 min)** — interim dome shape / continue. Preconditions printed+asserted at top (T<60 mK, |B|<5 mT at start, heater=0). Ends with gates at the optimum, B held at B_eff0.
