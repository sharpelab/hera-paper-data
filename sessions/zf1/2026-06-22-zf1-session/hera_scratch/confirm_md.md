## HERA — Run 4: confirm the candidate + pin the optimum + resolve the floor

Run 3 found a **coherent SC-like Rxx dip** (26→2.4 Ω over ~7 points, resistive phase, steady current) at **n≈−4.8×10¹¹, D≈−0.65 V/nm** — in the BBG/WSe₂ proximity-SC window, on the D<0 side, on the most-negative D line only. The survey missed it (coarse n-step). This is a genuine candidate; this run nails it down before characterization.

Three things at once (one `multisweep`, 204 pts, ~7 min):
1. **Reproduce + resolve the floor.** Re-measure D=−0.65 with **sr830_3 → 200 µV** (resolution ~0.07 Ω vs the 2 mV run's ~0.7 Ω; the dip bottomed at the old floor). Tells us if Rxx→0 (SC-leaning) or floors finite (failed-SC / anomalous-metal fork).
2. **Pin the optimum D.** Fine constant-D linecuts at D = −0.55, −0.60, −0.65 (the in-box bracket — see below), n = −3.7 → −6.2, step 0.05×10¹¹.
3. **Probe the max-|D| boundary.** An **edge sweep** (BG pinned at +4.198 V, TG −4→−6) — because **D≈−0.65 is essentially the most-negative D reachable at this density**: D=−0.70/−0.75 would need BG>+4.2 V (validator cap). The candidate sits near the accessible-D edge; the edge sweep traces the boundary the way the coverage gate prescribes. If the dip is still deepening at the edge, the optimum is **instrument-limited** (a stated coverage caveat, not a free pass).

Drive 1 nA (consistent; bias spectroscopy will map Ic next). tc 0.3 s, delay 1.5 (≥5×tc, better low-R SNR). Magnet untouched. **Preconditions** asserted: base T, B≈0. **Read after:** the floor value (SC vs failed-SC lean), the optimum (n,D) → that becomes the operating point for **bias spectroscopy** (the critical-current hallmark, the decisive next measurement).
