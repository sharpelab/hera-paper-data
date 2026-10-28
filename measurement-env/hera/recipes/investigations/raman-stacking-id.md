# Trilayer stacking identification from Raman data (ABA vs ABC)

*Investigation — reads **supplied** Raman spectra or hyperspectral maps of a
trilayer-graphene flake/device and produces a spot-resolved stacking call.
This modality is data-analysis, not instrument-driving: the acquisition
already happened, usually on another instrument at another time — which is
why acquisition metadata and build-stage provenance are load-bearing inputs,
not details.*

**References**: the three ingested papers ground every claim —
`hera/docs/papers/1011.3021/paper.md` (Lui 2011 — 2D lineshape + FWHM
mapping), `hera/docs/papers/nn203472f/paper.md` (Cong 2011 — M-band/G-width
cross-checks, q = 2k mechanism), `hera/docs/papers/srep04630/paper.md`
(Nguyen 2014 — excitation systematics, two-wavelength rule). Extraction
tool: `hera/models/raman_stacking/` (validated on labeled public data —
see its README for the gates and calibration facts).

## What

Classify the stacking of trilayer graphene — ABA (Bernal) vs ABC
(rhombohedral) — **per spot / per mapped region** from Raman data, chiefly
the 2D-band lineshape. Output is a region-resolved, evidence-cited, hedged,
**stage-stamped** call: Raman evidence is about the flake *at map time*, not
about the device after subsequent processing.

## When

