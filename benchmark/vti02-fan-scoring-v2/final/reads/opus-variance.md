# Variance reader notes (Opus 5.5)

Inputs: `final/episodes.json` (300 records), `final/analysis.json`, per-episode `episode.json` run blocks (start/end times, runner), job records `~/.local/state/hera/replay/jobs/<id>/job.json` (slot pools). No harness.log sampling was needed. All computation in python3 over those files; nothing else written.

Abbreviations: F5 = claude-fable-5, O5 = claude-opus-5, F5.1 = claude-fable-5-1, O5.5 = claude-opus-5-5, Astra = gpt-6-astra, Sol = gpt-6-sol. m1 = v = P(call)·[h ≤ 8], m2 = span, m3 = rows/F_L. "Fans" = the 20 (Astra corpus 19) graded fans per cell. Rounds: T1 = 20260929T2125*, R1 = T2345*, R2 = 20260930T0153*, R3 = T0343*, R4+ = T13–14*.

## 1. Within-cell spread (measured, fans only)

| cell | m1 mean / SD / IQR | m1 share <0.15 / >0.85 | m2 mean / SD / IQR | m3 mean / SD / IQR |
|---|---|---|---|---|
| F5 corpus | 0.445 / 0.505 / 0.995 | 0.55 / 0.45 | 4.22 / 0.43 / 0.35 | 3.47 / 0.71 / 0.03 |
| F5 none | 0.350 / 0.478 / 0.983 | 0.65 / 0.35 | 3.07 / 1.60 / 2.38 | 2.32 / 1.90 / 3.45 |
| O5 corpus | 0.893 / 0.306 / 0.013 | 0.10 / 0.90 | 4.07 / 0.42 / 0.60 | 3.94 / 0.71 / 1.13 |
| O5 none | 0.587 / 0.464 / 0.977 | 0.35 / 0.55 | 2.84 / 1.96 / 4.11 | 2.08 / 1.77 / 3.02 |
| F5.1 corpus | 0.945 / 0.222 / 0.002 | 0.05 / 0.95 | 4.31 / 0.31 / 0.05 | 3.76 / 1.41 / 1.13 |
| F5.1 none | 0.227 / 0.365 / 0.125 | 0.80 / 0.15 | 1.07 / 1.62 / 0.94 | 0.81 / 1.11 / 0.46 |
| O5.5 corpus | 0.982 / 0.036 / 0.009 | 0.00 / 0.95 | 3.99 / 0.47 / 0.48 | 3.60 / 0.80 / 0.74 |
| O5.5 none | 0.806 / 0.359 / 0.070 | 0.15 / 0.80 | 3.66 / 1.46 / 1.44 | 2.73 / 1.26 / 1.59 |
| Astra corpus | 0.542 / 0.222 / 0.101 | 0.11 / 0.00 | 1.40 / 0.50 / 0.00 | 6.22 / 3.28 / 5.06 |
| Astra none | 0.083 / 0.196 / 0.000 | 0.80 / 0.00 | 1.52 / 1.00 / 1.24 | 2.10 / 2.45 / 4.25 |
| Sol corpus | 0.853 / 0.215 / 0.094 | 0.05 / 0.90 | 2.61 / 0.42 / 0.41 | 3.43 / 0.25 / 0.04 |
| Sol none | 0.045 / 0.106 / 0.060 | 0.95 / 0.00 | 0.21 / 0.49 / 0.30 | 0.37 / 0.23 / 0.20 |

