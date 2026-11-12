# Multiverse (dev set, exploratory): 1080 universes

Axes: tones ∈ {Halder_ABAB, corpus, env_lo, env_hi, B}; light ∈ {0.75, 1.0}; lines ∈ {soft, hard m, hard k, both hard}; columns ∈ {1/2 bin, 7, 1 bin, 5, 1/2 bin, none}; score ∈ {both, split, P(>=4)}; A ∈ {on, off, noise model}. Noise-model A covers 19 of 37 dev fans; the rest keep the I·√τ A. An uncapped universe normalizes by 14 as if capped at 7; ΔHV1 uses h_ref 8 h and the universe's own maximum quality when it exceeds 1.

## Over all universes

| set | policy | D_pool at the frozen grader | D_pool min / median / max | share of D_pool with its sign | arm-pooled D min / median / max | ΔHV1_pool min / median / max | share of ΔHV1 > 0 |
|---|---|---|---|---|---|---|---|
| matrix-0822 | floor | +0.22 | -0.22 / +0.22 / +0.50 | 0.90 | -0.31 / -0.14 / +0.12 | -0.091 / +0.085 / +0.168 | 0.96 |
| matrix-0822 | landed | +0.50 | -1.00 / +0.00 / +0.50 | 0.41 | -0.30 / +0.20 / +0.65 | -0.409 / +0.027 / +0.171 | 0.71 |
| all-0822 | floor | +0.44 | +0.00 / +0.36 / +0.53 | 0.99 | +0.00 / +0.27 / +0.45 | -0.011 / +0.086 / +0.149 | 0.99 |
| all-0822 | landed | +0.39 | -0.44 / +0.22 / +0.56 | 0.87 | -0.21 / +0.10 / +0.57 | -0.140 / +0.119 / +0.186 | 0.97 |
| all-both | floor | +0.33 | +0.00 / +0.27 / +0.45 | 0.99 | +0.00 / +0.18 / +0.37 | -0.005 / +0.073 / +0.169 | 0.99 |
| all-both | landed | +0.21 | -0.08 / +0.17 / +0.48 | 0.95 | -0.23 / +0.01 / +0.45 | -0.025 / +0.124 / +0.232 | 0.99 |

## One axis at a time from the frozen grader (the other five at their frozen values)


**matrix-0822, floor**

| axis | level | D_pool | arm-pooled D | ΔHV1_pool |
|---|---|---|---|---|
| tones | Halder_ABAB (frozen) | +0.22 | -0.25 | +0.054 |
| tones | corpus | +0.22 | -0.26 | +0.048 |
| tones | env_lo | +0.06 | -0.27 | +0.047 |
| tones | env_hi | +0.22 | -0.25 | +0.053 |
| tones | B | +0.06 | -0.27 | +0.047 |
| light | 0.75 (frozen) | +0.22 | -0.25 | +0.054 |
| light | 1.0 | +0.06 | -0.26 | +0.058 |
| lines | soft (frozen) | +0.22 | -0.25 | +0.054 |
| lines | hard m | +0.22 | -0.25 | +0.063 |
| lines | hard k | +0.06 | -0.27 | +0.070 |
| lines | both hard | +0.39 | -0.12 | +0.089 |
| columns | 1/2 bin, 7 (frozen) | +0.22 | -0.25 | +0.054 |
| columns | 1 bin, 5 | +0.22 | -0.26 | +0.032 |
| columns | 1/2 bin, none | +0.22 | -0.25 | +0.038 |
| score | both (frozen) | +0.22 | -0.25 | +0.054 |
| score | split | +0.22 | -0.14 | +0.110 |
| score | P(>=4) | +0.28 | -0.12 | +0.080 |
| A | on (frozen) | +0.22 | -0.25 | +0.054 |
| A | off | +0.22 | -0.25 | +0.066 |
| A | noise model | +0.22 | -0.25 | +0.055 |

**all-0822, floor**

