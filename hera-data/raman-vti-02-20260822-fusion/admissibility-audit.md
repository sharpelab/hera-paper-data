# Step 1 — admissibility + independence audit (vti-02 fusion, 2026-08-22)

Recipe: `stacking-raman-transport-fusion.md` Step 1 + Verify (independence
audit). Both contracts audited axis-by-axis against the form their base
recipes require.

## Transport contract — `inputs/transport-call.md`

Base recipe: `tetralayer-stacking-fs-count.md` Step 7 (five-part output
contract).

| Axis | Status | Evidence |
|---|---|---|
| Weight words | **PASS** | "ABAB (Bernal) — strong" for B_1−B_2; "uninformative on its own" for region B; strength scale respected |
| Evidence list w/ coordinates | **PASS** | Six numbered items: tones (7.3 T, 22.0 T), (n, D) coordinates, run indices, FFT windows, δF, LK masses, degeneracy audit, Luttinger sum |
| Channel/pair named | **PASS** | sr1 = B_1−B_2 (pads 12, 04 per device card), "the only wired 4T pair; probes regions A + B in series" |
| Hedges | **PASS** | Heavy-mass window fork, mosaic caveat (region B unestablished), ABCB partner below 2.5 T floor, N = 4 optical not independently checked |
| Provenance | **PASS** | Session, transcript, notebook cell index + timestamp; verified: the contract body is **verbatim identical** to ana notebook cell 23 (diff clean) |
| Locked / verify executed | **PASS** | Protocol statement lists every mandatory Verify item as executed |

**Transport leg: admissible and fusible.** Stage: in-situ on the finished
device, 2026-08-22/23.

## Raman contract — `inputs/raman.md`

Base recipe: `raman-stacking-id.md` (Step 0 metadata table; Step 6 five-part
output contract). Per the session brief, this human-authored fab record *is*
the Raman leg in full — audited as written, not reconstructed.

| Axis | Status | Evidence |
|---|---|---|
| Weight words | **MARGINAL** | "Lean: ABC ... Strength: strong" — a *lean* with a strength word attached; base recipes hold that bare leans are not verdicts. The wording exists but is unsupported (below) |
| Evidence list (feature-level) | **FAIL** | No FWHM, no lineshape, no population split, no M-band/G-band values, no reference panel. "The Raman indicates a domain of rhombohedral" is a bare verdict. Spectra/flakemap "not yet in hand — pending from Ben" |
| Step 0 metadata | **FAIL** | Wavelength, power, spot size, resolution, acquisition date all unknown. Per `raman-stacking-id.md` Step 0: no wavelength → no lineshape comparison; no power → possible in-measurement conversion unflagged; missing metadata caps achievable strength at **weak** even *with* spectra |
| Spot/region positions + mask/raster | **FAIL** | No coordinates of the rhombohedral domain, no raster, no map, no cut outline. The only spatial statement is prose: "we cut out the rhombohedral domain" |
| Stage stamp | **PASS (with internal conflict)** | "Build stage at acquisition: pre-stacking, on parent flake." Conflict: the preamble lists **cut** among steps that *postdate* the read, while the findings say the domain "survived the cutting process" (implies a post-cut read exists). Carried as a stage fork, not resolved |
| Layer count (N) established | **FAIL** | Not stated in the document; N = 4 comes from the device card, not from the Raman record |
| Absence-claim resolvability | **FAIL** | "expect the cut region to contain no ABA" cites no coverage, spot/step vs domain scale, or power — per `raman-stacking-id.md` Verify, this reads "not resolved", not "absent" |

**Raman leg: not fusible as evidence.** Per fusion Step 1: "A bare verdict
without evidence coordinates is not fusible — return it to its recipe."
Assessed standing of the document's content: *unassessed testimony* — an
ABC lean at pre-stacking stage whose stated "strong" cannot be sustained
(metadata rules alone cap it at weak; zero feature-level evidence removes
even that). It enters the fusion as a **consistency narrative only**; rows
it would have covered degrade to single-modality, and its spatial claim
("device ⊂ rhombohedral domain") cannot establish coverage.

## Independence audit (Verify)

- Transport → Raman: the ana notebook (all 24 cells scanned) contains **no
  reference** to the Raman record's content — no "rhombohedral", "ABC
  prior", flake-record URL, or pre-fab lean anywhere; the sole Raman
  mention is the generic "Magneto-Raman ... cross-check" in
  what-would-firm. The contract's protocol statement: "no reference data
  consumed (first-session branch)". Session notes likewise clean.
- Raman → transport: the fab record predates the transport session
  (pre-stacking stage) and mentions no transport quantity.
- Corroboration of non-shaping: the transport call **opposes** the fab
  record's lean (ABAB vs ABC) — the opposite of anchoring.

**Independence: PASS.** Fusion is evidential in form; it degrades to a
partially-narrative product only because of the Raman leg's admissibility
failure, not because of contamination.