- **Coin-flip cells on m1:** F5 corpus (55/45), F5 none (65/35), O5 none (35/55). Every other cell is ≥ 80% at one extreme, except Astra corpus: 17 of 19 fans sit in the 0.15–0.85 middle, almost all at exactly 0.658. That cell is consistent, and consistently mediocre.
- **What drives the m1 flips (measured):** a within-cell OLS of v on spacing dummies plus [hours > 8] gives R² = 1.00 in F5 corpus, O5 corpus and F5.1 corpus, 0.87–0.88 in F5 none, O5 none and Sol corpus, 0.40 in F5.1 none, and 0.14 in Sol none. In the corpus cells P(call) itself is nearly constant (SD 0.006–0.040 for F5, O5, F5.1, O5.5). All 11 zeros in F5 corpus are budget zeros (P(call) ≥ 0.96, hours > 8). So in the corpus arm, m1 variance is almost entirely the 8 h cutoff. In the none arm it is the field-grid choice.
- **The cutoff sits in the bulk of two none cells:** 8 F5-none fans and 6 O5.5-none fans have P(call) ≥ 0.5 and 7 < h ≤ 9. Moving the cutoff by ±1 h moves S1(F5 none) 0.20 / 0.35 / 0.58 at 7 / 8 / 9 h. That flips F5's per-model Δ1 from +0.19 (7 h) to +0.09 (8 h) to −0.14 (9 h). O5.5's Δ1 goes +0.44 / +0.18 / +0.12. No other model changes sign across 7–9 h.
- **Does the corpus change variance (Brown–Forsythe, a permutation test on |x − median|, 5000 perms):**
  - **m2:** the corpus tightens it for 5 of 6 models. SD corpus/none: F5 0.43/1.60 (p < 0.001), O5 0.42/1.96 (p 0.002), F5.1 0.31/1.62 (p 0.013), Astra 0.50/1.00 (p 0.002), O5.5 0.47/1.46 (p 0.10). Sol 0.42/0.49 is unchanged.
  - **m3:** tighter for F5 (0.71/1.90, p < 0.001) and O5 (0.71/1.77, p 0.002). Looser for F5.1 (1.41/1.10) and Astra (3.28/2.45), both n.s.
  - **m1:** tighter for O5 (p 0.017), F5.1 (p 0.047) and O5.5 (0.04 vs 0.36, p 0.019). Unchanged for F5 (p 0.60, the cutoff cliff) and Astra. Sol is looser but its none arm sits on the floor.
  - **Hours:** the corpus widens F5 (SD 4.89 vs 1.97, p < 0.001) and narrows Astra (0.94 vs 2.74, p 0.026).
- **Astra corpus m1 spread** is mostly two hole-side-only fans (n −1.06..−0.84) that score 0 on all three metrics. Both come from round R2.

## 2. Design consistency (measured)

Design keys:
- **Exact:** the 7-tuple (spacing, B_min, B_max, n_B, nmin, nmax, ncols).
- **Window:** (spacing, B_min to 0.1 T, B_max to 0.5 T, nmin and nmax to 0.1). This is the envelope, with no point counts.
- **Coarse:** (spacing, B_min to 0.25 T, B_max to 1 T, hole side yes/no, nmin to 0.5, n_B and ncols in half-octave bins).
- **Dispersion:** the mean pairwise Euclidean distance over (B_min, B_max, ln n_B, nmin, nmax, ln ncols), each scaled by the SD pooled over all 239 fans, plus 1 when the spacing differs.

| cell | exact distinct | window distinct (modal count) | coarse distinct (modal) | mean pair dist | spacing mix |
|---|---|---|---|---|---|
| F5 corpus | 20 | 19 (2) | 19 (2) | 1.99 | invB 19, stitched 1 |
| F5 none | 20 | 15 (2) | 19 (2) | 1.91 | B 9, invB 7, stitched 4 |
| O5 corpus | 20 | 17 (2) | 18 (2) | 1.64 | invB 19, B 1 |
| O5 none | 20 | 15 (4) | 19 (2) | 2.04 | invB 9, B 6, stitched 5 |
| F5.1 corpus | 20 | 17 (2) | 17 (2) | 1.46 | invB 14, stitched 6 |
| F5.1 none | 20 | 10 (4) | 15 (3) | 1.60 | stitched 10, B 9, invB 1 |
| O5.5 corpus | 20 | 17 (3) | 16 (3) | 2.04 | invB 17, stitched 3 |
| O5.5 none | 20 | 15 (5) | 16 (3) | 1.69 | stitched 15, invB 4, B 1 |
| Astra corpus | 18 | 7 (9) | 10 (5) | 3.29* | invB 18, stitched 1 |
| Astra none | 19 | 8 (5) | 14 (3) | 2.34 | stitched 20 |
| Sol corpus | 19 | 14 (4) | 13 (6) | 1.37 | invB 19, B 1 |
| Sol none | 20 | 16 (3) | 17 (2) | 2.83 | B 13, stitched 7 |

\* Inflated by the two hole-side-only outliers. Without them Astra corpus is the tightest cell in the matrix.

- **No model repeats a fan exactly** except three pairs: Astra corpus (invB 1.02–6.5 T, 151 rows, n 2.48–2.84, 11 cols), Astra none (stitched 2–10 T, 65 rows, n −1.06–2.84, 111 cols) and Sol corpus (invB 0.8–10 T, 116 rows, n 2.13–2.84, 22 cols).
- **Astra is the stereotyped model.**
  - Corpus: 13 of 19 fans share the density grid (nmin 2.48, nmax 2.84, 11 cols), 9 of 19 share the window invB 1.0–6.5 T, and none reaches B_max = 10 T. This design lock is why its P(call) sits at 0.658 in 13 fans.
  - None: all 20 fans are stitched, all use n −1.06..2.84, and 15 of 20 have exactly 111 cols.
