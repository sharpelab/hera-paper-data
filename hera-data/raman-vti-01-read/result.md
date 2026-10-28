# vti-01 — Raman stacking read (Step 6 output contract)

Recipe: `hera/recipes/investigations/raman-stacking-id.md`. Tool gates: **7/7 pass**
(`tool/validate_output.txt`; A.pku-fig4, A.pku-fig2c, B.nemes-pair,
C.nemes-abc-layers, D.map-refs, D.map-clusters, E.decompose — run on a
byte-identical copy of the corpus tool, hashes in `tool/sha256.txt`).
Step 0: `provenance.md`. Region raster: `regions.npz` / `regions.png`.
Scripts `s0_inventory.py` … `s6_regions.py` (+ `common.py`) regenerate every
figure and number below from `/data/sharpelab/hera-data/raman-vti-01/vti-01.wip`.

Frame: WITec stage µm of the supplied project (sample label `73474_`), 1 µm
pitch. Excitation 532.34 nm (2.33 eV) for both Raman maps. Stage stamps
(imagery-inferred, no testimony — see hedges):
**S0** = 2026-05-28 12:57, map 22, bare flake on SiO₂/Si, pre-cut, pre-transfer;
**S1** = 2026-05-28 13:20, map 27, after the first laser cut, pre-transfer.

## 1. Per-region verdicts

| region (stage µm) | stage | verdict |
|---|---|---|
| **B — broad-2D population**, main-thickness flake; main lobe x −12060…−12032, y 1266…1291 (centroid −12047, 1282; 354-px largest component) plus a band x −12076…−12055, y 1296…1302; 461 µm² total, 57 % of the classified area | S0 | **ABC (strong)** |
| **Device rectangle (inferred channel)** x −12045.5…−12034, y 1274…1287 — lies inside region B: S0 149 broad / 3 narrow / 4 mixed px of 156; S1 123 broad / 1 narrow / 3 mixed px of 127 (FWHM 63.8 ± 1.1 / 64.0 ± 1.1 cm⁻¹) | S0 and S1 | **ABC (strong) as of S1**; ABA not resolved inside it at ≥ 1 µm scale (not "absent" — see §3) |
| **A — narrow-2D population**, main-thickness flake; band x −12076…−12035, y 1279…1298 (centroid −12058, 1288; 255-px largest component); 345 µm², 43 % | S0 | **ABA (strong)** |
| A in S1: strip x −12047…−12038, y 1290…1295 at the rectangle's slanted top (18-px component, same location as in S0) + 7 scattered px | S1 | ABA (strong); this strip sits inside the 13:27 cut footprint and is gone from the final piece |
| Mixed / wall pixels (label 12): 132 px in S0, 16 px in S1, tracing the A/B walls | S0/S1 | mixed / boundary — not a third stacking |
| Folded wedge x −12078…−12060, y 1282…1303 and the opaque chunk at y 1265…1267 (label 2); thin strip x −12080…−12068, y 1281…1288 (label 3) | S0 | **uninformative** for the device (other thickness populations, masked before the split) |
| Everything outside the two map footprints; the 1064 nm pass areas (items 30, 35) | — | unmapped / no Raman data |

Directionality: post-map processing converts ABC→ABA only. Region B may be
smaller or absent in the finished device; region A stays ABA (sub-spot slivers
and unmapped area excepted). The verdict for the finished vti-01 channel is
therefore "ABC as of 2026-05-28 13:20, modulo the build steps in §3".

## 2. Evidence

Primary — 2D-band width + lineshape, differential within one map
(`s3_split.py`, `figures/f3_split_22.png`, `f3_spectra_22.png`):

- Thickness-masked interior of map 22 (938 px: main G-area mode 3000–4700
  counts·cm⁻¹, one pixel eroded from the edge, r² ≥ 0.9, 2D amp ≥ 80): the
  single-Lorentzian FWHM histogram is **bimodal, 58.9 ± 1.5 vs 63.5 ± 1.2
  cm⁻¹** (2-means; 397 / 541 px), split 4.6 cm⁻¹, **Ashman D 3.4** against a
  per-pixel FWHM noise of 1.1 cm⁻¹ (same-cluster neighbour RMS). On 3×3-binned
  spectra: 59.7 ± 1.0 vs 63.2 ± 0.8, Ashman D 3.9 — the bimodality survives
  noise reduction.
- **Morphology = domain pattern**: 92 % of narrow-cluster and 99 % of
  broad-cluster pixels sit in connected components ≥ 9 px; largest components
  255 / 354 px; 92 % of pixel labels agree with their 3×3 majority; the two
  labels explain 74 % of the FWHM variance vs 32 % for a smooth quadratic
  surface. Walls are ≤ 1–2 px (1–2 µm) wide at this 1 µm step.
