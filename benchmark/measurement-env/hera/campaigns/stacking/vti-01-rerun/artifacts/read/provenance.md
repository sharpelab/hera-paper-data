# provenance.md — Step 0 inventory, vti-01 Raman stacking read (2026-08-18 brief, executed 2026-08-27)

## Input

Single file: `inputs/vti-01.wip` (WITec Project v8, 69,400,468 bytes,
system WS-3052, user `SB02-WITEC-PC\Witec`), supplied by the device
owner's group. Read via `witio` (`tools/raman_io.py:load_wip` + direct
`witio` access for bitmaps/transformations). Inventory scripts:
`s0_inventory.py`, `s0b_summary.py` (output `s0b_summary.out`).

The project holds 57 items, but **actual data (bitmaps + spectral graphs)
exists only for sample prefix `73474_`**. All other prefixes (73148,
73159, 73164, 73222, 73472, 74279, 74281, 74310, 74354, `Cut_Test_`)
survive only as orphaned space-transformations of deleted items — no
pixels, no spectra. They were not read further (sibling-sample names are
not inputs to this read).

## Data items (all sample 73474, all acquired 2026-05-28 UTC)

| # | Item | Kind | Size / span | Center (stage µm) | Time (UTC) |
|---|------|------|-------------|-------------------|------------|
| 19 | Video Image--002 | bitmap 2240×1680 RGB | 110.1×82.5 µm | (−12048.7, 1288.4) | 19:55:43 |
| 22 | Scan LA--003 (map A) | spectral map 55×40 px | 55×40 µm, 1.0 µm step | (−12050.4, 1283.9) | 19:57:34 |
| 24 | Video Image--004 | bitmap 2240×1680 RGB | 110.1×82.5 µm | (−12039.7, 1285.3) | 20:19:20 |
| 27 | Scan LA--005 (map B) | spectral map 22×35 px | 22×35 µm, 1.0 µm step | (−12038.7, 1282.0) | 20:20:29 |
| 30 | Scan LA--006 | fast map 56×39 px | 28×13 µm, 0.5 µm step | (−12037.6, 1294.5) | 20:27:24 |
| 32 | Video Image--007 | bitmap 2240×1680 RGB | 110.1×82.5 µm | (−12038.8, 1281.9) | 20:29:37 |
| 35 | Scan LA--008 | fast map 36×24 px | 18×8 µm, 0.5 µm step | (−12037.5, 1269.9) | 20:30:19 |

Map B's area lies inside map A's footprint (A spans x ≈ −12078…−12023,
y ≈ 1264…1304; B spans x ≈ −12050…−12028, y ≈ 1264.5…1299.5). Scan
rotation 0.5° for all scans (negligible; carried in the transforms).

## Acquisition metadata (maps A and B — the Raman-usable data)

- **Excitation**: 532.338 nm (in-file spectral interpretation + per-scan
  `laser_wavelength_nm`). E_laser = 2.33 eV — inside the 2.1–2.4 eV
  window where M-band assignments are muddy (recipe: treat M read as
  uninformative at in-zone excitation).
- **Power**: in-fiber 2.05 mW (map A) / 1.98 mW (map B). **At-sample
  power unknown** (in-fiber value carries the conversion flag); at-sample
  ≤ in-fiber, so ≥ 5× below the ~10 mW laser-conversion scale and within
  reach of the ≤1 mW "safe by an order of magnitude" criterion only if
  fiber+optics losses ≥ 50% — flagged, not assumed.
- **Optics**: Zeiss EC Epiplan-Neofluar DIC 100×/0.9. Derived spot size
  (flagged, from NA): d ≈ 1.22·λ/NA ≈ **0.72 µm** at 532 nm.
- **Spectrograph**: UHTS300S_VIS, grating G2 600 g/mm BLZ 500 nm, center
  585.37 nm; camera DR316B_LD (−60 °C), 0.3 s/pixel integration.
- **Spectral axis**: 2000 points, −890.5…+3651.9 rel. cm⁻¹ — covers G,
  M-band (1690–2150), 2D, and nominally the ULF region (usability below
  ~100 cm⁻¹ depends on the Rayleigh filter; checked in analysis).
  Pixel pitch ≈ 2.27 cm⁻¹. Derived resolution estimate (flagged, grating
  class): ~5–9 cm⁻¹ FWHM — comparable to Lui's 8 cm⁻¹ mapping.
- **Raw vs processed**: units "CCD cts", no background subtraction or
  normalization recorded in item history — treated as raw counts.

## Scans 006/008 ("1064 nm" fast maps)

Integration 5 ms/px, spectral interpretation "Wavelength = 1064 nm",
identical CCD window (center 585 nm) → spectral axis −10281…−5738
rel. cm⁻¹, i.e. absolute detection 508–661 nm, the same visible window.
With 1064 nm excitation this is anti-Stokes-only and cannot contain
graphene Raman bands; these are quick imaging/positioning scans. **Not
usable for the stacking read**; used (if at all) only as auxiliary
intensity images.

## Missing fields and the caps they impose

- **Build stage: none supplied** (brief: no build-stage testimony, no
  frame bridges/GDS). The device is described by the owner as a
  dual-gated, hBN-encapsulated Hall bar; whether the maps predate or
  postdate gating/contacts/etch is **not established metadata**. Any
  stage inference from the in-file video images is imagery-inferred and
  carried as a hedged inference (QC0426 lesson). Consequences: (a) the
  verdict cannot be firmly mapped onto the finished device; (b) the
  through-stack screen cannot be discharged by testimony — if the maps
  postdate graphite gating, everything is capped at consistent-with.
- **Layer count**: owner's characterization says trilayer (3LGr); no
  independent layer-count map supplied. N=3 is carried as supplied
  testimony, not verified here.
- **Wavelength coverage**: single usable excitation (532 nm). Under
  Nguyen's two-wavelength rule a single-wavelength call is legitimate
  only with N independently known — here N rests on owner testimony, so
  the call inherits that hedge.
- **At-sample power**: unknown (see above) — in-measurement conversion
  cannot be fully excluded, though the in-fiber ceiling (~2 mW) makes it
  unlikely.

## Provenance line

Received: `inputs/vti-01.wip` alone, plus the device facts in the brief
(3LGr trilayer per owner; dual-gated hBN-encapsulated Hall bar). Corpus
used: `hera/recipes/investigations/raman-stacking-id.md`,
`hera/models/raman_stacking/` (tool + README + validate.py, gates re-run
7/7 in `tools/`), and the public validation data those cite. No frame
bridges, no build-stage testimony. I saw **no transport result, no prior
Raman read, and no third-party view** for this device. No sibling run
directories were listed or read. Harness-injected environment context
contained no repository/git information bearing on this device; nothing
from it was used.
