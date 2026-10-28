# Provenance — vti-01 Raman stacking read (2026-08-24)

Written before any spectral analysis, per the read brief.

## What was received

- **Sole data input**: `/data/sharpelab/hera-data/raman-vti-01/vti-01.wip`
  (69,400,468 B, md5 `4a29bb519f1ccaa1806720febbd43759`), a WITec Project
  file (magic `WIT_PR06`), supplied by the device owner's group.
- **Device facts given in the brief**: material 3LGr (trilayer per the
  owner's characterization; no independent layer-count map supplied);
  dual-gated, hBN-encapsulated Hall bar.
- **Not supplied**: frame bridges (optical images outside the project,
  GDS), build-stage testimony (which build step the maps were taken at;
  steps between map and cooldown), any independent layer-count map.

**Isolation statement**: I read only the `.wip` file above. I saw no
transport result, no third-party read/lean/reaction to this device's
stacking, no prior Raman read of this device, no repository or notes
directory, and made no web/email/chat/wiki accesses. Parsing was done with
a custom WIT-tag parser (`s0_parse_wip.py`, this directory) using only
numpy. No forbidden material reached me.

## Project-file identity (all facts in-file)

| Field | Value |
|---|---|
| Format | `WIT_PR06`, project format "WITec Project 7.0.11.160" |
| Acquisition software | WITec Control 7.1.5.165 (Plus Version) |
| System ID | WS-3052 (ServiceID 10284, LicenseID 12896) |
| Acquisition PC / user | `SB02-WITEC-PC\Witec` |
| Spectrograph | UHTS300S_VIS, SN `UHTSWSN:13FK` |
| Grating | G2: 600 g/mm, blaze 500.00 nm; center wavelength 585.370 nm |
| Detector | CCD `DR316B_LD,DD` SN 11627, sensor at −60 °C (Si CCD) |
| Objective | Zeiss EC Epiplan-Neofluar DIC 100× / NA 0.9 (all acquisitions) |
| Data objects | 57 total: 4 `TDGraph` spectral maps + 3 `TDBitmap` video images (all sample `73474_`), plus transformations/interpretations |

The project also contains transformation/interpretation *stubs* whose
captions reference other sample names (`73472_`, `73148_`, `73159_`,
`73164_`, `73222_`, `74279_`, `74281_`, `74310_`, `74354_`, `Cut_Test_`)
whose graph/bitmap data objects are absent — the project was evidently
pruned to sample `73474_`'s data before sharing. One stub
(`74279_--Scan LA--017`, 2026-05-27) is the origin of the
"Wavelength = 1064nm" spectral interpretation (ID 63). Nothing in-file
maps `73474_` to "vti-01"; that identification is the owner group's, via
the brief.

## Spectral maps (TDGraph) — sample `73474_`, all 2026-05-28 (UTC)

All four maps: 2000 spectral bins, uint16 CCD counts, identical wavelength
calibration (free polynomial, λ = 508.244 → 659.270 nm across bins
0–1999). Stage-frame placement from each map's `TDSpaceTransformation`
(rotation of scan axes vs stage ≈ 0.50°; WorldOrigin = stage µm position
of the scan center).

| Map | UTC start (trace) | Px (X×Y) | Extent µm (X×Y) | Step µm | Stage center (x, y) µm | Excitation (recorded) | Power (recorded) | Integration |
|---|---|---|---|---|---|---|---|---|
| `Scan LA 003` | 19:57:34 | 55×40 | 55×40 | 1.0×1.0 | (−12050.40, 1283.90) | 532.338 nm | 2.050 mW | 0.3 s/px (scan duration 734.96 s) |
| `Scan LA 005` | 20:20:28 | 22×35 | 22×35 | 1.0×1.0 | (−12038.70, 1282.00) | 532.338 nm | 1.980 mW | 0.3 s/px (296.92 s) |
| `Scan LA 006` | 20:27:23 | 56×39 | 28×13 | 0.5×0.333 | (−12037.60, 1294.50) | **1064.400 nm** (see note) | not recorded | 0.005 s listed, 0.0251 s/px (112.42 s) |
| `Scan LA 008` | 20:30:19 | 36×24 | 18×8 | 0.5×0.333 | (−12037.50, 1269.90) | **1064.400 nm** (see note) | not recorded | 0.005 s listed, 0.0251 s/px (56.10 s) |

**Excitation-tag anomaly (recorded here as a file fact, resolved only in
analysis)**: maps 006 and 008 carry `XInterpretationID` 63 → "Wavelength
= 1064nm" (ExcitationWaveLength 1064.400 nm), and their trace records
list 1064.400 nm in the excitation slot with no laser-power entry. But
their stored wavelength axis is identical to the 532-nm maps
(508–659 nm), which under 1064.4 nm excitation would place the entire
axis at −10281 … −5773 rel. cm⁻¹ (deep anti-Stokes) on a Si CCD — not
physical for a Raman map. The 1064 interpretation object was created the
previous day (2026-05-27) for a different sample's scan (`74279_`). The
tag is therefore suspect (likely stale software state); whether 006/008
are in fact 532-excited is decided from the spectra themselves in
`result.md`, and is named there as a hedge.

Raman-shift span under 532.338 nm excitation: −890.5 … +3616.8 rel. cm⁻¹
(covers G ~1580 and 2D ~2700).

## Video images (TDBitmap) — sample `73474_`, 2026-05-28 (UTC)

All 2240×1680 px, 0.04913 µm/px (FOV 110.06×82.55 µm), stage-registered
(same ~0.51° rotation), grayscale uint16.

| Image | UTC | Stage top-left corner (x, y) µm | Stage center approx |
|---|---|---|---|
| `Video Image 002` | 19:55:43 | (−12104.30, 1328.79) | (−12048.7, 1288.4) |
| `Video Image 004` | 20:19:19 | (−12095.19, 1325.47) | (−12039.7, 1285.3) |
| `Video Image 007` | 20:29:37 | (−12094.29, 1322.02) | (−12038.8, 1281.9) |

## Acquisition timeline (UTC, 2026-05-28)

19:55:43 video 002 → 19:57:34 map 003 (55×40 µm survey) → 20:19:19 video
004 → 20:20:28 map 005 (22×35 µm) → 20:27:23 map 006 (28×13 µm fine) →
20:29:37 video 007 → 20:30:19 map 008 (18×8 µm fine). One sitting,
~35 min total. No build-stage label exists in-file; the file records only
that the maps were taken 2026-05-28, three months before this read.

## What the file does NOT carry

- No layer-count/thickness map, no AFM, no explicit "trilayer" marker.
- No build-stage annotation (before/after top-gate, anneal, etc.).
- No laser-power record for maps 006/008.
- No user notes/text objects (no `TDText` present).
