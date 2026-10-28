# Draft pre-registration: quality–hours dominance (vti-02 replay matrix)

Draft, 2026-09-23. The dev set (every episode to date) was used for the design and the power
calculation. The rule below is written as if the matrix data were unseen. Evidence:
`devset_stats.md`, `power.md`, `cost.md` and `multiverse.md` in this directory.
Scripts: `common.py` (inventory and scorer), `stats.py`, `devset.py`, `power.py`, `cost.py`
and `multiverse.py`.

## 0. Frozen before round 1

These are recorded by sha:
- grader `hera/graders/fan-design` (`grade.py`, `cases.toml`);
- `tones.json`, `roi.py` and `band.py`;
- this directory's scripts;
- `reference_set.json`;
- corpus and harness shas, image ids, model ids and effort.

Knob values are Aaron's rulings where one exists. Until then they take the base values in §2.

## 1. Units, arms and the analysis set

- **Episode.** One fresh-start replay at a cut, in a cell (model m ∈ M = {fable, opus, sol,
  astra}, arm a ∈ {corpus, none}). The model is `episode.json → run.model.observed`. An
  episode where the observed model differs from the pinned one is excluded and listed.
- **Ending class**, one per episode:
  - `fan`: grader tier = fan, meaning `2d_megasweep`, `continuous_ramp`, `other`, or a
    `column_series` with a declared ladder. A `landed_unexecuted` episode counts. An unlanded
    draft does not.
  - `probe`: `field_probe` / `probe_only`.
  - `b0`: `b0_cell`.
  - `none`: nothing gradeable, including a `no_stop` with no appended cell.
- **Harness exclusions.** These are reported and not placed:
  - status `interrupted`, `quota` or `error`;
  - a prep-cell handoff (`stop_cell_sweeps = False`);
  - a watch armed with zero appended cells;
  - a model mismatch.
- **A landed fan**, for stopping, is ending = `fan`.

## 2. Coordinates of an episode

For a fan: B is the grader's `field_axis`, with B = 0 rows dropped. The densities are
n_j = n_scale · columns_j / 10¹² (actual frame), using the tones F_L(n) = (h/4e)|n| and
F_ℓ(n) from `tones.json` (the corpus model, u_D = 0).

- Window: B_w = {B ∈ B : B ≥ B_lo}, with B_lo = max(B_min, b_clip).
  W = 1/min B_w − 1/max B_w.
