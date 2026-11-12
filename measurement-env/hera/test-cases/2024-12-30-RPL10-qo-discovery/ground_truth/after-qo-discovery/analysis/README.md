# Analysis-reproduction ground truth (test type A′)

*Staged 2026-06-05. **Data only — the test harness is a later phase.*** This
captures Aaron's actual analysis of the sweeps around this frontier so a future
harness can pose the second test: **given a raw sweep, can HERA (a) reproduce the
analysis Aaron did, and (b) produce the result he drew from it?** This is the
analysis-layer analogue of the next-move test — one turn back, with Aaron's ana
notebook (`fans_ana.ipynb`) as ground truth.

The QO work for this run is analyzed in **`fans_ana.ipynb`**, not a dated
`*_ana.ipynb` (there is no `241230_ana.ipynb`). The relevant cells live under the
`# D = 0.31 V/nm` markdown header (cell 7).

Each `method_<id>.py` is his **verbatim** ana cell for that input file_id (loads
via `sl.pload`, forms `Rxx = sr830_{ind}_X / sr830_4_X`, plots). The expected
output is the matching figure under `../figures/`.

## His method (how he forms the physics)
- **Current channel:** `I = sr830_4_X` (contacts `7-20`, `I_{7-20}`, gain −1e6).
  This is the AC current bias / current readout, the **denominator**.
- **Voltage channels:** `Vxx = sr830_{ind}_X` for `ind ∈ {1,2,3,5,6}` (the
  longitudinal pairs `28-25, 11-13, 13-14, 14-15, 15-17`). **`Rxx = Vxx / I`.**
  For the Hall indices `{7,8}` (`29-13`, `28-14`) the same `Vyx/I` ratio is
  plotted as `Ryx` (in `h/e²` via `/Rq`).
- **Density axis:** `n = (Vbg/dbg + Vtg/dtg)·ep·5.52634936`, with the fast-axis
  gate vectors `xs[0]=Vtg`, `xs[1]=Vbg`; B is the slow axis `ys[0]`.
- **Landau-fan FFT:** he crops to `B[:200]` (≈ 1 → 0.02 T), removes a 5th-degree
  polynomial background in B (`remove_fifth_deg_poly`), inverts to 1/B and
  interpolates onto an even grid (`interp_rxx`), then FFTs column-by-column
  (`make_mat_fft`) into a normalized fan-frequency spectrum `f_ν`
  (frequency / (φ₀·n)). Dashed guide lines mark candidate densities
  (n = −2.72, −2.675, −2.51, −2.2).

**Cell dependencies (not in the `method_*.py`):** the globals `dbg`, `dtg`,
`ep`, `Rq` come from `fans_ana.ipynb` **cell 3**, and the helpers
`remove_fifth_deg_poly` / `interp_rxx` / `make_mat_fft` from **cells 5–6**. A
reproduction harness must run those first.

| Input | His method | Expected figure | Result (what he concluded) |
|---|---|---|---|
| `data/159` | `method_159.py` (cell 8) | `ana_159_landau-fan_sr830_{1,3}.png`, `ana_159_hall-fan_sr830_7.png` | A **Landau fan** `Rxx(n, B)` at D = 0.31 V/nm: oscillatory transport that brightens/structures up as B → 1 T across n = −2.9…−2.1, with FFT power concentrating at low fan-frequency and strongest near n ≈ −2.2. Confirms a quantum-oscillation regime; the FFT panel is the path to Landau-fan slope / degeneracy. |
| `data/157` | `method_157.py` (cell 9) | `ana_157_resolution-check_sr830_1.png` | The single-density (**n = −2.6**) "resolution check": `Rxx` vs B (0 → 1 T) at fixed gate, decimated 1×/2×/3×. Oscillations grow toward B = 1 T — confirms SdH oscillations are *resolvable* at this density before committing to the full fan. Immediate in-section predecessor of 159. |

**Leakage note:** All file_ids here (157, 159) are **pre-cut** (in the frontier
allowlist `[132 … 159]`). The post-cut temperature-dependence sweeps (160+) are
**not** analyzed here and must never enter the served (≤ cut) workdir. (Aaron's
T-dependence move was not found in any ana notebook by file_id; see `next_move.md`.)

## Caveats
- **`dbg` mismatch.** Cell 3 sets the global `dbg = 40`, but
  `calculate_gate_voltages` (cell 5) and the device card use `dbg = 40.5`. Cell 8
  computes `n` from the **global `dbg = 40`**, so its density axis is off by the
  ~1.25% `40/40.5` ratio from the measure-side `n`. Minor; flag, don't "fix" his
  verbatim cell.

## Open design question (for the later harness)
The analysis test needs HERA to *run* code (load, reshape, FFT, plot), so it
requires a tool surface the next-move test doesn't: a data loader + matplotlib +
scipy + a way to compare its figure/result to Aaron's. Scoring is likely "does it
form Rxx correctly (the `sr830_4`-as-current insight) and does it read the fan /
SdH oscillations," judged against the result column — not pixel match.