- **Sol corpus is the next most repeatable:** all 20 have nmax 2.84, nmin sits in 1.59–2.39, ncols SD is 7.8, and dispersion is 1.37, the lowest in the matrix.
- **Claude models never repeat the full design.** F5 corpus has 19 distinct windows in 20 fans. The corpus arm pins their spacing (invB 14–19 of 20) and nmax (2.84 in 10–17 of 20), but B_min (SD 0.10–0.29 T), n_B (SD 23–87) and ncols (SD 8–26) wander.
- **The corpus pins the design distribution for Claude models:** mean pair distance falls for O5 (2.04 → 1.64) and F5.1 (1.60 → 1.46). It does not fall for F5 (1.91 → 1.99) or O5.5 (1.69 → 2.04; B_max SD 1.94 T, only 60% at 10 T).
- **Design spread tracks m2 spread only loosely.** Astra corpus and Sol corpus have the tightest designs and the tightest m2 (IQR 0.001 and 0.41). F5 corpus has the loosest Claude design and still a tight m2 (IQR 0.35), because every invB design saturates m2 near 4.4.

## 3. Stability across tranches (measured)

**Censoring by round (corpus cells, spot checks / episodes):**
- F5: T1 2/5, R1 9/17, R2 5/9, R3 0/5
- O5: 2/5, 2/17, 0/2
- F5.1: 2/5, 7/17, 3/7, 1/3, 0/1
- O5.5: 2/5, 3/17, 0/3
- Astra: 2/5, 8/17, 3/8, 2/3, 6/7
- Sol: 0/5, 0/15

Permutation χ² of heterogeneity across rounds: every p ≥ 0.19. Fisher T1 vs later: all p ≥ 0.18, pooled corpus 10/30 vs 49/148, p = 1.0. T1 happened to give 2/5 in every corpus cell except Sol. That overstates O5 (later 2/19) and O5.5 (later 3/20), but not significantly.

**Metric means, T1 fans vs later fans per cell:** 48 permutation comparisons (12 cells × m1, m2, m3, hours); 2 have p < 0.05, where about 2.4 are expected by chance.
- O5.5 corpus m3: T1 2.48 vs later 3.79, p 0.009. It is one stitched T1 fan at 1.14.
- Sol corpus hours: 5.22 vs 3.28, p 0.04. It is the single uniform-B T1 fan at 10.7 h.
- No cell drifted.

**Per-model Δ, T1 fans (corpus 3 per model, Sol 5; none 5) vs final N = 20:**

| model | m1 T1 → final | m2 T1 → final | m3 T1 → final | D T1 → final |
|---|---|---|---|---|
| F5 | −0.088 → +0.095 | +1.79 → +1.16 | +1.28 → +1.15 | 0.00 → +0.18 |
| O5 | +0.398 → +0.306 | +1.05 → +1.23 | +1.54 → +1.86 | +0.40 → +0.23 |
| F5.1 | +0.816 → +0.718 | +3.41 → +3.24 | +2.87 → +2.95 | +0.60 → +0.39 |
| O5.5 | +0.003 → +0.176 | −0.75 → +0.33 | −0.40 → +0.87 | +0.47 → +0.52 |
| Astra | +0.481 → +0.460 | −0.42 → −0.13 | +5.12 → +4.12 | +0.40 → +0.47 |
| Sol | +0.708 → +0.808 | +2.61 → +2.40 | +3.08 → +3.06 | +0.44 → +0.61 |
| pooled | +0.386 → +0.427 | +1.28 → +1.37 | +2.25 → +2.33 | +0.38 → +0.40 |

**Is the N = 5 change noise?** Method: from each cell's 20 fans, draw the T1-sized subset (corpus 3, or 5 for Sol; none 5) without replacement, 20 000 times. The draws are finite-population, so they slightly understate independent-draw noise.
- Sampling SD of a per-model Δ1 at T1 size: F5 0.33, O5 0.24, F5.1 0.19, O5.5 0.14, Astra 0.14, Sol 0.09.
- F5's negative T1 Δ1 is at the 25th percentile; P(Δ1 ≤ 0) at that size is 0.41. Pure noise.
- O5.5's T1 Δ1 ≈ 0 is at the 10th percentile (P(Δ1 ≤ 0) 0.08). Its T1 m2 and m3 sit at the 2nd and 3rd percentiles. That is the least likely T1 draw in the matrix, but it is one of 18 model × metric comparisons.
- Pooled Δ sampling SD at T1 size: m1 0.08, m2 0.24, m3 0.42. The T1 pooled values sit at the 31st–42nd percentiles.
- **T1 alone was already decisive:** the registered-style within-model permutation on T1 fans only (10 000 perms, seed 20260929) gives pooled p = 0.0008 (m1), 0.0034 (m2) and 0.0002 (m3).

