# Analysis-reproduction ground truth (test type A′)

*Staged 2026-06-05. **Data only — the test harness is a later phase.*** This
captures Aaron's actual analysis of the sweeps around the `after-qo-confirmed`
frontier so a future harness can pose the second test: **given a raw sweep, can
HERA (a) reproduce the analysis Aaron did, and (b) produce the result he drew
from it?** This is the analysis-layer analogue of the next-move test — one turn
back, with Aaron's ana notebook (`20260124_ana.ipynb`) as ground truth.

Each `method_<id>.py` is his **verbatim** ana cell for that input file_id (loads
via `sl.pload`, forms `Rxx = sr830_{1,2,3}_X / sr830_4_X` for `long1` and
`Rᵧₓ = sr830_{5,6}_X / I` for `realhall`, converts gates → n via
`calculate_n_D(..., dtg=17.25, dbg=25.5)`, plots). The expected output is the
matching figure under `../figures/`.

| Input | His method | Expected figure | Result (what he concluded) |
|---|---|---|---|
| `data/1776` | `method_1776.py` (cell 78) | `ana_1776_qo-fan-D1_sr830_{1,2,3}.png` (Rxx); `ana_1776_qo-fan-D1_ryx_sr830_5.png` (Rᵧₓ) | A **small Landau fan at D = 1** (n = 0.9 → 0.5, B = 0.9 → 2.5 T): explicit Landau-fan oscillation fringes in the high-n/high-field corner of the Rxx channels → **the oscillations are real** (not noise). Too coarse to extract B_F. See `../reading.md`. |
| `data/1777` | `method_1777.py` (cell 79) | `ana_1777_fixed-nd-cut_sr830_1.png` | **High-resolution fixed-(n, D) 1D field cut** (a single 2001-pt `mag.field` sweep 1 → 3 T at one (n, D)): a clean Rxx(B) trace with well-resolved Shubnikov–de Haas oscillations — the data you can 1/B-FFT to read the oscillation frequency B_F. *This is the **next-move** answer for `after-qo-confirmed` (post-cut → answer-key only).* |

**Leakage note:** `data/1777` is **post-cut** (cut index 176) — it is the
`# Cuts at fixed n and D` answer the agent must predict. It belongs to the
analysis-reproduction ground truth and the human review card, **never** to the
served (≤ cut) workdir. `data/1776` is pre-cut (in the frontier allowlist).

## Method notes (so a reproduction can be scored)
- **Current vs. voltage:** `sr830_4_X` is the AC **current** (`I_{30-21}`), the
  **denominator** in `Rxx = Vxx/I`.
- **Rxx vs Hall:** `long1` = `sr830_1/2/3` (Rxx); `realhall` = `sr830_5/6` (Rᵧₓ).
  No single canonical Rxx — all of 1/2/3 are valid longitudinal pairs.
- **Axes:** the 2D fan uses density `n` on x and field on y; the next-move
  fixed-(n,D) cut is Rxx vs `mag.field` (1D). Read the code, not the auto x-label.
- **Scoring** is likely "does it form Rxx with sr830_4 as current, read the
  Landau-fan fringes / SdH oscillations," judged against the result column — not
  pixel match.
