# Stacking identification — flake FLG_37, map_488nm.txt

Executed per `recipe.md` ("Trilayer stacking identification from Raman data"),
generalized to the few-layer flake at hand (N = 7/8, not 3): layer count
first, relative-not-absolute, per-spot reads, stage-stamping all applied.
Analysis code: `analyze.py`, `screens.py`, `screens2.py` (this directory);
figures `fig_maps.png`, `fig_spectra_wall.png`; cached metrics `metrics.npz`.

## Step 0 — data + provenance inventory

| Field | Value | Consequence |
|---|---|---|
| File | `data/map_488nm.txt` — WITec ASCII map export, flake `FLG_37`, scan `Scan Piezo--013` | loads via `raman_io.load_witec`, column (x/y) order confirmed (2160 cols = 48×45) |
| Excitation | 488 nm (2.54 eV) | single wavelength; lineshape comparisons anchored on the map's own populations only |
| Laser power | **not recorded** | in-measurement ABC→ABA conversion cannot be excluded; observed ABC extent is a lower bound; absence claims capped |
| Spot size | not recorded (confocal WITec; assume ~0.3–0.5 µm at 488 nm) | sub-spot blindness threshold unknown but sub-µm |
| Map geometry | 48 × 45 px over 32.0 × 30.0 µm → 0.667 µm step | step is domain-scale-adequate for the µm-scale domains seen |
| Dwell | 20 s/point | long dwell compounds the unrecorded-power hedge |
| Spectral axis | 2269.5–5814.2 cm⁻¹, 1600 pts, ~2.19 cm⁻¹/px | **2D band only.** No G (needs <1650), no M band (1690–2150), no ULF. Cross-check channels unavailable → single-channel call, capped at *strong* |
| Grating | 600 g/mm | ~2.2 cm⁻¹ sampling; resolution does not threaten a 17 cm⁻¹ split |
| Processing | background-subtracted (Sub BG), cosmic-ray removed (CRR) | widths/shapes usable; absolute intensities already untrusted per recipe |
| Acquired | 2023-10-11 | stage stamp date |
| Build stage | **pristine, post-exfoliation** — no contacts, no pickup, no bake before the map; no steps documented after it | verdict stamps "as of exfoliated flake, 2023-10-11"; no post-map conversion risk *on record* |
| Layer count | supplier optical contrast / AFM: two terraces, **7 and 8 layers**, thicker graphite at one edge | N known independently → single-wavelength read legitimate (Nguyen rule); N ≠ 3 → family-level call (see hedges) |

Tool gate note: `raman_stacking/validate.py` is not present in this sandbox,
so the 6/6 gate could not be re-run here; the tool modules supplied
(`metrics.py`, `map_tools.py`) are the recipe's named metric set, and the
population means recovered below (61 / 78 cm⁻¹) reproduce the README's
validated thicker-flake values (ABA 61 vs ABC 78 cm⁻¹) to ~1 cm⁻¹.

## Step 1 — layer count

N = 7 and 8 (two terraces) from the supplied optical/AFM characterization —
independent of Raman, as required. Not a trilayer: the ABA/ABC labels below
mean **Bernal-family vs rhombohedral-family (ABC-rich) stacking**, not a
literal three-layer sequence. The 7-vs-8 fork is carried, not absorbed: it
is shown below (terrace screen) to move 2D FWHM by <1 cm⁻¹ and therefore
does not touch the stacking read.

## Steps 2–3 — per-pixel read and map morphology

1091 / 2160 pixels carry a credible 2D band (SNR + junk-fit gates of
`map_tools.per_pixel_metrics`); the rest are substrate. 14 further pixels
along the top flake edge (y ≈ 2.7–6.7 µm) fit with center ≤ 2700 cm⁻¹ and
FWHM ~22–30 cm⁻¹ — monolayer-like or edge artifacts; excluded and stamped
uninformative.

**Two-population split on 2D FWHM (map-internal, relative):**

| population | n px | FWHM (cm⁻¹) | 2D center (cm⁻¹) | fit r² | integrated 2D |
|---|---|---|---|---|---|
| narrow ("ABA-like") | 629 | **60.9 ± 3.0** | 2727.8 ± 2.6 | 0.969 | 49.2 k |
| broad ("ABC-like") | 448 | **77.9 ± 2.3** | 2723.3 ± 1.6 | 0.964 | 41.8 k |

- **Split magnitude 17.0 cm⁻¹** between population means — well above the
  ≳10 cm⁻¹ confidence heuristic. Histogram is deeply bimodal (modes 60 and
  78; valley 63–76 holds ~130 px, almost all at walls).
- **Morphology (fig_maps.png):** the broad population forms two large,
  spatially coherent, straight-walled domains embedded in one connected
  narrow-population background — the domain pattern, not noise and not a
  gradient.
- **Wall sharpness:** median |∇FWHM| = 8.2 cm⁻¹/px at walls vs 0.5 cm⁻¹/px
  in domain interiors; the wall transition profile (fig_spectra_wall.png)
  completes 60→78 cm⁻¹ within ~1.3 µm (2 px), i.e. unresolved at the
  spot+step scale.
