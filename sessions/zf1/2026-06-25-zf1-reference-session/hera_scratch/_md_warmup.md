## HERA — Heater block START: warm-up + dwell calibration + Tc preview

Fig 1 done (selection: D=−0.64, n=−5.0×10¹¹). Now the **heater (T-axis) block** — the expensive, least-reversible phase. Gates are already at the optimum and B at B_eff0, so we're positioned.

**The block (heat up ONCE, get all T-data, then cool):**
1. **This cell** — warm up to the 6.5 V ceiling (~490 mK) in steps, *settle-gated*. Purpose: (a) **calibrate the per-step thermalization** so I can set the Fig-3 ~100-step ladder dwell empirically (the brief's "gate on settling, not absolute T"); (b) re-confirm the heater→T map; (c) read 4T R(T) at the dome center = a **free Tc preview** (expect R→normal by ~280 mK). ~1.5–2 h.
2. **Fig 3** — R(T,n) map: `multimegasweep`, heater the dense slow axis stepping **down** 6.5→0 V (~100 T-pts, measure-while-cooling), n-line fast at D=−0.64, B=B_eff0.
3. **Fig 4** — repeat the T-map at B_eff0+{1,2,4 mT} (3 more maps; Fig 3 is the 0-field member).
4. **⚑ verify + Fig 5** — cheap base dV/dI, then dV/dI vs (I_dc, T) on the same T-axis.
5. Cool to base → **Fig 2 Fraunhofer** last.

**Scale flag:** the full heater block is large — realistically **~25–35 h** across Figs 3/4/5 (four ~100-pt T-maps + a 2D dV/dI), consistent with the multi-day figure campaign. Each piece checkpoints; nothing locks us in. If you'd rather trim (fewer T-points, fewer Fig-4 fields, coarser dwell), say so and I'll re-scope. **This warm-up cell is the only commitment right now** — it's reversible (cool back anytime) and sets the dwell before the big map.

**Heater discipline (rig card):** ≤1 V steps, equilibrate each; confirm `heater.curr` drawing (asserted). The cell polls (T, R) every 30 s, breaks each step when |dT/dt| < 1 mK/min (or 15 min cap), and prints the settle time. **Watch the fridge MC** — interrupt if T runs away. Preconditions asserted at top (base T, B=B_eff0, gates at optimum, heater off). Leaves heater at 6.5 V for the descending Fig-3 ladder. I'll read the settle times and propose Fig 3 with the calibrated dwell.
