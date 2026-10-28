# Power of the headline: share of fans supporting the call within T hours (censored design)

v = P(call)·[h ≤ T] per fan; S = mean v over a cell's fans; Δ = mean over fable, opus, fable51, opus55, astra, gpt6sol of S(corpus) − S(none). Spot-check, B = 0 and no-call endings censored. Each cell runs to N fans, capped at 2N episodes. Simulations 400, bootstrap 500, permutations 400; prior weight N0 = 3.

## Dev set, 08-22 cut (the pilot)

| model | arm | episodes | censored | fans: P(call) @ h |
|---|---|---|---|---|
| fable | corpus | 1 | 0 | 1.00 @ 5.8 |
| fable | none | 1 | 1 | — |
| opus | corpus | 1 | 0 | 1.00 @ 4.8 |
| opus | none | 1 | 0 | 1.00 @ 3.1 |
| fable51 | corpus | 1 | 1 | — |
| fable51 | none | 1 | 0 | 0.00 @ 2.8 |
| opus55 | corpus | 1 | 0 | 0.99 @ 3.1 |
| opus55 | none | 1 | 1 | — |
| astra | corpus | 6 | 6 | — |
| astra | none | 3 | 1 | 0.42 @ 2.0, 0.90 @ 1.8 |
| gpt6sol | corpus | 1 | 0 | 0.98 @ 3.7 |
| gpt6sol | none | 1 | 0 | 0.10 @ 4.7 |
| all models | corpus | 26 | 7 | 19 fans, mean v(8 h) 0.77 |
| all models | none | 14 | 6 | 8 fans, mean v(8 h) 0.32 |

Dev-set Δ(8 h) over the models with fans in both arms: +0.44 (permutation p 1.00); exploratory.

## Population Δ and censoring by pilot

| pilot | Δ(6 h) | Δ(8 h) | Δ(12 h) | censoring rate corpus / none (mean over models) |
|---|---|---|---|---|
| smoothed | +0.416 | +0.459 | +0.459 | 0.34 / 0.41 |
| pooled | +0.399 | +0.451 | +0.451 | 0.27 / 0.43 |
| null | -0.001 | +0.000 | +0.000 | 0.33 / 0.33 |

## Precision, power and cost under the rule (T = 8 h)

| pilot | N | episodes / cell corpus, none | censored / cell corpus, none | cells short of N | median Δ̂ | CI half-width | MDE (80 %) | P(CI > 0) | P(CI < 0) | E[$] per cut |
|---|---|---|---|---|---|---|---|---|---|---|
| smoothed | 5 | 7.2, 8.0 | 2.7, 3.5 | 0.22 | +0.466 | 0.162 | 0.231 | 1.00 | 0.00 | 372 |
| smoothed | 10 | 14.6, 16.5 | 5.5, 7.1 | 0.23 | +0.465 | 0.125 | 0.179 | 1.00 | 0.00 | 759 |
| smoothed | 20 | 29.3, 33.2 | 11.1, 14.2 | 0.23 | +0.454 | 0.091 | 0.130 | 1.00 | 0.00 | 1532 |
| pooled | 5 | 6.8, 8.2 | 1.8, 3.5 | 0.12 | +0.449 | 0.165 | 0.236 | 0.99 | 0.00 | 362 |
| pooled | 10 | 13.6, 17.0 | 3.6, 7.4 | 0.10 | +0.456 | 0.122 | 0.175 | 1.00 | 0.00 | 743 |
| pooled | 20 | 27.5, 34.4 | 7.5, 14.8 | 0.07 | +0.448 | 0.090 | 0.128 | 1.00 | 0.00 | 1500 |
| null | 5 | 7.3, 7.2 | 2.4, 2.3 | 0.07 | -0.010 | 0.185 | 0.264 | 0.04 | 0.04 | 352 |
| null | 10 | 14.8, 14.8 | 4.9, 4.8 | 0.03 | +0.001 | 0.138 | 0.197 | 0.03 | 0.04 | 717 |
| null | 20 | 29.7, 29.7 | 9.7, 9.8 | 0.01 | -0.006 | 0.100 | 0.143 | 0.03 | 0.05 | 1438 |

## Half-width at the budget sensitivities (smoothed pilot)

| N | T = 6 h | T = 8 h | T = 12 h |
|---|---|---|---|
| 5 | 0.170 | 0.161 | 0.161 |
| 10 | 0.131 | 0.125 | 0.125 |
| 20 | 0.096 | 0.092 | 0.091 |

## Decision calibration (two-sided α = 0.05, T = 8 h)

| pilot | N | rejection, CI excludes 0 | rejection, permutation p < 0.05 | mean Δ̂ |
|---|---|---|---|---|
| null | 5 | 0.080 | 0.048 | -0.006 |
| null | 10 | 0.075 | 0.055 | +0.000 |
| null | 20 | 0.068 | 0.062 | -0.005 |
| smoothed | 5 | 0.998 | 0.983 | +0.461 |
| smoothed | 10 | 1.000 | 1.000 | +0.463 |
| smoothed | 20 | 1.000 | 1.000 | +0.457 |
| pooled | 5 | 0.993 | 0.985 | +0.447 |
| pooled | 10 | 1.000 | 1.000 | +0.454 |
| pooled | 20 | 1.000 | 1.000 | +0.446 |

$ per episode (common.EPISODE_USD: measured for fable, opus, astra; estimated for the rest): fable 8.72, opus 3.76, fable51 6.24, opus55 2.44, astra 1.96, gpt6sol 1.13. Censored episodes are paid for. The 2 × 2 cut design doubles the cost.
