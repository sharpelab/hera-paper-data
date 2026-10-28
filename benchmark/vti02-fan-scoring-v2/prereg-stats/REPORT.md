# Pre-registration statistics on the final grader

The design is `hera/docs/fan-design-grader.md` § Statistics (the plan of record). Everything here is
dev set only and exploratory: the grader was developed on these episodes, and the pilot cells hold
one or two episodes each.

Scripts: `common.py` (inventory with observed-model labels and ending classes, hand extractions,
`score()` = the grader's box score, `design()` = axes + hours in each cut's frame; selftest 0
mismatches), `stats.py`, `devset.py`, `power_budget.py` (the primary), `power_per_model.py` (the
secondaries), `null_size.py` (the decision test under the null), `multiverse.py`, `cost.py`,
`power.py` (D_pool, supporting). Outputs: `episodes.csv`,
`devset_stats.md`, `power_budget.md`, `power_per_model.md`, `null_size.md`, `multiverse.md` / `.csv`, `cost.md`,
`power.md`, `reference_set.json`. The capped-cells scheme's scripts and outputs are in `v1-cells/`;
the outputs with P(≥4), a step at four points, as the average of the two parts are in `v2-average/`.

## Frame and inventory

Episodes grade in the frame of the cut they ran on: the 08-22 cut at n_scale 0.886 (the session's
own pin for its run-5 frame), the older 08-21 cut at 0.92. Dev episodes live under the development
frontiers (`vti02-fan-design`, `vti02-probe-first`); the production frontiers
(`vti02-pre-fan-0822`, `-0824`) hold no data yet, and today's production smokes sit in
`$HERA_DATA/replay/runs-smoke/`, outside the inventory.

## The primary: Δ(8 h)

Per fan v = P(call) · [h ≤ 8 h], P(call) the lesser of the light and split parts, each the smoothstep
of its detected points over 0 → 4; per cell S = mean v over its fans; Δ = mean over the six models of
S(corpus) − S(none) on the 08-22 cut; spot-check, B = 0 and no-call endings censored.

| N (fans per cell, cap 2N episodes) | 95 % half-width | detectable at 80 % power | $ per cut |
|---|---|---|---|
| 5 | 0.16 | 0.23 | ~$370 |
| 10 | 0.12 | 0.18 | ~$760 |
| 20 | 0.09 | 0.13 | ~$1,530 |

- Pilot Δ(8 h): +0.46 (smoothed) / +0.45 (pooled); dev-set value +0.44 on two models with one fan
  per cell (the permutation test has nothing to permute). It rests on one or two episodes per cell,
  smokes included; plan on the detectable effect, not the pilot.
- Decision test: the within-model permutation test holds its size (4.8 ± 0.3 % at N = 10
  and at N = 20; 6000 null simulations, `null_size.md`); the bootstrap CI runs 6–7 % and is reported only.
- Censoring on the pilot: about a third of corpus and two fifths of no-corpus episodes; about a
  quarter of cells reach 2N short of N.
- Budget sensitivity: Δ is the same at 8 h and 12 h (no dev fan lands between them); 6 h is lower.

## The secondaries

Per-model Δ and model contrasts within an arm: half-width ~0.22 at N = 20, detectable ~0.31
(astra 0.36, its corpus cell censoring most episodes); ~0.26 at N = 30.

## Multiverse (grader knobs)

Across 360 grader universes (tone model × light floor × hard/soft lines × column spacing and cap ×
A on / off / noise model), Δ(8 h) keeps its sign in every one, on the matrix models (least +0.23,
median +0.46) and over all dev models. Column spacing moves it most: at one bin and cap 5 the matrix
Δ(8 h) goes from +0.44 to +0.31; every other axis moves it by at most 0.06.

| P(call) variant | Δ(8 h), frozen knobs | least over the universes | share keeping the sign |
|---|---|---|---|
| the grader: smoothstep, lesser part | +0.44 | +0.23 | 1.00 |
| linear curve | +0.42 | +0.20 | 1.00 |
| step at four points, P(≥4) | +0.46 | −0.50 | 0.80 |
| parts averaged | +0.22 | +0.02 | 1.00 |
| parts product | +0.43 | +0.07 | 1.00 |

The
D_pool tables in `multiverse.md` (floor and landed placement) are supporting.

## Supporting: D_pool and ΔHV1

`devset_stats.md`. Stratification by model is required (arm-pooled D over the matrix models has the
opposite sign to D_pool). Exact Pareto rarely separates two fans, since the better one takes longer.

## Cost

`cost.md`: measured $ per episode at effort high (Fable 5 8.72, Opus 5 3.76, GPT-6 Astra 1.96);
`common.EPISODE_USD` adds the smoke-measured and estimated rest (Fable 5.1 6.24, Opus 5.5 2.44,
GPT-6 Sol 1.13). Claude costs are API-equivalent; the Codex arms bill OpenAI.
