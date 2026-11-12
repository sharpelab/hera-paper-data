## HERA — Figure 3 (SETTLED re-do) — R-gated per-step equilibration

**Settle test result (cell 49) — important:** the thermal tail is *slow*. Parking at 4.5 V from base, R climbed 6→33 Ω over t=8→14 min while T crept 265→285 mK, still rising — τ is order **many minutes**. This means **even the warm-up was under-settled** (its dT/dt<1 mK/min gate was met by the probe long before the sample equilibrated), so the heater→T cal (this session *and* prior) is biased low. There's no fast settled measurement; rigor needs real dwell.

**This cell** does the rigorous re-do. Ascending V-ladder from base (**26 steps, dense in the transition ~3.5–5.5 V**); at each step it parks gates at the optimum and **settles until BOTH R (the sample proxy) and probe-T plateau** (|dR/dt|<0.4 Ω/min & |dT/dt|<0.3 mK/min, 2 consecutive, min 4 min / max 18 min), then sweeps the n-line → **one file per step**. R-gating auto-allocates dwell — flat in the SC/normal regions (fast), long through Tc (where it matters). The recorded settled T is the true T-axis.

**~6.5–7.5 h, ~26 files** (block stays ~37 h, inside your ~40–50 h). Knob: add points / widen the dense band if you want finer T (each point ≈ 15 min). It **waits for base first** (settle test left the fridge warm), then ascends; ends heater-off at base.

**Safety / verification:** I'll **watch the first 1–2 settled steps closely** (the step-0 file + the cell's printed settled-ladder) to confirm the loop and gating work before the full run commits — **interrupt (`nb-collab interrupt`) if the early steps look wrong** or the fridge MC runs away. This supersedes the dynamic Fig 3 (run 4). Run when ready; I'll read the first file, then check in periodically and build the quantitative R(T,n) at completion.