- **Lineshape** (cluster means, peak-normalised): the broad population has a
  sharper main peak at lower shift (~2685 cm⁻¹) with enhanced weight in both
  shoulders (difference spectrum positive at 2640, 2680 and 2725, negative at
  2700); the narrow population is smoother and peaks ~2697. This is the
  ABC-vs-ABA morphology of Lui Fig. 2c (514 nm, nearest panel; weakest-contrast
  excitation) and of Nguyen Fig. 1, 3LG column at 2.33 eV (dotted). Mean 2D
  position: broad 2695.6 vs narrow 2697.0 cm⁻¹ — ABA above ABC, as Lui SI
  Fig. S3 (1 cm⁻¹ effect, directional only).
- Map 27 (S1, 279 masked px) repeats the read independently: 59.7 ± 1.9 (32 px)
  vs 63.9 ± 1.0 (247 px), Ashman D 2.8; one 238-px broad component.
  Co-registered through the stage (`f4_coregistration.png`): FWHM r = +0.59
  over 275 shared px, mean difference +0.2 cm⁻¹, **label agreement 92 %**,
  best integer stage shift (0, 0) µm.
- Asymmetry metrics: skew −0.037 / −0.033, low/high ratio 1.02 / 1.01 —
  uninformative, as the tool README's calibration predicts; not used.

Screens (Verify section):

- **Terrace screen — passed.** Between the two clusters: G area 3829 ± 191 vs
  3812 ± 194, Si 520 area 14 117 ± 302 vs 14 032 ± 298 (Si line unclipped:
  max 2985 counts, no saturation), 2D/G area ratio 2.57 vs 2.60, 2D amplitude
  166 vs 160 counts. Same thickness population; the FWHM wall is not a layer
  step. The flake's real terraces (wedge, thin strip, chunk) were masked
  before the split (`f1_proxies_22.png`, `f1_histograms.png`).
- **Strain-mimic screen — passed.** corr(FWHM, 2D centre) r = −0.19 (map 22),
  −0.04 (map 27); the two clusters overlap completely in 2D centre
  (`f3_split_22.png` strain panel). A correlated G–2D position field exists
  (r = +0.79, d2D/dG = 1.8 — strain-like slope, few-cm⁻¹ blobs at ~(−12050,
  1285), (−12040, 1292), (−12030, 1282)) but it is orthogonal to the FWHM
  domain pattern: cluster-mean 2D centres differ by 1 cm⁻¹, G centres by 1 cm⁻¹.
  Broad + bimodal + sharp walls + stable 2D position → not strain.
- **Through-stack screen — not triggered.** Both maps are flake-stage (bare
  flake on substrate, no hBN, gate or contact visible in the in-file video
  images; Si line at full substrate strength around the flake). No other
  graphene in the spot except at the masked wedge/chunk.
