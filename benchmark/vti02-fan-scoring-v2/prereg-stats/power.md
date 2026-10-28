# Power / precision of D_pool (4 matrix models), pilot = 08-22 dev set, quality = quality, floor policy

Outer simulations S = 400, inner bootstrap B = 500. Mixture prior weight N0 = 3.

Pilot cells (episodes / landed fans / Q>0 fans):
- fable corpus: 1 / 1 / 1
- fable none: 1 / 0 / 0
- opus corpus: 1 / 1 / 1
- opus none: 1 / 1 / 1
- sol corpus: 2 / 2 / 2
- sol none: 1 / 1 / 1
- astra corpus: 6 / 0 / 0
- astra none: 3 / 2 / 2
- pool corpus: 21 / 15; pool none: 9 / 4

Pilot `smoothed`: population D_pool ≈ +0.144; landing rate corpus / none = 0.66 / 0.51
Pilot `pooled`: population D_pool ≈ +0.213; landing rate corpus / none = 0.71 / 0.45
Pilot `null`: population D_pool ≈ -0.014; landing rate corpus / none = 0.63 / 0.64

## Fixed n episodes per cell

| pilot | n / cell | median D̂ | median CI half-width | P(CI lower > 0) | P(CI upper < 0) | median per-cell ū half-width |
|---|---|---|---|---|---|---|
| smoothed | 5 | +0.12 | 0.260 | 0.18 | 0.01 | 0.360 |
| smoothed | 10 | +0.13 | 0.196 | 0.23 | 0.00 | 0.287 |
| smoothed | 20 | +0.13 | 0.141 | 0.46 | 0.00 | 0.206 |
| smoothed | 40 | +0.12 | 0.101 | 0.69 | 0.00 | 0.146 |
| pooled | 5 | +0.23 | 0.283 | 0.37 | 0.00 | 0.383 |
| pooled | 10 | +0.23 | 0.206 | 0.59 | 0.00 | 0.298 |
| pooled | 20 | +0.22 | 0.150 | 0.79 | 0.00 | 0.217 |
| pooled | 40 | +0.22 | 0.107 | 0.99 | 0.00 | 0.156 |
| null | 5 | +0.00 | 0.293 | 0.03 | 0.04 | 0.383 |
| null | 10 | -0.01 | 0.214 | 0.04 | 0.04 | 0.295 |
| null | 20 | -0.01 | 0.154 | 0.03 | 0.04 | 0.214 |
| null | 40 | -0.00 | 0.110 | 0.03 | 0.03 | 0.154 |

## Stopping rule: N landed fans, capped at 2N episodes

| pilot | N | mean episodes / cell (corpus, none) | median D̂ | median CI half-width | P(lower > 0) | P(upper < 0) | cells at cap | median per-cell ū half-width |
|---|---|---|---|---|---|---|---|---|
| smoothed | 5 | 7.1, 8.6 | +0.13 | 0.211 | 0.21 | 0.01 | 0.31 | 0.309 |
| smoothed | 10 | 14.4, 17.6 | +0.12 | 0.155 | 0.35 | 0.00 | 0.31 | 0.227 |
| smoothed | 20 | 28.8, 35.8 | +0.12 | 0.111 | 0.59 | 0.00 | 0.30 | 0.163 |
| pooled | 5 | 6.9, 9.2 | +0.23 | 0.222 | 0.51 | 0.00 | 0.26 | 0.321 |
| pooled | 10 | 14.0, 18.9 | +0.21 | 0.162 | 0.74 | 0.00 | 0.30 | 0.234 |
| pooled | 20 | 28.0, 38.9 | +0.22 | 0.116 | 0.95 | 0.00 | 0.35 | 0.168 |
| null | 5 | 7.6, 7.6 | +0.00 | 0.239 | 0.05 | 0.04 | 0.11 | 0.321 |
| null | 10 | 15.6, 15.6 | +0.00 | 0.172 | 0.04 | 0.05 | 0.07 | 0.237 |
| null | 20 | 31.5, 31.4 | +0.00 | 0.123 | 0.03 | 0.04 | 0.03 | 0.171 |

## Staged precision rule: stages N = 5, 10, 20 landed fans (each capped at 2N episodes); a cell stops at the first stage whose per-cell ū 95 % half-width <= δ

| pilot | δ | mean episodes / cell | share of cells stopping at N = 5 / 10 / 20 | median D̂ | mean D̂ | median D_pool half-width | P(lower > 0) | P(upper < 0) |
|---|---|---|---|---|---|---|---|---|
| smoothed | 0.15 | 28.4 | 0.15 / 0.03 / 0.82 | +0.137 | +0.130 | 0.110 | 0.61 | 0.00 |
| smoothed | 0.2 | 25.9 | 0.19 / 0.12 / 0.69 | +0.153 | +0.152 | 0.114 | 0.70 | 0.01 |
| smoothed | 0.25 | 17.2 | 0.24 / 0.58 / 0.19 | +0.156 | +0.152 | 0.142 | 0.53 | 0.00 |
| pooled | 0.15 | 31.6 | 0.07 / 0.01 / 0.92 | +0.253 | +0.245 | 0.113 | 0.94 | 0.00 |
| pooled | 0.2 | 30.3 | 0.10 / 0.05 / 0.85 | +0.265 | +0.265 | 0.115 | 0.93 | 0.00 |
| pooled | 0.25 | 18.9 | 0.14 / 0.66 / 0.20 | +0.266 | +0.263 | 0.150 | 0.86 | 0.00 |
| null | 0.15 | 29.7 | 0.07 / 0.00 / 0.93 | +0.001 | +0.002 | 0.122 | 0.10 | 0.08 |
| null | 0.2 | 29.0 | 0.09 / 0.03 / 0.88 | +0.005 | +0.002 | 0.124 | 0.12 | 0.12 |
| null | 0.25 | 18.8 | 0.12 / 0.61 / 0.27 | +0.009 | +0.010 | 0.156 | 0.10 | 0.07 |

## Decision calibration under the N-landed rule: bootstrap-CI vs within-model permutation test (two-sided α = 0.05)

| pilot | N | rejection rate, CI excludes 0 | rejection rate, permutation p < 0.05 | mean D̂ | population D |
|---|---|---|---|---|---|
| null | 5 | 0.098 | 0.065 | +0.004 | +0.012 |
| null | 10 | 0.083 | 0.072 | +0.005 | +0.012 |
| smoothed | 5 | 0.220 | 0.117 | +0.110 | +0.125 |
| smoothed | 10 | 0.300 | 0.220 | +0.112 | +0.125 |
