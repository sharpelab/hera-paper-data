# result.md — vti-01 Raman stacking call (ABA vs ABC), 2026-08-18 brief, executed 2026-08-27

Recipe: `hera/recipes/investigations/raman-stacking-id.md`. Tool gates:
**7/7 pass** (re-run in `tools/`, output reproduced by
`tools/validate.py`). Data: `inputs/vti-01.wip`, sample prefix `73474_`,
all acquired **2026-05-28 UTC** on WITec WS-3052, 532.338 nm, 100×/0.9,
600 g/mm, ~2 mW in-fiber, 1 µm map step (`provenance.md` = Step 0).

**Stage stamps** (imagery-inferred — no build-stage testimony supplied):

- **S0** — intact exfoliated flake on SiO₂/Si, *before* any pickup.
  Video 19:55 UTC; **map A** (55×40 µm, 1 µm step) 19:57 UTC.
- **S1** — after a first pickup step removed most of the flake
  (between ~20:10 and 20:19 UTC; video 20:19). **Map B** (22×35 µm)
  20:20 UTC covers the leftover rectangle. A second pickup removed the
  rectangle's upper part by 20:29 (video). The two fast scans
  (metadata-tagged 1064 nm, 5 ms) contain no Raman bands — imaging only.
- Post-session steps to the finished dual-gated hBN-encapsulated Hall
  bar: **not supplied**; carried as unquantified conversion risk
  (pickup/transfer, metal deposition, bake — all documented ABC→ABA
  converters; conversion runs ABC→ABA only).

## 1. Per-region verdicts (stage frame; raster in `regions.npz` / `regions.png`)

