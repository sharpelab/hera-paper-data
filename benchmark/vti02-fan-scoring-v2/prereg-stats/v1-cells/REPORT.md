# Pre-registered statistics: report (agent, 2026-09-23)

Draft pre-registration section: `PREREG_DRAFT.md`. Outputs: `devset_stats.md`, `power.md`,
`cost.md`, `multiverse.md` / `.csv`, `episodes.csv`. Scripts: `common.py` (inventory, hand
extractions, generalized scorer, selftest), `stats.py`, `devset.py`, `power.py`, `cost.py`,
`multiverse.py`. Everything here is dev-set only and exploratory.

## Dev-set problem: the arm labels are not the models

The observed model is recorded in `episode.json → run.model.observed`.
- **Fable + corpus:** 11 of the 15 counted episodes are Sonnet 5 or Haiku 4.5. These are
  the smokes, which ran with `--model claude-sonnet-5`.
- **Sol + corpus:** 2 of 4 are gpt-5.6-luna.
- **Four early episodes** are at another frontier cut (`22c6ddf4` / `8097821b`).
- **The case ran two cuts:** the 08-21 cut (`45433bea`) on 09-22, then the 08-22 cut
  (`3a4cf818`).
- **The proposal doc's "fable-corpus/…" rows are mostly Sonnet and Haiku.**
- **Four fans at the 08-22 cut were never graded:** r3w0gf, 005529, tayua3 #00/#01. They are
  hand-extracted from `appended_cells.json` and flagged `hand`, and used in the pilot only.

Counted episodes at the 08-22 cut, by observed model:

| model | corpus: episodes (fans) | none: episodes (fans) |
|---|---|---|
| fable | 1 (1) | 1 (0, probe) |
| opus | 1 (1) | 1 (1) |
| sol | 2 (2) | 1 (1, Q = 0) |
| astra | 6 (0: 5 probes + 1 none) | 3 (2) |
| sonnet | 5 (5) | 1 (0) |
| haiku | 4 (3) | 2 (0) |
| luna | 2 (1) | 0 |

## Quality candidates

- **band:** the ROI band count.
- **credit:** the per-column credit.
- **cells:** capped at ≤ 3 columns per δF cell, 1.0 = 5 cells.
- **cells×acq:** cells × SNR × clipping × quantization.

The generalized scorer reproduces `band.cells` / `band.credit` exactly (selftest: 0
mismatches). No dev-set design triggers clipping or quantization. SNR is 0.12 or 0.20 for
every agent.

**Primary: capped tone cells.** It saturates at 1.0, which is what gives the hours axis
meaning. The acquisition term is a pre-registered sensitivity until the synthetic-detection
check validates it.

## Dominance statistics (08-22 cut, cells quality, floor placement)

| statistic | dev-set value | note |
|---|---|---|
| **D_pool**: mean over models of P(c≻n) − P(n≻c) | **+0.33** (4 matrix models), +0.51 (6 models) | Ordinal. Ties and incomparable pairs count 0. No reference point. |
| Arm-pooled D | −0.08 to −0.28 | Simpson reversal: astra is 6 of the 10 corpus episodes, all non-fan. Stratify by model. |
| Set hypervolume difference | +0.23 (h_ref 8) | Grows with n (0.15 → 0.59 at 1–15 episodes), so it is unusable when n differs between cells. |
| **HV1**: mean over episodes of Q·(1 − h/h_ref)+ | +0.09 (h_ref 8) | Doesn't depend on n. This is the budget-form scalar. |
| Frontier share | 0.14 / 0.11 | Coarse, and depends on the other arm's n. |

Per-model D: fable +1.0, opus 0.0, sol +1.0, astra −0.67. The astra corpus arm probes
because of the censored-onset clause.

Placing episodes without a useful fan:
- **floor (recommended):** non-fan endings and Q = 0 fans go to (0, ∞).
- **own (rejected):** Q = 0 fans at their own hours become incomparable with better, costlier
  fans. Sol's D drops from +1.0 to +0.5.
