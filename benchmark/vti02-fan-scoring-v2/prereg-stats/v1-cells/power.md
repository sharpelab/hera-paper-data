# Power / precision of D_pool (4 matrix models), pilot = 08-22 dev set, quality = cells, floor policy

Outer simulations S = 400, inner bootstrap B = 500. Mixture prior weight N0 = 3.

Pilot cells (episodes / landed fans / Q>0 fans):
- fable corpus: 1 / 1 / 1
- fable none: 1 / 0 / 0
- opus corpus: 1 / 1 / 1
- opus none: 1 / 1 / 1
- sol corpus: 2 / 2 / 2
- sol none: 1 / 1 / 0
- astra corpus: 6 / 0 / 0
- astra none: 3 / 2 / 2
- pool corpus: 21 / 15; pool none: 9 / 4

Pilot `smoothed`: population D_pool ≈ +0.229; landing rate corpus / none = 0.66 / 0.51
Pilot `pooled`: population D_pool ≈ +0.264; landing rate corpus / none = 0.71 / 0.45
Pilot `null`: population D_pool ≈ -0.008; landing rate corpus / none = 0.63 / 0.64

## Fixed n episodes per cell

| pilot | n / cell | median D̂ | median CI half-width | P(CI lower > 0) | P(CI upper < 0) | median per-cell ū half-width |
|---|---|---|---|---|---|---|
| smoothed | 5 | +0.21 | 0.254 | 0.38 | 0.00 | 0.348 |
| smoothed | 10 | +0.22 | 0.194 | 0.56 | 0.00 | 0.281 |
| smoothed | 20 | +0.22 | 0.139 | 0.83 | 0.00 | 0.202 |
| smoothed | 40 | +0.21 | 0.099 | 0.98 | 0.00 | 0.144 |
| pooled | 5 | +0.27 | 0.275 | 0.47 | 0.00 | 0.381 |
| pooled | 10 | +0.29 | 0.203 | 0.76 | 0.00 | 0.297 |
| pooled | 20 | +0.27 | 0.147 | 0.93 | 0.00 | 0.211 |
| pooled | 40 | +0.27 | 0.105 | 1.00 | 0.00 | 0.152 |
| null | 5 | +0.01 | 0.295 | 0.03 | 0.04 | 0.396 |
| null | 10 | -0.01 | 0.218 | 0.04 | 0.04 | 0.303 |
| null | 20 | -0.01 | 0.156 | 0.04 | 0.04 | 0.218 |
| null | 40 | -0.00 | 0.111 | 0.04 | 0.02 | 0.156 |

## Stopping rule: N landed fans, capped at 2N episodes

| pilot | N | mean episodes / cell (corpus, none) | median D̂ | median CI half-width | P(lower > 0) | P(upper < 0) | cells at cap | median per-cell ū half-width |
|---|---|---|---|---|---|---|---|---|
| smoothed | 5 | 7.1, 8.6 | +0.22 | 0.214 | 0.51 | 0.00 | 0.31 | 0.305 |
| smoothed | 10 | 14.4, 17.6 | +0.21 | 0.156 | 0.72 | 0.00 | 0.31 | 0.223 |
| smoothed | 20 | 28.8, 35.8 | +0.21 | 0.111 | 0.95 | 0.00 | 0.30 | 0.162 |
| pooled | 5 | 6.9, 9.2 | +0.29 | 0.224 | 0.65 | 0.00 | 0.26 | 0.318 |
| pooled | 10 | 14.0, 18.9 | +0.27 | 0.162 | 0.88 | 0.00 | 0.30 | 0.232 |
| pooled | 20 | 28.0, 38.9 | +0.27 | 0.117 | 0.99 | 0.00 | 0.35 | 0.166 |
| null | 5 | 7.6, 7.6 | +0.00 | 0.249 | 0.04 | 0.04 | 0.11 | 0.333 |
| null | 10 | 15.6, 15.6 | -0.00 | 0.178 | 0.03 | 0.05 | 0.07 | 0.246 |
| null | 20 | 31.5, 31.4 | -0.00 | 0.126 | 0.01 | 0.04 | 0.03 | 0.177 |

## Staged precision rule: stages N = 5, 10, 20 landed fans (each capped at 2N episodes); a cell stops at the first stage whose per-cell ū 95 % half-width <= δ

| pilot | δ | mean episodes / cell | share of cells stopping at N = 5 / 10 / 20 | median D̂ | mean D̂ | median D_pool half-width | P(lower > 0) | P(upper < 0) |
|---|---|---|---|---|---|---|---|---|
| smoothed | 0.15 | 28.8 | 0.12 / 0.04 / 0.85 | +0.226 | +0.226 | 0.110 | 0.91 | 0.00 |
| smoothed | 0.2 | 24.4 | 0.20 / 0.15 / 0.65 | +0.252 | +0.253 | 0.117 | 0.94 | 0.00 |
| smoothed | 0.25 | 17.1 | 0.26 / 0.51 / 0.23 | +0.248 | +0.252 | 0.144 | 0.86 | 0.00 |
| pooled | 0.15 | 32.0 | 0.05 / 0.01 / 0.94 | +0.298 | +0.297 | 0.114 | 0.99 | 0.00 |
| pooled | 0.2 | 29.0 | 0.09 / 0.11 / 0.80 | +0.322 | +0.320 | 0.119 | 0.99 | 0.00 |
| pooled | 0.25 | 19.6 | 0.15 / 0.57 / 0.29 | +0.306 | +0.309 | 0.146 | 0.94 | 0.00 |
| null | 0.15 | 30.9 | 0.03 / 0.00 / 0.97 | +0.001 | -0.002 | 0.126 | 0.06 | 0.06 |
| null | 0.2 | 29.8 | 0.05 / 0.04 / 0.92 | -0.004 | +0.000 | 0.127 | 0.11 | 0.10 |
| null | 0.25 | 21.6 | 0.08 / 0.50 / 0.42 | -0.003 | -0.002 | 0.154 | 0.08 | 0.09 |

## Decision calibration under the N-landed rule: bootstrap-CI vs within-model permutation test (two-sided α = 0.05)

| pilot | N | rejection rate, CI excludes 0 | rejection rate, permutation p < 0.05 | mean D̂ | population D |
|---|---|---|---|---|---|
| null | 5 | 0.092 | 0.072 | +0.009 | +0.017 |
| null | 10 | 0.055 | 0.048 | +0.005 | +0.017 |
| smoothed | 5 | 0.432 | 0.320 | +0.203 | +0.212 |
| smoothed | 10 | 0.752 | 0.693 | +0.216 | +0.212 |