- **Lineshape:** broad-population mean spectrum shows the enhanced low-side
  shoulder and structured top on a band peaking sharp on the high side —
  the ABC-like asymmetric lineshape; narrow-population mean is smoother and
  more symmetric (fig_spectra_wall.png, left). Secondary metrics (skew
  +0.067 narrow / +0.014 broad; ratio_lh 1.14 / 1.05) were calibrated on
  the map's own populations per the recipe; their directions at this
  wavelength/metric convention are not naively ABC-positive and were given
  no weight — the call rides on FWHM + morphology + lineshape.

## Verify screens

- **Strain-mimic (mandatory, passed):** broad regions show *stable* 2D
  center (σ = 1.6 cm⁻¹) and only −4.5 cm⁻¹ offset from the narrow
  population. Uniaxial strain sufficient to broaden by 17 cm⁻¹
  (~0.15–0.3%) would shift the 2D by −10…−40 cm⁻¹ and present smooth
  spatial gradients; observed walls are sharp and bimodal with a deep
  histogram valley. Broad + bimodal + sharp walls + stable center →
  **strong ABC pattern**, not strain. (Residual within-population
  FWHM–center correlations, r = +0.57 narrow / −0.44 broad on ~2 cm⁻¹
  scatter, indicate mild internal strain/doping texture — noted, does not
  approach the 17 cm⁻¹ split.)
- **Terrace screen (passed):** no registered AFM map was supplied, so the
  screen ran on the map's own integrated-2D intensity as thickness proxy.
  The visible intensity terrace *inside* the narrow region (+6.7%
  contrast, the plausible 7/8-layer step) changes FWHM by only
  −0.7 cm⁻¹; intensity sub-populations inside the broad domains differ by
  0.75 cm⁻¹. Thickness steps on this flake move FWHM by <1 cm⁻¹; the
  17 cm⁻¹ walls are therefore not layer-number steps. (Scale check from
  the validated table: ABC trend ~1.9 cm⁻¹/layer over N = 3–10; ABA flat.
  A 7→8 step cannot fake this split.) The broad domains do sit ~15% lower
  in integrated 2D intensity than the narrow background — co-located with
  the stacking walls; whether that is stacking-intrinsic or partially
  thickness cannot be settled without the registered thickness map (named
  hedge below).
- **Mixed-spectrum decomposition (passed):** 73 intermediate-FWHM pixels
  (65–73 cm⁻¹); 95% lie within 1.5 px of a wall; fitting
  α·mean_narrow + (1−α)·mean_broad puts 88% at α ∈ (0.2, 0.8). These are
  boundary mixtures from the spot straddling walls — reported as
  mixed/boundary, not as a third stacking.
- **Twist screen (no trigger):** no fold/tear/wrinkle history supplied; no
  1L+2L-decomposable bands in the interior; the monolayer-like top-edge
  strip (14 px, y ≈ 2.7–6.7 µm) is flagged but is outside both regions of
  interest.
- **Excitation-transfer ban (respected):** all thresholds and lineshape
  references are the map's own populations at 488 nm; the only external
  anchor is the same-tool validated 61/78 cm⁻¹ pair, quoted as
  corroboration, not as a threshold.

## Steps 5–6 — the call (output contract)

### 1. Per-region verdicts (stage: **as-exfoliated, pristine, map of 2023-10-11** — no fabrication steps preceded or, on record, followed the map)

Coordinates are map-frame µm (origin = map corner, 0.667 µm/px); pixel
indices (x, y) in the 48×45 grid.

- **Region A — narrow background** (619 px ≈ 275 µm²; spans x 0.7–26.0,
  y 6.0–28.7 µm; centroid (13.9, 18.0) µm; px x1–38, y9–42):
  **ABA / Bernal-family (strong)**, as of stage as-exfoliated.
- **Region B1 — broad domain, upper-left** (297 px ≈ 132 µm²; x 0.7–14.0,
  y 4.7–23.3 µm; centroid (6.5, 12.2) µm; px x1–20, y7–34):
  **ABC / rhombohedral-family (strong)**, as of stage as-exfoliated.
- **Region B2 — broad domain, lower-right** (136 px ≈ 60 µm²; x 16.7–30.0,
  y 17.3–26.0 µm; centroid (23.5, 22.4) µm; px x25–44, y26–38):
  **ABC / rhombohedral-family (strong)**, as of stage as-exfoliated.
- **Wall/boundary pixels** (~73 px lining the B1/B2 perimeters):
  **mixed/boundary (by decomposition)** — spot-straddling linear
  combinations, not a third phase.
- **Broad specks ≤4 px** near the lower-left edge (around (2–5, 23–28) µm)
  and three isolated px near (15–19, 6–7) µm: **weak** — plausible ABC
  slivers at/near the flake edge, below the coherence bar; not called.
- **Top-edge strip** (14 px, y ≈ 2.7–6.7 µm, center ≤ 2700, FWHM
  ~22–30 cm⁻¹): **uninformative** for this flake's stacking
  (monolayer-like/edge artifact).
- **Unmapped/substrate pixels** (1069 px): no 2D band — no claim.

