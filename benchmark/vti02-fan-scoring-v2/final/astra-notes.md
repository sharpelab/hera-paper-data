# Exploratory physicist-analyst notes — 2026-09-30

Read-only review of the completed matrix; only this file was written. These are exploratory observations, not additional registered tests. The registered results remain unchanged.

Sources: campaign `prereg.md` §§3–9; final `analysis.md`, `analysis.json`, `episodes.json`; `hera/docs/fan-design-grader.md`; scorer code; saved fan extractions; five targeted saved fan cells. No web search or agent transcripts. All 239 fan records agree exactly between the two JSON files on hours, P(call), span and rows/F_L. P(call) below means the modeled design score, not an observed frequency of correct stacking calls.

## 1. A concrete extraction/scoring mismatch: interruptible settling

**Observed:** five Astra fans specify `fast_delay=0` but implement a 3-second sleep in the registered before-point hook. Their extraction notes explicitly document this. Saved `cell_fan.py` files confirm four; `cell_landau_fan.py` confirms the remaining none-arm episode. The sweep implementation calls the hook after setting the axes and before measuring. `box.acquisition()` uses only `fast_delay_s`; the time model also omits the hook. Thus these fans receive both an unwarranted acquisition penalty and underestimated hours.

The following is an **in-memory sensitivity**, not a correction to the final files. Set effective fast delay to 3 seconds, recompute P(call) with the existing `box.score`, and add `3 × all field rows × density columns / 3600` to saved hours (including B=0 rows). Other overheads remain unchanged.

| Episode suffix (all `vti02-fan-request-0822-`) | Saved h → effective-dwell h | Saved P → effective-dwell P |
|---|---:|---:|
| astra-corpus/20260929T212521-qy46wv/03 | 1.393 → 3.377 | .262 → .381 |
| astra-corpus/20260929T234511-d9dmed/15 | .983 → 2.019 | .456 → .658 |
| astra-corpus/20260930T015331-xmv9jb/04 | .831 → 1.456 | 0 → 0 |
| astra-none/20260929T234512-7x4jav/03 | 1.924 → 10.580 | 0 → 0 |
| astra-none/20260929T234512-7x4jav/09 | 2.075 → 10.955 | .750 → .918 |

Astra's mean 8-hour scores become .559 corpus and .045 none; its gap becomes .514 instead of .460. Keeping all other fans fixed, the six-model mean gap becomes **+.436 instead of +.427**. No permutation test was rerun. The direction is reassuring, but Pareto comparisons involving these fans need separate treatment: underestimated time and underestimated quality pull in different directions. This warrants a prospective extraction field for effective settling, including hooks, rather than assuming API argument names describe actual acquisition.

## 2. Stable design families, few literal repeats

Computed medians over fans within each cell, using parsed axes from `episodes.json`. Density endpoints are actual-frame values in 10^12 cm^-2; endpoint medians need not describe a single episode. P is unbudgeted.

| Corpus model | Median density interval | Rows × columns (separate medians) | Hours | P | Rows/F_L |
|---|---|---:|---:|---:|---:|
| Fable 5 | .98–2.84 | 158.5 × 81 | 9.48 | .997 | 3.40 |
| Fable 5.1 | .89–2.84 | 144 × 61 | 4.88 | .997 | 3.45 |
| Opus 5 | 1.38–2.84 | 138.5 × 48.5 | 4.80 | .996 | 3.44 |
| Opus 5.5 | 1.57–2.85 | 103 × 35 | 3.36 | .995 | 3.43 |
| Astra | 2.48–2.84 | 151 × 11 | 2.48 | .658 | 6.17 |
| Sol | 2.13–2.84 | 113 × 22.5 | 3.26 | .901 | 3.41 |

**Interpretation:** most corpus models target roughly the same field-sampling margin, about 3.4 rows/period, but choose substantially different density coverage and acquisition duration. Fable 5.1 and Opus 5.5 achieve nearly the same median P as Fable 5 at roughly half or one-third its median hours. These are between-model descriptions, not isolated causal effects of a particular setting.

Astra is qualitatively different: **16/19 fans use 2.48–2.84**, one uses 2.39–2.84, and **two are hole-only**, −1.06 to −.84. Thus “corpus fans are electron-only” has two exceptions, both scoring zero. Astra's field oversampling does not buy density leverage: mean span is 1.40 bins versus 1.52 without corpus, despite its +4.12 rows/period arm gap. Fourteen corpus fans have exactly P=.657598243; **all 19 score zero under the registered step-at-four-points curve**. The pooled sensitivity conceals this model-specific failure to reach four detected independent columns.

