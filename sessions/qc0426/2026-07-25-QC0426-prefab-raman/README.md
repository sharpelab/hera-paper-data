# 2026-07-25 — QC0426 pre-fab Raman ladder: provenance + recipe-path exercise

Grower-supplied fabrication-record set for QC0426, completing the Raman
stage ladder around the already-held post-fab map
(`$HERA_DATA/raman-qc0426/06_3LGr-device.wip`). Dev-side exercise of
`raman-stacking-id.md` Steps 0/2/3 + screens on the new files — **not a
fresh-instance run**; the standing per-device call remains with
`../2026-07-17-QC0426-raman-fusion/` and its correction.

## Provenance

Received 2026-07-25 from the grower (qingrui) via file handoff;
re-download duplicates deduped by md5; ingested to
`$HERA_DATA/raman-qc0426/`:

| File | Content |
|---|---|
| `04_3LGr.wip` | WITec project, bare exfoliated flake, acquired 2026-04-28 |
| `05_3LGr-stack.wip` | WITec project, assembled stack, acquired 2026-05-05 |
| `20260428-3LGr.gds` | device layout (cell `FIRST`, 8209 polys, layers 0, 9–15, 5.3×5.3 mm) |
| `session.lys` | KLayout session for the GDS; references grower path `…\Qingrui\stacks\20260428-3LGr\2_ebeam\` — build id `20260428-3LGr`, e-beam step |
| `50x_02.jpg`, `100x_00.jpg` | stack on the marked target chip (alignment squares + `0 0` labels from the GDS marker layer), burned-in scale bars, 2880×2048 |

## Stage ladder

flake `04` (2026-04-28) → stack `05` (2026-05-05) → finished device `06`
(2026-05-14/15) → VTI load → transport sessions (2026-06/07, call locked
2026-07-16). Stage order and dates are in-file (trace timestamps); the
**build-step list between stages** (pickup order, bake, metal deposition,
with dates) is grower testimony, not in any file.

## Inventory (Step 0, from in-file metadata)

All traces: 532.34 nm, Zeiss 100×/0.9, UHTS300S spectrograph; survey
spectra + maps on the 600 g/mm grating (−891…3652 cm⁻¹), band spectra on
1800 g/mm. In-fiber laser power recorded per trace; **at-sample power not
recorded** (recurring gap, same as `06`).

- `04`: video image (2240×1680, stage-registered); spot1 + spot2 each
  with survey (20 s, ~2.4 mW), G, 2D (20 s), M (60 s) spectra — spot1 at
  stage x = 13.3 µm, spot2 at −23.1 µm; map `Scan LA--009` 101×57 px over
  75×42 µm, 10 s/px, 2.43 mW; grower's own PsdVoigt fit maps embedded.
- `05`: video image; Spot1 + Spot2 with survey/G/2D (30 s, ~5.0 mW — no
  M spectra); map `Scan LA--007` 76×61 px over 50×40 µm, 10 s/px,
  **8.0 mW in-fiber**; PsdVoigt fit maps embedded.

## Mechanical read (dev-side; scripts in this dir regenerate everything)

Tool gates green before metrics (`validate.py`, 2026-07-25).

**`04` (flake, gate-clean — nothing else in the spot):**

- Map two-population split, thick region (FWHM > 45): **57.5 vs
  63.8 cm⁻¹** (n = 1837/1610), separation 6.3; clusters form spatially
  coherent domains, not noise.
- Strain screen: pass — cluster 2D centers 2692.7 vs 2693.1 cm⁻¹
  (Δ 0.4), no center gradient tracking the FWHM pattern.
- Terrace screen: pass without an external thickness map, on the
  2D-amplitude proxy (cluster ratio ≈ 0.98; a layer step would step
  it). The Si 520 cm⁻¹ line is detector-saturated (65535) across the
  flake map — a clipped substrate line reads as a perfect match and is
  unusable as a proxy. A thin-ribbon population (FWHM ≈ 29.6, n = 281,
  distinct amp) excluded as non-trilayer before the split.
- Spots (grower placed one per population): spot1 2D FWHM 64.5 / G 12.2
  on a high-FWHM domain; spot2 58.7 / G 9.6 on the body. M-window maxima
  spot1 ≈ 1740–42 vs spot2 ≈ 1733–37 cm⁻¹ — directionally
  ABC-consistent for spot1 (blueshift), hedged near the 2.1–2.4 eV
  crossing.
- Dominant-max position (2650–2800 cm⁻¹ window, the 2026-07-20
  follow-up queue's item 1): cluster means 2693.7 vs 2697.6 cm⁻¹ —
  high-FWHM cluster blueshifted, per the practitioner prediction — but
  per-pixel scatter (±4.5) swamps the 3.2 cm⁻¹ mean separation at this
  SNR; FWHM separates better on this map.
- Differential read: **mixed-domain trilayer flake — low-FWHM body with
  coherent high-FWHM (ABC-candidate) patches.** Population separation
  (6.3) is below the ≳10 cm⁻¹ heuristic; morphology + screens carry the
  pattern. The call itself belongs to a fresh-instance run.

**`05` (stack):**

- Main body a single population 62.9 ± 1.7 cm⁻¹; a 55.1 cm⁻¹ sliver on
  the right edge. Whole-map 2D centers shifted ≈ +10 cm⁻¹ vs `04`
  (encapsulation-consistent).
- The video image and the two JPGs show hBN + graphite pieces already in
  the stack ⇒ **the through-stack screen applies from stage 05 onward**,
  not just at `06`.
- 8.0 mW in-fiber mapping is within an order of magnitude of the
  documented laser-conversion scale — the in-measurement-conversion
  hedge attaches to any stage-05 ABC-absence claim.

## Fresh-instance runs (2026-07-25)

- `raman-read-contract.md` — fresh instance, corpus-allowlisted, no
  sight of transport results or prior session records, executing
  `raman-stacking-id.md` on all three stages. Verdict set: R1 ABA
  (strong) / R2 ABC (strong) at flake stage (masked-split populations
  58.75 vs 63.95 cm⁻¹, magnitude hedge carried); stages 05/06 capped at
  consistent-with (through-stack); finished-device call refused as
  unsupported. Independently caught the Si-line saturation this note's
  first-pass terrace read missed.
- `fusion-contract.md` — second fresh instance fusing that contract
  with the locked 2026-07-16 transport call. **Fused: QC0426 probed
  device = ABA (strong), all covered channels concur**; headline
  mechanism is geometric — the mesa was fabricated from the interleaved
  R1/R2 zone and the coherent ABC core was never picked into the
  device (~25 µm away in GDS frame). sr2's domain share is
  registration-limited (cross-pickup non-rigid strain, ±2–3 µm); all
  four audits pass. Registration figures:
  `$HERA_DATA/raman-qc0426-fusion-2026-07-25/`.

## Fusion-path status

- Transport leg: the locked contract
  (`../2026-07-16-QC0426-session-3/hera_scratch/call_draft.md`) is
  admissible under fusion Step 1 (per-region verdicts, coordinates,
  hedges).
- Raman leg: `04` is the gate-clean map and carries the pre-fab
  stacking evidence the `06` read could not (through-stack correction,
  2026-07-18).
- Registration chain to contact pairs now exists end-to-end in supplied
  artifacts: `04` stage frame (video image) → `05` stack imagery →
  50x/100x marked-chip images → GDS marker/contact geometry → device
  card contact map. Weak link: `04`↔`05` correspondence across pickup
  (the flake tears into ribbons; deformation can exceed the µm domain
  scale — the registration-uncertainty clause decides coverage labels).
- Open stage question a fused call must carry: whether the device
  channel was built on the flake body or a high-FWHM patch, and what
  the intervening steps (pickup, e-beam, metal) imply under the
  conversion-directionality rule.

## What a grower Raman package carries / lacks (from this set)

Carries: raw spectral cubes and spot spectra with in-file wavelength,
in-fiber power, scan geometry, stage coordinates, timestamps;
stage-registered video images; marked-chip optical images with scale
bars; layout GDS. Lacks: at-sample laser power; an explicit build-step
list between acquisition stages; flake-stage calibrated optical contrast
for independent layer count (in-map proxies — thin-population FWHM,
Si-line attenuation — substitute, weakly); spot size (diffraction limit
assumed).
