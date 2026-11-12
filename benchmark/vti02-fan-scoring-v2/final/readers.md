# Four reads of the finished matrix — variance and instruction following

Aggregated 2026-09-30 from four independent read-only passes over the final data (two Opus 5.5, two Fable 5.1; one of each per domain), all working from `reads/BRIEF.md`. The individual notes are in `reads/`. Exploratory throughout; nothing here is a registered result. Where the two readers of a domain agree, the number is given once; where they differ, both are given with the reason.

## Variance

**Metric 1 is a pass rate, and its variance has different causes in the two arms.**
- Coin-flip cells (SD ≥ 0.45): Fable 5 corpus (55% of fans below 0.15, 45% above 0.85), Fable 5 none (65/35), Opus 5 none (35/55). Tight cells: Opus 5.5 corpus (SD 0.04), Sol none (0.10), Astra none (0.19), Fable 5.1, Sol and Astra corpus (0.21–0.22).
- In the corpus arm the spread is the 8 h budget: P(call) itself has SD 0.006–0.04 in the four Claude cells, and grid spacing plus [hours > 8] explains 100% of the metric 1 variance in Fable 5, Opus 5 and Fable 5.1 corpus. All 11 Fable 5 corpus zeros are budget zeros. Hours track n_B × ncols at Spearman +0.98.
- In the no-corpus arm the spread is the grid choice. Opus 5 none is the only cell whose spread is genuine P(call) spread (uniform-B fans at 0.02, 1/B and stitched at 0.83).
- The 8 h line sits mid-distribution for two no-corpus cells: eight Fable 5 none and six Opus 5.5 none fans have P(call) ≥ 0.5 at 7–9 h. Fable 5's metric 1 Δ is +0.19 at a 7 h budget, +0.09 at 8 h, −0.14 at 9 h; a 6 h budget drops Opus 5.5 none from 0.81 to 0.44.
- The corpus tightens span spread 3–5× for every Claude model (SD 0.30–0.46 against 1.42–1.96; Brown–Forsythe permutation p ≤ 0.013) and tightens metric 1 for Opus 5, Fable 5.1 and Opus 5.5 (Opus 5.5: 0.04 vs 0.36); it widens Fable 5's hours (SD 4.9 vs 2.0 h) and rows/F_L for Fable 5.1 and Astra.

**Claude models never repeat a design; the GPT-6 models do.**
- On an exact key over (spacing, B_min, B_max, n_B, nmin, nmax, ncols) all 160 Claude fans are distinct; Fable 5 corpus has 19 distinct windows in 20 fans. The corpus fixes their spacing and top density, not B_min, rows or columns.
- Astra corpus is a template: 13–16 of 19 fans on the density grid n = 2.48–2.84 with 11 columns, none reaching 10 T, 14 at exactly P(call) 0.658. Astra none: 20 of 20 stitched, 15 with exactly 111 columns. Sol corpus has the lowest dispersion in the matrix. Three exact repeats in all, two Astra and one Sol.
- Repetition does not predict metric variance (Spearman of distinct fraction with SD of v +0.28).

**Nothing drifted between tranche 1 and the rounds; the N = 5 per-model picture was noise.**
- Of 48 tranche 1 vs later comparisons (12 cells × 4 quantities), 2 reach p < 0.05 against 2.4 expected; one |z| > 2 among 36 cell × metric pairs. Corpus spot-check rate 10 of 30 in tranche 1 and 49 of 148 after, both 0.33; censoring is not heterogeneous by round in any cell (p ≥ 0.19).
- Redrawing tranche-1-sized subsets from the final cells 20 000 times: Fable 5's negative metric 1 Δ (−0.088) sits at the 25th percentile, with Δ ≤ 0 in 41% of draws; Opus 5.5's near-zero Δ sits at the 10th, its span and rows values at the 2nd–3rd, the least likely tranche 1 draw in the matrix but one of 18 model × metric comparisons.
- Tranche 1 alone already passed the pooled tests (p 0.0008, 0.0034, 0.0002 on metrics 1–3), and its pooled Δs were inside the N = 5 half-widths of the final ones.
- Two post-hoc round tails at nominal p ≈ 0.02 (Astra corpus deferred 8 of its last 10; Fable 5 corpus round 3 landed 5 of 5) are the tails expected from twelve cells × several splits.