**Discrete metric behavior:** for astra-corpus/20260929T212521-qy46wv/01, I held the extracted field grid, density endpoints and acquisition settings fixed and varied only the number of uniformly spaced density columns. Existing scorer output: 10 → P=.381334; 11 → .657598; 21 and 41 → .657598. The half-bin independence selection admits a different number of separated points. This is a real property of the metric, not evidence that one extra physical trace nearly doubles experimental information. It makes narrow fans sensitive to grid alignment.

**Duplicates:** reconstructed full B and density arrays with `grade.field_axis/columns`, rounded B and density-in-10^12 units to nine decimals, and compared within cells. All eight Claude cells and Sol-none have 20 distinct axes. Astra-corpus has 18/19 distinct axes, Astra-none 19/20, Sol-corpus 19/20. Adding D, both delays, named lock-in τ/sensitivity, drive, resistor and extracted gate-current settings leaves one repeated scored design: astra-none/20260929T212522-w72phb/00 and /20260929T234512-7x4jav/04. Different code or safeguards remain possible; these were not transcript-identity comparisons. Stable families are much more prominent than literal duplication.

## 3. Acquisition signatures the geometry summary misses

Every fan extracts to **10 nA**, so none tests whether changing excitation improves the tradeoff. Signal-channel τ=.3 s in 117/119 corpus fans and 111/120 none fans; the rest use .1 s except one none fan at .05 s. These are overwhelmingly inherited acquisition conditions.

Corpus delay choices remain model-specific: Fable 5 uses 1.8 s in 15/20 fans; Fable 5.1 uses 1.2 s in 9/20; Opus 5 uses 1.8 s in 12/20; Opus 5.5 uses 1.8 or 2.1 s in 15/20. Astra uses 3 s effectively in all 19, counting the three hooks. Longer delays beyond sufficient settling cost time but earn no further acquisition factor in this scorer.

Signal sensitivity is also structured: Opus 5.5 and Sol corpus each use 50 µV in 18/20 fans; Astra-none uses 100 µV in 20/20; Sol-none uses 500 µV or 1 mV in 7/20. Recomputed `box.acquisition(..., 'sr1')['quantized']` flags **0/119 corpus versus 12/120 none**, including six Sol-none fans. Quantization is not a score multiplier. The final analysis `flags` field does not expose these acquisition flags; an empty table flag is not a clean acquisition bill of health.

Inference: the present metrics can miss poor digitization while rewarding extra geometric sampling. Conversely, the universal 10 nA choice puts essentially the whole matrix in the scorer's disclosed regime of optimistic independent-column failures.

## 4. Hours buy quality unevenly; the metrics are not interchangeable

Computed Spearman correlation of saved hours with unbudgeted P, using all fans and average ranks for ties. No significance tests; hook mismatches above are retained here to describe the registered dataset.

| Model | Corpus rho | None rho |
|---|---:|---:|
| Fable 5 | .415 | −.230 |
| Fable 5.1 | .133 | .701 |
| Opus 5 | .134 | .419 |
| Opus 5.5 | .519 | −.121 |
| Astra | .702 | .575 |
| Sol | .238 | .487 |

Pooled corpus rho=.654 overstates the consistency of the within-model relationship. P already exceeds .99 in 64/119 corpus fans. Pooled corpus means by hours (0,4], (4,6], (6,8], >8 are .802, .990, .997, .962 (N=55,42,7,15). These are associations across different designs, not evidence that extending a fixed fan improves it.

**Rows/F_L is neither necessary nor sufficient for high P:** 8 corpus and 18 none fans have rows/F_L<3 yet P≥.9; 3 corpus and 4 none fans have rows/F_L≥3 yet P<.5. Counted directly from saved fan scores. The row metric is the worst interval at the highest density; P can use better-sampled intervals and lower-density columns. Conversely, increasing field rows cannot repair a narrow density window or missing electron-side coverage. Treat these disagreements as different design questions, not contradictions.

Astra's unbudgeted arm means are .542 versus .478, a gap of only .065; the registered .460 is mainly a time-budget distinction. Opus 5.5 has median hours 3.36 versus 6.34 and median P .995 versus .989: its benefit includes reliable economy even when typical unbudgeted quality looks similar.

