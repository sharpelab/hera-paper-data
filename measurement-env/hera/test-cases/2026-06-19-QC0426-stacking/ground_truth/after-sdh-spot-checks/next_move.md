# Ground truth — next move (the Landau fan, and its two acquisition faults)

Layer-B answer key. **What the expert actually did** (cells 46–47, `data/4`) and
**what a correct design fixes** — the grading axis for the A/B.

## What the expert did (the as-run fan)

A Landau fan on the **electron side at D = 0**: field the **slow** axis (0.4→4.0 T,
8 mT, 451 rows — per-column FFT window [1,4] T alias-free), the paired-gate
**n-line** the fast axis (n = 1.0→4.5e12, 41 points), via `multimegasweep`. The
*scope* (electron, D = 0, this B-axis, this n-span) is correct and not in
dispute.

## The two faults it carried (flagged-but-accepted in the as-run)

1. **Under-ranged sensitivity → clipping.** It reused the spot-check's fixed
   `sr1/sr2 = 1e-5`, sized for the metallic spot-check R-scale. A fan's worst
   corner is `R(n_min, B_max)` — low density, high field — which is far more
   resistive; the as-run **clipped ~17 % of the map**, exactly the low-n / high-B
   region (the bottom of the labeling band the fan exists to resolve). Clipping
   distorts the per-column FFT.
2. **Shaved fast-axis dwell → under-settling.** It set `fast_delay ≈ 3·τ` as an
   "amplitude-for-time" trade. But the fast axis feeds a per-column FFT, where
   under-settling **suppresses the high-frequency tones** — it guts the stacking
   discriminator the fan is for (only the full-settling spot checks held the
   amplitude reference).

## The correct design (the "win" answer)

Same scope, faults removed:

- **Size sensitivity to the worst corner** `R(n_min ≈ 1e12, B_max = 4 T)` (or
  autorange), so the low-n / high-B labeling region is not clipped — not the
  metallic spot-check R-scale.
- **Hold the fast-axis settling floor** (≈ 7·τ, as the spot checks did), or, if
  time-bound, **buy the amplitude back with n-density** rather than silently
  shaving the dwell — never an unexamined sub-floor `fast_delay` on the FFT axis.
- Keep the rest: electron D = 0, B 0.4–4 T at 8 mT (alias-free [1,4] T), the
  n-line span, and a mid-sweep checkpoint (re-form a few n-columns, confirm the
  two-pocket structure tracks F(n), leakage < 1 nA).

## Grading the A/B (commit A vs B)

The fix lives in `landau-fan.md`: the **worst-corner dynamic-range guard**
(burn #7) and the **fast-axis-settling-×-density** rule (burn #8), both absent at
commit A. A correct A/B outcome:

- **Commit A** (no guards): proposes a fan that **inherits the spot-check fixed
  sensitivity** (clips low-n/high-B) and/or **shaves `fast_delay`** — i.e.
  reproduces the as-run faults.
- **Commit B** (guards present): proposes a fan that **sizes sensitivity to the
  worst corner** and **holds the settling floor / compensates with density** —
  i.e. avoids both faults.

Score on those two axes (clipping-avoidance, settling). If A and B propose the
same flawed fan, the recipe guards did not change the decision — a valid (and
important) null result.

**Third axis — sweep cost (always score it).** A proposal that fixes the faults
but **inflates fridge time** is not strictly better. Price the cost delta vs the
as-run (~8 h): a correctness fix that lands near ~12 h is justified; a design
that doubles to ~24 h for a marginal or out-of-validity corner (e.g. pushing
`n_max` past the Onsager-overlay validity ≤3.5e12 just to chase the high-n ML
partner) is an **overreach ding**, even if its sampling is otherwise better. The
recipe's measurement-dominated branch is explicit: buy the high-n Nyquist floor
by trimming n-points, **never by coarsening B**, and don't extend n_max for an
out-of-validity claim.
