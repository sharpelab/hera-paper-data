# vti-02 — fused stacking verdict (Raman × transport, 2026-08-27 run over the 2026-08-22 session)

Recipe: `stacking-raman-transport-fusion.md`, Step 5 output contract.
Bases: `tetralayer-stacking-fs-count.md` (transport, per device-card
material line: tetralayer graphene) and `raman-stacking-id.md` (Raman,
family-level N = 4 reading).

## Headline

**Channel B_1−B_2 (the only wired 4T pair): ABAB (Bernal), strong —
single-modality (transport).** The Raman leg (`raman.md`, the device
group's fab record) fails admissibility on the evidence and coordinates
axes — no spectra, no acquisition metadata, no positions — and is not
fusible; it enters only as a consistency narrative. Its apparent
disagreement with transport (pre-stacking ABC lean vs in-situ ABAB) is
**conversion-consistent** (rhombohedral→Bernal, with named risky steps:
contact-metal litho > stacking pickup > anneal) and on no reading produces
an unreconciled conflict. No fused upgrade is claimed anywhere; no
per-device verdict is issued.

This is the degraded outcome the recipe anticipates: a fused verdict that
is honest about carrying one modality, not a forced concordance.

## Step 1 — admissibility + independence

Full audit: `admissibility-audit.md`.

- **Transport contract** (`transport-call.md`): admissible on every axis —
  weight words, six-item evidence list with per-tone coordinates, named
  channel, hedges, provenance. Verified verbatim-identical to ana notebook
  cell 23 (`20260822_ana.ipynb`, parsed as JSON; diff clean).
- **Raman contract** (`raman.md`): **not fusible.** Axis failures:
  evidence (no feature-level values — a bare verdict; spectra "pending
  from Ben"), Step 0 metadata (wavelength/power/spot size/date all
  unknown — caps achievable strength at weak even with data), positions
  (no coordinates, mask, or raster of the rhombohedral domain), layer
  count (N not established within the document), absence-claim
  resolvability ("no ABA in the cut region" cites no coverage/power →
  "not resolved", not "absent"). Axis passes: stage stamp (pre-stacking,
  parent flake — with an internal stage conflict, see hedges). The
  document's "Lean: ABC / Strength: strong" is assessed, not inherited:
  it cannot be sustained above **unassessed testimony**.
- **Independence: PASS.** Neither call cites the other's evidence (whole
  notebook scanned; the fab record predates the session); the transport
  call opposes the fab-record lean, corroborating non-shaping.

Consequence: rows the Raman leg would have covered degrade to
single-modality; the fusion carries a consistency narrative in place of a
fused Raman weight.

## Step 2 — spatial registration

Artifact: **`registration-artifact.md` + `registration_chain.png`**
(script `make_registration_figure.py`).

- Registration uncertainty: **not quantifiable** — zero anchors on the
  Raman side (no positions of any kind), no device image/GDS on the
  transport side, three transfer/processing boundaries between the frames.
- Domain scale: **unknown** (no map, no spot size).
- Coverage of channel sr1 (B_1−B_2), and of regions A and B separately:
  **uncovered**. The sole linkage ("cut region ⊂ rhombohedral domain") is
  uncoordinated testimony and cannot establish coverage. No interpolation.

## Step 3 — temporal registration

Raman stage stamp: pre-stacking, on the parent flake (acquisition date
unknown). Build steps between the last Raman and the transport
measurement (2026-08-22), tagged by conversion-risk class per
`raman-stacking-id.md`:

| Step | Risk class | Note |
|---|---|---|
| Laser cut | local heating | Stage fork: `raman.md`'s preamble lists the cut as post-dating the read, while its findings say the domain "survived the cutting process" (implies a post-cut read). Unresolved — carried as a fork either side of the last Raman |
| Stacking (pickup) | transfer/pickup | Documented converter (hBN pickup along armchair) |
| Anneal | chemical + bake | Documented converter |
| Litho / contact metal | **metal deposition (highest)** | Documented: anisotropic strain from contact deposition moves walls by µm; contacts B_1/B_2 bound the measured channel |

Only one Raman stage exists — no map differencing available.
Directionality: all listed risks run ABC→ABA only.

## Step 4 — per-region fusion table

| Channel / region | Transport verdict + strength | Raman verdict + strength + stage | Fused verdict + strength | Mechanism class |
|---|---|---|---|---|
| **sr1 = B_1−B_2** (only wired 4T pair; regions A + B in series; call is for the dominant region A) | ABAB (Bernal), **strong**, in-situ 2026-08-22 | Not fusible; coverage **uncovered**. (Fab-record testimony: ABC lean, stage pre-stacking, unassessed) | **ABAB (Bernal), strong** — transport strength carried, no fused upgrade | **Single-modality (transport)** |
| — sub-row: region B (faint parallel CNP ridge, +0.43×10¹² cm⁻², weak series weight) | Uninformative alone (no attributable tone set above floor) | Not fusible; **uncovered** | **Cannot tell** | Single-modality (no informative leg) |
| Device footprint = "cut region" (the only region `raman.md` names; resolves no sub-regions) | Sampled only through B_1−B_2 (row above); rest of footprint unprobed | ABC, stated "strong" → assessed **not fusible** (bare verdict, no coordinates/metadata), stage pre-stacking | **No device-level fused verdict.** Probed channel: ABAB (strong); remainder: uncovered | Single-modality + consistency narrative (below) |

