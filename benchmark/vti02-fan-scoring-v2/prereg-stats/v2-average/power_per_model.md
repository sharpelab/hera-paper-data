# Precision of the per-model contrasts (T = 8 h)

Each cell runs to N fans, capped at 2N episodes; 400 simulations × 500 bootstraps. MDE = the difference detectable with 80 % power at two-sided 5 % ≈ 1.43 × the 95 % half-width.

| pilot | N | Δ per model: half-width (MDE), by model | model contrast within an arm: median half-width (MDE) |
|---|---|---|---|
| smoothed | 10 | fable 0.31 (0.44), opus 0.32 (0.46), fable51 0.30 (0.42), opus55 0.31 (0.44), astra 0.36 (0.51), gpt6sol 0.28 (0.39) | 0.30 (0.43) |
| smoothed | 20 | fable 0.22 (0.32), opus 0.24 (0.34), fable51 0.21 (0.30), opus55 0.22 (0.31), astra 0.27 (0.39), gpt6sol 0.20 (0.29) | 0.22 (0.32) |
| smoothed | 30 | fable 0.18 (0.26), opus 0.19 (0.27), fable51 0.17 (0.25), opus55 0.18 (0.26), astra 0.23 (0.33), gpt6sol 0.16 (0.23) | 0.18 (0.26) |
| pooled | 10 | fable 0.31 (0.44), opus 0.31 (0.44), fable51 0.31 (0.44), opus55 0.31 (0.44), astra 0.31 (0.44), gpt6sol 0.31 (0.44) | 0.31 (0.44) |
| pooled | 20 | fable 0.22 (0.32), opus 0.22 (0.32), fable51 0.22 (0.32), opus55 0.22 (0.32), astra 0.22 (0.32), gpt6sol 0.22 (0.32) | 0.22 (0.32) |
| pooled | 30 | fable 0.18 (0.26), opus 0.18 (0.26), fable51 0.18 (0.26), opus55 0.18 (0.26), astra 0.18 (0.26), gpt6sol 0.18 (0.26) | 0.18 (0.26) |

The per-model half-width is about twice the pooled Δ's (power_budget.md), as four models average down the pooled one. A per-model Δ is also noisier where a cell is near 0.5 than where it is near 0 or 1.
