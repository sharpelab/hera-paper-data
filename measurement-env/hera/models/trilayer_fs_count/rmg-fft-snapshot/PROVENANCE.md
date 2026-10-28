# RMG SdH-FFT pipeline — snapshot

Frozen copy of the SdH quantum-oscillation FFT analysis code from the RMG / chiral-SC paper,
captured for the ABA/ABC stacking campaign so the proven pipeline isn't lost as that repo
keeps iterating.

- **Source:** `/home/aaron/rmg19_quantumoscillations` (private: `sharpelab/rmg19_quantumoscillations`)
- **Snapshot commit:** `552149c` (branch `main`), captured 2026-06-15.
- **Files:** `utils.py` (canonical helpers), `utils_v2.py`, `linecut_fft_grid.py`,
  `two_carrier_explorer.py`.
- **Deps:** these import lab modules (`sweep` loader etc.) — this is a *reference snapshot*,
  not a standalone runnable package. Reconcile into the corpus `hera.analysis.sdh_fft` later.

## The pipeline (Aaron's proven recipe)
1. Acquire data **evenly spaced in B**.
2. **Background-subtract in B** — Butterworth high-pass (`detrend_butterworth`), or 5th-order
   poly + Butterworth (`detrend_poly` + `detrend_butterworth`).
3. **Interpolate to 1/B** (`interp_rxx`).
4. **Zero-pad + window**, then **FFT** (`make_vec_fft` / `fft_single_bw`).
5. **Stability hygiene** — `fft_stability_sweep`: vary detrender + window/cutoff; a real peak
   sharpens vertically as the record lengthens, an artifact wanders. Detrender *choice* is not
   load-bearing; the *scale* (cutoff) is.

## Key functions (in `utils.py`)
- Detrenders: `detrend_butterworth`, `detrend_poly`, `detrend_savgol`, `detrend_divide`,
  `detrend_linear`, `detrend_endpoints`.
- FFT: `interp_rxx` / `interp_rxx_B`, `make_vec_fft` / `make_vec_fft_B`, `make_mat_fft_bw`
  (per-density Butterworth), `fft_single_bw`, `fft_stability_sweep`.

## Related (not copied — large/iterating notebooks in the source repo)
- `capacitance_fitting.ipynb` — the CNP-line capacitance-ratio fit (ε_r = 3 for hBN → n within
  ~10% from dielectric thicknesses).
- `sdh.ipynb`, `fft_redux.ipynb` — canonical worked FFT analysis.
