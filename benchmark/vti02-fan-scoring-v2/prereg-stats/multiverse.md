# Multiverse (dev set, exploratory): 2520 universes

Axes: tones ∈ {Halder_ABAB, corpus, env_lo, env_hi, B}; light ∈ {0.75, 1.0}; lines ∈ {soft, hard m, hard k, both hard}; columns ∈ {1/2 bin, 7, 1 bin, 5, 1/2 bin, none}; score ∈ {both, split, P(call), parts averaged, parts product, step at 4, linear}; A ∈ {on, off, noise model}. Noise-model A covers 19 of 37 dev fans; the rest keep the I·√τ A. An uncapped universe normalizes by 14 as if capped at 7; ΔHV1 uses h_ref 8 h and the universe's own maximum quality when it exceeds 1.

## Over all universes

| set | policy | D_pool at the frozen grader | D_pool min / median / max | share of D_pool with its sign | arm-pooled D min / median / max | ΔHV1_pool min / median / max | share of ΔHV1 > 0 |
|---|---|---|---|---|---|---|---|
| matrix-0822 | floor | +0.22 | +0.00 / +0.22 / +0.50 | 0.99 | -0.31 / -0.12 / +0.27 | -0.057 / +0.114 / +0.214 | 0.99 |
| matrix-0822 | landed | +0.50 | -0.50 / +0.00 / +0.50 | 0.43 | -0.20 / +0.20 / +0.75 | -0.306 / +0.083 / +0.200 | 0.86 |
| all-0822 | floor | +0.44 | +0.00 / +0.36 / +0.53 | 1.00 | +0.00 / +0.27 / +0.45 | -0.025 / +0.103 / +0.172 | 0.99 |
| all-0822 | landed | +0.39 | -0.28 / +0.22 / +0.56 | 0.96 | -0.19 / +0.10 / +0.57 | -0.167 / +0.154 / +0.267 | 0.98 |
| all-both | floor | +0.33 | +0.00 / +0.28 / +0.49 | 1.00 | +0.00 / +0.17 / +0.37 | -0.011 / +0.087 / +0.178 | 0.99 |
| all-both | landed | +0.21 | -0.02 / +0.21 / +0.49 | 0.99 | -0.12 / +0.02 / +0.45 | -0.038 / +0.152 / +0.268 | 0.99 |

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
| score | P(call) | +0.22 | -0.14 | +0.137 |
| score | parts averaged | +0.22 | -0.25 | +0.053 |
| score | parts product | +0.39 | -0.12 | +0.147 |
| score | step at 4 | +0.28 | -0.01 | +0.165 |
| score | linear | +0.22 | -0.14 | +0.134 |
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
| score | P(call) | +0.36 | +0.30 | +0.123 |
| score | parts averaged | +0.44 | +0.22 | +0.081 |
| score | parts product | +0.53 | +0.31 | +0.122 |
| score | step at 4 | +0.36 | +0.39 | +0.098 |
| score | linear | +0.36 | +0.30 | +0.118 |
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
| score | P(call) | +0.41 | +0.32 | +0.111 |
| score | parts averaged | +0.32 | +0.18 | +0.066 |
| score | parts product | +0.45 | +0.33 | +0.110 |
| score | step at 4 | +0.31 | +0.25 | +0.089 |
| score | linear | +0.41 | +0.32 | +0.109 |
| A | on (frozen) | +0.33 | +0.20 | +0.052 |
| A | off | +0.33 | +0.19 | +0.076 |
| A | noise model | +0.38 | +0.25 | +0.089 |

## Main effects (all universes; mean D_pool at each level)

- matrix-0822, floor: tones: Halder_ABAB +0.30, corpus +0.26, env_lo +0.25, env_hi +0.28, B +0.23; light: 0.75 +0.28, 1.0 +0.25; lines: soft +0.25, hard m +0.28, hard k +0.24, both hard +0.30; columns: 1/2 bin, 7 +0.27, 1 bin, 5 +0.26, 1/2 bin, none +0.27; score: both +0.20, split +0.28, P(call) +0.29, parts averaged +0.19, parts product +0.31, step at 4 +0.29, linear +0.29; A: on +0.24, off +0.22, noise model +0.33
- all-0822, floor: tones: Halder_ABAB +0.43, corpus +0.37, env_lo +0.38, env_hi +0.40, B +0.36; light: 0.75 +0.40, 1.0 +0.38; lines: soft +0.39, hard m +0.42, hard k +0.37, both hard +0.38; columns: 1/2 bin, 7 +0.39, 1 bin, 5 +0.39, 1/2 bin, none +0.39; score: both +0.41, split +0.39, P(call) +0.40, parts averaged +0.40, parts product +0.42, step at 4 +0.30, linear +0.40; A: on +0.37, off +0.35, noise model +0.45

## The primary, Δ(8 h), across the grader universes (P(call) per fan; censored endings excluded)

| set | P(call) variant | Δ(8 h) at the frozen knobs | min / median / max | share with the frozen grader's sign |
|---|---|---|---|---|
| matrix-0822 | P(call) | +0.44 | +0.23 / +0.46 / +0.50 | 1.00 |
| matrix-0822 | parts averaged | +0.22 | +0.02 / +0.22 / +0.25 | 1.00 |
| matrix-0822 | parts product | +0.43 | +0.07 / +0.44 / +0.50 | 1.00 |
| matrix-0822 | step at 4 | +0.46 | -0.50 / +0.39 / +0.50 | 0.80 |
| matrix-0822 | linear | +0.42 | +0.20 / +0.45 / +0.50 | 1.00 |
| matrix-0822 | all variants | +0.44 | -0.50 / +0.41 / +0.50 | 0.96 |
| all-0822 | P(call) | +0.54 | +0.20 / +0.51 / +0.60 | 1.00 |
| all-0822 | parts averaged | +0.40 | +0.23 / +0.46 / +0.60 | 1.00 |
| all-0822 | parts product | +0.53 | +0.07 / +0.49 / +0.61 | 1.00 |
| all-0822 | step at 4 | +0.40 | -0.28 / +0.29 / +0.50 | 0.91 |
| all-0822 | linear | +0.50 | +0.19 / +0.48 / +0.56 | 1.00 |
| all-0822 | all variants | +0.54 | -0.28 / +0.46 / +0.61 | 0.98 |

One axis at a time (matrix models, 08-22), Δ(8 h):
- tones: Halder_ABAB +0.44, corpus +0.45, env_lo +0.43, env_hi +0.44, B +0.43
- light: 0.75 +0.44, 1.0 +0.44
- lines: soft +0.44, hard m +0.48, hard k +0.49, both hard +0.50
- columns: 1/2 bin, 7 +0.44, 1 bin, 5 +0.31, 1/2 bin, none +0.44
- A: on +0.44, off +0.44, noise model +0.44
- parts: P(call) +0.44, parts averaged +0.22, parts product +0.43, step at 4 +0.46, linear +0.42
