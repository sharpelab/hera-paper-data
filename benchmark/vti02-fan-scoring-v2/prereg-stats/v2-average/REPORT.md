# Pre-registration statistics on the final grader

The design is `hera/docs/fan-design-grader.md` § Statistics (the plan of record). Everything here is
dev set only and exploratory: the grader was developed on these episodes, and the pilot cells hold
one or two episodes each.

Scripts: `common.py` (inventory with observed-model labels and ending classes, hand extractions,
`score()` = the grader's box score, `design()` = axes + hours in each cut's frame; selftest 0
mismatches), `stats.py`, `devset.py`, `power_budget.py` (the primary), `power_per_model.py` (the
secondaries), `multiverse.py`, `cost.py`, `power.py` (D_pool, supporting). Outputs: `episodes.csv`,
`devset_stats.md`, `power_budget.md`, `power_per_model.md`, `multiverse.md` / `.csv`, `cost.md`,
`power.md`, `reference_set.json`. The capped-cells scheme's scripts and outputs are in `v1-cells/`.

## Frame and inventory

Episodes grade in the frame of the cut they ran on: the 08-22 cut at n_scale 0.886 (the session's
own pin for its run-5 frame), the older 08-21 cut at 0.92. Dev episodes live under the development
frontiers (`vti02-fan-design`, `vti02-probe-first`); the production frontiers
(`vti02-pre-fan-0822`, `-0824`) hold no data yet, and today's production smokes sit in
`$HERA_DATA/replay/runs-smoke/`, outside the inventory.

## The primary: Δ(8 h)

Per fan v = P(≥4) · [h ≤ 8 h]; per cell S = mean v over its fans; Δ = mean over the six models of
S(corpus) − S(none) on the 08-22 cut; spot-check, B = 0 and no-call endings censored.

| N (fans per cell, cap 2N episodes) | 95 % half-width | detectable at 80 % power | $ per cut |
|---|---|---|---|
| 5 | 0.17 | 0.24 | ~$370 |
| 10 | 0.13 | 0.18 | ~$760 |
| 20 | 0.09 | 0.13 | ~$1,530 |

- Pilot Δ(8 h): +0.32 (smoothed) / +0.31 (pooled); dev-set value +0.22 (p 0.50). It rests on one or
  two episodes per cell, smokes included; plan on the detectable effect, not the pilot.
- Decision test: the within-model permutation test holds its size (5.4 ± 0.5 % at N = 10,
  4.3 ± 0.5 % at N = 20; 2000 null simulations); the bootstrap CI runs 6–9 % and is reported only.
- Censoring on the pilot: about a third of corpus and two fifths of no-corpus episodes; about a
  quarter of cells reach 2N short of N.
- Budget sensitivity: Δ is the same at 8 h and 12 h (no dev fan lands between them); 6 h is lower.

## The secondaries

Per-model Δ and model contrasts within an arm: half-width ~0.22 at N = 20, detectable ~0.31
(astra 0.39, its corpus cell censoring most episodes); ~0.26 at N = 30.

## Multiverse (grader knobs)

Across 360 grader universes (tone model × light floor × hard/soft lines × column spacing and cap ×
A on / off / noise model), Δ(8 h) keeps its sign in 69 % on the matrix models (95 % over all dev
models). The sensitive axis is column spacing: at one bin and cap 5, P(≥4) needs four points a full
bin apart, and the matrix Δ(8 h) goes to −0.10; every other axis moves it by at most 0.09. The
D_pool tables in `multiverse.md` (floor and landed placement) are supporting.

## Supporting: D_pool and ΔHV1

`devset_stats.md`. Stratification by model is required (arm-pooled D over the matrix models has the
opposite sign to D_pool). Exact Pareto rarely separates two fans, since the better one takes longer.

## Cost

`cost.md`: measured $ per episode at effort high (Fable 5 8.72, Opus 5 3.76, GPT-6 Astra 1.96);
`common.EPISODE_USD` adds the smoke-measured and estimated rest (Fable 5.1 6.24, Opus 5.5 2.44,
GPT-6 Sol 1.13). Claude costs are API-equivalent; the Codex arms bill OpenAI.