**Power.**
- Pooled minimum detectable Δ at 80% power, N = 20: 0.117 (metric 1), 0.38 (span), 0.57 (rows); the observed effects are 3.6–4.2× those. The prereg's stated 0.13 at N = 20 and 0.23 at N = 5 reproduce. N = 40 shrinks the minimum by 29%, N = 80 by 50%, at about $2.4k and $4.8k against the $1.2k spent (GPT-6 notional).
- Per model, N = 40 brings every effect with |z| ≥ 2 at N = 20 to ≥ 94% power. Fable 5 on metric 1 (+0.10), Opus 5.5 and Astra on span stay undetectable at N = 80 (power 0.23, 0.45, 0.17).
- Ranking the top two corpus cells is out of reach: Opus 5.5 0.982 vs Fable 5.1 0.945 on metric 1 needs N ≈ 290 per cell; Fable 5.1 vs Fable 5 on span N ≈ 270. In the no-corpus arm Opus 5.5 vs Opus 5 on metric 1 needs N ≈ 57. At N = 20 the matrix ranks "top four against bottom two", no finer.
- Because v is bimodal (deciles of v: 84, 7, 4, 2, 3, 1, 15, 2, 10, 111; 12% mid-range, every Claude and Sol cell ≤ 2 mid fans, only Astra corpus continuous), the permutation mean test is a proportion test with an SE floor of about 0.11 per cell at N = 20. The pooled verdict cannot change with the statistic; the untested per-model Δs can. One reader notes the within-model permutation compares whole distributions, so Opus 5.5's Δ partly reflects its arms' different spreads (0.04 vs 0.36), not only their means.

**Cost and wall.** Cost CV 0.09–0.26 per cell, no heavy tail (max/median ≤ 1.62); corpus costs 1.2–1.5× none; censored episodes are cheaper than fans in the same cell (Astra corpus $2.38 vs $3.61), so Fable 5 corpus paid $12.3 per fan. Within cells cost does not predict quality (pooled rank correlation −0.02 with metric 1). Wall CV 0.11–0.34; all 300 ended `ok`, longest 20.1 min against the 30 min timeout. Doubling Claude slots from 8 to 16 changed per-cell mean wall by ≤ 3 min and wall per tool call from 18.3 to 17.0 s; concurrency and start order do not correlate with fan metrics (|r| ≤ 0.10).

## Instruction following

**The operator's request.**
- Deferrals per corpus cell: Astra 21 of 40, Fable 5 16 of 36, Fable 5.1 13 of 33, Opus 5.5 5 of 25, Opus 5 4 of 24, Sol 0 of 20; no-corpus 1 of 122 (Opus 5, a "step 4a" pre-leg) plus one Sol episode that landed nothing. Sol corpus never deferred despite reading the fan recipe in 20 of 20 episodes and computing the onset in 10.
- Of the 60 deferrals, 57 cite the recipe's censored-onset lever, often near-verbatim ("the fan recipe requires…" in Astra's final messages); 2 are explicit data-quality judgments (re-acquire run 6 at 40 nA; record the positioning ramp); 0 misreads. No agent called the request premature, and none asked the operator a question. All frame the spot check as step 0 of the fan.
- The landed markdown names the operator's request in 7 of 60 deferrals (both readers; the Opus reader's 12 of 60 also counts final chat messages). Opus 5.5 is the one model that plainly says "I haven't landed the fan yet" and why (3 of 5); Fable 5.1 never does (0 of 13).