## 4. Power and sample size

Method: normal approximation with unequal variances, SE = √(s_c²/N + s_n²/N) from the observed cell SDs; MDE = (z_{α/2} + z_{0.8})·SE. Brackets give α = 0.0125 (Holm, worst rung). This is a check on the within-model permutation test, not a reproduction of it.

**Per-model MDE (80% power, α 0.05), N fans per cell = 20 / 40 / 80:**

| model | m1 obs Δ (z) | m1 MDE | m2 obs Δ (z) | m2 MDE | m3 obs Δ (z) | m3 MDE |
|---|---|---|---|---|---|---|
| F5 | +0.095 (0.6) | 0.44 / 0.31 / 0.22 | +1.16 (3.1) | 1.04 / 0.73 / 0.52 | +1.15 (2.5) | 1.27 / 0.90 / 0.64 |
| O5 | +0.306 (2.5) | 0.35 / 0.25 / 0.17 | +1.23 (2.7) | 1.26 / 0.89 / 0.63 | +1.86 (4.4) | 1.19 / 0.84 / 0.60 |
| F5.1 | +0.718 (7.5) | 0.27 / 0.19 / 0.13 | +3.24 (8.8) | 1.03 / 0.73 / 0.52 | +2.95 (7.4) | 1.12 / 0.79 / 0.56 |
| O5.5 | +0.176 (2.2) | 0.23 / 0.16 / 0.11 | +0.33 (1.0) | 0.96 / 0.68 / 0.48 | +0.87 (2.6) | 0.93 / 0.66 / 0.47 |
| Astra | +0.460 (6.9) | 0.19 / 0.13 / 0.09 | −0.13 (−0.5) | 0.70 / 0.50 / 0.35 | +4.12 (4.5) | 2.56 / 1.81 / 1.28 |
| Sol | +0.808 (15.1) | 0.15 / 0.11 / 0.08 | +2.40 (16.6) | 0.40 / 0.29 / 0.20 | +3.06 (40.8) | 0.21 / 0.15 / 0.11 |

**Pooled Δ (mean of 6):**
- m1: 0.117 / 0.083 / 0.058 [Holm 0.139 / 0.098 / 0.070]
- m2: 0.38 / 0.27 / 0.19 [0.46 / 0.32 / 0.23]
- m3: 0.57 / 0.40 / 0.29 [0.68 / 0.48 / 0.34]

The observed pooled Δs are 3.6×, 3.6× and 4.1× the N = 20 MDE, so the pooled test was heavily overpowered at N = 20.

**Bootstrap cross-check** (resample each cell to N with replacement, within-model permutation, 1000 perms, 600 sims; power at the observed Δ, α 0.05). This is plug-in power, so optimistic.

| model × metric | N = 20 | N = 40 | N = 80 |
|---|---|---|---|
| F5 m1 | 0.09 | 0.13 | 0.23 |
| O5 m1 | 0.69 | 0.94 | 1.00 |
| O5.5 m1 | 0.66 | 0.98 | 1.00 |
| O5.5 m2 | 0.10 | 0.20 | 0.45 |
| Astra m2 | 0.08 | 0.09 | 0.17 |
| F5 m3 | 0.72 | 0.94 | 1.00 |
| O5.5 m3 | 0.76 | 0.96 | 1.00 |

N = 40 lifts every per-model effect whose |z| at N = 20 is ≥ 2 to ≥ 0.94 power. The F5 m1, O5.5 m2 and Astra m2 effects are too small to find at any N considered.

**Separating the top two models** (N fans per cell for 80% power, α 0.05, normal approximation):

| arm × metric | 1st vs 2nd | δ | z at N = 20 | N per cell |
|---|---|---|---|---|
| corpus m1 | O5.5 0.982 vs F5.1 0.945 | 0.037 | 0.73 | ≈ 290 |
| corpus m2 | F5.1 4.31 vs F5 4.22 | 0.09 | 0.76 | ≈ 270 |
| none m1 | O5.5 0.806 vs O5 0.587 | 0.22 | 1.67 | ≈ 57 |
| none m2 | O5.5 3.66 vs F5 3.07 | 0.60 | 1.23 | ≈ 104 |

