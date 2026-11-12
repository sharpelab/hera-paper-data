# Dev-set dominance statistics (box grader at its frozen parameters; exploratory)

## Inventory (observed model)

| model | arm | cut | fan | probe | b0 | none | excluded | ungraded |
|---|---|---|---|---|---|---|---|---|
| fable | corpus | 08-22 | 1 | 0 | 0 | 0 | 1 | 0 |
| fable | corpus | 08-21 | 2 | 0 | 0 | 0 | 0 | 0 |
| fable | none | 08-22 | 0 | 1 | 0 | 0 | 0 | 0 |
| fable | none | 08-21 | 1 | 0 | 0 | 0 | 0 | 0 |
| opus | corpus | 08-22 | 1 | 0 | 0 | 0 | 0 | 0 |
| opus | corpus | 08-21 | 1 | 0 | 0 | 0 | 0 | 0 |
| opus | none | 08-22 | 1 | 0 | 0 | 0 | 0 | 0 |
| opus | none | 08-21 | 1 | 0 | 0 | 0 | 1 | 0 |
| sol | corpus | 08-22 | 2 | 0 | 0 | 0 | 0 | 0 |
| sol | none | 08-22 | 1 | 0 | 0 | 0 | 0 | 0 |
| astra | corpus | 08-22 | 0 | 5 | 0 | 1 | 0 | 0 |
| astra | corpus | 08-21 | 0 | 0 | 0 | 0 | 1 | 0 |
| astra | none | 08-22 | 2 | 0 | 1 | 0 | 2 | 0 |
| sonnet | corpus | 08-22 | 6 | 0 | 0 | 0 | 0 | 0 |
| sonnet | corpus | 08-21 | 4 | 0 | 0 | 0 | 0 | 0 |
| sonnet | corpus | other | 0 | 0 | 0 | 0 | 2 | 0 |
| sonnet | none | 08-22 | 1 | 0 | 1 | 0 | 0 | 0 |
| sonnet | none | 08-21 | 1 | 1 | 0 | 0 | 0 | 0 |
| sonnet | none | other | 0 | 0 | 0 | 0 | 2 | 0 |
| haiku | corpus | 08-22 | 4 | 0 | 0 | 0 | 0 | 0 |
| haiku | none | 08-22 | 0 | 1 | 0 | 1 | 2 | 0 |
| luna | corpus | 08-22 | 2 | 0 | 0 | 0 | 0 | 0 |
| luna | corpus | 08-21 | 0 | 0 | 0 | 1 | 0 | 0 |

## Fans

