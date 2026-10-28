# Ground truth — the Step-7 stacking call + next move

Layer-B answer key. Under the stacking-ID goal the agent's **read of `data/0213`
is the Step-7 call**; its **next experiment** corroborates the call. Scoring
rubric for both.

## The correct Step-7 call (the "read" section)

**Per-region verdict: `ABAB (strong)`** — two bilayer-like Fermi surfaces
partitioning F_L (both tones below F_L, summing to the Luttinger line, each
Onsager-tracking across n). Required supporting reasoning:

- **The F_L-tone-origin discrimination fired.** The tone at F_L is resolved as a
  **magnetic-breakdown sum-tone** (B-window split: grows with B relative to the
  fundamentals) — **not** an ABCA singleton. This check is mandatory before any
  singleton call, and it is the crux of this fixture.
- **ABCA is excluded** (or heavily downweighted): two fundamentals below F_L are
  resolved, and the F_L tone is breakdown, not a chiral pocket.
- g = 4 symmetric metal; Σf = |n| closes.

A `moderate` (rather than `strong`) ABAB is acceptable if the agent hedges on
resolution; the essential content is **ABAB, pair partitioning F_L, F_L tone =
breakdown**.

## The correct next experiment (the "next move" section)

Firm the two-band call: **per-branch LK effective-mass split** (the ABAB branches
differ by ≈ φ² ≈ 2.6×) via a temperature series at a fixed large-|n| column, or a
same-side spot check with an explicit low-B/high-B split to nail the breakdown
origin, or the electron-side fan. NOT a follow-up premised on a single chiral
pocket.

## Judging buckets (score the distribution across samples)

- **BEST (same class):** `ABAB` verdict **and** the F_L-tone-origin
  discrimination explicitly fired (F_L tone identified as breakdown / sum-tone
  via the B-window behavior) **and** ABCA excluded.
- **OK (reasonable):** reads two fundamentals partitioning F_L and calls / leans
  **ABAB**, but does not fully resolve the F_L tone as breakdown (flags it
  origin-ambiguous). Still the right class; partial discrimination.
- **MISS (the failure this fixture exists to catch):** a confident **ABCA** call
  — taking the F_L breakdown/sum-tone for the single chiral pocket, skipping or
  failing the F_L-tone-origin discrimination. A singleton call with resolved
  partner tones and no discrimination is a **protocol violation** (recipe: F_L-
  tone origin is mandatory).

## Comparison to the rung-3a mechanical baseline

The mechanical evaluator (RESULTS.md) called this fan **ABAB** and identified the
breakdown tone in 17/23 tested columns via the B-window split — it did **not**
call ABCA. The question here is whether the *agent*, under next-move pressure,
runs the same discrimination rather than eagerly calling the singleton.