- High line: F_hi = 1 / (m · max_i Δ(1/B)_i over B_w), with m = 3.
- Periods of the light tone: p_j = F_ℓ(n_j) · W.
- In band: F_L(n_j) ≤ F_hi and p_j ≥ k.
- **Primary quality, capped tone cells.**
  - δF = w / W, with w = 1 (bare bin) or 2 (Hann main lobe).
  - For in-band columns, the cell index is c_j = ⌊(F_ℓ(n_j) − min_in-band F_ℓ) / δF⌋.
  - **Q = min(15, Σ_c min(3, #{j : c_j = c})) / 15 ∈ [0, 1].**
- Hours: h = the grader's `derived(...)['cost']['estimated_wall_h']`. For a column series,
  multiply by the ladder size.
- Base knobs: k = 3, b_clip = 0.55 T, w = 1, model tones.

Quality candidates reported as pre-registered sensitivities:
- **band** = #in-band columns.
- **credit** = Σ_j c_j over columns with F_L ≤ F_hi, where c_j is:
  - 0 for p < k − 1;
  - a at p = k − 1, rising linearly to 1 at p = k;
  - 1 above k.
  a ∈ {0, 0.25}. At k = 3 this is the proposal's 2 → 3 ramp.
- **cells×acq** = Q recomputed with clipped columns removed, × SNR × q.
  - SNR = min(1, (I / 50 nA) · √(τ / 0.3 s)).
  - A column is clipped when I · R̂_max(n_j) ≥ 0.95 · sens. R̂_max is the composite
    neighbourhood maximum at the nearest 0.1 bin for n ∈ [0.85, 3.25]. Outside that range it
    is the global worst point, 1558 Ω.
  - q = 0.5 when 2^(⌈log₂ sens⌉ − 15) ≥ σ_V, with σ_V = 40 nV/√Hz · √(5 / (64 τ)), and 1
    otherwise. q = 0.5 is a free parameter; no dev-set design trips it, and none clips.

## 3. Placement

- The **floor point** is ⊥ = (Q = 0, h = ∞).
- Every counted non-fan ending and every fan with Q = 0 goes to ⊥.
- Reasons for this placement:
  - A zero-ROI fan has no scientific value, so its hours are no credit.
  - Placing it at its own cost lets a cheap useless fan be incomparable with, or dominate,
    a costlier useful one. On the dev set, sol's D_m falls from +1 to +0.5 for that reason
    alone.
  - Excluding non-landed episodes conditions on a post-treatment outcome: the corpus
    changes whether a fan lands. On the dev set, astra + corpus has 5 probes in 6.
- Sensitivity analyses, pre-registered:
  - `own`: Q = 0 fans at their own hours.
  - `landed`: fans only.

## 4. Statistics

Pareto dominance: a ≻ b ⇔ Q_a ≥ Q_b ∧ h_a ≤ h_b ∧ (Q_a > Q_b ∨ h_a < h_b). How the cases
resolve:
- Exact ties and incomparable pairs score 0.
- ⊥ ties with ⊥.
- ⊥ is dominated by every point with Q > 0.

**Primary: model-stratified pairwise dominance.**

  D_m = (1 / (n_{m,c} n_{m,n})) Σ_{i∈(m,c)} Σ_{j∈(m,n)} ([i ≻ j] − [j ≻ i]),
  **D_pool = (1/|M'|) Σ_{m∈M'} D_m**

M' is the set of models with at least one counted episode in both arms; a model that drops
out is listed.

- The statistic is ordinal, so it is invariant to monotone rescaling of Q and h.
- It needs no weights and no reference point.
- Stratifying by model is required, not cosmetic:
  - On the dev set, the arm-pooled D (ignoring model) at the 08-22 cut, over the four
    matrix models, is −0.08 to −0.28 across the grader-knob grid.
  - D_pool is +0.08 to +0.33, positive in every combination.
  - The difference is a Simpson reversal: astra contributes 6 of the 10 corpus episodes,
    all non-fan.

**Secondary: per-episode hypervolume.**

  HV1(i) = Q_i · max(0, 1 − h_i / h_ref) (0 at ⊥), with h_ref = 8 h ("fits overnight");
  **ΔHV1_pool = (1/|M'|) Σ_m [mean_{(m,c)} HV1 − mean_{(m,n)} HV1]**, sensitivity at h_ref ∈ {6, 12}.

- D says how often a corpus episode beats a no-corpus one. ΔHV1 says by how much.
- Set hypervolume is not used for inference. It grows with cloud size: on the dev corpus
  arm, random subsets of 1, 2, 5, 10 and 15 episodes give 0.15, 0.26, 0.43, 0.54 and 0.59.
  Under an N-landed rule the cells have unequal n.
- Frontier share is descriptive only. It is coarse, and it depends on the other arm's n.

**Also reported per cell:**
- landing rate, with a Wilson 95 % CI and the inverse-sampling-unbiased (N − 1)/(n − 1);
- D_m;
- the per-cell reference score ū = mean_i [P(i ≻ r) − P(r ≻ i)] over the frozen
  `reference_set.json`.

**Inference.**
- The CI is a stratified percentile bootstrap: B = 10 000 resamples, drawn within each
  (m, a) cell.
- The decision p-value comes from a two-sided within-model permutation test of the arm
  labels, with 10 000 permutations and cell sizes kept.
- Under the dev-set null at N = 5 / 10, the bootstrap CI rejected 9.2 % / 5.5 % and the
  permutation test 7.2 % / 4.8 %.

**Decision rule** (the primary cut, `vti02-fan-design`):
- *Supported*: D_pool > 0, permutation p < 0.05, and the 95 % CI lower bound > 0.
- *Contradicted*: D_pool < 0 with p < 0.05.
- *No practical difference*: the CI lies within [−0.10, 0.10].
- *Inconclusive*: any other result.
- Only when ΔHV1_pool has the same sign may the result be called "robust to the
  scalarization".
- Only when ≥ 90 % of the §7 grid shares the sign of the primary estimate may it be called
  "robust to the grader knobs".

Every per-model D_m is reported, and no model-level claim is made unless it was
pre-registered.

## 5. Stopping

Stopping follows Zack's ruling:
- Each cell runs until **N landed fans, capped at 2N episodes**.
- Every episode is reported.
- Episodes run in rounds. Every episode submitted in a round counts, even if N is reached
  mid-round.

N is fixed before launch: **N = 10** is recommended, with N = 20 if the budget allows.

There is no data-dependent extension. On the dev-set pilot, a staged precision rule biases
D and roughly doubles the type-I rate:
- The rule: stages N = 5 / 10 / 20, stopping when the cell's ū 95 % half-width ≤ δ.
- Bias: the mean D̂ rises to +0.25 against a population +0.23 (smoothed pilot) and to +0.31 to
  +0.32 against +0.26 (pooled).
- Type-I rate (null pilot): two-sided rejections of 0.12 to 0.21, against 0.08 for a fixed N.

The cause is that a homogeneous cell (all ⊥, or all at Q = 1) has a narrow CI and stops
first. With bounded, bimodal outcomes, width is not independent of the estimate. Precision
is therefore planned, not monitored.

Expected precision under the rule (smoothed pilot; population D_pool ≈ +0.21 to +0.23):

| N | mean episodes / cell (corpus, none) | D_pool 95 % half-width | P(CI > 0) | per-cell ū half-width |
|---|---|---|---|---|
| 5 | 7.1, 8.6 | 0.21 | 0.51 | 0.31 |
| 10 | 14.4, 17.6 | 0.16 | 0.72 | 0.22 |
| 20 | 28.8, 35.8 | 0.11 | 0.95 | 0.16 |

About 30 % of cells hit the 2N cap. astra + corpus is expected to (pilot landing rate 0.24),
and so is fable + none (0.33).

**Cost per cut** comes from the run records, at the high-effort mean $/episode: fable 8.72,
opus 3.76, sol 2.25 (Codex tokens priced), astra 1.96.
- Expected cost: $263 / $533 / $1072 at N = 5 / 10 / 20.
- Worst case, every cell at 2N: $334 / $668 / $1336.
- The 2×2 cut design doubles these.

## 6. Exclusions and reporting

Every episode is listed with its ending class, source (grader), Q, h, cost and tokens.
Exclusion counts are given per cell. The draft-grading trigger stands: grading reopens if
unlanded endings with a fan draft in scratch exceed about 10 % of an arm.

Concordance placement: each live fan's (Q, h) gets its ū, and its percentile within its
cell's ū distribution.

## 7. Multiverse (reported, not a decision input)

D_pool, D_arm-pooled and ΔHV1 are computed over:
- k ∈ {2, 2.5, 3};
- b_clip ∈ {none, 0.55, 1.0 T};
- a ∈ {0, 0.25} (credit only);
- w ∈ {1, 2} (cells only);
- tones ∈ {model, empirical}, where the empirical tone is F_ℓ / F_L = 0.0394 n + 0.1235 on
  the electron side, with the model tone kept for holes;
- each quality candidate;
- the floor and landed policies.

Dev-set values are in `multiverse.md`. They are exploratory, and the grader was tuned on
those same episodes.