| axis | level | D_pool | arm-pooled D | ΔHV1_pool |
|---|---|---|---|---|
| tones | Halder_ABAB (frozen) | +0.44 | +0.22 | +0.066 |
| tones | corpus | +0.44 | +0.20 | +0.064 |
| tones | env_lo | +0.28 | +0.20 | +0.063 |
| tones | env_hi | +0.44 | +0.21 | +0.064 |
| tones | B | +0.28 | +0.19 | +0.061 |
| light | 0.75 (frozen) | +0.44 | +0.22 | +0.066 |
| light | 1.0 | +0.28 | +0.22 | +0.068 |
| lines | soft (frozen) | +0.44 | +0.22 | +0.066 |
| lines | hard m | +0.44 | +0.22 | +0.069 |
| lines | hard k | +0.36 | +0.28 | +0.087 |
| lines | both hard | +0.53 | +0.31 | +0.090 |
| columns | 1/2 bin, 7 (frozen) | +0.44 | +0.22 | +0.066 |
| columns | 1 bin, 5 | +0.44 | +0.22 | +0.056 |
| columns | 1/2 bin, none | +0.44 | +0.23 | +0.073 |
| score | both (frozen) | +0.44 | +0.22 | +0.066 |
| score | split | +0.36 | +0.30 | +0.085 |
| score | P(>=4) | +0.36 | +0.29 | +0.074 |
| A | on (frozen) | +0.44 | +0.22 | +0.066 |
| A | off | +0.44 | +0.23 | +0.084 |
| A | noise model | +0.49 | +0.30 | +0.114 |

**all-both, floor**

| axis | level | D_pool | arm-pooled D | ΔHV1_pool |
|---|---|---|---|---|
| tones | Halder_ABAB (frozen) | +0.33 | +0.20 | +0.052 |
| tones | corpus | +0.32 | +0.17 | +0.053 |
| tones | env_lo | +0.28 | +0.18 | +0.051 |
| tones | env_hi | +0.33 | +0.19 | +0.050 |
| tones | B | +0.28 | +0.17 | +0.049 |
| light | 0.75 (frozen) | +0.33 | +0.20 | +0.052 |
| light | 1.0 | +0.29 | +0.19 | +0.054 |
| lines | soft (frozen) | +0.33 | +0.20 | +0.052 |
| lines | hard m | +0.33 | +0.20 | +0.056 |
| lines | hard k | +0.23 | +0.13 | +0.069 |
| lines | both hard | +0.27 | +0.15 | +0.071 |
| columns | 1/2 bin, 7 (frozen) | +0.33 | +0.20 | +0.052 |
| columns | 1 bin, 5 | +0.33 | +0.20 | +0.040 |
| columns | 1/2 bin, none | +0.33 | +0.20 | +0.052 |
| score | both (frozen) | +0.33 | +0.20 | +0.052 |
| score | split | +0.41 | +0.32 | +0.074 |
| score | P(>=4) | +0.14 | +0.12 | +0.062 |
| A | on (frozen) | +0.33 | +0.20 | +0.052 |
| A | off | +0.33 | +0.19 | +0.076 |
| A | noise model | +0.38 | +0.25 | +0.089 |

## Main effects (all universes; mean D_pool at each level)

- matrix-0822, floor: tones: Halder_ABAB +0.26, corpus +0.21, env_lo +0.19, env_hi +0.23, B +0.17; light: 0.75 +0.23, 1.0 +0.20; lines: soft +0.17, hard m +0.20, hard k +0.21, both hard +0.28; columns: 1/2 bin, 7 +0.24, 1 bin, 5 +0.15, 1/2 bin, none +0.25; score: both +0.20, split +0.28, P(>=4) +0.16; A: on +0.20, off +0.18, noise model +0.27
- all-0822, floor: tones: Halder_ABAB +0.42, corpus +0.35, env_lo +0.35, env_hi +0.39, B +0.33; light: 0.75 +0.39, 1.0 +0.35; lines: soft +0.35, hard m +0.38, hard k +0.36, both hard +0.39; columns: 1/2 bin, 7 +0.37, 1 bin, 5 +0.35, 1/2 bin, none +0.38; score: both +0.41, split +0.39, P(>=4) +0.29; A: on +0.34, off +0.33, noise model +0.43

## The primary, Δ(8 h), across the grader universes (P(≥4) per fan; censored endings excluded)

| set | Δ(8 h) at the frozen grader | min / median / max | share with its sign |
|---|---|---|---|
| matrix-0822 | +0.22 | -0.75 / +0.14 / +0.25 | 0.69 |
| all-0822 | +0.35 | -0.19 / +0.36 / +0.50 | 0.95 |

One axis at a time (matrix models, 08-22), Δ(8 h):
- tones: Halder_ABAB +0.22, corpus +0.13, env_lo +0.14, env_hi +0.21, B +0.14
- light: 0.75 +0.22, 1.0 +0.21
- lines: soft +0.22, hard m +0.22, hard k +0.22, both hard +0.23
- columns: 1/2 bin, 7 +0.22, 1 bin, 5 -0.10, 1/2 bin, none +0.22
- A: on +0.22, off +0.25, noise model +0.21
