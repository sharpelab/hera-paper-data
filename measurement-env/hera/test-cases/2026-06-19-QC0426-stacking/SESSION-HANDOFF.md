# Session handoff — cost-floor gate + decomposition experiment

*2026-06-20/21. On the `NO_PUSH_replay_test` branch. Carries the gate-text
variants tried, the open thread (decomposition is NOT settled — keep testing),
and proposed minor edits to STYLE rule 16. All replay runs are under
`runs/after-sdh-spot-checks/` on this branch.*

## What we were testing

Frontier `after-sdh-spot-checks` (design the electron Landau fan). The earlier
A/B/C found HERA proposed a clipped, over-priced fan. We iterated the
`landau-fan.md` step-1 **cost-floor gate** and measured the proposed fan's cost
at **n = 3 per variant** (serial replays — parallel `claude -p` failed,
only 1/3 produced output; the future tool must isolate workers).

## Variants tried + results

| Variant | Gate form | proposed-fan cost (n=3) | onset computed |
|---|---|---|---|
| **V0 — weak/advisory** | "estimate cost, drive levers to limit" (advisory) | 13 / 16 / 27 / 35 h | 1/4 |
| **V1 — fix-a: co-located + forceful** | one block; binding, `sdh_onset`, "exactly one fan", "don't eyeball" | **3 / 3.9 / 7 h** | 3/3 |
| **V2 — F: split + terse** | step 1 → substeps 1a–1e, forcing *trimmed out* | 14 / 19 / 30 h | ~1/3 |
| **V3 — G: split + forceful** | substeps 1a–1e, forcing *restored* | 16 / 19 / 20 h | ~2/3 |

**Reproduction anchors:** V0 = `git show 7ed3441:hera/recipes/measurements/landau-fan.md`;
V1 (landed) = `git show ba1d0b6:…` (current `hera`); V2/V3 are uncommitted
experiments — V3 verbatim below, V2 = V3 minus the **bolded forcing** in 1b/1e.

### V3 (G) — decomposed step 1, verbatim (the form to keep iterating)

```
1. **Design the fan — compute these in order; each output feeds the next.** *Read-type fork: an SdH-FFT fan and a Středa/SC fan differ in B-sampling — state which.*
   - **1a — Scope + `n_max` clamp.** … **Clamp `n_max` to the claim's validity** — overlay/labeling ⇒ ≤ 3.5e12; read the high-n ML partner from a spot check, not by extending the fan. → `n_min, n_max, D`.
   - **1b — `B_lo` (compute it, do not eyeball).** SdH-FFT: `B_lo = hera.analysis.sdh_onset(R, B).onset_b` — **eyeballed onsets run systematically low** … Středa/SC: may start at 0. `B_max` = the claim. → `B_lo, B_max`.
   - **1c — Nyquist → `N_B`, `N_n`** (both axes; re-run whenever `n_max` changes). [SdH-FFT Δ(1/B) ≤ 1/(3·F) at n_max; Středa ≥2 rows/LL-period; n-axis ray-Nyquist at B_lo; trim N_n or floor high-n at B≥5–6T, never coarsen B.] → `N_B, N_n`.
   - **1d — Dynamic range → sensitivity.** full-scale ≥ I_bias·R(n_min, B_max), worst corner low n × high B; clipping corrupts the whole column's FFT. → `sensitivity` (fixed, autorange off).
   - **1e — Cost floor → one fan.** Wall-clock = N_B·N_n·t_pt. 1a–1d floored every lever, so **this is the proposal: exactly one fan — do not offer a cheaper alternative or defer the trim.** State N_B, N_n, wall-clock.
```
*(full text in the `dvar` worktree's `landau-fan.md` at session end, if still mounted.)*

## OPEN THREAD — decomposition is NOT settled

The n=3 read was "co-located (V1) beats decomposed (V3) ~4×", but **Zack is not
on board with a 'legibility-by-decomposition hurts' conclusion** — one frontier,
n=3, and V2/V3 confound structure with my trims. **Keep testing before
concluding.** Suggested next tests:
- **Larger n** (n≥5) per variant — the 3–7 vs 16–20 gap is big, but variance is
  high; confirm it's not sampling.
- **Cleaner decomposition** — V3 may just be a *bad* split (substeps too terse,
  or the per-substep "→ output" not forcing enough). Try a decomposition where
  each substep is itself forceful and demands its artifact be printed, vs the
  co-located block — isolate structure from wording.
- **Other frontiers / other recipes** — does the co-located>decomposed effect
  reproduce, or is it specific to this gate?
- **Why it might be real:** decomposition lets the agent satisfy each substep
  *locally* (onset called, but B_lo still 0.5; n_max clamped, but B_hi/N_n fat),
  losing the global "hit the floor" pressure a single block keeps. Worth a
  targeted test of that mechanism.

## Workshop — minor edits to STYLE rule 16 (landed `c54361c`)

Rule 16 as landed asserts facet (c) "co-located beats a tidy split" fairly
firmly. Given the open thread, **soften (c) to an observation under test**, not a
law:
- (c) current: *"Forceful — keep the forcing … trimming it to a bare formula
  re-opens the escape."* — this part (forcing matters) **is** well-supported; keep.
- **Add/replace the decomposition claim** with a hedge: *"Provisional [n=3, one
  frontier]: decomposing a forceful gate into terse substeps regressed it (~4×);
  whether that's the split or the trim is still under test — don't decompose a
  binding gate for legibility without re-measuring."*
- **Provenance line:** keep the advisory→binding→trimmed numbers (well-replicated);
  mark the co-located-vs-decomposed comparison as `[provisional, n=3]` rather than
  settled.

(Do not self-land these — workshop with Zack next session.)

## Pointers
- Landed on `hera`: fix-a gate `ba1d0b6`, STYLE rule 16 `c54361c`, field_invB→analysis `31bd351`.
- Run artifacts (this branch): `runs/after-sdh-spot-checks/{D-var,E-strong,F-split,G-splitforce}-*`.
- Fixture + answer-key: this dir (`VERIFICATION-PLAN.md`, `ground_truth/`).
- Replay harness traps + n=3-parallel note: `VERIFICATION-PLAN.md` "Operator notes".