- **Twist screen — considered, not triggered.** History trigger present (a
  fold at the flake's top-left, the masked wedge). The broad domain is the
  lower-right lobe, far from the fold; 2D/G and G area are identical across
  clusters and no monolayer-like sharp 2D component appears in the broad
  cluster mean — no 1L+2L signature.
- **Mixed-spectrum decomposition** (`s5_mixed.py`, `f5_mixed.png`): α fit
  r² median 0.99; cluster medians α = 1.00 / 0.00. Of 167 intermediate-FWHM
  pixels (60.5–62.5 cm⁻¹), 77 % are wall-adjacent and 41 % decompose at
  α ∈ (0.2, 0.8); wall-adjacent pixels are mid-α at 27 % vs 14 % in the
  interior. Intermediate pixels are wall mixtures, not a third population.

Secondaries (quantitative only, never the call):

- **M band** (`f4_mband.png`): 2.33 eV is inside the 2.1–2.4 eV dispersive-
  mode crossing → uninformative by recipe. Numerically: a ~1-count feature at
  ~1745 cm⁻¹ in both cluster means (SNR ≈ 3–4 at 0.3 s integration); the
  map-27 broad-cluster spike at 1830 cm⁻¹ is a single-pixel cosmic ray.
- **G width**: broad cluster 12.54 vs narrow 12.76 cm⁻¹ (map 22); 12.60 vs
  13.20 (map 27). ABC-narrower direction (Cong Fig. 6) but ≤ 0.6 cm⁻¹ — within
  noise, not counted as an agreeing channel. G position broad 1580.1 vs
  narrow 1581.3 cm⁻¹ — ABC-redshifted direction (Lui Fig. 3), same caveat.
- **Pristine check**: D band at noise level everywhere on the flake (D area
  ~ 20–120 counts·cm⁻¹ vs G ~ 3800; D/G ≈ 0).

Layer count (Step 1): N = 3 is inherited from the owner's characterization;
no independent map supplied. In-map support: the device rectangle lies in one
G-area / Si-attenuation population (Si attenuated 18 % vs bare substrate,
2D/G area ratio 2.6, 2D FWHM 59–64 cm⁻¹ at 532 nm — consistent with 3L, not
with 1–2L; 3 vs 4 is not resolvable at a single green excitation).

## 3. Confidence + named hedges

Confidence: the A/B split is a real, reproducible domain pattern on a single
thickness population with the ABC/ABA lineshape signature — **strong**, not
decisive (no shear-mode coverage, no second wavelength). Hedges, each named:

- **Split magnitude 4.6 cm⁻¹ is below the recipe's ≳ 10 cm⁻¹ heuristic.** The
  pattern sets the grade; the magnitude stays a hedge. For calibration only:
  the labeled public trilayer pair (gate A, different instrument, wavelength
  unstated) separates by 3.9 cm⁻¹ (67.1 vs 63.2), and Lui's ~55–80 cm⁻¹ map
  scale was at 8 cm⁻¹ resolution on 514 nm — trilayer splits at green
  excitation are small; absolute numbers do not transfer.
- **Sub-spot blindness (structural).** Spot ~0.7 µm [derived], step 1.0 µm
  (≈ 40 % areal fill): domains below ~1 µm and slivers between spots are
  invisible; wall positions are ±1 µm. Any "no ABA inside the rectangle"
  statement is **not resolved below 1 µm**, not "absent".
- **Stage stamp is imagery-inferred.** Flake stage, pre-transfer, read from
  the in-file video images and timestamps — no testimony. Which cut piece
  became vti-01 is inferred (the 11.5 × 13 µm rectangle is the only
  Hall-bar-shaped remnant). Post-map steps with ABC→ABA risk, all undated:
  1064 nm laser cutting at 13:27/13:30 (clean-thermal, conversion-capable
  locally; the device rectangle's interior is outside the pass footprints
  except its top 0–1 µm and bottom ~0–2 µm margins — unobserved after the
  cut), hBN pickup/encapsulation (transfer–pickup class), dual-gate stack,
  contact metal deposition (walls move by µm), any anneal/bake. The cut
  between 12:57 and 13:19 is covered by map 27: no conversion visible inside
  the rectangle (S0→S1 label agreement 92 %; the S1 narrow strip at the top
  existed in S0).
- **Single wavelength, 532 nm**, inside the M-band crossing zone: no
  cross-excitation lineshape check, M read uninformative; Nguyen's
  two-wavelength rule is satisfied only by inheriting N = 3.
- **Layer count inherited.** If N = 4, the same read maps to
  ABCA (B) vs ABAB (A) and cannot exclude ABCB.
- **At-sample power unknown** (2.0 mW in fiber; below the ~10 mW conversion
  scale by ≥ 5×, but the ≤ 1 mW "safe" bar is not established on record).
- **Spectral resolution [derived]** ~4–6 cm⁻¹ (600 g/mm, 2.2 cm⁻¹/px) —
  common-mode to both populations; absolute FWHM not portable.
- **Per-pixel SNR**: 0.3 s integration, 2D amplitude ~160 counts over a
  ~480 floor; per-pixel FWHM noise 1.1 cm⁻¹. Population statistics carry the
  read; no single pixel does.
- **Unmapped area / no frame bridge.** Stage-frame coordinates only; no GDS or
  post-fab image registers this frame to the finished device. The right edge
  column of the rectangle (x ≈ −12034.5) is a partial-spot edge in map 27.

## 4. What would firm it

- A 633 nm map of the same piece (Lui: strongest ABA/ABC contrast; M band
  outside the crossing zone) — one map settles both the magnitude hedge and
  the M-band cross-check.
- M-band spectra at red excitation with ≥ 10 s integration on an A and a B
  spot (one vs split M⁻; iTOLA/LOLA +10 cm⁻¹ in ABC).
- Higher-resolution map (1800 g/mm, ≤ 0.3 µm step) of the device rectangle for
  wall positions and sub-µm ABA inclusions.
- Near-field (s-SNOM) imaging of the finished device — resolves walls and any
  post-processing conversion Raman cannot see.
- The transport check on the finished device
  (`trilayer-stacking-fs-count.md`) — the in-situ arbiter after all
  conversion-capable steps.
- From the owner: build timeline with dates and which piece became vti-01;
  gate material (graphite vs metal decides whether any post-fab Raman is
  usable); a post-fab optical image to bridge this stage frame to the device.

## 5. Status

A call is made, not a "cannot tell": the evidence is feature-level (bimodal
FWHM populations, coherent domains with sharp walls, ABC/ABA lineshape
morphology, terrace and strain screens passed, reproduced in two
acquisitions). The device channel was cut from the broad / ABC-candidate
domain — **ABC (strong) as of 2026-05-28 13:20, flake stage**, perishable
through every subsequent build step, sub-µm structure unresolved.

## Provenance line

Received: `vti-01.wip` (sha256 5b5ffe6b…8434); the brief's device facts
(3LGr per owner, dual-gated hBN-encapsulated Hall bar); the recipe; the
`raman_stacking` tool and README; the three ingested paper notes and
`raman-public-data.md`. No frame bridges and no build-stage testimony were
supplied. I saw no transport result, no notebook, no session note or archive,
no prior Raman read and no third-party view for this device; the tool's
`dryrun/` folder was left unopened. Nothing was written under the corpus.