**Pareto effect size:** enumerate every corpus×none fan pair within each model, count strict dominance, then average the six model proportions. Corpus dominates **44.66%**, none **4.73%**, leaving **50.61%** incomparable or tied. The reported +.399 is the difference of the first two, not “corpus dominates 40%” or “dominates most pairs.”

## 5. What the censoring sensitivity and preregistration do not establish

Scoring censored episodes zero changes the estimand from quality conditional on producing a fan to yield per attempted episode. Its +.232 pooled gap is valuable, but the per-model gaps include **Fable 5 −.103 and Opus 5.5 −.020**. Thus aggregate robustness does not establish superior immediate task completion for every model.

This sensitivity assigns no future value or time cost to the spot checks. It cannot determine whether a check was scientifically justified, whether it would improve a subsequent fan, or whether corpus agents would eventually make better calls. It also does not test session-level correctness, correlated column failures, tone-model error, hook timing, or alternate scientific evidence from the hole side. Fan-count stopping gives arm-dependent numbers of attempts; these remain repeated draws at one frozen state, not 300 independent devices or full campaigns.

Three graded fans carry “extraction reads a fan; the harness saw no sweep cell appended”: fable-none/20260929T234510-ktxxq0/11, opus-corpus/20260929T234507-4ky568/08, opus-none/20260929T234508-4kxt1o/09. Extraction notes describe append-in-flight artifacts; I did not independently resolve landing status. As a bounded check, assigning these three zero 8-hour credit while retaining fan denominators gives pooled Δ=+.424 rather than +.427. This does not adjudicate the preregistered ending.

The four results share field/density information and are not four independent validations. Their identical raw p=.00009999 is the resolution floor of 10,000 permutations with the +1 correction, not a measurement of their relative evidential strength. Metric selection on development fans is disclosed; production significance addresses the frozen scoring system, not external calibration of P(call).

Finally, the preregistration calls the gap a lower bound on the live gap because both arms inherit corpus-prompted spot checks. That is an interpretation requiring a monotonicity assumption, not a mathematical bound: removing those data could change either arm's strategy in either direction.

## 6. Most useful next experiment

1. Fix the prospective measurement contract: extract effective settling including hooks; separately record append requested, cell landed, and executable cell. Preserve this completed analysis and report any audit sensitivity alongside it.
2. Continue every episode through the next diagnostic and fan under one total remaining-rig-time budget. Use a fixed attempt count, retain deferrals as outcomes, and score actual subsequent decisions rather than treating every diagnostic as either free or worthless.
3. Test held-out devices/frontiers with blinded stacking truth and measured spectra. Include density-calibration uncertainty, correlated failures and noise-session variation; keep scorer and thresholds frozen before those data.
4. Compare a small preregistered design set that separates density leverage from field oversampling: Astra-like narrow/dense, Opus-5.5-like wider/sparser, and a matched acquisition comparison if the device permits it. Evaluate recovered tones and stacking evidence, not only the present scalar P. Include a grid-alignment sensitivity around the half-bin threshold.

## 7. Expanded extraction audit

### Scope and limits

Inspected all 239 fan extractions and the appended measurement code for the 236 fans that have it. Parsed that code with Python AST; did not execute measurement cells. A restricted numerical evaluator reconstructed 222 field arrays and 211 density arrays from constants, arithmetic and whitelisted NumPy operations. It checked 473 resolved sweep-delay arguments against the extraction without a mismatch; one argument remained unresolved automatically. Registered local hooks and direct instrument-setting calls were screened across all 236 cells. Targeted reads resolved the consequential flags below. This is a broad screen, not certification of all runtime branches, inherited state, or executability.

The hook-delay problem in §1 is specifically a **contract mismatch**: the extraction prompt asks for the delay passed to the sweep call, so those extractions obey it; the scorer then treats that argument as effective settling and acquisition time. By contrast, the prompt explicitly requires full `B_values` for nonuniform grids, making the following axis approximations extraction errors.

### Six confirmed field-axis errors

Five extractions replace nonuniform grids with endpoint/count/uniform-spacing representations. A sixth omits a B=0 anchor row. Reconstructed their actual field arrays directly from the landed code and passed those arrays as `B_values` to the unchanged scorer, in memory. All other extraction fields were held fixed.

Episode suffixes below have prefix `vti02-fan-request-0822-`.