**Consistency narrative (not a mechanism-class assignment).** Taking the
fab record at face value would give Raman-rhombohedral (pre-stacking) vs
transport-Bernal (now) — the reconciled-by-conversion geometry, with the
required risky steps named in Step 3 (contact metal deposition foremost).
The class itself is unavailable because reconciliation-by-conversion
requires both calls to stand, and the Raman call carries no evidence to
stand on. On **either** treatment — inadmissible leg (single-modality) or
face-value leg (reconciled-by-conversion) — the channel's fused verdict
and strength follow transport: **ABAB, strong**. No reading yields an
unreconciled row: the disagreement direction is exactly the one
conversion permits.

## Verify — four audit outcomes

1. **Independence audit: PASS.** No cross-citation in either direction
   (notebook scanned in full; fab record predates the session; transport
   protocol statement "no reference data consumed"). Call opposes the
   fab-record lean.
2. **Registration stress: PASS (degenerate).** No quantitative
   registration exists to shift; every row already sits at the coverage
   floor (uncovered → single-modality), so no perturbation can flip any
   mechanism class, coverage label, or domain share. No row is classified
   on registration grounds; the limitation is total and priced in as
   "uncovered" rather than hidden in a spread.
3. **Directionality audit: PASS.** Zero reconciled-by-conversion rows
   claimed (class unavailable — Raman leg inadmissible); zero
   Raman-Bernal/transport-rhombohedral rows exist. The consistency
   narrative invokes conversion only in the permitted direction
   (ABC→ABA) and only with named risky steps.
4. **No-averaging audit: PASS.** Fused strengths: B_1−B_2 = strong =
   its strongest (only) input; region B = cannot tell; no concordant-class
   upgrade anywhere; no per-device verdict issued (only one channel
   probed; footprint remainder uncovered).

## Named hedges

- **Raman leg not fusible** — no spectra, no wavelength/power/spot
  size/date, no coordinates. The fused product is single-modality; the
  "ABC (strong)" wording in `raman.md` is unsupported testimony, and the
  ABAB call is *not* contradicted by any admissible Raman evidence.
- **Stage fork inside `raman.md`** — cut listed as post-dating the read
  vs the domain "survived the cutting"; reported as a fork (QC0426
  lesson: stage conflicts are forks, not revisions). Does not change any
  row (both branches leave stacking, anneal, and litho after the last
  Raman).
- **Registration/coverage** — channel uncovered by Raman; domain scale
  unknown; "device ⊂ ABC domain" cannot be checked.
- **Mosaic** — region B's stacking is not established by either leg; a
  different stacking at weak series weight is not excluded (transport
  hedge, inherited).
- **ABCB blind spot (double)** — transport: a J = 1 Dirac partner below
  the 2.5 T tone floor is not excluded (citation-grade template);
  Raman: even a full FWHM map cannot separate ABCB from ABAB at N = 4
  (`raman-stacking-id.md`, Wirth et al.). The two modalities' blind spots
  overlap here — a future Raman map would *not* retire this hedge.
- **Absence claim** — "cut region contains no ABA" fails resolvability
  requirements; treated as "not resolved", never as evidence of absence.
- **Inherited transport hedges** — heavy-branch mass window fork
  (φ²-ratio 1.4–2.0 vs 2.2); absolute N = 4 supported by transport but
  optical N-assignment not independently checked; density scale
  0.886 ± 0.03.

## What would settle / firm (per row)

No row is **unreconciled**; the items below settle the degraded and
cannot-tell rows.

- **Row B_1−B_2 (upgrade path from single-modality toward concordant):**
  obtain the flakemap/spectra files and acquisition metadata from Ben and
  run `raman-stacking-id.md` end-to-end (Step 0 table → per-spectrum
  metrics → map split), plus one frame bridge (parent-flake image with
  cut outline → device optical/GDS) to make the coverage classifiable;
  then re-run this fusion. Note the stage stamp stays pre-stacking — at
  best this yields concordance-with-conversion-narrative, not a
  measurement-time Raman.
- **Measurement-time, region-resolved check:** near-field imaging
  (s-SNOM) of the channel region, or magneto-Raman on the finished
  device — a through-gate far-field Raman map would be capped at
  consistent-with (through-stack screen) and would not carry the call.
- **Region B (cannot tell):** a second independent 4T pair (operator
  rewiring at the breakout) for per-region transport; or the near-field
  image above.
- **ABCB residual:** transport LK ladder over 1.5–10 T at 10 mT (the
  transport contract's firming item) plus G-peak-position/near-field —
  FWHM-only Raman cannot decide this.

## Provenance

Inputs received: `inputs/transport-call.md`, `inputs/raman.md`,
`inputs/20260822_ana.ipynb` (parsed as JSON, not executed),
`inputs/session_notes.md`, `inputs/device_card.md`; the session brief;
and the corpus (`hera/recipes/`, `hera/models/` — read-only; no model
code executed this run, no quantitative Raman data existed to run it on).
The parent-flake URL in `raman.md` was not fetched; nothing under
`/data/sharpelab/hera-data/` outside this run directory was listed or
read. I saw **no prior fusion attempt, draft, or verdict for this
device**, and **no third-party view of the transport call** (the fab
record predates it and does not mention transport). Harness-injected
environment context (working-directory path, platform info, user email)
was present but not used as evidence; the working directory is not a git
repository and no git/repository metadata reached me. No forbidden
material was encountered.