- m1 thresholded at 0.5 (corpus) is 20 / 19 / 18 / 19 fans for O5.5 / F5.1 / O5 / Sol: a ceiling.
- The corpus arm cannot rank its top 3–4 models on m1 or m2 at any affordable N. The none arm can rank the top two on m1 at N ≈ 60.
- m3 has a pass mark of 3, so "best" is not meaningful there. Astra's lead (6.2) is oversampling.

**Cost of more N** (episodes = N / fan rate, cost = agent + grade, GPT-6 notional):
- N = 20: 302 episodes, ≈ $1.2k (observed $1,201)
- N = 40: ≈ 604 episodes, ≈ $2.4k
- N = 80: ≈ 1,208 episodes, ≈ $4.8k

The dominant cells are F5 corpus ($7.25/episode, fan rate 0.56) and Astra corpus (fan rate 0.47).

## 5. Cost and wall variance (measured, all episodes per cell)

- **Cost CV:** 0.09–0.26; max/median ≤ 1.62; skew −0.9 to +0.9. There is no heavy tail.
  - Highest: Astra corpus (CV 0.26, max/median 1.62) and F5.1 corpus (0.20, 1.57).
  - Lowest: F5 none 0.10 and Astra none 0.09.
- **Wall CV:** 0.11–0.34 (Astra corpus 0.34, max/median 1.88; Sol none 0.23, 1.79). All 300 episodes ended `ok`. The maximum wall was 20.1 min, well inside the 30 min timeout, so there is no timeout censoring.
- **Censored episodes are cheaper** than fans in the same cell: Astra corpus $2.38 vs $3.61, F5.1 corpus $4.36 vs $5.33, F5 corpus $6.38 vs $7.17. Spot checks therefore raise $/fan more than the episode count alone suggests (F5 corpus $12.3 per fan against $7.2 per fan episode).
- **Cost does not predict quality within a cell.** Pooled within-cell rank correlation over 239 fans: cost~v −0.02, cost~span −0.01. Per cell, |ρ| ≤ 0.45 with 12 cells × 4 tests. The largest are F5.1 none cost~v +0.45 and O5 none cost~hours +0.55; both are marginal and unreplicated.
- **Across cells:** Spearman(CV of cost, SD of v) = −0.31 over 12 cells. Cost variance and quality variance are unrelated.

## 6. Other variance-domain observations

- **Concurrency was confounded with round.** Job records: T1 ran with pools claude 8, codex 4; R1–R4+ ran with claude 16, codex 4.
  - Measured mean same-runner concurrency at episode midpoint: Claude 7.7 in T1, 15.7 in R1, 13.4 in R2, 8.0 in R3. Codex was 4.0 throughout T1–R2.
  - Doubling Claude slots did not slow episodes. R1 vs T1 mean wall per Claude cell is within ±3 min, and API time is 0.89–0.97 of wall in both.
  - Within-cell rank correlation of concurrency with Claude wall is −0.22 and with cost −0.15 (n 199). With fan metrics it is |r| ≤ 0.04 (n 160). Codex: |r| ≤ 0.20 on every quantity (n 61 / 39).
  - Concurrency had no measurable effect on quality.
- **No run-order drift:** within-cell rank correlation of start time with each fan metric, pooled over 239 fans, is v −0.02, span −0.08, rows −0.04, hours −0.05, cost −0.10.
- **The sequential top-up makes later rounds cell-selective.** R2+ contain only high-censoring cells (Astra corpus reached R4+ with 6/7 spot checks). No cell's censoring rate is heterogeneous across rounds (above), so the top-up did not select a different population.
- **Heteroscedasticity inside the registered test:** O5.5 m1 has SD 0.04 (corpus) against 0.36 (none), and F5 hours 4.9 against 2.0. The within-model label permutation tests equality of distributions, not of means. A significant Δ in such a model partly reflects the dispersion difference. The dispersion difference is measured; its effect on p is inferred, not simulated.

## Could not determine

- **Grader repeatability.** Each episode was extracted once, so the grader's share of within-cell variance cannot be separated from the agent's.
- **Concurrency apart from round and time of day.** Only one T1 per cell ran at 8 slots, and API-side load was not logged, so neither can be isolated from concurrency.
- **Whether O5.5's weak T1 draw reflects anything.** It sits at the 2nd–10th percentile of subsampled Δ on m1–m3, and nothing in the logs (not sampled) was checked to explain it.
- **Exact permutation-based MDEs.** The MDE table uses a normal approximation, and the bootstrap power uses plug-in distributions. Neither simulates shifting a bounded, near-binary metric.
