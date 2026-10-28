## HERA — extremal-|D| corner map (out to the −0.76 V/nm cap)

**Correcting my premature call** (operator, right): the clean linecuts stopped at D=−0.60 and the wedge from there to the −0.76 V/nm cap was only seen coarse + sr3-clipped. This maps it properly. The extremal-|D| region is bounded by **BG=+4.2** (the validator that caps −D); the max reachable |D| rises **0.66 → 0.76 V/nm as n deepens** (−3 → −14×10¹¹), so this is a corner wedge, not a constant-D line.

**Map:** TG [−7, −4.5] (slow) × BG [+3.0, +4.2] (fast), 51×49, tc=100 ms, **sr3 = 200 µV (no clip)**, 1 nA. Coverage: **D = −0.51 → −0.76 V/nm** (72% of points |D|>0.60, reaching the cap), n = +3 → −24×10¹¹, steps TG 50 mV / BG 25 mV (Δn ≈ 2–3×10¹⁰, resolves the ~5×10¹⁰ arc). **Est ~25 min.**

**Checkpoint (~12 min, TG row ~20):** leakage (this is the extremal-field corner — highest risk; the row order hits TG=−7/BG=+4.2 first so the worst case is seen early), any low-Rxx pocket, and rate. Abort on leakage runaway. B untouched. After this I re-issue the SC call on the full D coverage. I'm arming a background `hera-watch` monitor when this lands.