| Region (label) | Location (stage µm) | Stage | Verdict |
|---|---|---|---|
| R2 — ABC main domain (label 2) | centroid (−12043.2, 1280.0), x −12058…−12031, y 1266…1291, 416 px ≈ 416 µm² | S0 (2026-05-28 19:57 UTC) | **ABC (strong)** |
| R1 — ABA band (label 1) | centroid (−12057.7, 1287.1), diagonal band x −12076…−12028, y 1268…1302, 394 px | S0 | **ABA (strong)** |
| R3 — top-band texture (label 3) | centroid (−12063.0, 1293.3), x −12074…−12030, y 1279…1301, 128 broad-pop. px interleaved with ABA px | S0 | **mixed ABA+ABC domains, 2–5 µm scale (strong as a mixture read; per-pixel assignment weak)** |
| R4 — fold triangle (label 4) | centroid (−12072.8, 1290.5), 80 px | S0 | **uninformative** (thicker: Si-520 −16%, G ×1.5; folded → twisted t(3+3) fork) |
| R5 — thin sliver (label 5) + rim (label 6) | flake edges | S0 | **uninformative** (non-trilayer / edge-straddling) |
| Leftover rectangle (dashed box; = part of R2) | x −12047…−12035, y 1266…1289 | **S1** (20:20 UTC) | **ABC (strong** — anchored to map A's in-footprint read; map B alone, being unimodal, would support only consistent-with**)** |

Directionality: R1's ABA verdict survives all subsequent processing
(sub-spot ABC slivers excepted). R2/R3's ABC may have shrunk or converted
in any post-map step; the S1 re-measurement shows the leftover part of R2
was still ABC after the first pickup.

## 2. Evidence

- **Two-population 2D-FWHM split (primary), map A, 532.34 nm**, on
  quality-gated trilayer-consistent pixels (938 px; amp>100, r²>0.9,
  interior, Si-520 within ±8%/−7% of body median): populations
  **58.42 ± 2.43 cm⁻¹ (n=394) vs 63.38 ± 1.19 cm⁻¹ (n=544)**; separation
  4.96 cm⁻¹ = 2.0× the larger within-cluster spread; clearly bimodal
  histogram (`fig_fwhm_hist.png`).
- **Domain morphology**: spatially coherent clusters (main components 416
  and 289 px), **wall 10–90 % width 1.2 µm** across 22 transects — one
  map step, i.e. resolution-limited sharp (`fig_zonesA.png`,
  `fig_split.png`).
- **Strain screen (mandatory, passed)**: corr(FWHM, 2D center) = 0.07 on
  clean pixels; 2D center flat across the wall (< 1 cm⁻¹ over ±4 µm)
  while FWHM steps 59→63; cluster mean centers 2696.6 vs 2695.8. No
  smooth-gradient/center-tracking pattern → not a strain mimic.
- **Terrace screen (mandatory, passed)**: proxy unclipped (raw max 7528
  counts ≪ 65535). Si-520 amp 2030 ± 44 vs 2011 ± 40 (Δ ≈ 1 %), G
  integral 1696 vs 1714 (Δ ≈ 1 %), 2D amp 166 vs 161 between clusters —
  no thickness step at the FWHM wall. The only thickness features (fold
  triangle: Si −16 %, G ×1.5; edge slivers FWHM < 50 with high Si) were
  masked before the split.
- **Through-stack screen (mandatory)**: S0 imagery shows bare flake on
  SiO₂/Si — no gates, no other graphene under the mapped regions except
  the fold triangle (excluded). Gate-clean map (imagery-inferred, hedged).
- **Reference panel at matching wavelength** (Nguyen srep04630 Fig. 1,
  2.33 eV, 3LG): broad cluster mean = low-side-peaked band with enhanced
  high shoulder, single-Lorentzian r² 0.981 (more structured) — matches
  ABC-3L; narrow cluster mean = smoother band, r² 0.989 — matches ABA-3L.
  Split direction and size consistent with the trilayer gate on labeled
  data (PKU 3L: 67.1 vs 63.2 cm⁻¹, Δ3.9, label assumption flagged);
  values not compared absolutely (excitation/resolution non-transferable).
- **Mixed-spectrum decomposition**: 271 intermediate-FWHM pixels
  (59.5–62.5) decompose against the map's own cluster means at median
  r² 0.988; 40 % at α ∈ (0.2, 0.8) — wall pixels are two-component
  mixtures, not a third phase; treated as boundaries.
- **Cross-map consistency (S0→S1)**: map A pixels inside map B's
  footprint: 62.3 ± 3.3; map B rectangle (y ≤ 1289): 63.5 ± 3.3,
  unimodal; 2D center offset A→B ≈ 1 cm⁻¹. Same population 23 min later.
- **Quantitative secondaries** (lab convention: ~zero weight, never the
  call): FWHM(G) 12.69 (ABA-cand) vs 12.56 cm⁻¹ (ABC-cand) — ABC
  narrower, direction agrees (Cong); G center 1581.3 vs 1580.2 — ABC
  redshifted ~1 cm⁻¹, agrees (Lui); G* ~2455 cm⁻¹ weaker in ABC-cand,
  agrees (Nguyen). **M band: uninformative** — E_laser 2.33 eV is inside
  the 2.1–2.4 eV crossing window *and* SNR ≲ 1 count on cluster means
  (`fig_secondaries.png`). **ULF**: only the Rayleigh wing below
  100 cm⁻¹ — shear modes not resolvable at 600 g/mm.

## 3. Confidence + named hedges

Confidence: **strong** for the S0 domain pattern (R1/R2), on the pattern
axis of the primary discriminator with all mandatory screens passed.
Named hedges:

1. **Sub-spot blindness (structural, always)**: domains below the
   ~0.72 µm spot / 1 µm step are invisible; wall positions are only
   ±1 µm; the ~146 rim pixels are unclassified.
2. **Split magnitude below the ≳10 cm⁻¹ heuristic** (4.96 cm⁻¹): pattern
   sets the grade per recipe; the size is consistent with trilayer-scale
   separations (PKU Δ3.9 at N=3, label assumption flagged) but small.
3. **Single wavelength** (532 nm): under Nguyen's two-wavelength rule the
   call is legitimate only because N is taken as known — and **N = 3
   rests on owner testimony**, not on an independent layer-count map. The
   in-map proxies show one uniform thickness across R1/R2 but cannot fix
   absolute N; if N were actually 4, the same split would read
   Bernal-vs-rhombohedral family (ABCB caveat applies).
4. **Stage stamps are imagery-inferred** (QC0426 lesson): "flake stage,
   pre-pickup" comes from the in-file videos, not testimony.
5. **No bridge to the finished device**: which picked piece(s) became
   vti-01 is unknown (no frame bridge, no build testimony); post-map
   processing (pickup, gating, contacts) can only have converted ABC→ABA,
   so the finished-device channel could be less ABC than mapped. **For
   the finished vti-01 device this read is, on its own, at most
   consistent-with per region until the piece-to-device bridge is
   supplied.**
6. At-sample power unknown (≈2 mW in-fiber ceiling): in-measurement
   conversion unlikely (≥5× under the ~10 mW scale) but not excluded to
   the ≤1 mW criterion.
7. Spectral resolution ~5–9 cm⁻¹ (derived, grating class) inflates
   absolute FWHM; all reads are differential within-map.
8. Map A covers only this flake; unmapped areas of the wafer are
   unconstrained. Coverage for the "no ABA in the leftover rectangle at
   S1" statement: 22×35 µm at 1 µm step, 276 quality px, unimodal.

## 4. What would firm it

- **Build-stage testimony + frame bridge** (which pickup went into
  vti-01; GDS/optical registration to stage coordinates) — the single
  highest-value item; it converts these S0/S1 verdicts into a
  finished-device constraint.
- Second excitation (red 633 nm preferred — largest lineshape contrast)
  on any remaining material.
- ULF shear-mode spectra (C ~33 cm⁻¹ vs C′ ~19 cm⁻¹) — decisive per spot.
- Higher-res map or s-SNOM for sub-spot walls.
- The transport check on the finished device
  (`trilayer-stacking-fs-count.md`) — the in-situ arbiter.

## 5. Outcome statement

This is a **mixed-domain flake**: at S0 it carried a large coherent ABC
domain (~400 µm², right/lower body), a large ABA band (upper/left), a
mixed 2–5 µm domain texture along the top, and an uninformative folded
region. That is a successful read, not an ambiguity. What this read
**cannot tell** is the stacking of the finished vti-01 device: the
piece-to-device bridge and post-map build steps were not supplied, and
conversion (ABC→ABA only) during pickup/fab cannot be bounded from the
supplied data.

## Provenance line

Inputs received: `inputs/vti-01.wip` (device owner's WITec project) plus
the brief's device facts (3LGr per owner; dual-gated hBN-encapsulated
Hall bar). Corpus used: the recipe, `hera/models/raman_stacking/` (gates
re-run 7/7), the three ingested papers, and the cited public validation
data. No frame bridges, no build-stage testimony, no transport result,
no prior Raman read, and no third-party view of this device were seen.
No sibling run directories were listed or read. Harness-injected
environment context contained no repository/git information about this
device; none was used.

## File map

- `provenance.md` — Step 0. `regions.npz` / `regions.png` — region raster,
  stage µm frame, label→verdict key inside the npz.
- Scripts (rerun in order): `s0_inventory.py`, `s0b_summary.py`,
  `s1_images.py`, `s2_metrics.py` (→ `map_metrics.npz`), `s3_split.py`
  (→ `split_results.npz`), `s4_zones.py` (→ `zonesA.npz`),
  `s5_regions.py` (→ `regions.npz`). Tool copy + gate rerun: `tools/`.
- Figures: `fig_video_images.png`, `fig_img00{2,4,7}_full.png`,
  `fig_firstlook.png`, `fig_map{A,B}_metrics.png`, `fig_fwhm_hist.png`,
  `fig_split.png`, `fig_mapB_fwhm.png`, `fig_secondaries.png`,
  `fig_zonesA.png`, `regions.png`.
