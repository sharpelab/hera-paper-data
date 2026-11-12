# QC0426 Raman stacking read — raman-stacking-id output contract

Executed 2026-07-17 on `/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip`
per `hera/recipes/investigations/raman-stacking-id.md`. Extraction tool
`hera/models/raman_stacking/` — validation gates re-run before use: **7/7 pass**.
All coordinates below are in the WITec stage µm frame (the frame shared by the
scan position grids and the two video images' per-pixel µm grids), taken from
each dataset's embedded `position_grid` — directly usable for registration
against device contacts.

---

## Step 0 — data inventory and provenance

| Field | Spot1 | Scan LA--002 | Scan LA--004 |
|---|---|---|---|
| Type | single spectrum | map 61×61 px, 20×20 µm | map 51×51 px, 20×20 µm |
| Stage center (x, y) µm | (11.2, −4.3) | (−1.3, −1.1) | (0.6, −2.8) |
| Extent (stage µm) | point | x −11.4…+8.5, y −10.9…+9.0 | x −9.5…+10.3, y −12.5…+7.3 |
| Acquired | full | **partial: stripe y +2.2…+8.8 only** (21 of 61 lines, 1281 px; aborted at 5.9 h of ~13 h) | full (10.4 h) |
| Step | — | 0.328 µm | 0.392 µm |
| Excitation | 532.34 nm (2.329 eV) | same | same |
| Power (in fiber) | 4.00 mW | 4.11 mW | 5.99 mW |
| **Power at sample** | **not recorded** (fiber/objective losses unknown) | same | same |
| Integration | 30 s ×10 acc | 13 s/pt | 11 s/pt |
| Grating / sampling | 600 g/mm, −891…3652 cm⁻¹, 2000 pts (~2.3 cm⁻¹/px) | same | same |
| Objective / spot | 100×/0.9 (diffraction-limited ~0.4 µm expected; not recorded) | same | same |
| Raw/processed | raw counts (CCD saturates only at Rayleigh line; **0 saturated samples above 1200 cm⁻¹** in any credible pixel) | same | same |
| Date (local) | 2026-05-14 16:47 | 2026-05-14 17:11 | 2026-05-15 (start ~day after 002) |
| Scan rotation | — | 0.5° | 0.5° |

**Build stage: formally UNKNOWN** (pending grower's answer). However the two
in-file video images (2240×1680, stage-registered) show a **fully fabricated
device at map time**: gold leads from all sides landing on an etched
comb-shaped mesa (central channel + many contact arms), Raman-dead exactly
where metal covers the stack. The maps are therefore internally evidenced as
**post-metallization / post-etch** — the highest-risk ABC→ABA converter (metal
deposition, Geisenhof) *precedes* the map. This is internal evidence, not
grower confirmation; verdicts below are stamped "stage: post-fab (apparent,
unconfirmed)". Post-map steps: none documented.

**Missing fields and what they cap:** at-sample power unknown → any
absence-of-ABC claim is capped (in-measurement conversion at the several-mW
scale cannot be strictly excluded; documented conversion scale ~10 mW, safe
mapping ≤1 mW — Zhang LSA 9 174); no AFM/optical thickness map → N rests on
fabrication records; single wavelength → cross-wavelength lineshape
confirmation unavailable; stage unconfirmed → pre-fab stacking history cannot
be reconstructed from this file.

**Scan002 data-quality flag:** its Raman signal is ~100× weaker than scan004
(median 2D amp 84 vs 9833 counts; G amp ~166 vs ~22000) at comparable power —
defocus/misconfiguration, consistent with its mid-scan abort and next-day
rerun as scan004. Scan002 supports aggregate reads only; its per-pixel FWHM
is fit-noise dominated.

## Step 1 — layer count

N = 3 from fabrication records only; no independent AFM/optical map supplied.
Raman-internal consistency: the 2D lineshape at 2.33 eV matches the trilayer
reference row (Nguyen Fig. 1); the edge minority pixels (below) look
thinner-like, the mapped interior is uniform. Per Nguyen's two-wavelength
rule a single-wavelength call is legitimate **only because N is independently
asserted**; if N were actually 4, the Bernal-vs-rhombohedral direction of the
call survives (ABAB-4L vs ABC-4L separate the same way at 2.33 eV) but the
exact N inherits the record's uncertainty. Reported as a fork, not absorbed.

## Steps 2–3 — 2D reads

**Spot1 (11.2, −4.3):** no 2D band, no G band (window max ≈ 5% over a flat
background). Registered position is bare substrate right of the device in
both video images. It is a background/substrate reference, not a graphene
spectrum. **Uninformative** (by design, apparently).

**Scan004 (primary):** 543/2601 px carry a credible 2D band (junk-fit gates:
SNR ≥ 8×, FWHM 15–200, r² > 0.4); footprint reproduces the mesa channel +
contact-arm comb exactly (metal-covered stack is Raman-dark).

- Main population: **n = 521, single-Lorentzian FWHM 63.7 ± 0.7 cm⁻¹** —
  essentially one delta-function population (5–95%: 61.3–65.1). 3×3 spatial
  block means all within 63.3–64.1; spine 63.8 ± 0.5, upper arms 63.8 ± 0.9,
  lower arms 63.5 ± 0.8. **No bimodality, no domains, no walls anywhere in
  the mapped area.**
- 2-means split lands at 55.7 / 63.7 cm⁻¹ but the low cluster is 22 scattered
  perimeter pixels (edge/boundary; see Verify), not a spatial domain.
- 2D center 2703.7 median (5–95%: 2700.1–2705.2); mildly redder on the spine
  (2704.3 ± 0.7) than the arms (2703.3 ± 1.2).
- Mean-spectrum lineshape (main population): dominant maximum at ~2712 cm⁻¹
  with a low-frequency shoulder/knee at ~2685, steeper high side;
  single-Lorentzian FWHM 63.9, r² 0.971, moment skew −0.00, ratio_lh 1.19.
- **Reference match at 2.33 eV** (excitation-matched panels only):
  - Nguyen Fig. 1, 3LG row, 2.33 eV trace: ABA = rounded single max with
    low-side tail — **matches**; ABC = sharp low-frequency feature + enhanced
    high-side shoulder (double-humped) — **does not match**.
  - Cong Fig. 8c/8d (2.33 eV six-Lorentzian panels): ABA (8d) single dominant
    high-frequency max with low-side shoulder — **matches our lineshape
    point-for-point in morphology**; ABC (8c) two comparable humps ~2685/2715
    with a dip — absent in our data.
- Scan002 aggregate agrees: mean spectrum over its 456 credible px gives FWHM
  62.5, center 2704.6, r² 0.971, same single-humped shape (overlay in
  `lineshape_panels.png`); its 170-pair overlap with scan004 agrees in median
  FWHM to 1.8 cm⁻¹ (per-pixel correlation nil, as expected at its SNR).

**Scan002 (partial stripe y +2.2…+8.8):** covers the mesa top edge and the
upper-left gate-lead region; only ~10 credible px fall outside scan004's
footprint (x −10…−3.5, y 4.6…7.6), mean-spectrum FWHM 62.0, same lineshape —
nothing qualitatively new, low weight.

## Step 4 — cross-checks (all at 2.33 eV, matched to references)

- **M band (Cong Fig. 2, same energy; Nguyen Fig. 3):** one dominant M⁻ peak
  at **1746 cm⁻¹** (only peak with prominence > 25 cts in 1700–1810; prom.
  150 cts on a mean of 521 px), small M⁺ satellite ~1773, broad iTOLA/LOLA
  hump peaking ~2010–2020 with its falling edge at the ABA position (~2020)
  rather than the ABC position (~2030). **Single M⁻ = ABA-consistent; no
  split, no +10 cm⁻¹ blueshift.** Hedge: 2.33 eV sits inside the 2.1–2.4 eV
  dispersive-crossing window — mitigated by comparing against Cong's own
  2.33 eV panel rather than mode assignments, but a red-excitation M spectrum
  would be cleaner.
- **G band (Cong Fig. 6 channel):** G at 1578.2 median, FWHM 13.8 median,
  spatially uniform — no domain pattern in FWHM(G), consistent with a
  single-stacking map. (Absolute G width is instrument-relative; used only
  as a uniformity/pattern channel.)
- **G-vs-2D positions:** both vary by ≲ ±1.5 cm⁻¹, smoothly, with no
  accompanying FWHM change — small strain/doping texture only.
- **ULF shear modes:** axis nominally covers < 50 cm⁻¹ but the region is the
  saturated Rayleigh wing (65535 at 0 cm⁻¹, smooth decay through 15–45) — no
  ULF filter, channel unavailable.
- **G\* window (Nguyen Fig. 2):** band visible at ~2441 with high-side
  shoulder; ABA/ABC contrast at 2.33 eV is weak (their contrast grows toward
  blue) — not weighted.
- hBN E₂g at 1361 cm⁻¹ confirms encapsulation; it overlaps the D window, so
  a D/G disorder read is not available.

## Verify screens

- **Tool gates:** 7/7 pass (validate.py, this session).
- **Strain-mimic:** no broad population exists to explain away; FWHM is flat
  (±0.7 cm⁻¹) while 2D position moves ±1.5 cm⁻¹ smoothly — strain texture
  without broadening. The formal corr(FWHM, center) = +0.70 in scan004 spans
  a < 2 cm⁻¹ FWHM range — not a strain-broadened subpopulation. Passed.
- **Terrace:** no thickness map supplied. No candidate stacking wall exists
  to test; the only minority population is *narrower* + redshifted (2696.9,
  FWHM ~55.9) — a thinner/edge signature, which cannot mimic ABC (mimicking
  ABC requires *broader*). Passed with the no-AFM caveat.
- **Twist:** no folds/wrinkles inside the mesa in either video image; no
  moiré features; main-population band is not decomposable as 1L+2L (single
  smooth trilayer band, r² 0.97). Edge pixels show a 2L-like band — flagged
  as edge, not twist. Passed.
- **Mixed-spectrum (decompose_mixed):** 28 px with FWHM below the main 5th
  percentile, decomposed against the map's own population means: α spans
  0→1 with several mid-α (0.2–0.8) wall-type mixtures; **all 28 sit on the
  mesa perimeter**. Reported as boundary/edge mixtures, not a third phase
  and not a stacking domain.
- **Excitation-transfer ban:** every lineshape/M-band comparison above is at
  2.33 eV (Nguyen 2.33 traces; Cong Fig. 2 and Fig. 8c/d). Lui's 514 nm
  panels were not used for the call. PKU absolute FWHM values quoted nowhere
  as thresholds. Passed.
- **Absence-claim resolvability:** coverage = the exposed (unmetallized)
  mesa within scan004's 20×20 µm window at 0.392 µm step, ~0.4 µm spot —
  domains ≳ 1 µm would be resolved. Power: at-sample unknown (6 mW in
  fiber); above the ≤1 mW discipline threshold, so the claim is stated as
  **"no ABC resolved"**, not "ABC absent", with the in-measurement-conversion
  hedge. Surface: encapsulated, D-band read unavailable but 2D/G lineshapes
  are sharp and pristine-like.

## Step 5 — stage stamp

Stage S = **post-fabrication (apparent from in-file video images; grower
confirmation pending)**. Post-map risk steps: none documented. Directionality:
documented conversion runs ABC→ABA only, so the mapped-ABA regions remain ABA
in the finished device regardless of any later clean processing; conversely,
**nothing in this file constrains the flake's pre-fabrication stacking** —
metal deposition (already on the device at map time) is a documented converter
that moves walls by µm, so an originally-ABC flake could have converted before
this map was taken.

## Step 6 — the call

### 1. Per-region verdicts (stage S = post-fab apparent, unconfirmed)

| Region (stage µm frame) | Verdict |
|---|---|
| R1 — mesa channel/spine: x −7…+8, y −4.5…+0.5 (scan004, 267 px) | **ABA / Bernal (strong)** |
| R2 — upper contact arms: x −9.5…+8, y +0.5…+6.5 (scan004, 107 px) | **ABA / Bernal (strong)** |
| R3 — lower contact arms: x −8.5…+8.5, y −11.5…−4.5 (scan004, 147 px) | **ABA / Bernal (strong)** |
| R4 — mesa perimeter pixels (28 px scattered on region edges, scan004) | mixed/edge — **uninformative for stacking** (thinner/edge signature) |
| R5 — mesa top + upper-left lead area: x −11.4…+8.5, y +2.2…+8.8 (scan002 stripe, defocused) | **ABA (weak / consistent-with)** — aggregate lineshape only |
| Spot1 (11.2, −4.3) | substrate, no graphene bands — **uninformative** |
| Graphene under metal contacts; everything outside the two 20×20 µm windows | **unmapped** — no claim |

No ABC-consistent region was resolved anywhere in the mapped area.

### 2. Evidence

- Primary: 2D band at 532.34 nm (2.329 eV). Main population n = 521 px:
  single-Lorentzian FWHM 63.7 ± 0.7 cm⁻¹, unimodal (histogram
  `fwhm_histograms.png`); mean lineshape = dominant max 2712 + low-side
  shoulder 2685, r² 0.971, skew ≈ 0 — matches ABA-3L and excludes the
  double-humped ABC-3L morphology at the same excitation (Nguyen Fig. 1 3LG
  2.33 eV; Cong Fig. 8c vs 8d). Morphology read is qualitative
  (shape-vs-shape), so it survives the no-absolute-FWHM-transfer rule.
- Map morphology: no two-population split, no walls; FWHM flat across spine
  and all arms (`scan004_metric_maps.png`, `segmentation_maps.png`).
- Cross-check 1 (M band, same energy): single M⁻ at 1746 cm⁻¹ + M⁺ ~1773,
  LOLA edge at ABA position (`mband_comparison.png`) — ABA-consistent.
  Independent channel agreement → verdict raised one grade to **strong**.
- Cross-check 2 (G band): FWHM(G) map uniform (13.8 median) — no domain
  pattern; supporting only.
- Scan002 (independent acquisition, lower power, different day-focus):
  aggregate FWHM 62.5 / same lineshape — consistent replication.

### 3. Confidence + named hedges

- **Sub-spot blindness (structural, always):** domains below the ~0.4 µm
  spot / 0.39 µm step are invisible; ABC slivers at that scale, and under
  the metal contacts, cannot be excluded.
- **Single wavelength:** all calls rest on 2.33 eV; no red/blue
  confirmation. Legitimate only because N = 3 is taken from fabrication
  records — the (N, stacking) joint read is not independently closed.
- **Layer count:** N = 3 is records-only; no AFM/optical map in the file.
  If N were 4 the Bernal-family direction survives but the stamp changes.
- **M-band crossing window:** 2.33 eV is inside the 2.1–2.4 eV
  dispersive-crossing region; mitigated by same-energy panel comparison,
  not eliminated.
- **Power:** at-sample power unrecorded (4–6 mW in fiber). The
  no-ABC-resolved statement is capped accordingly; and this map cannot
  speak to pre-fab stacking (metal deposition preceded it).
- **Coverage:** scan002 is a partial, defocused map; scan004's credible
  pixels are only the exposed mesa (543/2601 px of the window); Spot1 is
  substrate. Areas outside the windows are unmapped.
- **Resolution:** 600 g/mm at ~2.3 cm⁻¹/px sampling — mapped FWHM values
  are instrument-inflated (Lui caveat) and were used only relatively /
  morphologically.

### 4. What would firm it

- A red-excitation (633 nm) spectrum set: strongest 2D contrast + clean
  M-band away from the crossing (Lui, Nguyen); a blue point would close the
  (N, stacking) joint assignment.
- Grower's answers: build stage of these maps, at-sample power, and an
  AFM/optical layer-count map.
- ULF (< 50 cm⁻¹, with filters): C ~33 cm⁻¹ vs C′ ~19 cm⁻¹ would be
  decisive per spot.
- s-SNOM for sub-spot walls; transport FS-count
  (`trilayer-stacking-fs-count.md`) as the in-situ arbiter on the finished
  device — feed this contract to `stacking-raman-transport-fusion.md`.

### 5. Honesty clause

The strongest defensible statement is: *the Raman-visible, unmetallized parts
of this device were uniformly Bernal (ABA)-consistent at map time
(2026-05-14/15), with no rhombohedral domain resolved at ≳ 1 µm scale.*
Whether the flake was ABC before fabrication, and what lies under the
contacts, this file cannot tell — those are named coverage/metadata gaps, not
resolvable by more analysis of the same data.

---

## Files produced (all in /tmp/qc0426-raman-read/)

- `result.md` (this contract)
- `scan002_metric_maps.png`, `scan004_metric_maps.png` — 2D/G metric maps, stage frame
- `segmentation_maps.png` — FWHM 2-means label maps
- `fwhm_histograms.png` — per-map FWHM distributions + cluster centers
- `lineshape_panels.png` — 2D lineshape + fit, population comparison, M-band + G* windows
- `mband_comparison.png` — M-band vs Cong 2.33 eV mode positions
- `mean_full_range.png` — full-range mean spectrum (log)
- `video_images_scanboxes.png` — both video frames, stage frame, with scan
  outlines (incl. scan002's acquired stripe) and Spot1 marker
- `nguyen_3lg_zoom.png` — enlarged reference crop used for the 2.33 eV match
- `d_g_windows.png` — D/hBN, G, high-frequency windows
- `spot1.npz`, `scan002_metrics.npz`, `scan004_metrics.npz`, `mean_spectra.npz` — arrays
- `s0_inventory.py` … `s4_spectra.py` — the analysis scripts (rerunnable)
