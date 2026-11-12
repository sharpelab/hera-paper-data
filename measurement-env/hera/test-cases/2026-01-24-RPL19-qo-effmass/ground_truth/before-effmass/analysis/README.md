# Analysis-reproduction ground truth (test type A′)

*Staged 2026-06-05. **Data only — the test harness is a later phase.*** This
captures Aaron's actual analysis of the sweeps around the `before-effmass`
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
| `data/1638` | `method_1638.py` (cell 39) | `ana_1638_prep-fan-D0.2_sr830_{1,2,3}.png` (Rxx); `ana_1638_prep-fan-D0.2_ryx_sr830_5.png` (Rᵧₓ) | A **density × field Landau fan at D = 0.2** (n = 0 → 1.5, B = 0 → 1.5 T): clean Landau-level fan in the Rxx channels, smooth Hall background in `sr830_5/6`. Quantum oscillations are present; the rig and (n, B) landscape are ready for the m* series. See `../reading.md`. |
| `data/1639`–`1642`,`1646` | `method_1639.py` (cell 42) | `ana_1639_effmass-tdep_sr830_1.png` | **Effective-mass temperature series:** 1D Rxx(B) field sweeps at fixed (n = 1, D = 1) overlaid at a ladder of heater temperatures, over a narrow field window (~0.75–1.25 T). The oscillation amplitude damps with increasing T — the raw material for the Lifshitz–Kosevich m* fit. *This is the **next-move** answer for `before-effmass` (post-cut → answer-key only).* |

**Leakage note:** `data/1639`–`1642`/`1646` are **post-cut** (cut index 100) —
they are the `# Effective mass` answer the agent must predict. They belong to the
analysis-reproduction ground truth and the human review card, **never** to the
served (≤ cut) workdir. `data/1638` is pre-cut (in the frontier allowlist).

## Method notes (so a reproduction can be scored)
- **Current vs. voltage:** `sr830_4_X` is the AC **current** (`I_{30-21}`); it is
  the **denominator** in `Rxx = Vxx/I`. Reading transport *out of* `sr830_4` is
  the canonical mistake.
- **Rxx vs Hall:** `long1` = `sr830_1/2/3` (`29-28`/`28-25`/`25-24`) are the
  **longitudinal Rxx** pairs; `realhall` = `sr830_5/6` (`28-10`/`25-11`) are the
  **Hall Rᵧₓ** pairs. (No single canonical Rxx — all of 1/2/3 are valid.)
- **Axes / reshape:** the 2D maps use density `n` on x (from
  `calculate_n_D(vtg, vbg, dtg=17.25, dbg=25.5)`) and field on y; the 1D m* plots
  are Rxx vs `mag.field` per temperature. The figure x-labels sometimes fall back
  to the raw gate-column name — read the code, not the auto-label.
- **Scoring** is likely "does it form Rxx with sr830_4 as current, pick a
  longitudinal pair, and read the Landau fan / temperature-damping," judged
  against the result column — not pixel match.
