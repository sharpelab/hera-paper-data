## HERA — Figure 1 (REVISED) — wide high-res dome map, ~10 h budget · **supersedes cell 31**

Per your call: this is the figure-grade dome map at a **~10 h budget** (not the 1 h version in cell 31 — **don't run cell 31; run this one**).

**Grid:** full requested range **n ∈ [−7, −1]×10¹¹ fast (0.015 step, 401 pts)** × **D ∈ [−0.69, −0.40] slow (0.004 step, 73 rows)** — *finer than the 0.02/0.005 you rejected on both axes*, B held at **B_eff0 = −0.366 mT**, AC 1 nA, 4T sens 1 mV, DC bias 0. **26,561 pts** in validators.

**Extremal-D edge / coverage trade (on the page):** D runs out to the BG-cap-limited extremal (~−0.69 at n=−7, ~−0.635 at n=−1). The 7 most-negative-D rows are partially clipped at the +4.2 V cap (row lengths 16→401) — this is *intended* ("out to the extremal limit"), not a calibration problem; it traces the accessible boundary. Max V_bg = 4.20 V (at the cap, validator-safe).

**Why this grid:** ~10 h at delay 1.3 → ~2.1× the per-point dwell-equivalent density of run 8 and 2.5–3× finer spatial sampling, over a much wider landscape. Sizing: 26,561 pts × ~1.44 s/pt = **~10.6 h** (priced off run 0's measured 1.34 s/pt at delay 1.2; +session margin → realistically ~10.5–11.5 h). I capped delay at 1.3 to spend the 10 h budget on resolution + range as you asked; if you'd rather trade some pixels for higher per-point SNR (delay ~2), say so and I'll re-balance.

**D ordered extremal → −0.40** so the **dome core (D≈−0.66→−0.59) lands in the first ~2 h** — an early checkpoint then confirms the map is good before committing the full 10 h.

**Checkpoints (I'll watch live):** (1) **first ~5 min** — leakage <1 nA, 4T not railed/flat, sweep advancing (this is the extremal-D normal-metal edge; no SC yet). (2) **~hourly** — by ~hr 1.5–2 the dome core appears → go/no-go on the full run; then periodic continue/adjust. Preconditions printed+asserted at top (T<60 mK, |B|<5 mT at start, heater=0). Ends with gates parked at the optimum, B held at B_eff0.
