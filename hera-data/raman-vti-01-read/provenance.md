# vti-01 Raman read — Step 0: inventory + provenance

Written before any spectral metric was computed. Source: in-file metadata of
`/data/sharpelab/hera-data/raman-vti-01/vti-01.wip`
(sha256 `5b5ffe6ba15784227d6d01ea2f744200b332cab22652297a8854c6888e383434`,
69 400 468 bytes), read with `witio` (`s0_inventory.py` →
`intermediates/inventory.json`, `intermediates/inventory.md`). Every number
below is either copied from the file or marked **[derived]** / **[inferred]**.

## Provenance line

Inputs received: the `.wip` file above; the device facts in the brief
(material 3LGr per owner's characterization, dual-gated hBN-encapsulated
Hall bar); the recipe `raman-stacking-id.md`; the tool
`hera/models/raman_stacking/` (README, `raman_io.py`, `metrics.py`,
`map_tools.py`, `validate.py`, `FUTURE_WORK.md`); the three ingested paper
notes (Lui 2011, Cong 2011, Nguyen 2014) and `hera/docs/raman-public-data.md`.
Not received / not read: any transport result, notebook, session note or
archive for this device; any human's read, lean or reaction to its stacking;
any prior Raman read of this device; the `dryrun/` folder inside the tool dir
(a worked example of another device — left unopened); anything outside the
allowlist. No frame bridges (optical images, GDS) and no build-stage testimony
were supplied. I saw no transport result and no third-party views for this
device.

## Project file

- WITec Project v8 (`WIT_PR06`), WITec Control 7.1.5.165, system `WS-3052`,
  user `SB02-WITEC-PC\Witec`. All data items carry the sample prefix
  `73474_` and were acquired **2026-05-28, 12:55–13:30 local** (UTC 19:55–20:30).
- 57 project items: 4 spectral scans, 3 video images, 39 orphaned
  space-transformation records from other samples/projects (`73472_`,
  `73148_`, `73159_`, `73164_`, `73222_`, `742xx_`, `Cut_Test_`) with no data
  payload — they carry no information about this device, but the
  `Cut_Test_` captions are consistent with the laser-cutting workflow inferred
  below.
- Raw CCD counts (uint16), no background subtraction, no normalization, no
  cosmic-ray removal (single-pixel spikes present — handled downstream).
  Floor ≈ 470–490 counts. No saturated (65535) pixel in any scan.

## Inventory

| item | caption | px | span µm | pitch µm | λ nm | P in-fiber mW | t_int s | grating | spectral axis | local time | stage centre µm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 22 | Scan LA--003 | 55×40 | 55.0×40.0 | 1.00×1.00 | 532.34 | 2.05 | 0.300 | G2 600 g/mm BLZ 500 nm | −891…3652 cm⁻¹, 2000 px, 2.22 cm⁻¹/px | 12:57:34 (735 s) | (−12050.4, 1283.9) |
| 27 | Scan LA--005 | 22×35 | 22.0×35.0 | 1.00×1.00 | 532.34 | 1.98 | 0.300 | same | same | 13:20:28 (297 s) | (−12038.7, 1282.0) |
| 30 | Scan LA--006 | 56×39 | 28.0×13.0 | 0.50×0.33 | 1064.4 | not recorded | 0.005 | same CCD window | −10281…−5738 cm⁻¹ (1064-referenced) | 13:27:23 (112 s) | (−12037.6, 1294.5) |
| 35 | Scan LA--008 | 36×24 | 18.0×8.0 | 0.50×0.33 | 1064.4 | not recorded | 0.005 | same CCD window | same | 13:30:19 (56 s) | (−12037.5, 1269.9) |

| item | caption | px | span µm | stage extent µm (x0→x1, y0→y1) | local time |
|---|---|---|---|---|---|
| 19 | Video Image--002 | 2240×1680 | 110.1×82.5 | (−12104.3→−11994.3, 1328.8→1246.3) | 12:55:43 |
| 24 | Video Image--004 | 2240×1680 | 110.1×82.5 | (−12095.2→−11985.2, 1325.5→1243.0) | 13:19:19 |
| 32 | Video Image--007 | 2240×1680 | 110.1×82.5 | (−12094.3→−11984.3, 1322.0→1239.5) | 13:29:37 |

Scan rotation 0.5° (all scans); objective Zeiss EC Epiplan-Neofluar
100×/0.9; spectrograph UHTS300S_VIS centre 585.37 nm; camera DR316B_LD
(Andor), −60 °C, pre-amp gain 4, track height 20 px. Video images share the
stage frame (µm) with the scans via the in-file space transformations;
figures `figures/f0_overview.png`, `figures/f0c_crops.png` overlay the scan
footprints on them.

### Step 0 table (recipe fields)