**The brief's constraints and the state's caps held.**
- Field cap: 0 of 239 fans exceed 10 T, and `B_SESSION_CAP` is asserted in 236 of 236 fan cells. Gate limits: one design over, Fable 5.1 none/…ifyqf5/04 at n_max 3.30e12 → Vtg +1.012 V against the +1.0 V limit, caught by its own in-cell assert (a dead cell, not a breach); 67 of 238 fans sit within 5 mV of the top-gate limit. No cell touches a heater, the Si gate, a ramp rate or a validator; no blocklisted reads; no data-isolation breach.
- Reading order followed in 300 of 300 (session notes, notebooks, scratch, cards); every no-corpus episode wrote the `hera_scratch/plan.md` its brief asks for and 117 of 120 fan cells cite a plan step.
- Self-execution under the E1 grant: 259 episodes ended on `append --execute` (3 with the invalid `--follow`), 40 on `hera-watch` after a plain append, 0 used `--wait`. Sol executes in only 12 of 39 landings and says "unexecuted" outright in 8; the other models execute in ≥ 38 of 45.
- Lock-ins: all 239 fans set the sr1 sensitivity explicitly (none inherited the handoff's 2 µV), 11 changed the time constant the state had fixed, 1 left autorange on, 1 changed the drive (1 → 4 V, an Opus deferral).
- Neither brief states a time budget; 48 fans (14 corpus, 34 none, Astra none 18 of 20) state a run time over 8 h knowingly. Stated versus grader hours agree at a median ratio 0.93–1.14 per cell, apart from the hook-dwell Astra fans (see `audit.md`).

**Corpus-arm recipe adherence in the 119 fans.** Done nearly always: 1/B grid 117, B and n Nyquist checks 117 and 113, δF check 117, dynamic-range check 118, exactly one fan with a price 119 (0 offered a cheaper alternative), the `landau-fan-vti` tag 118, field endpoint stated. Skipped: notify inside the cell 0 of 119; gate parking (Astra 4 of 19, Sol 10 of 20); the structured D/n/B sweep comment (Astra 8 of 19); a 6τ dwell (Fable 5.1 8 of 20). Recipe followed against the operator: the 59 deferrals, and 12 fans (8 Fable 5, 4 Fable 5.1) that took the censored record's low edge, 0.3–0.5 T, literally as B_lo; the eight Fable 5 ones run 9.5–20.4 h and said so in their ETAs. Fable 5 cites the measured onset for B_lo in only 3 of 20 fans, Sol 2 of 20.

**What the no-corpus arm used instead.** Both arms copy the state's cell scaffolding equally (thermometry assert 118 vs 118; the run-5 calibration literal 92 vs 91). The state shows in the field grid: the spot checks' `10.0001` literal appears in 47 of 120 no-corpus fans against 2 of 119 corpus. The API doc was read in 121 of 121 and `sdh_onset` run in 105–118 of 122, so the onset tool was known; what the arm lacked was the design reasoning: F_L cited in 49 fans vs 117, a ray-Nyquist check in 2 vs 113, a forward model in 0 vs 161 episodes. Field axes: 38 fans uniform in B (Sol 13, Fable 5 9, Fable 5.1 9, Opus 5 6, Opus 5.5 1, Astra 0), at 50–250 mT steps, 5–25× coarser than the spot checks they resemble; one reader counts 56 by including 11 two-segment grids in the state's 50 mT / 10 mT style. No-corpus scales run coarser (100–1000 µV against 50–100).

**Tool use.** The stop hook: Opus 5 and Opus 5.5 stop at the first "episode complete" denial (45 of 45 each, none with a second); Fable 5 keeps going (24 episodes with ≥ 2 denials, 80 in all) and Fable 5.1 switches to Write/Edit, which the hook does not cover, editing session notes and plans after the stop in 12 episodes. Foreground `sleep` was blocked in 69 episodes (Opus 5 35 of 45; the GPT-6 runner has no such block); background waits in 190 of 219 Claude episodes, the watcher armed before the append in 189. Off-list tools, not blocked: ToolSearch 10, one Skill call and one TaskStop (Fable 5.1); ScheduleWakeup/Monitor 3, denied. The `--follow` without `--wait` error hit exactly the 3 known landings. 272 post-stop denials across 205 episodes; 25 attempted session-note writes were cut off by the stop, 5 landed via Edit/Write.

**Other.** Every fan is n_fans = 1; 2 landed more than the fan (a chained ride-up or extension plus the fan, priced in `audit.md`); 194 of 300 episodes also appended to the analysis notebook; 11 corpus episodes skipped the investigation step of the reading order.

## Where the readers disagree

- Deferrals that name the operator's request: 7 (landed markdown only) versus 12 (markdown plus final chat message). Both agree the acknowledgement rate is low and Opus 5.5 is the exception.
- Uniform-B no-corpus fans: 38 (single uniform grid, the analysis's own `spacing` parse) versus 56 (including 11 two-segment B grids and 4 Codex forms). The registered analysis's count is 38.

## What none of the four could determine

Executability of landed cells (all are static reads; the gate check is static); whether Sol's 27 unexecuted landings and the 40 watch-first endings would have executed next; the grader's own repeatability (every episode graded once); concurrency on its own (confounded with round and time of day); whether the Claude models' never-repeated designs are sampling or sensitivity to trivial differences; hidden-reasoning acknowledgement of the request.
