# Ground truth — next move at the frontier (cut idx 176)

*What Aaron actually did in the next section (`# Cuts at fixed n and D`, cells
177–184, → `data/1777`+). One expert path among several reasonable ones — this
is a genuinely contested frontier; used to route to review, never as an
exact-match score.*

> **Re-grounded 2026-06-09 (Aaron, expert-review card).** Capture confirmed
> (*"Correct, great job"*) and the contested framing affirmed — with a stated
> preference: *"I would favor (a) [finishing the effective-mass number] and (c)
> [a 1/B-spaced field sweep to read B_F directly] over (b) [a broader/denser
> Landau-fan map]."* The broader-fan branch below is therefore defensible but
> rated weaker than the m\* or direct-B_F branches. (His read of `data/1776`
> on the same card: "your read is right!")

## The move: `# Cuts at fixed n and D`

**High-resolution 1D field cuts at individual fixed (n, D) operating points**,
to read the quantum-oscillation frequency cleanly now that the small fan
confirmed the oscillations are real:

- `s.sweep(mag.field, np.linspace(3, 1, 2001), delay=0.6)` at **(n = 0.5, D = 1)**
  → `data/1777`, then `s.sweep(mag.field, np.linspace(1, 3, 2001), delay=0.6)` at
  **(n = 0.55, D = 1)** → `data/1778` (cells 178, 180). I.e. dense 2001-point
  field sweeps over 1–3 T at single (n, D) points.
- Followed (`## Large series`, cell 183) by a loop over **13 densities
  n = 0.5 → 0.75 at D = 1**, each a 3001-point `mag.field` sweep 1 ↔ 4 T
  (alternating direction) → `data/1779`+.
- His own analysis of the first cut (`20260124_ana.ipynb` cell 79,
  `files=[1777]`) plots Rxx vs `mag.field`, 1 → 3 T, showing well-resolved SdH
  oscillations — see `figures/ana_1777_fixed-nd-cut_sr830_1.png` (answer-key
  only; post-cut).

## Why this is a (good) next step
The small fan (`data/1774–1776`) established *that* the oscillations are real but
at coarse field resolution. To turn them into physics you want the **oscillation
frequency B_F** (∝ Fermi-surface area ∝ carrier density of the oscillating
pocket), which requires **dense, wide-range 1D field cuts at fixed (n, D)** so
the periodicity in 1/B is well sampled. Stepping (n, D) then charts how B_F (and
thus the pocket) evolves with filling. It is the natural "characterize the
confirmed oscillation" path.

## Class for judging (CONTESTED frontier)
This frontier is deliberately open — multiple classes are defensible:
- **Same experiment (Aaron's move):** high-resolution fixed-(n, D) 1D field cuts
  (≥2000 pts over a wide field range) to extract B_F, optionally swept over a set
  of densities. Parameter-level choices (which (n, D), 1–3 T vs 1–4 T, #points)
  are not the decision.
- **Same class, different params:** a denser/wider fan at the confirmed point, or
  a 1/B-spaced field sweep, to read B_F — same intent, different sampling.
- **Different but reasonable:** committing to the **effective-mass temperature
  series** at the confirmed oscillation point (finish m* now that QO are real) —
  rated equivalent-or-better by Aaron (2026-06-09), alongside the 1/B-spaced
  direct-B_F route above.
- **Defensible but weaker:** a **broader Landau-fan map** over (n, B) to see the
  global LL structure before drilling in — Aaron (2026-06-09) would favor the
  m* or direct-B_F branches over it. Credit a well-argued case, but it should
  not score as equal to the favored branches.
- **Divergent / worse:** re-running the small fan with no change, abandoning the
  QO/m* thread for unrelated gate hysteresis checks, or a single coarse sweep
  that can't resolve B_F.

## Notes
- Because this is contested, the directive briefs (`directive-short/-long`)
  encode Aaron's actual move (the fixed-(n,D) cuts); the open briefs
  (`open-short/-long`) leave the branch to the agent and lean on the
  strategic-match read above.
- The subsequent `# Heating at CSC` / `# Cooling in QM` / `# CSC out to 5T`
  sections (cells 185+) are *later* moves, not the immediate next step.