| field | value | source |
|---|---|---|
| excitation | **532.34 nm (2.33 eV)** for the two Raman maps (items 22, 27) | in-file |
| laser power | 2.05 / 1.98 mW **in fiber**; **at-sample power unknown** (fiber coupling + objective transmission losses — carry the in-fiber value with the conversion flag). 2 mW in-fiber is ≥ 5× below the ~10 mW conversion scale; at-sample is lower still. | in-file + flag |
| spot size | **~0.7 µm [derived]** (Airy diameter 1.22 λ/NA at 532 nm, NA 0.9; confocal FWHM ~0.5 µm) | derived from objective NA |
| map step | 1.0 µm (both Raman maps) — pixels are ~independent spots with ~0.3 µm gaps; 0.5 × 0.33 µm for the 1064 nm passes | in-file |
| spectral resolution | sampling 2.22 cm⁻¹/px; instrument FWHM resolution **~4–6 cm⁻¹ [derived, grating class]** (600 g/mm — Lui's 600 g/mm maps ran ~8 cm⁻¹; this UHTS300 is finer, value not recorded in-file) | derived |
| raw vs processed | raw CCD counts; no subtraction, no normalization, no despiking | in-file |
| acquisition date | 2026-05-28 | in-file |
| build stage | **not supplied** — see inference below | missing |
| layer count | owner's characterization "3LGr"; **no independent layer-count map supplied** | brief |

### The two 1064 nm scans are not Raman data

Items 30 and 35 (λ label 1064.4 nm, 5 ms dwell, sub-µm pitch) record the
same 508–661 nm CCD window as the 532 nm maps. Item 30 contains only one
sharp line (at the CCD pixel ≈ 520 nm absolute, max 6264 counts) and no G,
2D or Si band; item 35 is noise floor throughout (max 534 counts). Together
with the imagery (below) they read as **laser-cutting passes**, not
spectroscopy — **uninformative for stacking**, but load-bearing for the
stage stamp: the flake was locally heated far above any conversion
threshold along those footprints. (`figures/f0b_spectra_overview.png`.)

## Build-stage inference [inferred from in-file imagery — hedged, not metadata]

No testimony was supplied; the following is read off the three stage-
registered video images and the scan timestamps. Carry it as an inference.

1. **12:55 (image 002)**: a bare exfoliated graphene flake, ~55 × 30 µm,
   on a SiO₂/Si-looking substrate (Si 520 cm⁻¹ line present, unsaturated).
   No hBN, no contacts, no gate visible — **flake stage, pre-transfer**.
   Visible thickness structure: a much darker folded wedge at the top-left
   (x −12078…−12060, y 1282…1303); a lighter, thinner strip at the
   bottom-left (x −12080…−12068, y 1281…1288); a faint diagonal contrast
   boundary running from about (−12066, 1298) to (−12048, 1282); a thin
   lighter fringe along the bottom-middle edge. The main body (centre and
   right, including x > −12048) looks uniform in contrast.
2. **12:57 — map 22** (532 nm, whole flake, 55 × 40 µm at 1 µm step).
3. **Between 12:57 and 13:19**: the flake was cut (process not recorded in
   this file). **13:19 (image 004)**: what remains is a ~12 × 28 µm
   rectangular piece (x ≈ −12045.5…−12034, y ≈ 1267…1296, top edge
   slanted) and the thick folded left-over at x ≈ −12077…−12070. Everything
   else is gone.
4. **13:20 — map 27** (532 nm, 22 × 35 µm at 1 µm step, covering the
   rectangle and the cut margin).
5. **13:27 — item 30** (1064 nm pass over x −12051.6…−12023.6,
   y 1288…1301): in **image 007 (13:29)** the rectangle's top is now a
   straight edge at y ≈ 1287 — the pass removed the slanted top.
   **13:30 — item 35** (1064 nm pass over x −12046.5…−12028.5,
   y 1266…1274): after the last image; by analogy it trimmed the bottom
   (the stub and dark fold flap at y < 1274 seen in image 007).
6. **Plausible device channel**: the rectangle **x ≈ −12045.5…−12034 µm,
   y ≈ 1274…1287 µm (≈ 11.5 × 13 µm)**, stage frame of this file — the only
   piece consistent with a Hall-bar channel. Which piece actually went into
   vti-01 is **not established** by anything I received.

**Post-map steps implied by the brief's device description** (order and
dates unknown — all after 2026-05-28 13:20): hBN pickup/transfer
(transfer–pickup risk class: armchair-direction pickup can convert ABC→ABA),
dual-gate stack assembly (if graphite gates: through-stack confound for any
later Raman, not for these pre-stack maps), contact metal deposition
(metal-deposition risk class: walls move by µm), any bake/anneal (chemical +
bake class), plus the in-session **1064 nm laser cuts** (clean thermal class
at the cut lines, conversion-capable by a wide margin locally; the
rectangle's interior ≥ 1–2 µm from the cut lines is outside the footprints
except where the pass overlaps the rectangle's top 1 µm and bottom 0–2 µm).

## What the missing metadata caps

- **No build-stage testimony** → the stage stamp is imagery-inferred; the
  verdict is "as of 2026-05-28, flake stage, pre-transfer" and maps onto the
  finished device only modulo every post-map step listed above (ABC→ABA
  direction only).
- **No independent layer-count map** → the 2D read inherits the owner's
  "3L" and the in-map thickness proxies (G / Si amplitude; Step 1); the
  3-vs-4 fork is not resolvable at a single 532 nm excitation (Nguyen).
- **At-sample power unknown** → in-measurement conversion flagged as
  unlikely (in-fiber 2 mW), not excluded.
- **Single wavelength (532 nm = 2.33 eV)** → no cross-wavelength lineshape
  comparison; M-band at 2.33 eV sits inside the 2.1–2.4 eV dispersive-mode
  crossing → M read uninformative by recipe; lineshape reference is Lui
  Fig. 2 (514 nm panel, nearest — weakest-contrast excitation) and Nguyen
  Fig. 1 (532 nm column).
- **No frame bridge to the device** (no GDS, no post-fab optical image) →
  stage-frame coordinates only; the map→device mapping is left to fusion.
- **Short integration (0.3 s) and a weak 2D band** (~80–280 counts above a
  ~480 floor per pixel) → per-pixel FWHM scatter will be several cm⁻¹;
  population statistics carry the read, not single pixels.