| Episode suffix | What was lost | P(call), saved → actual grid | Rows/F_L, saved → actual grid |
|---|---|---:|---:|
| gpt6sol-none/20260929T234513-e9946u/00 | 0.2 T steps plus a final 0.1 T step treated as uniform B | 0 → 0 | .439 → .435 |
| gpt6sol-none/20260929T234513-e9946u/14 | 0.05 T steps to 3 T, then 0.2 T steps treated as uniform B | **.052 → .590** | .378 → .716 |
| opus55-none/20260929T234509-e2rujz/06 | 64 inverse-B rows from 1–4 T plus 0.2 T steps to 9 T treated as uniform inverse-B | .997286 → .997286 | **3.325 → 2.808** |
| opus55-none/20260929T234509-e2rujz/11 | inverse-B increments .05 below 1 T, .01 to 5 T, then .25 T steps treated as one inverse-B grid | **.874 → .993** | **2.155 → 3.392** |
| opus-none/20260929T212518-7hk80x/02 | B=0 row omitted before 109 inverse-B rows | .949 → .949 | 4.043 → 4.043 |
| opus-none/20260929T234508-4kxt1o/14 | inverse-B recursion with a .40 T maximum step treated as uniform inverse-B | .997290 → .997397 | 3.322 → 3.185 |

The missing B=0 row increases modeled time from **4.819 to 4.975 h**: both one density row and the 0→1 T traverse are restored. Other five durations are unchanged because row counts and endpoints match. Sol-none /14 span rises .217→1.720 bins; Opus-5.5-none /11 rises 3.092→4.429. These are not merely cosmetic grid labels.

For reproducibility, the consequential arrays are:

- Sol /14: `round(r_[arange(.50,3.001,.05), arange(3.20,10.001,.20)],4)`.
- Opus-5.5 /06: `unique(round(hstack((1/linspace(1,1/4,64), arange(4.2,9.0001,.2))),4))`.
- Opus-5.5 /11: `unique(round(hstack((1/arange(2,1-1e-9,-.05), 1/arange(1,.2-1e-9,-.01), arange(5.25,10+1e-9,.25))),4))`.
- Opus /14: start at .7; repeatedly append `min(1/(1/B-.0105), B+.4, 10)` while below 10, guarding a nonpositive denominator with 10; round to four decimals.

All six errors happen to be in the none arm. That is an audit observation, not evidence of intent; stitched grids are especially vulnerable to lossy extraction. Two notes actually justify an inverse-B label by “the bulk of the vector” or “the cell's own construction,” although the schema requires the vector itself.

| Exploratory recalculation | Δ P within 8 h | Δ span | Δ rows/F_L | Pareto D |
|---|---:|---:|---:|---:|
| Registered saved data | .427272 | 1.370733 | 2.334177 | .399298 |
| Six explicit field arrays | .421798 | 1.346730 | 2.326534 | .395965 |
| Those arrays plus five effective hook delays | **.430857** | **1.346730** | **2.326534** | **.406053** |

Same fan denominators and equal model weights; Pareto recomputed over all within-model cross-arm pairs. No tests rerun, no registered artifact changed. The pooled conclusion is stable in effect size, while several individual grades and threshold classifications are not.

The screen also found small differences from rounding otherwise uniform grids (up to .00005 T); their score effects were not quantified. Apparent density-count mismatches in Fable-5.1-none /00 and /03 were explained by the code's gate-validator masks, which the extraction correctly applies. Several apparent row-count mismatches were explained by conditional terminal-row insertion or loops omitted by the restricted evaluator. No duplicate entries were found in the saved explicit `B_values` arrays.

### Dynamic settings and bundled measurements

**Autorange is extracted but not modeled.** Opus-5.5-none/20260929T234509-e2rujz/10 explicitly registers `autorange_sr830s`, starting at 10 µV with that floor. The extraction flags it correctly; the scorer applies clipping using a fixed 10 µV throughout. The hook can change sensitivity and sleep 10τ after an adjustment. A sensitivity calculation with fixed 20, 50 or 100 µV gives P=.050104 instead of .045764 at 10 µV: this particular fan's main limitation remains its field grid. Actual autorange behavior and its time cost require signal data; none of these fixed-range alternatives is an asserted correction. The final fan table also drops this extraction flag.

