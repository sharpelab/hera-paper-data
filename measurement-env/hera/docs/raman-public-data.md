# Public Raman data for graphene stacking ID

*Openly licensed trilayer/few-layer graphene Raman data with stacking
labels, found 2026-07 for the Raman stacking investigation. Local copies:
`$HERA_DATA/raman-public-data/`. The `raman_stacking` tool's validation
gates run against both sets (`hera/models/raman_stacking/validate.py`).*

## Usable datasets

### Zenodo 10931524 — Nemes-Incze group (HUN-REN EK-MFA Budapest), CC-BY-SA 4.0

Accompanies "Identification of graphite with perfect rhombohedral stacking
by electronic Raman scattering", Carbon **224**, 119113 (2024),
arXiv:2401.17779. Local: `zenodo-10931524-nemes/`.

- **Labeled single spectra** (WITec ASCII): hexagonal-vs-rhombohedral
  pairs (e.g. `Figure 2/FLG_38--Spectrum--045/046`), per-layer ABC
  spectra 4–12 L at 488/532/633 nm, two analyzer polarizations
  (`Figure 3 and 4/data/`).
- **Hyperspectral map with ground truth**: FLG_37, 48×45 px over
  32×30 µm, 488 nm, 2D-band export
  (`Figure 2/FLG_37--Scan Piezo--013...2D only_anal90.txt`) + labeled
  **region-average spectra** for the 7/8-layer hexa/rhomb areas
  (`Figure 3 and 4/*mask*.txt`). No per-pixel masks — population-level
  ground truth only.
- **Caveat**: the deposit's 3/5/6-layer spectra are ERS-region-only
  (3200–6600 cm⁻¹, their flat-band identification channel) — no 2D band;
  trilayer 2D-band truth comes from the PKU set below.
- Also in the deposit: AFM (.gwy), STM (.sm4), analysis notebooks using
  their open `ramantools` package.
- License note: CC-BY-SA is share-alike — fine for internal
  test/validation use; redistribution of derivatives inherits the
  license.

### Zenodo 20374368 — PKU (Kaihui Liu / Xiaobo Lu groups), CC-BY 4.0

Accompanies "Step geometry–guided growth of rhombohedral graphene"
(published 2026-07; paper not yet indexed — figure assignments inferred,
see below). Local: `zenodo-20374368-pku/`.

- **Layer × stacking spectral grid** (per-figure CSVs, normalized):
  `Figure4A.csv` / `Figure4B.csv` — G+2D spectra for 3–10 and 200
  layers, one file per stacking; `Figure2C1/2C2.csv` — single 2D-band
  pair. **The only public trilayer 2D spectra with stacking labels found.**
- `Figure4C/4D.csv`: their per-layer 2D-width and sub-peak-intensity
  tables with std devs, ABC vs AB columns.
- **Flagged assumption**: 4A/2C1 = ABC, 4B/2C2 = AB (ABC-first column
  convention + lineshapes); confirm against the paper when indexed.
  Excitation wavelength not stated in the files.

## Nearest misses (checked, not usable)

- **Ju group (MIT)** Nature papers: Raman panels exist (e.g. orbital
  multiferroicity, Extended Data Fig. 1) but deposits carry main-figure
  transport data only; Raman "available on request".
- **Weitz group** (RTG Nat. Phys. 2024; ABCB ACS Nano 2022): Raman/SNOM
  maps are figure-only, no deposits.
- Rhombohedral-graphene Zenodo deposits 14458163, 14641744, 10966640,
  19675446, 21290623, 20571193: transport/optics only (verified).
- Databases: Raman Open Database (one bulk graphite entry), RRUFF
  (minerals), Materials Cloud (first-order computed spectra — cannot
  produce the double-resonant 2D band): all unusable.
- Fallback if more lineshapes are ever needed: digitize figures from the
  open-access/arXiv versions of Lui 2011, Cong 2011, Nguyen 2014, Torche
  2017 (`hera/docs/papers/`).

## Watch

- Nemes-Incze group preprint on ABC enrichment by exfoliation
  (arXiv:2605.22282, 2026) uses large-area 2D **skewness** mapping; no
  deposit yet — their track record suggests one may appear.