| episode | model | arm | effort | cut | src | light | split | A | quality | P(≥4) | h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| astra-none/20260923T020213-9t26k2/00 | astra | none | high | 08-22 | grader | 2.14 | 2.14 | 0.82 | 0.25 | 0.00 | 1.97 |
| astra-none/20260923T020213-9t26k2/01 | astra | none | high | 08-22 | grader | 5.05 | 4.49 | 0.82 | 0.56 | 0.69 | 1.78 |
| fable-corpus/20260923T031220-4eoepm/00 | fable | corpus | high | 08-22 | grader | 6.91 | 6.91 | 0.82 | 0.81 | 0.99 | 5.84 |
| fable51-none/20260927T030302-gwp6xo/00 | fable51 | none | high | 08-22 | grader | 4.77 | 0.00 | 0.82 | 0.28 | 0.44 | 2.79 |
| gpt6sol-corpus/20260927T022824-zzkfr1/00 | gpt-5.6-terra | corpus | high | 08-22 | grader | 5.00 | 3.22 | 0.82 | 0.48 | 0.46 | 1.97 |
| gpt6sol-none/20260927T022825-9lekya/00 | gpt-5.6-terra | none | high | 08-22 | grader | 0.05 | 0.05 | 0.82 | 0.01 | 0.00 | 1.58 |
| gpt6sol-corpus/20260927T030304-rywznx/00 | gpt6sol | corpus | high | 08-22 | grader | 6.00 | 6.00 | 0.82 | 0.70 | 0.92 | 3.66 |
| gpt6sol-none/20260927T030304-jenrdg/00 | gpt6sol | none | high | 08-22 | grader | 7.00 | 0.65 | 0.82 | 0.45 | 0.50 | 4.71 |
| fable-corpus/20260923T010641-3xn8hn/00 | haiku | corpus | medium | 08-22 | grader | 3.24 | 3.24 | 0.82 | 0.38 | 0.18 | 18.35 |
| fable-corpus/20260923T010641-3xn8hn/01 | haiku | corpus | medium | 08-22 | grader | 3.52 | 0.86 | 0.82 | 0.26 | 0.13 | 4.38 |
| fable-corpus/20260923T010641-3xn8hn/02 | haiku | corpus | medium | 08-22 | grader | 6.91 | 6.91 | 0.82 | 0.81 | 0.99 | 5.32 |
| fable-corpus/20260923T011400-r3w0gf/00 | haiku | corpus | medium | 08-22 | hand | 7.00 | 6.85 | 0.82 | 0.81 | 0.99 | 12.50 |
| sol-corpus/20260923T011408-tayua3/00 | luna | corpus | medium | 08-22 | hand | 2.64 | 2.63 | 0.82 | 0.31 | 0.00 | 3.32 |
| sol-corpus/20260923T011408-tayua3/01 | luna | corpus | medium | 08-22 | hand | 6.98 | 6.98 | 0.82 | 0.82 | 0.98 | 4.38 |
| opus-corpus/20260923T013750-rkg9dn/00 | opus | corpus | high | 08-22 | grader | 7.00 | 6.77 | 0.82 | 0.80 | 0.99 | 4.79 |
| opus-none/20260923T013750-ou2xbh/00 | opus | none | high | 08-22 | grader | 6.81 | 6.81 | 0.82 | 0.80 | 0.98 | 3.10 |
| opus55-corpus/20260927T030303-6yqqk4/00 | opus55 | corpus | high | 08-22 | grader | 6.46 | 6.46 | 0.82 | 0.76 | 0.95 | 3.09 |
| sol-corpus/20260923T005529/00 | sol | corpus | medium | 08-22 | hand | 5.00 | 5.00 | 0.82 | 0.58 | 0.77 | 2.99 |
| sol-corpus/20260923T013751-g3iq70/00 | sol | corpus | high | 08-22 | grader | 3.00 | 3.00 | 0.82 | 0.35 | 0.00 | 2.26 |
| sol-none/20260923T013751-ls25bv/00 | sol | none | high | 08-22 | grader | 3.39 | 0.00 | 0.82 | 0.20 | 0.25 | 2.39 |
| fable-corpus/20260922T192335/00 | sonnet | corpus | medium | 08-22 | grader | 7.00 | 5.71 | 0.82 | 0.74 | 0.94 | 7.89 |
| fable-corpus/20260922T192335/01 | sonnet | corpus | medium | 08-22 | grader | 7.00 | 5.98 | 0.82 | 0.76 | 0.94 | 4.53 |
| fable-corpus/20260922T200401/00 | sonnet | corpus | medium | 08-22 | grader | 7.00 | 6.02 | 0.53 | 0.49 | 0.73 | 3.57 |
| fable-corpus/20260922T200401/01 | sonnet | corpus | medium | 08-22 | grader | 6.71 | 6.71 | 0.82 | 0.78 | 0.97 | 2.72 |
| fable-corpus/20260922T232408/00 | sonnet | corpus | medium | 08-22 | grader | 7.00 | 6.37 | 0.82 | 0.78 | 0.97 | 2.71 |
| opus55-corpus/20260927T022823-lnz7ab/00 | sonnet | corpus | high | 08-22 | grader | 7.00 | 5.05 | 0.82 | 0.70 | 0.87 | 5.57 |
| opus55-none/20260927T022824-6tn4qo/00 | sonnet | none | high | 08-22 | grader | 1.64 | 1.27 | 0.61 | 0.13 | 0.00 | 4.91 |
| fable-corpus/20260922T031124/00 | fable | corpus | medium | 08-21 | grader | 1.38 | 1.38 | 0.53 | 0.10 | 0.00 | 2.43 |
| fable-corpus/20260922T163113/00 | fable | corpus | medium | 08-21 | grader | 0.79 | 0.79 | 0.53 | 0.06 | 0.00 | 1.58 |
| fable-none/20260922T032000/00 | fable | none | medium | 08-21 | grader | 1.64 | 1.64 | 0.53 | 0.12 | 0.00 | 4.40 |
| opus-corpus/20260922T032801/00 | opus | corpus | medium | 08-21 | grader | 6.46 | 6.46 | 0.53 | 0.48 | 0.52 | 2.09 |
| opus-none/20260922T162048/00 | opus | none | medium | 08-21 | grader | 3.76 | 3.76 | 0.53 | 0.28 | 0.07 | 1.89 |
| fable-corpus/20260922T021159/00 | sonnet | corpus | medium | 08-21 | grader | 0.82 | 0.82 | 0.53 | 0.06 | 0.00 | 1.23 |
| fable-corpus/20260922T155920/00 | sonnet | corpus | medium | 08-21 | grader | 0.86 | 0.86 | 0.53 | 0.06 | 0.00 | 1.13 |
| fable-corpus/20260922T182621/00 | sonnet | corpus | medium | 08-21 | grader | 0.90 | 0.90 | 0.53 | 0.07 | 0.00 | 4.85 |
| fable-corpus/20260922T182621/01 | sonnet | corpus | medium | 08-21 | grader | 0.86 | 0.86 | 0.53 | 0.06 | 0.00 | 1.26 |
| fable-none/20260922T022209/00 | sonnet | none | medium | 08-21 | grader | 1.62 | 0.00 | 0.53 | 0.06 | 0.00 | 1.36 |
| live 0821-r8 | — | — | — | live | grader | 0.86 | 0.86 | 0.53 | 0.06 | 0.00 | 1.38 |
| live 0822-r8 | — | — | — | live | grader | 6.95 | 6.95 | 0.82 | 0.81 | 0.99 | 3.77 |
| live 0823-r6 | — | — | — | live | grader | 4.44 | 0.00 | 0.53 | 0.17 | 0.21 | 0.94 |
| live 0824-r4 | — | — | — | live | grader | 4.16 | 0.00 | 0.53 | 0.16 | 0.05 | 1.19 |
| live 0825-r5 | — | — | — | live | grader | 0.00 | 0.00 | 0.99 | 0.00 | 0.00 | 1.42 |
| live 0825-r8 | — | — | — | live | grader | 6.76 | 6.76 | 1.00 | 0.97 | 1.00 | 4.80 |

