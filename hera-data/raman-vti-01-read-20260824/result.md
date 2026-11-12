# vti-01 Raman stacking read — result (2026-08-24)

Device: vti-01, 3LGr (trilayer per owner's characterization), dual-gated
hBN-encapsulated Hall bar. Data: WITec project `vti-01.wip`, sample
`73474_`, four maps + three video frames, all 2026-05-28 UTC (see
`provenance.md`).

## Headline

**The mapped graphene sheet is a mixed-stacking crystal: interleaved ABA
and ABC lamellar domains at roughly 50:50 by area, at 5–20 µm domain
scale.** A pickup event recorded *inside the file* (between video 002 →
video 004, i.e. ~20:10–20:19 UTC) removed most of the sheet between map
003 and map 005. The portion that was picked up — the likely device
graphene if vti-01 was built from this pickup — is therefore covered only
by pre-pickup map 003 and is **mixed-domain, not single-stacking**. The
remnant left on the substrate (the "tombstone", fully mapped post-pickup)
is ABC-dominant (~78%). The two fine maps (006, 008) contain no Raman
signal (stale 1064 nm laser selection) and are uninformative.

No build-stage testimony was supplied; the pre-/post-pickup staging above
is in-file evidence (timestamped videos + maps), and nothing in the inputs
says which portion (picked-up sheet vs remnant) became the vti-01 channel.

## 1. Per-region verdicts

Stage frame = WITec stage µm coordinates as stored in-file (scan-axis
rotation ~0.5° included via per-pixel coordinates). Raster masks with the
same label numbers: `regions.npz` / `regions.png` (layers `labels_pre` =
map-003 state, `labels_post` = map-005 state).

| Region | Centroid (x, y µm) | Stage stamp | Verdict (strength) |
|---|---|---|---|
| R1 sheet, ABC domains (label 1) | (−12050.1, 1282.8); lamellae across x −12078…−12028, y 1265…1303; 528 µm² | pre-pickup (map 003, 19:57 UTC) | **ABC** (strong) |
| R2 sheet, ABA domains (label 2) | (−12054.8, 1287.3); interleaved with R1; 516 µm² | pre-pickup (map 003) | **ABA** (strong) |
| R1+R2 sheet as a whole (the picked-up material, minus remnants) | x −12078…−12027, y 1264…1304 | pre-pickup (map 003) | **mixed ABA/ABC, ~50:50, lamellar 5–20 µm domains** (strong) |
| R5 tombstone remnant, interior (label 5) | (−12040.6, 1278.9); x −12047…−12035, y 1266…1295; 236 µm² | post-pickup (maps 005 @20:20; corroborated by 003 pre-pickup) | **ABC** (strong) |
| R6 tombstone remnant, W edge strip + SE patch (label 6) | (−12042.4, 1282.1); mostly x −12047…−12044 column and (−12038, 1268) patch; 66 µm² | post-pickup (map 005) | **ABA** (weak — edge-adjacent, 66 px) |
| R3 thick wedge (label 3) | (−12073.5, 1292.5); 66 µm² | present pre & post | multilayer graphene >3L, Bernal-consistent 2D (consistent-with); not the trilayer |
| R4 graphite sliver/chunk (label 4) | (−12068.6, 1265.1); 39 µm² | present pre & post | graphite, decisive; not device-relevant |
| Strip right of remnant | x −12035.5…−12031, y 1267…1290 | post-pickup | **uninformative** (optically dark, no G band, Si slightly enhanced ×1.04, broad ~1350 hump — likely pickup-tear debris/residue; not graphene, no sharp hBN 1366 line) |
| Map 006 footprint | center (−12037.6, 1294.5), 28×13 µm | post-pickup, 20:27 | **uninformative** — detector noise only (recorded 1064.4 nm excitation; no signal on Si CCD) |
| Map 008 footprint | center (−12037.5, 1269.9), 18×8 µm | post-pickup, 20:30 | **uninformative** — detector noise only (same cause) |

## 2. Evidence

All spectra: 532.338 nm excitation, axis −890…+3617 rel. cm⁻¹; per-pixel
despiked, linear-baselined; scripts `s0`–`s11` regenerate everything.

**Thickness uniformity (the domain split is not a layer-count step):**
- G-band area is single-moded across the sheet: ABC domains 4492, ABA
  domains 4551 (median CCD·cm⁻¹; 1.3% apart). Si 520 attenuation identical:
  0.821 vs 0.821–0.840 of bare-substrate value. A 3L↔4L step would move G
  by ~25–30%. (`final_stats.txt`, `histograms.png`)
- 2D/G area ratio 2.26, D/G ≈ 0.0005 (pristine). 2D FWHM 60–63 cm⁻¹ —
  few-layer, consistent with 3L; layer number is not independently
  verifiable from these data (named hedge #2).

**Stacking discrimination — four independent signatures, all pointing the
same way** (cluster medians; k-means K=2 on area-normalized 2D lineshapes,
1344 sheet pixels from maps 003+005; `final_lineshapes.png`,
`final_stats.txt`):

| Metric | ABC-like cluster | ABA-like cluster | expected ABC−ABA sign (lit.) |
|---|---|---|---|
| 2D single-Lorentzian center | 2695.0 cm⁻¹ | 2697.4 cm⁻¹ | red-shifted ✓ |
| 2D single-Lorentzian FWHM | 63.4 cm⁻¹ | 60.3 cm⁻¹ | broader ✓ |
| 2D lineshape | sharper peak at ~2683 cm⁻¹, enhanced 2630–2690 weight, kink near 2710 | rounder maximum at ~2690–2697 | more asymmetric ✓ |
| G center | 1579.9 cm⁻¹ | 1581.1 cm⁻¹ | red-shifted ~1 cm⁻¹ ✓ |

- 3-Lorentzian decomposition of cluster means (center/FWHM/amp):
  ABC-like: (2641.5, 31, 0.0009), (2683.2, 36, 0.0116), (2711.3, 41, 0.0095);
  ABA-like: (2643.1, 45, 0.0005), (2686.5, 39, 0.0112), (2712.9, 41, 0.0094).
  The discriminating weight sits in the sharper, red-shifted main component
  and the low-ω shoulder (difference curve peaks at ~2678 cm⁻¹,
  `final_lineshapes.png` right panel).
- Not an instrumental artifact: Rayleigh (−0.5 cm⁻¹) and Si (519.50 cm⁻¹)
  anchors are identical in maps 003 and 005 (`calib_check.txt`); both
  clusters are populated within each map.
- Not strain/doping gradients: domains are lamellar with sharp (1–2 px =
  1–2 µm) boundaries interleaved across a contiguous uniform-thickness
  crystal (`regions.png`, `clusters_k3.png`) — the canonical ABA/ABC domain
  morphology — rather than smooth radial gradients.
- Cross-map consistency through the pickup: the tombstone footprint reads
  72% ABC-like in pre-pickup map 003 and 78% in post-pickup map 005 — two
  independent acquisitions agreeing on the same physical region.

**The pickup event (staging evidence):** video 002 (19:55) shows one large
dark sheet covering the whole survey footprint, matching map 003's G-area
region shape in the stage frame (`video_002.png` vs `compare_worldframe.png`);
videos 004/007 (20:19/20:29) show only the tombstone + wedge remnants.
Map 003's G-region does not match video 004 but matches video 002;
map 005 registers on video 004 at r = 0.77 (`orient_results.txt`,
`orient_overlay.png`). Raster orientation was verified against the video
(no flip; `s6_orient.py`).

**Region classes:** wedge: G area 7443 (1.6× sheet), Si 12899 (more
attenuated), 2D 2699.8/58.4 — thicker Bernal-like multilayer. Graphite
sliver: Si ~500 (blocked), 2D peak 2712 with 2690 shoulder — classic
graphite doublet (also validates the lineshape method).

## 3. Confidence and named hedges

Overall: **the mixed-domain read of the sheet and the ABC-dominant read of
the remnant are strong**; no single-region call is offered as decisive.

1. **ABA/ABC assignment direction rests on literature signatures recalled
   from memory** (2D red-shift + broadening + asymmetry and G red-shift for
   ABC at 2.33 eV — Lui et al. / Cong et al. 2011). The *existence* of two
   equal-thickness stacking domains is data-decisive; the *labeling* of
   which is which would invert if those signatures were misremembered. Four
   concordant signatures make inversion unlikely.
2. **Layer count is the owner's testimony.** These data show a uniform
   few-layer sheet (2D FWHM ~60–63, complex multi-component; 2D/G 2.26)
   consistent with 3L, but no independent layer-count map exists. If it
   were 4L, the Bernal-vs-rhombohedral split would still stand as read.
3. **Which region is the device channel is not determined by the inputs.**
   No frame bridge (GDS/optical of the finished device) and no build-stage
   testimony were supplied. In-file evidence shows most of the sheet was
   picked up on 2026-05-28 20:10–20:19 UTC; if the device came from that
   pickup, the channel is somewhere in the mixed R1/R2 mosaic and the
   channel-scale stacking depends on where the Hall bar landed within it.
   If the device was made later from the remnant, R5/R6 applies
   (ABC-dominant with ABA edge strips).
4. **Post-map history unknown.** The maps predate the cooldown by ≥3
   months (map 2026-05-28, read 2026-08-24); stacking domains in trilayers
   are mobile under processing (encapsulation, annealing, gating can move
   ABA/ABC walls). The read is a statement about 2026-05-28, not about the
   cooled device.
5. **R6 (remnant ABA strips) is edge-adjacent** (one ~2 µm column plus a
   small patch, 66 px); edge-mixed spectra could mimic the ABA direction.
   Hence "weak".
6. **Maps 006/008 carry no information** — their "1064.4 nm" laser
   selection produced no CCD signal; the intended fine maps of the remnant
   never happened (see provenance, excitation-tag anomaly).
7. Minor: 003↔005 registration agrees to ~1 µm but the G-threshold edge
   sits ~1 px differently between maps; domain-boundary positions carry
   ±1–2 µm uncertainty.

## 4. What would firm it

- **A reference spectrum from a known-stacking flake on the same tool**
  (or published 532 nm ABA/ABC trilayer lineshapes) to lock the assignment
  direction of hedge #1 without memory reliance.
- **A frame bridge**: optical image or GDS of the finished vti-01 Hall bar
  registered to this stage frame (or to the picked-up flake on its stamp),
  to say which lamellae the channel and gates actually cover.
- **Build-stage testimony**: whether the device came from the 20:10 pickup
  or a later pickup of the remnant; any anneals between map and cooldown.
- **A post-encapsulation Raman map of the actual device** (2D lineshape
  survives encapsulation; hBN even sharpens it) — the single most decisive
  follow-up, since domains may have moved during processing.
- Re-run of the failed fine maps (006/008 footprints) at 532 nm if the
  remnant still exists and matters.
- An independent layer-count check (AFM step, optical contrast
  calibration) for hedge #2.

## Provenance line

Inputs received: `vti-01.wip` (md5 `4a29bb519f1ccaa1806720febbd43759`)
plus the brief's device facts (3LGr, dual-gated hBN-encapsulated Hall
bar). No frame bridges, no build-stage testimony supplied. I saw no
transport result, no third-party read/lean/reaction for this device, no
prior Raman read of this device, and accessed no repositories, notes,
web, email, chat, or wiki. Analysis used only public parsing/numeric
libraries (numpy/scipy/scikit-learn/matplotlib via `uv`). No forbidden
material reached me.

## File index (this directory)

- `provenance.md` — file inventory & acquisition facts (written first)
- `s0_parse_wip.py` — WIT-tag parser; `tree.txt` — full project tree dump
- `s1_extract.py` → `data.npz`, `video_00{2,4,7}.{npz,png}`
- `s2_firstlook.py` → `firstlook_spectra.png`, `firstlook_maps.png`,
  `orientation_check.txt`
- `s3_metrics.py` → `metrics.npz` (per-pixel band metrics)
- `s4_maps.py` → `metric_maps.png`, `histograms.png`
- `s5_stacking.py` → `clusters_k{2,3,4}.png`, `cluster_stats.txt`,
  `labels_k*.npy`
- `s6_orient.py` → `orient_results.txt`, `orient_overlay.png`
- `s7_spots.py` → `spots.png`, `spots_2d.png`
- `s8_regions_check.py` → `region_avg_spectra.png`, `region_stats.txt`
- `s9_compare.py` → `compare_worldframe.png`, `edge_profiles.png`
- `s10_calib.py` → `calib_check.txt`
- `s11_final.py` → `final_lineshapes.png`, `final_stats.txt`,
  **`regions.npz`**, **`regions.png`**