**A data-dependent range is not an untraced constant.** Fable-5.1-corpus/20260929T212520-paekuu/04 chooses the fan's sensitivity from 50/100/200/500 µV after a sizing row, and aborts if that row clips. `sensitivity_V=null` is reasonable as an unknown realized value, but the scorer interprets null as “do not check clipping.” The branch structure and abort probability are not represented. The initial 50 and 100 µV settings belong to preceding runs, not competing fan settings.

**Bundling changes what is counted.** That Fable episode lands a measured ride-up, sizing row and fan in one cell; Opus-5.5-corpus/20260929T234508-msonbj/05 lands a ~22-minute low-field probe followed by a fan in two code cells. Both are graded as fans, with preceding diagnostics outside fan time. Standalone diagnostic episodes are censored. This is consistent with the fan-only metric but makes “deferral” partly depend on where the agent places the handoff. A follow-up should charge all landed measurements and explicitly distinguish a conditional future fan from an immediately executable one.

The Fable extraction's `stated_wall_clock_h=6.83` quotes the whole package, although its own notes state the fan alone is 4.7 h and the prompt asks for the landed sweep's duration. This does not change registered scores, which use modeled hours. Its notes also say 921 ride-up points; the numerical expression gives **421**. Prose claims of recomputation are not a substitute for saving evaluated arrays.

## 8. Further data findings

### Low-field time expenditure is highly model-specific

A targeted counterfactual removes rows strictly below .75 T, the scorer's light-tone floor. It leaves both scoring windows and all acquisition settings unchanged. To avoid claiming free magnet motion, retain the full original traverse time and subtract only each removed row's fast-point time, slow delay, field settle and flyback:

`saved_h = count(B < .75) × [slow_delay + row_time_s(ncols, fast_delay, cost) + field_settle_s] / 3600`.

Using saved extractions, 13/20 Fable-5 corpus fans contain such rows; affected fans save a median **3.536 h**. **Eight** move from >8 h to ≤8 h. The corresponding counts are one Fable-5.1 and one Opus-5 corpus fan; four Fable-5 none fans cross. Fable-5's mean budgeted score becomes .843 corpus versus .460 none, gap **+.383**, compared with the registered +.095. The pooled gap becomes +.492. These are scorer-defined efficiency calculations, not a recommendation to discard low-field onset, background or calibration information.

Thus Fable's time penalty is not simply buying an unusually high score: a large part buys measurements to which this endpoint deliberately assigns no information.

### A density grid can serve a different physics question

For every fan, calculated the worst density spacing from the extracted actual-frame density array. At 1 T, a fourfold Landau-level density interval is `4eB/h = .09671957 × 10^12 cm^-2`; divide that by the largest density step to obtain points per fourfold interval. This is a sampling diagnostic, not a claim to resolve an actual gap.

Cell medians range **2.44–3.68 corpus** and **2.45–3.63 none**. All 119 corpus fans and 117/120 none fans have at least two points per fourfold interval at 1 T. The strong arm difference in field-frequency sampling therefore does not have a matching difference in this simple density-direction sampling measure. At lower field or for lifted degeneracies, the requirement is tighter.

A targeted example, the autoranging Opus-5.5-none fan, explicitly says it prioritizes LL degeneracy, crossings and a second fan apex, while keeping the existing spot check as its high-resolution high-density record. The registered scorer does not credit that joint use of prior data. This explains a possible mismatch between a useful transport map and a good *standalone F_L/F_heavy fan*; it does not establish that its stacking inference would be correct.

### The hard clock and independent-column assumptions matter differently

Multiplying every saved duration by .92, 1 or 1.08 before applying the 8 h cutoff gives pooled gaps **+.399, +.427, +.472**. Fable-5's corresponding gaps are **−.061, +.095, +.195**. This ±8% scale exercise is motivated by the time model's reported live agreement, not a calibrated confidence interval. The pooled effect is stable; that model's sign at a sharp deadline is not.

A separate correlation stress test shares the acquisition-success event across columns within each part while retaining independent geometric weights. For each part, select exactly the same half-bin-separated columns as the scorer, then replace `P_call(A*w_j)` with `A * P_call(w_j)`; retain the lesser part and original hours. The pooled 8-hour gap becomes **+.387**. No p-values were computed and this is not a fitted noise model.

Correlation does not simply lower every score: Astra-corpus's mean rises .542→.574 in this construction, because several columns succeed together and the call curve is nonlinear. Other corpus means decrease. This reinforces the distinction between the reported P values and experimentally calibrated probabilities; the direction and size of dependence effects cannot be read off the word “optimistic” alone.