## D_pool: mean over models of P(corpus ≻ none) − P(none ≻ corpus); 95 % stratified bootstrap (B 2000), within-model permutation p (10 000)

| set | score | floor | own | landed | p (floor) |
|---|---|---|---|---|---|
| matrix models, 08-22 | quality | +0.22 [+0.17, +0.33] (m=6) | +0.22 [+0.17, +0.33] (m=6) | +0.50 [+0.50, +0.50] (m=2) | 0.626 |
| matrix models, 08-22 | p4 | +0.28 [+0.17, +0.33] (m=6) | +0.22 [+0.17, +0.33] (m=6) | +0.50 [+0.50, +0.50] (m=2) | 0.618 |
| all models, 08-22 | quality | +0.44 [+0.29, +0.60] (m=6) | +0.44 [+0.29, +0.60] (m=6) | +0.39 [+0.11, +0.61] (m=3) | 0.024 |
| all models, 08-22 | p4 | +0.36 [+0.22, +0.50] (m=6) | +0.36 [+0.25, +0.46] (m=6) | +0.17 [+0.00, +0.33] (m=3) | 0.138 |
| all models, both cuts | quality | +0.33 [+0.13, +0.53] (m=6) | +0.33 [+0.15, +0.53] (m=6) | +0.21 [+0.05, +0.38] (m=4) | 0.014 |
| all models, both cuts | p4 | +0.14 [-0.05, +0.32] (m=6) | +0.31 [+0.17, +0.44] (m=6) | -0.02 [-0.30, +0.27] (m=4) | 0.427 |

## ΔHV1_pool: mean over models of [mean HV1 corpus − mean HV1 none], HV1 = Q·(1 − h/h_ref)+; floor

| set | h_ref 6 | h_ref 8 | h_ref 12 |
|---|---|---|---|
| matrix models, 08-22 | +0.001 [-0.033, +0.032] | +0.054 [+0.016, +0.089] | +0.107 [+0.066, +0.145] |
| all models, 08-22 | -0.001 [-0.040, +0.037] | +0.066 [+0.017, +0.115] | +0.140 [+0.086, +0.199] |
| all models, both cuts | +0.016 [-0.030, +0.063] | +0.052 [-0.004, +0.108] | +0.092 [+0.017, +0.169] |

## Per model (08-22 cut, floor, quality)

| model | corpus: episodes (fans) | none: episodes (fans) | D | ΔHV1 (h_ref 8) | frontier share c / n |
|---|---|---|---|---|---|
| fable | 1 (1) | 1 (0) | +1.00 | +0.218 | 1.00 / 0.00 |
| opus | 1 (1) | 1 (1) | +0.00 | -0.165 | 1.00 / 1.00 |
| sol | 2 (2) | 1 (1) | +0.50 | +0.170 | 1.00 / 0.00 |
| astra | 6 (0) | 3 (2) | -0.67 | -0.207 | 0.00 / 0.33 |
| sonnet | 6 (6) | 2 (1) | +0.83 | +0.285 | 0.33 / 0.00 |
| haiku | 4 (4) | 2 (0) | +1.00 | +0.097 | 0.75 / 0.00 |
| luna | 2 (2) | 0 (0) | +nan | +nan | nan / nan |

## Arm-pooled, ignoring model (08-22, quality): the stratification check

| models | policy | n corpus / none | arm-pooled D | D_pool | ΔHV1 h_ref 6 / 8 / 12 | frontier share c / n |
|---|---|---|---|---|---|---|
| matrix | floor | 11 / 8 | -0.25 | +0.22 | -0.074 / -0.058 / -0.043 | 0.27 / 0.25 |
| matrix | landed | 4 / 5 | +0.05 | +0.50 | -0.032 / +0.051 / +0.135 | 0.75 / 0.40 |
| all | floor | 22 / 10 | +0.22 | +0.44 | +0.005 / +0.050 / +0.105 | 0.14 / 0.20 |
| all | landed | 16 / 5 | -0.01 | +0.39 | -0.061 / -0.012 / +0.051 | 0.19 / 0.40 |

Set hypervolume grows with cloud size (corpus arm, floor, h_ref 8; mean over 2000 random subsets):

| subset size | 1 | 2 | 5 | 10 | all |
|---|---|---|---|---|---|
| set HV | 0.173 | 0.296 | 0.440 | 0.514 | 0.553 |