Directionality note: since no post-map processing is documented, the map
should describe the flake as it stands; if any processing has in fact
occurred since 2023-10-11, conversion runs ABC→ABA only — B1/B2 may have
shrunk, Region A stays Bernal (sub-spot slivers excepted).

### 2. Evidence

- Two-population split of single-Lorentzian 2D FWHM at 488 nm:
  60.9 ± 3.0 vs 77.9 ± 2.3 cm⁻¹, Δ = 17.0 cm⁻¹ (map-internal, relative);
  deeply bimodal histogram (modes 60/78, near-empty valley).
- Population means reproduce the tool's validated same-metric thick-flake
  ABA/ABC pair (61 vs 78 cm⁻¹) — corroboration at matching metric
  definitions.
- Morphology: two spatially coherent straight-walled broad domains in a
  connected narrow background; wall |∇FWHM| 8.2 vs 0.5 cm⁻¹/px interior;
  60→78 transition complete in ~1.3 µm.
- Lineshape: broad-population mean shows the ABC-type enhanced low-side
  shoulder + asymmetric top (fig_spectra_wall.png) vs the smoother
  narrow-population band — matching the Lui-type contrast pattern
  (reference panels compared at the pattern level only; no cross-wavelength
  thresholds used).
- 2D center stable in broad domains (2723.3 ± 1.6 cm⁻¹, −4.5 cm⁻¹ vs
  narrow) — kills the strain-mimic explanation for a 17 cm⁻¹ broadening.
- Terrace decoupling: intensity terrace inside Region A (+6.7%) shifts
  FWHM −0.7 cm⁻¹; intensity substructure inside B1/B2 shifts it
  <0.8 cm⁻¹.
- Mixed-pixel decomposition: intermediate pixels are wall-localized (95%)
  and fit as α-mixtures (88% with α ∈ 0.2–0.8).
- Cross-checks (M band, G width, G-vs-2D correlation, ULF): **not
  available** — spectral coverage starts at 2269.5 cm⁻¹. No second channel
  agrees or disagrees; the verdict is single-channel.

### 3. Confidence and named hedges

Strong (not decisive) for all three regions. Named hedges:

1. **Sub-spot blindness (structural, always):** domains below the
   ~0.3–0.5 µm spot / 0.667 µm step are invisible; walls are placed only
   to ~±1 px; Region A may contain ABC slivers below this scale.
2. **Laser power unrecorded (+ 20 s/pt dwell):** if mapping power was at
   the multi-mW scale, the measurement itself could have converted
   ABC→ABA during acquisition — the mapped ABC extent is a lower bound and
   any "no ABC here" reading inside Region A is *not resolved* rather than
   absent.
3. **Single wavelength (488 nm):** legitimate because N is independently
   known, but there is no second-excitation confirmation of the lineshape
   assignment; all lineshape anchors are map-internal.
4. **No cross-check channel:** 2D-only coverage. A single-channel call
   cannot be upgraded past strong under this recipe.
5. **Layer count / family-level call:** N = 7/8, not 3. At N ≥ 4,
   intermediate stackings (ABCB…, mixed sequences) exist; "ABC (strong)"
   here means rhombohedral-rich stacking through a substantial fraction of
   the stack, not a verified pure ABC sequence of 7–8 layers. The 7-vs-8
   fork itself is shown not to matter for the split (<1 cm⁻¹).
6. **Terrace registration:** no spatially registered AFM/optical map was
   supplied; the terrace screen used the map's own intensity proxy. The
   15% intensity offset co-located with the B1/B2 walls is unexplained-
   but-bounded: thickness cannot produce the FWHM split, but the exact
   terrace geometry vs domain geometry is unverified.
7. **Tool gate:** `validate.py` not runnable in this sandbox (not
   supplied); metrics corroborated instead against the validated
   population values they reproduce.

### 4. What would firm it

- Second excitation wavelength (e.g. 532 or 633 nm) over the same area —
  population split reproducing at matching Δ pattern upgrades toward
  decisive (and 633 nm opens a cleaner M-band window).
- Extended spectral coverage: M band (1690–2150 cm⁻¹) and G band per
  pixel — an independent channel agreeing on B1/B2 adds a grade.
- Registered AFM/optical thickness map overlaid on the label map — closes
  hedge 6 outright.
- Re-map at recorded ≤1 mW power — closes hedge 2 and licenses absence
  claims inside Region A.
- s-SNOM near-field imaging for wall positions below the spot scale;
  ULF (<50 cm⁻¹) shear-mode spectra at one point per region would be
  decisive per spot.
- If this flake becomes a device: the transport FS-count check
  (`trilayer-stacking-fs-count.md` analogue for N = 7/8) as the in-situ
  arbiter on the finished device.

### 5. Protocol statement

This is a positive call, not a cannot-tell: the primary discriminator is
present at full strength (17 cm⁻¹ bimodal split, coherent sharp-walled
domains, ABC-type lineshape, strain and terrace screens passed), with the
evidence itemized above at feature level. The missing metadata (laser
power) and missing channels (M/G/ULF, second wavelength) are what hold the
verdict at **strong** rather than decisive, and are named as hedges 2–4.
