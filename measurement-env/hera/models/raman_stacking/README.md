# raman_stacking — 2D-band metrics + map segmentation for stacking reads

Extraction tool backing `recipes/investigations/raman-stacking-id.md`: computes
the standard stacking-discriminating Raman metrics from supplied spectra or
hyperspectral maps, and segments a map into candidate stacking populations.
This is an **extraction/metric tool, not a forward model** — no double-resonance
lineshape is computed; reference lineshapes come from labeled public data.

## Files

| File | What it does |
|---|---|
| `raman_io.py` | Loaders: WITec ASCII exports (spectra + maps), **WITec `.wip` project files** (`load_wip`, optional `witio` package — also exposes the in-file video images + µm grids for registration), headerless two-column, PKU interleaved CSV. Data root `$HERA_DATA/raman-public-data`. |
| `metrics.py` | Per-spectrum 2D-band metrics (single-Lorentzian FWHM, center, moment skew, low/high-side ratio, fit r²) + G-band position/FWHM + `decompose_mixed()` (α-fit of a spectrum against two same-instrument reference means — the boundary/mixed-pixel read). All 2D metrics are **center-relative** — absolute windows don't transfer across excitation wavelengths (2D disperses ~100 cm⁻¹/eV). |
| `map_tools.py` | Per-pixel metrics with junk-fit rejection (SNR, FWHM ∈ 15–200 cm⁻¹, r² > 0.4), two-population 1-D 2-means split, cluster mean spectra. |
| `validate.py` | The validation gates below. Re-run after any metric change. |
| `flg37_map_validation.png` | Worked map overlay (gate D output). |

Run: `uv run --no-project --with numpy --with scipy --with matplotlib python3 validate.py`

## Validation — gated on labeled public data (2026-07-17, 7/7 pass)

Datasets in `$HERA_DATA/raman-public-data/` (`hera/docs/raman-public-data.md`):
Zenodo 20374368 (PKU, CC-BY 4.0) and Zenodo 10931524 (Nemes-Incze group,
CC-BY-SA 4.0).

| Gate | Data | Result |
|---|---|---|
| A | PKU labeled ABC-vs-AB spectra, N = 3–10, 200 | FWHM(ABC) > FWHM(AB) at every N; **trilayer: 67.1 vs 63.2 cm⁻¹**; separation grows with N (10 L: 80.3 vs 63.9) |
| B | Nemes labeled single pair (hexa vs rhomb) | rhomb 80.7 vs hexa 64.0 cm⁻¹ |
| C | 29 labeled-ABC spectra, 488/532/633 nm | FWHM 72–92 cm⁻¹ across all three wavelengths (4–12 L) |
| D | Nemes FLG_37 hyperspectral map (488 nm, 48×45 px) | two-population split at 60.2 / 77.9 cm⁻¹; cluster-mean FWHM 62.0 / 77.9 vs labeled region averages hexa 60.6–60.9 / rhomb 78.1–78.6; domains spatially coherent with sharp walls |
| E | synthetic mixtures of gate D's cluster means (2% noise) | `decompose_mixed` recovers α = 0–1 within ±0.1; 78% of the map's real intermediate-FWHM pixels decompose at α ∈ (0.2, 0.8) — wall mixtures, not a third phase |

Validation-derived calibration facts (this data, not universal):

- **FWHM is the workhorse metric.** Clean separation in every gate. The
  asymmetry metrics (moment skew, low/high-side ratio) are **weak and
  direction-inconsistent** across datasets/excitations here — e.g. PKU AB
  spectra show a *higher* low/high ratio than ABC. Treat asymmetry as a
  secondary, locally calibrated check, never the call. (Consistent with Lui
  et al. 2011 settling on FWHM for imaging.)
- **Absolute FWHM values do not transfer** between instruments (spectral
  resolution folds in) — classify by the two-population split within one
  map/flake, or against same-instrument references, never by a universal
  threshold.
- **Layer number also raises 2D FWHM** (PKU: ABC 67→80 cm⁻¹ over N = 3–10).
  A two-population split on a multi-thickness flake confounds thickness with
  stacking — interpret clusters against the thickness map.

## Caveats / assumptions

- **PKU label assumption (flagged):** Figure4A/2C1 = ABC, Figure4B/2C2 = AB —
  inferred from the deposit's ABC-first column convention and lineshapes
  (4A trilayer 2D at 2689.6 cm⁻¹ broad/asymmetric vs 4B 2703.3 narrow); the
  paper (published 2026-07) is not yet indexed to confirm. Direction of every
  gate matches four independent labeled sources, so a label swap would be
  visible.
- The Nemes deposit's trilayer spectra are **ERS-region-only** (3200–6600
  cm⁻¹, their flat-band identification method) — public trilayer 2D-band
  truth rests on the PKU set. Map gate D is a 7/8-layer flake: it validates
  the pipeline, not trilayer specifically.
- Gate D scores population-level agreement (labeled **region-average
  spectra**; the deposit has no per-pixel masks).