- **landed-only:** conditions on a post-treatment outcome and drops fable and astra.
  Sensitivity only.

**Recommendation:** primary = D_pool with floor placement. Secondary = ΔHV1_pool at
h_ref 8 h, with 6 and 12 h as sensitivities.

## Power, stopping, cost

The pilot is the 08-22 dev set. Each cell shrinks toward its arm's pool (N0 = 3, a free
parameter). 400 simulations × 500 bootstrap resamples. The pilot's population D_pool is
about +0.21 to +0.23.

| episodes per cell | 5 | 10 | 20 | 40 |
|---|---|---|---|---|
| 95 % CI half-width | 0.25 | 0.19 | 0.14 | 0.10 |
| P(CI lower bound > 0) | 0.38 | 0.56 | 0.83 | 0.98 |

Under Zack's rule (N landed fans, capped at 2N episodes):

| N | episodes per cell (corpus, none) | half-width | P(CI lower bound > 0) | cells at cap |
|---|---|---|---|---|
| 5 | 7.1, 8.6 | 0.21 | 0.51 | 31 % |
| 10 | 14.4, 17.6 | 0.16 | 0.72 | 31 % |
| 20 | 28.8, 35.8 | 0.11 | 0.95 | 30 % |

**Null calibration:**
- The bootstrap CI rejects 9.2 % at N = 5 and 5.5 % at N = 10.
- A within-model permutation test rejects 7.2 % and 4.8 %.
- Use the bootstrap for the CI and the permutation test for the decision.

**Against precision-based stopping** (stages at N = 5/10/20, stop once the half-width ≤ δ):
- It biases D̂ upward: +0.25 against a true +0.23, and +0.31–0.32 against +0.26.
- It inflates null rejections to 0.12–0.21, against 0.08 at a fixed N.
- The cause: homogeneous cells have narrow CIs and stop first, because the outcomes are
  bounded and bimodal.
- **Recommendation:** fix N before launch (10, or 20 if the budget allows). Use precision only
  to choose N.

**Cost:**
- Mean per episode, high effort: fable $8.72, opus $3.76, sol $2.25 (Codex tokens priced),
  astra $1.96.
- Per cut, expected / worst case: $263 / $334 at N = 5, $533 / $668 at N = 10,
  $1072 / $1336 at N = 20.
- The most expensive cell is fable + none, about $173 at N = 10.
- The 2×2 cut design doubles these.
- The summary CSV under-reports the sol-luna episodes run before the Codex token
  write-back fix; their costs are recomputed from token counts.

## Multiverse

72 knob combinations: k, onset clip, 2-period credit, cell width, tone source.
- **Floor placement:** D_pool > 0 in 100 % of combinations, for every quality and every set:
  - 08-22 cut, matrix models: +0.08 to +0.33;
  - all models: +0.35 to +0.51;
  - both cuts: +0.29 to +0.53.
- **Landed-only placement with cells quality:** 22 % of combinations give 0 (opus:
  1.0 at 4.8 h against 0.6 at 3.1 h is incomparable).
- **Individual knobs:** each moves D by ≤ 0.05–0.16. k is the largest on landed-only
  (k = 2: band +0.69, cells +0.63).
- **Caveat:** the stable sign mostly reflects fan vs no-fan within a model. It supports the
  direction, not the effect size.

## Other

- `band.py` reads `sys.argv[1]` on import; `common.py` works around it.
- `.pyc` caches may sit under `vti02-fan-scoring-v2/__pycache__` and
  `hera/graders/fan-design/__pycache__`.
- The empirical tone fit is electron-only (n 1.2–3.05). It is extrapolated linearly, and holes
  use the model tone.
- `q = 0.5` for a quantized channel is a free parameter, and nothing in the dev set trips it.
