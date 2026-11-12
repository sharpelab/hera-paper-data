## Variance (exploratory; two independent reads, Opus 5.5 and Fable 5.1, agreeing)

**Metric 1 is a pass rate.** 195 of 239 fans score below 0.15 or above 0.85. Its spread has different causes per arm:

| Cell | SD of v | What the spread is |
|---|---|---|
| Fable 5 corpus | 0.51 | the 8 h budget: P(call) is 0.99 ± 0.01, 11 of 20 fans run 9.4–20.4 h |
| Fable 5 none | 0.48 | budget plus grid: 8 fans at P(call) ≥ 0.5 sit at 7–9 h |
| Opus 5 none | 0.46 | genuine P(call) spread: uniform-B fans at 0.02, 1/B and stitched at 0.83 |
| Fable 5.1 none | 0.37 | grid |
| Opus 5.5 none | 0.36 | budget: 10 of 20 fans at 6–8 h, so a 6 h budget drops it 0.81 → 0.44 |
| Opus 5 corpus | 0.31 | budget |
| Fable 5.1, Astra, Sol corpus | 0.22 | budget (Fable 5.1); Astra sits at 0.658 in 14 of 19 |
| Astra none | 0.20 | 13 of 20 fans over 8 h |
| Sol none | 0.11 | floor |
| Opus 5.5 corpus | 0.04 | ceiling |

In the corpus arm, grid spacing plus [hours > 8] explains 100 % of the metric 1 variance for Fable 5, Opus 5 and Fable 5.1. Hours track rows × columns at Spearman +0.98. The 8 h line sits mid-distribution for two no-corpus cells: Fable 5's per-model Δ is +0.19 at 7 h, +0.09 at 8 h, −0.14 at 9 h.

**The corpus tightens spread.** Span SD shrinks 3–5× for every Claude model (0.31–0.47 against 1.46–1.96 bins; Brown–Forsythe permutation p ≤ 0.013 each) and metric 1 tightens for Opus 5, Fable 5.1 and Opus 5.5. It widens Fable 5's hours (SD 4.9 vs 2.0 h) and rows/F_L for Fable 5.1 and Astra. One reader notes the within-model permutation compares whole distributions, so Opus 5.5's Δ (spreads 0.04 vs 0.36) partly reflects spread, not only means.

**Claude never repeats a design; GPT-6 does.** All 160 Claude fans are distinct on (spacing, B_min, B_max, rows, n_min, n_max, columns); Fable 5 corpus has 19 distinct windows in 20 fans. Astra corpus is a template (13–16 of 19 on n = 2.48–2.84 × 11 columns), Astra none 20 of 20 stitched, 15 with exactly 111 columns; Sol corpus has the lowest dispersion in the matrix. Repetition does not predict variance (Spearman +0.28).

**No drift between tranche 1 and the rounds, and the N = 5 picture was noise.** 2 of 48 tranche-versus-rounds comparisons reach p < 0.05 against 2.4 expected; corpus deferral 10 of 30 then 49 of 148, both 0.33. Drawing 5-per-cell tranches from the final cells 20 000 times, tranche 1's Fable 5 Δ sits at the 23rd percentile (Δ ≤ 0 in 41 % of draws) and Opus 5.5's at the 12th (its span and rows at the 1st). Tranche 1 alone already passed the pooled tests (p 0.0008, 0.0034, 0.0002).

**Power.** Minimum detectable pooled Δ at 80 %: N = 5 → 0.233, 20 → 0.117, 40 → 0.082, 80 → 0.058 (metric 1); 0.38 / 0.27 / 0.19 bins on span; 0.57 / 0.40 / 0.29 rows. The observed effects are 3.6–4.2× the N = 20 minimum. Per model, Fable 5 on metric 1 (+0.10) stays undetectable at N = 80; Opus 5.5 (+0.18) needs N ≈ 40. Ranking the top two corpus cells needs N ≈ 290 (Opus 5.5 0.982 vs Fable 5.1 0.945). With v this bimodal the permutation mean test is a proportion test with an SE floor of about 0.11 per cell at N = 20: the matrix ranks "top four against bottom two", no finer. N = 40 would cost about $2.4k, N = 80 about $4.8k, against $1.2k spent.

**Cost, wall, concurrency.** Cost CV 0.09–0.26 per cell, no heavy tails; uncorrelated with quality within cells (ρ −0.02). Censored episodes are cheaper than fans, so Fable 5 corpus paid $13 per fan. 8 → 16 Claude slots changed wall per tool call from 18.3 to 17.0 s and nothing in the metrics (|r| ≤ 0.04). Two post-hoc round tails at nominal p ≈ 0.02 (Astra corpus deferred 8 of its last 10; Fable 5 corpus round 3 landed 5 of 5) are what twelve cells × several splits produce by chance.

Figures 7–9 beside this note; full reads in `final/readers.md` and `final/reads/`.
