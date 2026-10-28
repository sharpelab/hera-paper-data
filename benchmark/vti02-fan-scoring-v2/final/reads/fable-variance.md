# Variance read — vti02-fan-request-0822 (Fable 5.1 reader)

Source: `/data/sharpelab/hera-data/vti02-fan-scoring-v2/final/episodes.json` (300 records, 239 fans) and `analysis.json`; per-episode `episode.json` + `run.json` under `/data/sharpelab/hera-data/replay/runs/` for timing, turns and job labels. No harness.log was needed. All numbers computed with python3 stdlib. "v" = p_call·[hours ≤ 8] (metric 1's per-fan value); "SD" is population SD unless a power formula, where it is ddof=1.

## 1. Within-cell spread

Per cell, fans only (n = 20, Astra corpus 19):

| cell | v mean | SD | IQR | f<0.15 | f>0.85 | span mean | SD | IQR | rows/F_L mean | SD | IQR | hours mean | SD | f>8h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fable 5 / corpus | 0.44 | 0.49 | 0.99 | 0.55 | 0.45 | 4.22 | 0.42 | 0.35 | 3.47 | 0.70 | 0.03 | 9.84 | 4.77 | 0.55 |
| Fable 5 / none | 0.35 | 0.47 | 0.98 | 0.65 | 0.35 | 3.07 | 1.56 | 2.38 | 2.32 | 1.85 | 3.45 | 8.22 | 1.92 | 0.60 |
| Opus 5 / corpus | 0.89 | 0.30 | 0.01 | 0.10 | 0.90 | 4.07 | 0.41 | 0.60 | 3.94 | 0.70 | 1.13 | 5.22 | 1.53 | 0.10 |
| Opus 5 / none | 0.59 | 0.45 | 0.98 | 0.35 | 0.55 | 2.84 | 1.91 | 4.11 | 2.08 | 1.72 | 3.02 | 4.87 | 1.19 | 0.05 |
| Fable 5.1 / corpus | 0.94 | 0.22 | 0.00 | 0.05 | 0.95 | 4.31 | 0.30 | 0.05 | 3.76 | 1.37 | 1.13 | 5.28 | 1.26 | 0.05 |
| Fable 5.1 / none | 0.23 | 0.36 | 0.12 | 0.80 | 0.15 | 1.07 | 1.57 | 0.94 | 0.81 | 1.08 | 0.46 | 4.98 | 1.27 | 0.05 |
| Opus 5.5 / corpus | 0.98 | 0.04 | 0.01 | 0.00 | 0.95 | 3.99 | 0.46 | 0.48 | 3.60 | 0.78 | 0.74 | 3.57 | 0.91 | 0.00 |
| Opus 5.5 / none | 0.81 | 0.35 | 0.07 | 0.15 | 0.80 | 3.66 | 1.42 | 1.44 | 2.73 | 1.23 | 1.59 | 6.24 | 1.11 | 0.05 |
| Astra / corpus | 0.54 | 0.22 | 0.10 | 0.11 | 0.00 | 1.40 | 0.48 | 0.00 | 6.22 | 3.19 | 5.06 | 2.45 | 0.91 | 0.00 |
| Astra / none | 0.08 | 0.19 | 0.00 | 0.80 | 0.00 | 1.52 | 0.98 | 1.24 | 2.10 | 2.38 | 4.25 | 8.61 | 2.67 | 0.70 |
| Sol / corpus | 0.85 | 0.21 | 0.09 | 0.05 | 0.90 | 2.61 | 0.41 | 0.41 | 3.43 | 0.24 | 0.04 | 3.76 | 1.80 | 0.05 |
| Sol / none | 0.04 | 0.10 | 0.06 | 0.95 | 0.00 | 0.21 | 0.48 | 0.30 | 0.37 | 0.22 | 0.20 | 3.89 | 0.88 | 0.00 |

Findings:

- **Coin-flip cells on metric 1** (SD ≥ 0.45, IQR ≈ 1): Fable 5 corpus, Fable 5 none, Opus 5 none. **Tight**: Opus 5.5 corpus (SD 0.04), Sol none (0.10), Astra none (0.19), Sol corpus/Astra corpus/Fable 5.1 corpus (0.21–0.22). Metric 1's SD is bounded at 0.5 for a binary variable; the coin-flip cells sit at that bound.
- **Fable 5's variance in both arms is the 8 h budget, not P(call).** Raw p_call in Fable 5 corpus is 0.99 ± 0.01 (every fan supports the call); 11 of 20 fans exceed 8 h (hours 9.4–20.4) and score v = 0. Fable 5 none: raw p_call 0.75 ± 0.32, 12/20 over 8 h. Astra none: raw p_call 0.48 ± 0.30, 13/20 over 8 h (median 9.3 h). Within cell, hours tracks n_B·ncols at Spearman ρ = +0.98 (Fable 5 corpus), +0.94 (Fable 5 none), +0.89 (Astra corpus); ρ ≥ 0.61 in every cell. So the "coin flip" is a step function of a continuous design variable (grid size) sitting at the threshold, not stochastic quality.
- **Budget-sensitivity of within-cell SD** (v recomputed at 6 / 8 / 12 h / none): Fable 5 corpus 0.48 / 0.49 / 0.45 / 0.01; Fable 5 none 0.34 / 0.47 / 0.36 / 0.32; Opus 5.5 none 0.49 / 0.35 / 0.30 / 0.30 (10 of its 20 fans sit in 6–8 h, so at a 6 h budget its mean drops 0.81 → 0.44); Astra none 0.16 / 0.19 / 0.32 / 0.30. Opus 5 none is the one cell whose SD (0.45) is unmoved by the budget: its spread is genuine P(call) (9 invB/5 stitched fans at v 0.83, 6 uniform-B fans at 0.02).
- **Corpus effect on variance, per model** (SD corpus vs none): metric 1 — Fable 5 0.49 vs 0.47 (same), Opus 5 0.30 vs 0.45, Fable 5.1 0.22 vs 0.36, Opus 5.5 0.04 vs 0.35 (corpus tighter for the three), Astra 0.22 vs 0.19, Sol 0.21 vs 0.10 (corpus wider, but only because none sits at the floor). Span — corpus SD 0.30–0.48 in all six cells vs none 0.48–1.91; corpus cuts span SD by 3–5× for every Claude model, 2× for Astra. Rows/F_L — corpus tighter for Fable 5 (0.70 vs 1.85), Opus 5 (0.70 vs 1.72), Opus 5.5 (0.78 vs 1.23); wider for Fable 5.1 (1.37 vs 1.08) and Astra (3.19 vs 2.38, Astra corpus IQR 5.06 — it alternates between ~3.4 and ~10 rows/period). Caveat: with bounded metrics, SD is a function of the mean; the span and rows/F_L reductions are real (means are mid-range), the metric-1 reductions are partly ceiling effects.
- **Corpus-arm hours tails:** Fable 5 corpus p90 16.5 h, max 20.4 h; every other corpus cell p90 ≤ 6.6 h. Fable 5 corpus's 8 fans with B_min ≤ 0.5 T all exceed 8 h (mean 14.4 h, v = 0.00); its 12 fans with B_min > 0.5 T average 6.8 h, v 0.74 (3 still over 8 h).

## 2. Design consistency

Exact key = (spacing, B_min to 0.01, B_max to 0.1, n_B, nmin to 0.01, nmax to 0.01, ncols). Coarse key = (spacing, B_min to 0.1, B_max to 1, n_B to nearest 50, nmin/nmax to 0.1, ncols).

| cell | distinct exact / n | distinct coarse | spacing mix |
|---|---|---|---|
| Fable 5 / corpus | 20/20 | 20 | invB 19, stitched 1 |
| Fable 5 / none | 20/20 | 20 | B 9, invB 7, stitched 4 |
| Opus 5 / corpus | 20/20 | 19 | invB 19, B 1 |
| Opus 5 / none | 20/20 | 20 | invB 9, B 6, stitched 5 |
| Fable 5.1 / corpus | 20/20 | 20 | invB 14, stitched 6 |
| Fable 5.1 / none | 20/20 | 19 | stitched 10, B 9, invB 1 |
| Opus 5.5 / corpus | 20/20 | 19 | invB 17, stitched 3 |
| Opus 5.5 / none | 20/20 | 19 | stitched 15, invB 4, B 1 |
| Astra / corpus | 17/19 | 12 | invB 18, stitched 1 |
| Astra / none | 19/20 | 14 | stitched 20 |
| Sol / corpus | 19/20 | 19 | invB 19, B 1 |
| Sol / none | 20/20 | 20 | B 13, stitched 7 |

- **No Claude model repeats a design** at the exact key (160/160 distinct) and at most one coarse collision per cell. The GPT-6 models are the only repeaters: Astra corpus lands `invB, 1.02–6.5 T, n 2.48–2.84, 11 cols` with n_B 151 twice and 101 twice (12 coarse-distinct designs in 19: a template with the row count varied); Astra none `stitched, 2–10 T, −1.06–2.84, 111 cols, 65 rows` twice; Sol corpus `invB 0.8–10 T, 116 rows, 2.13–2.84, 22 cols` twice. Astra's template values are not in the recipe or brief (grep for 2.48 / 6.5 / 1.02 in `landau-fan.md` and `corpus.md`: no hits); they come from the session state.
- Where Claude designs differ is mostly n_B (16–19 unique values per cell), ncols (11–16 unique) and B_min (6–11 unique); B_max is 10 T in nearly every fan (2–5 unique values), nmax is 2.84 ± 0.04 everywhere.
- **Design repetition does not predict metric variance.** Spearman between the distinct-exact fraction and SD(v) over 12 cells: +0.28; vs SD(span) +0.26; vs SD(rows/F_L) −0.62 (the repeaters, Astra, have the widest rows/F_L spread; the never-repeaters span SD(v) 0.04–0.49). What does predict metric-1 variance is a coarse design bucket: grouping fans by (spacing, B_min ≤ 0.5, n_B ≥ 150) explains 100 % of v variance in Fable 5 corpus, 68 % in Fable 5 none and Opus 5 none, 58 % Fable 5.1 none, 55 % Opus 5 corpus, 88 % Sol corpus, but ≤ 20 % in Fable 5.1 corpus, Opus 5.5 corpus, Astra both, Sol none (those cells are already at a floor or ceiling).

## 3. Tranche 1 versus later rounds

Tranche 1 = job "tranche 1", stamps 20260929T2125*, 5 episodes per cell, 60 total, 50 fans. Later = tranche 2 rounds 1–9 (190 + 31 + 11 + 3 + 5×1 episodes).

| cell | T1 fans/ep | T1 spot rate | T1 v / span / rows | later fans/ep | later spot rate | later v / span / rows |
|---|---|---|---|---|---|---|
| Fable 5 / corpus | 3/5 | 0.40 | 0.33 / 4.26 / 3.40 | 17/31 | 0.45 | 0.46 / 4.22 / 3.48 |
| Fable 5 / none | 5/5 | 0 | 0.42 / 2.47 / 2.12 | 15/15 | 0 | 0.33 / 3.27 / 2.38 |
| Opus 5 / corpus | 3/5 | 0.40 | 0.99 / 3.82 / 4.08 | 17/19 | 0.11 | 0.88 / 4.12 / 3.92 |
| Opus 5 / none | 5/5 | 0 | 0.59 / 2.77 / 2.54 | 15/16 | 0.06 | 0.59 / 2.87 / 1.93 |
| Fable 5.1 / corpus | 3/5 | 0.40 | 1.00 / 4.44 / 3.32 | 17/28 | 0.39 | 0.94 / 4.29 / 3.83 |
| Fable 5.1 / none | 5/5 | 0 | 0.18 / 1.03 / 0.45 | 15/15 | 0 | 0.24 / 1.09 / 0.92 |
| Opus 5.5 / corpus | 3/5 | 0.40 | 0.98 / 3.63 / 2.48 | 17/20 | 0.15 | 0.98 / 4.05 / 3.79 |
| Opus 5.5 / none | 5/5 | 0 | 0.98 / 4.38 / 2.88 | 15/15 | 0 | 0.75 / 3.43 / 2.67 |
| Astra / corpus | 3/5 | 0.40 | 0.53 / 1.54 / 8.58 | 16/35 | 0.54 | 0.55 / 1.37 / 5.78 |
| Astra / none | 5/5 | 0 | 0.04 / 1.96 / 3.46 | 15/15 | 0 | 0.10 / 1.38 / 1.65 |
| Sol / corpus | 5/5 | 0 | 0.73 / 2.69 / 3.42 | 15/15 | 0 | 0.89 / 2.58 / 3.43 |
| Sol / none | 5/5 | 0 | 0.02 / 0.08 / 0.34 | 15/16 | 0.06 | 0.05 / 0.25 / 0.38 |

- **Pooled Δ from T1 alone vs the final:** metric 1 +0.386 vs +0.427; span +1.28 vs +1.37; rows/F_L +2.25 vs +2.33. T1 already had the sign and roughly the size of all three, off by 0.04 / 0.09 / 0.09 — within the N = 5 half-widths (0.16 / 0.54 / 0.80 from the observed SDs).
- **Per-model Δ from T1 was wrong in sign or size for two models:** Fable 5 metric 1 T1 Δ −0.09 (final +0.10); Opus 5.5 metric 1 T1 Δ 0.00 (final +0.18), span −0.75 (final +0.32), rows/F_L −0.40 (final +0.87). Metric 4 (dominance) per model: Fable 5 T1 D 0.00 → final +0.18; Fable 5.1 +0.60 → +0.39; Sol +0.44 → +0.61. With 3 corpus fans per cell in T1 the per-model numbers are anecdotes.
- **Consistent with sampling noise:** z = (mean_T1 − mean_later)/SE using each cell's own SD; over 12 cells, mean |z| = 0.53 (v), 0.73 (span), 0.75 (rows/F_L); one |z| > 2 out of 36 (Opus 5.5 corpus rows/F_L, z = −2.63, n = 3 vs 17), against ~1.8 expected under the null. No tranche drift.
- **Spot-check rate T1 vs later:** corpus cells 10/30 = 0.33 vs 49/148 = 0.33. T1 had exactly 2/5 spot checks in each of the five deferring cells; the later per-cell rates spread 0.11–0.54, so the T1 uniformity was coincidence (per-cell rates 0.17–0.53 give a joint probability ~0.001 for that exact pattern, but any specific 5-tuple is that unlikely).

## 4. Power

Method: normal approximation, Δ80 = (z_0.975 + z_0.80) · SE = 2.80 · SE, with sample SDs (ddof=1). Per-model two-sample SE = sqrt((SD_c² + SD_n²)/N). Pooled Δ (mean over 6 per-model Δ) SE = sqrt(Σ_m (SD_c² + SD_n²)/N)/6. Checked against a 4000-draw within-cell bootstrap of the pooled Δ at the observed N.

**Pooled Δ detectable at 80 % power:**

| metric | N = 5 | N = 20 | N = 40 | N = 80 | bootstrap Δ80 at observed N | observed Δ | bootstrap 95 % CI |
|---|---|---|---|---|---|---|---|
| P(call) 8 h | 0.233 | 0.117 | 0.083 | 0.058 | 0.112 | +0.427 | [0.35, 0.50] |
| span | 0.77 | 0.38 | 0.27 | 0.19 | 0.37 | +1.37 | [1.11, 1.63] |
| rows/F_L | 1.14 | 0.57 | 0.40 | 0.29 | 0.55 | +2.33 | [1.95, 2.71] |

The prereg's development-set numbers (N = 20 → Δ ≥ 0.13, half-width 0.09; N = 5 → 0.23) match the production SDs: 0.117 / 0.082 / 0.233. The bootstrap agrees with the normal approximation to 5 %. All three observed pooled effects are 3.6–4.2× their Δ80.

**Per-model Δ detectable on metric 1** (N per cell = 20 / 40 / 80): Fable 5 0.44 / 0.31 / 0.22 (observed +0.10 — not detectable per model at any listed N); Opus 5 0.35 / 0.25 / 0.17 (observed +0.31, marginal at N = 20); Fable 5.1 0.27 / 0.19 / 0.13; Opus 5.5 0.23 / 0.16 / 0.11 (observed +0.18, needs N ≈ 40); Astra 0.19 / 0.13 / 0.09; Sol 0.15 / 0.11 / 0.08. Span: Δ80 at N = 20 is 0.96–1.26 for the four Claude models (none-arm SD 1.5–2.0 dominates), so Opus 5.5's +0.32 and Astra's −0.13 are per-model nulls; Fable 5's +1.16 and Opus 5's +1.23 are at the threshold. Rows/F_L: Δ80 at N = 20 0.93–1.27 for Claude, 2.56 for Astra (SD 3.28), 0.21 for Sol; Opus 5.5's +0.87 is under its threshold.

**Separating the two best models** (corpus arm, two-sample, 80 % power): metric 1, Opus 5.5 0.98 (SD 0.04) vs Fable 5.1 0.94 (SD 0.22), Δ 0.037 → N ≈ 293 per cell. Span, Fable 5.1 4.31 vs Fable 5 4.22, Δ 0.09 → N ≈ 274. Rows/F_L, Astra 6.22 (SD 3.28) vs Opus 5 3.94, Δ 2.28 → N ≈ 17 (already separated, but Astra's rows/F_L is a bimodal 3.4-or-10 mixture, so this is a mean of two designs). The two largest per-model corpus effects on metric 1, Sol +0.81 vs Fable 5.1 +0.72, need N ≈ 232 per cell to separate. The benchmark at N = 20 ranks models within the corpus arm only at the level of "top four (0.85–0.98) vs bottom two (0.44, 0.54)".

## 5. Cost and wall variance

Per cell, all episodes (cost in USD, wall in min; CV = SD/mean; tail = p90/median):

| cell | n | cost mean | CV | p90/med | max | wall mean | CV | p90/med | max |
|---|---|---|---|---|---|---|---|---|---|
| Fable 5 / corpus | 36 | 6.82 | 0.15 | 1.24 | 8.67 | 12.5 | 0.13 | 1.17 | 16.1 |
| Fable 5 / none | 20 | 5.14 | 0.10 | 1.06 | 5.93 | 9.5 | 0.11 | 1.11 | 11.3 |
| Opus 5 / corpus | 24 | 4.89 | 0.18 | 1.22 | 6.72 | 15.2 | 0.16 | 1.24 | 20.1 |
| Opus 5 / none | 21 | 3.27 | 0.11 | 1.10 | 4.28 | 11.4 | 0.13 | 1.19 | 15.2 |
| Fable 5.1 / corpus | 33 | 4.95 | 0.20 | 1.32 | 7.67 | 11.2 | 0.18 | 1.28 | 15.8 |
| Fable 5.1 / none | 20 | 4.08 | 0.14 | 1.15 | 5.46 | 9.8 | 0.15 | 1.15 | 12.8 |
| Opus 5.5 / corpus | 25 | 2.54 | 0.16 | 1.27 | 3.35 | 9.9 | 0.15 | 1.24 | 12.5 |
| Opus 5.5 / none | 20 | 2.01 | 0.14 | 1.15 | 2.79 | 8.2 | 0.15 | 1.14 | 11.7 |
| Astra / corpus | 40 | 2.96 | 0.26 | 1.35 | 4.63 | 6.0 | 0.34 | 1.37 | 11.6 |
| Astra / none | 20 | 2.18 | 0.09 | 1.11 | 2.59 | 5.8 | 0.11 | 1.11 | 7.1 |
| Sol / corpus | 20 | 0.94 | 0.14 | 1.09 | 1.15 | 7.8 | 0.13 | 1.11 | 11.0 |
| Sol / none | 21 | 0.69 | 0.17 | 1.15 | 0.87 | 7.2 | 0.22 | 1.20 | 12.6 |

- Cost is tight everywhere: CV 0.09–0.20 in 11 of 12 cells, no heavy tails (p90/median ≤ 1.35, max ≤ 1.6× mean). The one CV of 0.26 (Astra corpus) is the fan/spot-check mixture: fan episodes $3.61, spot-check episodes $2.38, wall 7.9 vs 4.3 min; within-ending cost SD 0.44 vs raw 0.76. For the Claude corpus cells the spot-check episodes cost about the same as fans (Fable 5 $6.38 vs $7.17, Opus 5 $4.94 vs $4.88, Fable 5.1 $4.36 vs $5.33, Opus 5.5 $2.36 vs $2.58); within-ending SD is 0.86–0.92 of raw. Tool calls per episode: mean 22–57, CV 0.07–0.20.
- Corpus costs 1.2–1.5× none in every model (Fable 5 1.33×, Opus 5 1.50×, Fable 5.1 1.21×, Opus 5.5 1.26×, Astra 1.36×, Sol 1.36×) and adds 1–4 min of wall.
- **Cost variance does not track quality variance.** Across the 12 cells, Spearman(cost CV, SD v) = −0.32, (cost CV, SD span) = −0.75, (cost CV, SD rows/F_L) = −0.71: the cells that vary most in what they land vary least in what they spend. Within cells, Spearman(cost, v) among fans ranges −0.25 to +0.39 (median −0.07); the strongest is Fable 5.1 none at +0.39 (its 4 good fans were the more expensive ones), and Fable 5 corpus's is −0.21 (more spend → bigger grid → over budget). Spending more agent money buys nothing measurable in fan quality at this N.

## 6. Other variance-domain items

- **Concurrency.** Measured from episode start/end overlap (no slot count is recorded in run.json; `parallel` is null). Tranche 1 ran 8 Claude slots (max 9 concurrent) and 4 Codex; tranche 2 rounds 1–2 ran 16 Claude (max 17) and 4 Codex; round 3 was 8 Claude, 3 Codex; rounds 4–9 were 1–2 episodes at a time. Within Claude cells, 8-slot vs 16-slot episodes: wall 12.4 vs 12.7 min (Fable 5 corpus), 17.7 vs 14.5 (Opus 5 corpus), 12.0 vs 10.7 (Fable 5.1 corpus), 11.1 vs 9.6 (Opus 5.5 corpus); wall per tool call 18.3 s (8 slots, n 55) vs 17.0 s (16 slots, n 137). Sixteen slots did not slow the agents. Metric means at 8 vs 16 slots: v differs by ≤ 0.09 in all eight Claude cells except Opus 5.5 none (0.98 vs 0.75, n 5 vs 15: the T1 five were all good). Cost differs ≤ $1.0 (Fable 5.1 corpus 5.55 vs 4.57, cheaper at 16, driven by ending mix). No concurrency effect detectable.
- **Censoring by round** (corpus cells; spot / episodes): Fable 5 — T1 2/5, r1 9/17, r2 5/9, r3 0/5. Opus 5 — 2/5, 2/17, 0/2. Fable 5.1 — 2/5, 7/17, 3/7, 1/3, 0/1. Opus 5.5 — 2/5, 3/17, 0/3. Astra — 2/5, 8/17, 3/8, 2/3, 1/2, then five singleton rounds 5/5 spot. Sol — 0/5, 0/15. Two round clusters reach nominal significance if tested alone: Astra corpus rounds 3–9 8/10 spot vs 13/30 earlier (binomial p = 0.021), Fable 5 corpus round 3 0/5 vs 16/31 earlier (p = 0.027). Both were picked post hoc out of ~12 cells × several splits and are the two tails one expects; the Astra tail cost the cell its 20th fan (capped at 40 episodes, 19 fans). Not evidence of drift, but note that Astra's late episodes ran solo at 13:32–14:30 the next day, so a time-of-day or API-state effect cannot be separated from chance.
- **Bimodality and the test statistic.** Pooled over 239 fans, v by decile: [84, 7, 4, 2, 3, 1, 15, 2, 10, 111]; 38 % below 0.15, 50 % above 0.85, 12 % in between. Every Claude cell and both Sol cells have 0–2 mid-range fans of 20; the only continuous cell is Astra corpus (17/19 mid-range, v 0.54 ± 0.22 around the two-column P = 0.5 step). Raw p_call is also mostly binary (20 % mid-range) and the budget makes it more so. Implications: (a) the within-model mean-difference permutation is effectively a difference in proportions, so it is valid but its power is that of a binomial test — the per-model SE floor is sqrt(p(1−p)/N), 0.11 at N = 20 when p = 0.5; (b) a bootstrap/normal CI on a cell mean is fine at N = 20 but a Wilson interval on P(v > 0.5) is the honest per-cell summary: Fable 5 corpus 9/20 [0.26, 0.66], Fable 5 none 7/20 [0.18, 0.57], Opus 5 corpus 18/20 [0.70, 0.97], Opus 5 none 12/20 [0.39, 0.78], Fable 5.1 corpus 19/20 [0.76, 0.99], Fable 5.1 none 4/20 [0.08, 0.42], Opus 5.5 corpus 20/20 [0.84, 1.00], Opus 5.5 none 16/20 [0.58, 0.92], Astra corpus 14/19 [0.51, 0.88], Astra none 1/20 [0.01, 0.24], Sol corpus 19/20 [0.76, 0.99], Sol none 0/20 [0.00, 0.16]; (c) span (28 zeros, 89 of 239 in the top decile) and rows/F_L (73 in the bottom decile, 90 in the fourth) are also lumpy, so their SDs overstate what a rank test would see, but the pooled Δs are so large relative to the bootstrap CIs that the choice of statistic cannot change the verdict. The per-model Δs, which the analysis reports but does not test, are where the statistic matters: a rank or proportion test on Opus 5.5's metric-1 Δ (+0.18, 20/20 vs 16/20) gives a different picture from the mean difference against an SD of 0.36.
- **Metric 4 by tranche:** D per model from T1 fans only vs all: Fable 5 0.00 → 0.18, Opus 5 0.40 → 0.23, Fable 5.1 0.60 → 0.39, Opus 5.5 0.47 → 0.52, Astra 0.40 → 0.47, Sol 0.44 → 0.61; pooled 0.39 → 0.40.

## What I could not determine

- The configured slot counts: `run.json` has `parallel: null` and no job file is under `/data/sharpelab/hera-data/replay/`; the 8/16/4 figures are measured overlap, not the launcher's setting.
- Whether the Astra late-round spot-check cluster (8/10, solo runs the next afternoon) is chance, time-of-day, or API state — no per-episode API latency or error field distinguishes them, and I did not open their harness.logs.
- Whether the design-key non-repetition of Claude models reflects genuine sampling or deterministic dependence on tiny prompt/timing differences — the faked clock is identical per cell, so nothing in episodes.json separates the two.
- Any within-cell autocorrelation between episodes running concurrently (shared API load, shared host); episode indices within a run dir show no ordering pattern in T1 spot checks (00–04 spot positions differ per cell), but I did not test beyond that.
- Grade-cost variance (grade_cost field) was not analysed; it is a grader property, outside the agent-variance question.