- Raman data for the flake/device exists (fabrication screening, a
  collaborator's characterization) and stacking bears on the science.
- As the second modality against a transport stacking call
  (`stacking-raman-transport-fusion.md` consumes this recipe's output).
- Prerequisite: none on the rig — this runs from files. Prerequisite on
  the data: acquisition metadata (Step 0). Data lacking metadata supports
  at most weak calls.

## Why

The 2D (G′) band is a double-resonance process sampling the electronic
bands near K; stacking changes those bands, which changes the resonant
phonon wavevectors (q ≈ 2k, larger in ABC — Cong, paper-data). Phonon
frequencies themselves are stacking-blind (Γ differences ≤ 0.2 cm⁻¹), so
**the contrast is electronic** and rides on the band structure — the same
physics transport reads, seen optically.

Discriminators, by strength (each with confounds inline):

- **2D-band width + lineshape (primary).** ABC: broader (single-Lorentzian
  FWHM), asymmetric, sharp peak + enhanced shoulder; ABA: narrower,
  smoother (Lui Fig. 2; validated on labeled public data — magnitudes in
  the tool README's gate table, not quoted here). Split the axes:
  *presence* of a broad population is weak alone; a *pattern* — bimodal
  FWHM populations forming spatially coherent domains with sharp walls —
  is strong; *magnitude* of the split (≳ 10 cm⁻¹ between population
  means, heuristic from the labeled sets) calibrates confidence. When
  pattern and magnitude disagree — coherent bimodal domains below the
  magnitude heuristic — the pattern sets the grade and the split size
  becomes a named hedge.
  **Confounds**: uniaxial strain broadens *and* asymmetrizes the 2D
  exactly like the ABC signature (0.1–0.2% suffices; strain shifts run
  −60…−140 cm⁻¹/% — citation, Mohiuddin PRB 79 205433 / Zabel NL 12 617);
  doping/disorder broaden (Lui: chemically processed samples can lose the
  contrast); **layer number raises FWHM** (validated: ABC 67→80 cm⁻¹ over
  N = 3–10), so a terrace step mimics a stacking wall; low-twist
  reconstructed t(1+2) presents a broad asymmetric 2D (citation, Gadelha
  2DM 9 025007); spectral resolution inflates FWHM (Lui mapped at
  8 cm⁻¹); **the probe integrates the whole vertical stack** — on a
  gated/finished device, graphite gates and any other graphene in the
  spot contribute their own (Bernal-like) 2D weight, and the collected
  band is a superposition the single-layer metrics cannot unmix (Verify:
  through-stack screen; QC0426 burn, 2026-07-17).
- **M band, 1690–2150 cm⁻¹ (secondary cross-check).** One dominant M⁻
  peak = ABA-consistent; split/multiple sharp peaks = ABC-consistent;
  iTOLA/LOLA ~10 cm⁻¹ blueshifted in ABC (Cong Fig. 2; Nguyen Fig. 3).
  **Confounds**: weak modes (needs SNR); assignments muddy near
  E_laser ≈ 2.1–2.4 eV (dispersive-mode crossing); prefer red
  excitation. At in-zone excitation treat the M read as uninformative —
  direction-inverted signatures are expected there, not anomalies.
  Practitioner note: lab convention weights the M-band and G-width
  channels at ~zero (PI review, 2026-07-17) — they stay here as
  *quantitative secondaries* for agent use, never the call.
- **G-band width (supporting only).** ABC narrower (Cong Fig. 6,
  FWHM(G) maps 18–24 cm⁻¹ window). **Confounds**: strain and doping both
  move G; a few-cm⁻¹ effect — confirming channel, never the call.
- **Ultra-low-frequency shear modes (decisive when present, rarely
  acquired).** ABA: C mode ~33 cm⁻¹, ABC: C′ ~19 cm⁻¹ — symmetry-
  forbidden in the other stacking (citation, Lui APL 106 041904;
  suspended samples, ULF filters). If the data includes < 50 cm⁻¹
  coverage, this alone can settle a spot.
- **Non-discriminators**: G position (~1 cm⁻¹ — below strain/doping
  systematics), layer-breathing modes (stacking-blind — citation, Lui
  APL 106 041904), absolute intensities (substrate interference
  modulates them — read widths and shapes, not brightness).

Four disciplines keep the read honest:

- **Differential, never absolute.** Absolute FWHM folds in instrument
  resolution and wavelength; classify by the **differential across one
  flake/map** (the two-population split) or against same-instrument
  references — Raman is only trustworthy as a differential measurement
  on the same flake. A lone spectrum with no reference supports at most
  consistent-with.
- **Wavelength is metadata.** Lineshape comparisons only at matching
  excitation energy; single-wavelength calls are legitimate only with the
  layer number independently known (Nguyen's two-wavelength rule).
- **Layer count before stacking.** FWHM grows with N; confirm the layer
  count (optical contrast / prior characterization) before reading width
  as stacking. A thickness terrace inside the map is the first
  alternative hypothesis for any "domain wall".
- **Per-spot reads; mixed spectra are mixtures.** Domains span any size,
  but µm-scale domains are common (Lui: ~40% of trilayers mixed, none
  purely ABC), so walls crossing the ~µm spot are the norm: a spot
  straddling a wall gives a linear combination (Lui SI), which FWHM
  thresholding mis-bins either way; an intermediate-FWHM spectrum with
  poor single-Lorentzian fit is a **mixed candidate, not a third
  category**. Domains *below* the spot size are invisible outright.

**Stage-stamping (the perishability rule).** ABC is the metastable
stacking; documented converters: laser heating at the ~10 mW scale
(~430 K local; mapping at ≤ 1 mW is safe by an order of magnitude —
citation, Zhang LSA 9 174), adsorbate chemistry + modest bake (citation,
Zhang NC 4 2074), **anisotropic strain from metal-contact deposition —
walls move by µm** (citation, Geisenhof AANM 2 6067), hBN pickup along
armchair (zigzag preserves — citation, Yang NL 19 8526). Conversion runs
**ABC→ABA only**; spontaneous ABA→ABC during processing is undocumented.
Every verdict therefore carries the acquisition stage and the list of
subsequent build steps; a pre-fab map constrains the finished device only
modulo those steps.

**Beyond trilayer (tetralayer+).** The 2D-FWHM discriminator is
family-level and validated across N = 3–10 (rhombohedral-family FWHM
exceeds Bernal-family at every N, separation growing with N — extraction
tool gates A/C, `hera/models/raman_stacking/README.md`); at N = 4 read
Bernal (ABAB) vs rhombohedral (ABCA) the same way, with the
within-one-map two-population split carrying the classification (Bernal
widths are nearly N-flat; rhombohedral widths grow with N, so absolute
thresholds transfer even worse across N). Trilayer-specific numbers in
this recipe (Lui's mixed-domain statistics, converter list) are N = 3
facts; treat the conversion direction — rhombohedral→Bernal only — as
the family-level rule. The mixed order ABCB is a two-way-FWHM blind spot
[citation, Wirth et al. arXiv:2203.07971 — not ingested]: FWHM alone may
not separate ABCB from ABAB (literature discriminates via G-peak
position and near-field imaging), so a Bernal-family FWHM call at N = 4
cannot exclude ABCB — hedge accordingly.

## Recipe

**Step 0 — inventory the data and its provenance (binding: produce the
table, not an acknowledgement).** For each file: excitation wavelength,
laser power, spot size, map step, spectral resolution/grating, raw vs
processed (background-subtracted? normalized?), acquisition date, and
**build stage** (what fabrication steps preceded the map; which followed
it, by risk class — metal deposition / transfer–pickup / chemical+bake /
clean thermal). Derived estimates satisfy the table when flagged as such
(spot size from objective NA, resolution from grating class); recorded
in-fiber power is not at-sample power — treat at-sample as unknown and
carry the conversion flag on the in-fiber value. Missing fields cap the
achievable strength: no wavelength
→ no lineshape comparison against references; no power → flag possible
in-measurement conversion if ≥ several mW; no stage → the call cannot be
mapped onto the finished device.

**Step 1 — layer count.** Establish N independently (optical contrast,
AFM, the supplier's characterization). If N is uncertain between 3 and 4,
the 2D read inherits that fork (Nguyen: ABC-3L vs ABC-4L needs blue
excitation) — report it, don't absorb it.

**Step 2 — per-spectrum 2D read.** Run the tool's metrics
(`raman_stacking/metrics.py`: single-Lorentzian FWHM, center, skew,
low/high ratio, fit r²) on every spectrum. Compare lineshapes against the
reference panels **at matching wavelength** (Lui Fig. 2; Nguyen Fig. 1).
Low r² with intermediate FWHM → mixed-spectrum candidate (Verify). Skew
and low/high ratio are secondary — their sign is excitation-dependent;
calibrate direction on the map's own populations, never assume it.

**Step 3 — map read (when a map exists).** Per-pixel metrics + junk-fit
rejection; **mask thickness populations before the split** (distinct
FWHM modes and amplitude steps belonging to other N) — a whole-map
split latches onto the thickness contrast and hides the stacking
bimodality. Then the two-population split
(`raman_stacking/map_tools.py`), trusted only where it is a population
structure (separation exceeding within-cluster spread, visible in the
histogram) — 2-means returns two clusters on any input, unimodal or
junk. Read the *morphology*: spatially
coherent clusters with sharp walls = domain pattern (strong); smooth
FWHM gradients tracking 2D-position shifts = strain field
(consistent-with strain, not ABC); population split co-locating with a
thickness terrace = layer-number artifact (uninformative for stacking).
Overlay spot/region coordinates on the flake image so the call is
spatially addressable downstream.

**Step 4 — cross-checks (as the data allows).** M-band region per
spectrum (red excitation preferred; away from the 2.1–2.4 eV crossing);
FWHM(G) map if G is covered; G-vs-2D position correlation to separate
strain from doping trends (citation, Lee NC 3 1024 — monolayer
calibration, use directionally). Where two independent channels agree on
a region, the verdict strengthens one grade; where they disagree, report
the conflict, not the average.

**Step 5 — stage-stamp the verdict.** From Step 0's build timeline:
verdict is "as of stage S". List post-map steps with their conversion
risk. Directionality: post-map processing can only have converted
ABC→ABA — a mapped-ABC region may be smaller/absent now; a mapped-ABA
region stays ABA (sub-spot ABC slivers and unmapped areas excepted).

**Step 6 — the call.** Output contract (all five parts mandatory):

1. Per-spot/per-region verdict on the strength scale (decisive / strong /
   weak / consistent-with / uninformative), each with its weight word and
   stage stamp: `region R (x,y µm, stage S): ABC (strong)`. Ship the
   region label mask/raster alongside the prose coordinates — fusion
   consumes the raster, and a prose-only region forces a lossy
   re-derivation downstream.
2. Evidence list: metric values with spectral coordinates (FWHM,
   population means, wavelength), the reference panel matched, map
   morphology, cross-check outcomes.
3. Confidence + named hedges: sub-spot blindness (domains below the spot
   size are invisible — this is structural, state it every time),
   wavelength coverage, resolution, unmapped areas, layer-count
   certainty.
4. What would firm it: second wavelength, M-band spectra, higher-res
   map, near-field imaging (s-SNOM resolves walls Raman cannot —
   citation, Kim ACS Nano 9 6765), or the transport check
   (`trilayer-stacking-fs-count.md`).
5. **A reasoned "cannot tell" (with the missing metadata or coverage
   named) is a successful outcome. A confident call without
   feature-level evidence is a protocol violation.**

## Verify

- **Tool gates current.** `raman_stacking/validate.py` green (all gates;
  count and table in the tool README) before trusting metrics on new
  data; the gates double as the worked example of every metric.
- **Strain-mimic screen (mandatory before any ABC verdict from width
  alone).** Broad-FWHM region + smooth spatial gradient + correlated 2D
  position shift → consistent-with strain; broad region + bimodal
  population + sharp walls + stable 2D position → strong ABC. Uniaxial
  strain is the one confound that reproduces both broadening *and*
  asymmetry.
- **Through-stack screen (mandatory on any post-gate / mid-stack map).**
  From the build stage, list every graphene layer in the spot besides
  the target (graphite gates, contacts, adjacent flakes). A map taken
  **through a graphite gate is weak at best for the buried channel** —
  the collected 2D superposes the gate stack's Bernal-like band with the
  target's, and the per-spectrum metrics cannot unmix them; cap the
  verdict at consistent-with unless the gate contribution is modeled/
  subtracted or a pre-gate map exists (which then carries the call).
  [heuristic, QC0426 burn 2026-07-17: a post-fab map of a
  graphite-gated device read "uniform ABA (strong)" — PI review
  identified the signal as substantially the gate stack.]
- **Terrace screen.** Any candidate domain wall checked against the
  thickness map (optical/AFM); a wall coinciding with a layer step is
  uninformative for stacking. Without an external thickness map, in-map
  proxies can rule a terrace out: G/2D amplitudes — and the substrate
  line (e.g. Si 520 cm⁻¹) where unsaturated — step across a layer
  change and match across a stacking wall. **Check the proxy line is
  unclipped first**: a saturated line reads as a perfect match
  [heuristic, QC0426 flake map 2026-07-25 — Si line saturated, 2D
  amplitude carried the screen].
- **Twist screen (history-triggered only).** Run when the flake history
  suggests it — fold/tear/wrinkle near the region or a transfer anomaly;
  fabricated devices rarely warrant it. Trigger: moiré features or a 2D
  band decomposable as 1L+2L superposition → twist-contamination fork
  (citation, APL 118 133101): report, don't refine.
- **Mixed-spectrum decomposition.** For straddling candidates, run
  `raman_stacking/metrics.decompose_mixed` against the map's own
  population means; α in (0.2–0.8) (heuristic) → report as
  mixed/boundary, not as either stacking.
- **Excitation-transfer ban.** No threshold, reference lineshape, or
  skew direction crosses wavelengths; re-anchor on same-wavelength
  references or the map's own populations.
- **Absence claims cite resolvability.** "No ABC found" requires: map
  coverage stated, spot/step vs expected domain scale, power ≤ ~1 mW
  (else the measurement itself may have erased domains), pristine
  surface (processing broadening obscures contrast — Lui). Otherwise the
  outcome is "not resolved", not "absent".

## Examples

- QC0426 worked example (our-measurement,
  `hera/docs/notes/2026-07-17-QC0426-raman-fusion/raman-read/` + the
  correction in its README): a grower-supplied WITec project read
  end-to-end via `load_wip`. The read called uniform ABA (strong);
  **PI review identified the map as substantially probing the graphite
  gate stack** (post-fab device, graphite gates — Bernal-like 2D from
  the gates superposed on the channel's), and the verdict was downgraded
  to consistent-with — the burn that produced the through-stack screen
  (Verify). Mechanical lessons that stand: one of two scans proved
  partial *and* defocused (caught by Step 0 + per-pixel quality metrics);
  the single Spot spectrum landed on bare substrate (uninformative).
  Stage lesson: imagery-inferred stage stamps (both agents') were
  settled only by the grower — carry them as hedged inferences, never
  as established metadata.

- QC0426 pre-fab ladder (our-measurement,
  `hera/docs/notes/2026-07-25-QC0426-prefab-raman/`): maps of the same
  device at three build stages (flake / stack / finished device). Only
  the flake-stage map is gate-clean — graphite enters at the stack
  stage, so the through-stack screen triggers mid-ladder. Also the
  worked case for masking thickness populations before the split, the
  bimodality gate, and proxy-saturation checking (the flake map's Si
  line is clipped). Read details live in the note's contract.

- The FLG_37 mixed-flake map (labeled public data, 488 nm): per-pixel
  FWHM + two-population split resolved 60 vs 78 cm⁻¹ populations as
  spatially coherent domains with sharp walls; cluster means matched the
  deposit's labeled region averages to ~1 cm⁻¹
  (`hera/models/raman_stacking/README.md`, `flg37_map_validation.png`).
  Also the worked case for the layer-number discipline: the flake's 7-
  and 8-layer terraces carry distinct FWHM baselines.
- Metric calibration facts (which metrics are robust, which directions
  flip) live in the tool README's validation table — consult before
  weighting skew/ratio evidence.

## Next

- **Feeding fusion**: hand this contract's per-region verdicts to
  `stacking-raman-transport-fusion.md` for reconciliation with a
  transport call on the same device.
- **ABC-positive regions**: if the device/science depends on them,
  near-field imaging or the transport check before committing fridge
  time — Raman cannot see sub-spot structure or post-map conversion.
- **Ambiguous/strained/mixed**: the transport FS-count is the in-situ
  arbiter on the finished device; price it rather than re-arguing the
  same Raman data.
