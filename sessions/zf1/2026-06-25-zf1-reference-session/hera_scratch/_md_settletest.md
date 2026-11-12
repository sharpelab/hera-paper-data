## HERA — Settle test: measure the true equilibration time (for the settled re-do)

**Decision: full settled re-do of the heater block** (rigorous T-axis). Fig 3 (run 4) had a ~50 mK sample-probe lag at 90 s dwell — the dome shape is right but the T-axis is biased low (Tc 223 vs true ~280 mK). To do the re-do right, I need the *actual* dwell, not another guess.

**This cell** parks the heater at the transition midpoint (4.5 V ≈ 262 mK — the most lag-sensitive point) from base and watches **R (the sample-T proxy) equilibrate**, printing (t, T, R) every 15 s for 14 min. The time for R to plateau (within 2%) = the per-step dwell the settled ladder needs. Then returns the heater to 0 (cool back to base for the ascending settled re-do).

~14 min + a brief cool-back. Preconditions asserted (base T, B=B_eff0, gates at optimum, heater off). **Watch the fridge MC.** I'll read the settle time and build the settled Fig 3 (ascending from base, dwell = measured settle + margin, ~50 T-points) — then apply the same dwell to Figs 4/5. Run cell when ready.
