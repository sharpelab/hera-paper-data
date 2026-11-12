# VTI Cernox calibration data

Zero-field LakeShore calibration packages for the two CX-1030 Cernox sensors
on the VTI's **Lakeshore 335** controller (sample + vaporizer loops).

## Provenance
- Pulled read-only from the VTI PC `dgg-vti:~/Downloads/{X225149,X225150}/`
  on 2026-06-11. These are the as-shipped LakeShore deliverables; the same
  curves are programmed into the LS335 nonvolatile memory via the desktop
  "Lake Shore Curve Handler".
- The lab Dropbox `VTI/CryoIndustriesFlashDrive` (magnet/thermometry wiring,
  Cryo Industries manual) is **not** synced locally — chase there for wiring
  maps and the magnet manual if needed.

## Sensors
Both **CX-1030-CU-HT-0.3M** Cernox resistors, NIST-traceable ITS-90,
range 0.3-420 K, 95% CL (k=2):

| Serial | Cal date | Notes |
|---|---|---|
| X225149 | (2025 download) | |
| X225150 | 2024-10-01 | newer folder (2025-11) |

Per-serial files: `.340`/`.330`/`.234`/`.34A` curve files (LakeShore controller
formats), `.cof`/`.dat`/`.tbl` coefficient & raw-data tables,
`.linear.curve`/`.spline.curve` interpolation exports, and `.pdf` calibration
certificate.

## Channel map (from `src/vti_drivers/Lakeshore_335.py`)
- `sample_temperature` = `KRDG? A`  → **LS335 input A = sample-mount Cernox**
- `vaporizer_temperature` = `KRDG? B` → **LS335 input B = vaporizer Cernox**

### RESOLVED (2026-06-12, read from NVRAM): input A = X225149
`INCRV?`/`CRVHDR?` read with the rig kernel-free:
- input A → curve 23, header `CX-1030-CU-HT-0,X225149` → **sample sensor
  is X225149**.
- input B → curve 21, header **also** `CX-1030-CU-HT-0,X225149` — anomaly:
  either X225150's curve was loaded under an unedited header name, or A's
  curve was duplicated into slot 21. Vaporizer (B) is control-only and both
  sensors share model/cal class, so impact ≤ the inter-sensor cal delta —
  but if absolute vaporizer T ever matters, resolve with Bingcheng (compare
  curve-21 breakpoints against `X225150/*.340`).

### Doc nit
"How to use the VTI" doc lists these as `CX-1030-CU-HT-1.4L`; the sticker/cert
say `-0.3M`. The suffix is lead/packaging only — same sensor, same calibration.

## Accuracy (for LK fits / absolute-T error budget)

**Zero-field** typical calibrated-sensor accuracy (LakeShore Cernox spec):
±6 mK @ 10 K, ±9 mK @ 20 K, ±10 mK @ 30 K.

**Field-induced error** — these certs are zero-field. LakeShore's published
typical ΔT/T (%) vs B (tabulated for CX-1050, the field-optimized model; use
as a reference — CX-1030 magnetoresistance is somewhat *larger* at low T):

| T | 2.5 T | 8 T | 14 T | 19 T |
|---|---|---|---|---|
| 10 K | +0.04% | -0.40% | -1.1% | -1.5% |
| 20 K | +0.04% | +0.02% | -0.16% | -0.20% |
| 30 K | +0.01% | +0.04% | +0.06% | +0.11% |

Negligible above ~30 K. For this campaign's regime (<=6 T, 10-25 K):
- ~20-25 K end: <=0.03% → <=~6 mK (negligible).
- 10 K floor @ 6 T: ~-0.24% (CX-1050 interp) → ~-24 mK; CX-1030 likely a few x
  larger → order tens of mK.

Since raw `sample_temperature` **and** B are logged per point, the field term
is a clean post-hoc subtraction. The likely-larger uncharacterized systematic
is the mount→device thermal gradient (heater-power dependent) — operator to
characterize.

## Sources
- LakeShore Cernox catalog (field-error table):
  https://www.lakeshore.com/docs/default-source/product-downloads/catalog/lstc_cernox_l.pdf
- Per-sensor Certificate of Calibration: `X225149.pdf`, `X225150.pdf`
