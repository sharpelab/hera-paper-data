# Stacking verdict fusion — Raman × transport

*Investigation — consumes the locked output contracts of two sibling
investigations on the same device: a transport stacking call
(`trilayer-stacking-fs-count.md`, `tetralayer-stacking-fs-count.md`, or
`trilayer-stacking-id.md`, per-channel — the device card's material line
routes) and a Raman call (`raman-stacking-id.md`, per-spot, stage-stamped) — and
produces a fused per-region verdict. Small by design: the modality
knowledge lives in the two base recipes; this recipe owns only the
reconciliation logic.*

## What

A region-resolved fused stacking verdict for one device, with every
agreement and disagreement classified by mechanism. **Verdicts are never
averaged; evidence is fused.** A traceable disagreement is a first-class
result, not a failure of either modality.

## When

Both modalities' contracts exist for one device. Fusion is evidential only
if each call was produced **without sight of the other** — verify this
first; if either call could have been shaped by the other, the fusion
degrades to a consistency narrative and says so.

## Why

The modalities are complementary, and differ on exactly the axes that
matter on mixed-domain flakes:

- **Transport**: in-situ on the **finished** device; probes the channel
  between a contact pair — a weighted average over whatever domains span
  it; blind to where domains sit.
- **Raman**: spot-resolved µm-scale geometry, but taken at **build stage
  S** (typically pre-fab), blind below the spot size, and perishable —
  post-map processing moves domain walls (base recipe, stage-stamping).

So fusion is **spatial and temporal reconciliation**, and the key
asymmetry is directional: documented conversion runs
**rhombohedral→Bernal only** (strain/chemistry/heat destabilize the
metastable rhombohedral order; the reverse is undocumented — converter
list in `raman-stacking-id.md`). A Raman-rhombohedral region can
legitimately measure Bernal later; a Raman-Bernal region that measures
rhombohedral cannot be explained by conversion.

## Recipe

**Step 1 — admissibility.** Both contracts carry weight words, evidence
lists, and coordinates (transport: which contact pair/channel; Raman:
spot/region positions + stage stamp, preferably with the region
mask/raster artifact — prose ranges force a re-derivation that
reproduces geography but not boundary pixels). A bare verdict without
evidence coordinates is not fusible — return it to its recipe.

**Step 2 — spatial registration (binding: produce the artifact).** Place
the Raman spots/regions and the transport channels on one device image or
coordinate frame. Use every supplied frame bridge: stage-registered
video images inside the Raman files, marker-frame optical images, and
the device GDS (exact pad/contact geometry beats a lead census read off
imagery — but identify gate leads vs channel leads from layer overlaps
before trusting the census). Across a transfer/pickup boundary do not
assume one rigid transform: fit multiple independent anchors; if they
disagree beyond their fit error (non-rigid strain), carry the
anchor-variant spread as the registration uncertainty and run the
stress audit over the variants. For each transport channel, classify
its Raman coverage: **covered / partial / uncovered**, with
registration uncertainty stated against the domain scale (a
µm-registration error on µm domains can flip a region's label — if
uncertainty ≳ domain scale, coverage is at best partial; it can also
leave a covered footprint's domain *composition* unresolved, which
limits the row the same way). Uncovered stays uncovered — no
interpolation from neighboring spots.

**Step 3 — temporal registration.** From the Raman stage stamp: list the
build steps between map and measurement, tagged by conversion risk
(metal deposition on/near the region > transfer/pickup > chemical+bake >
clean thermal). When maps exist at multiple build stages, difference
them: a region's evolution between two maps is direct evidence and
replaces risk-class inference for the steps they bracket
(directionality still binds — see Why). **Difference only
like-conditioned maps** (same through-stack status): a through-stack
superposition shifts the apparent metrics — apparatus, not evolution —
and differencing unlike stages manufactures wall motion. Assess each
stage's through-stack status separately; the gate-clean stage carries
the buried-channel call.

**Step 4 — per-region fusion.** For each named transport channel, one
row: transport verdict+strength | Raman verdict+strength+stage | fused
verdict+strength | mechanism class. A footprint straddling multiple
Raman verdicts splits into share sub-rows (each share ± its
registration spread), classified separately — the channel's fused
verdict follows the share picture, never an average. Classes:

- **Concordant** — verdicts agree: fused strength = the stronger, noting
  the agreement is across independent physics (band structure read
  electrically and optically) — the strongest evidence class this recipe
  produces.
- **Reconciled-by-conversion** — Raman rhombohedral, transport Bernal,
  and Step 3 names a risky intervening step: both calls stand (Raman
  true at stage S, transport true now); the channel's fused verdict
  *and strength* follow transport; the region is recorded as "converted
  (consistent-with), step ⟨X⟩". Without a named risky step this class is
  unavailable — don't invoke conversion as a free pass.
- **Reconciled-by-geometry** — verdicts differ and registration shows
  the modalities probed different regions (partial/uncovered channel, or
  sub-spot mixing flagged in the Raman contract): no conflict; report
  per-region, resist the urge to produce a per-device headline.
- **Single-modality** — one leg is uninformative or uncovered for the
  channel (a Hall pair with no stacking read, an unmapped channel):
  report the informative leg with its stage stamp, no fused upgrade. A
  Bernal-family Raman verdict propagates to measurement time
  (conversion directionality); a rhombohedral one does not — it stays
  "as of stage S".
- **Unreconciled** — Raman Bernal vs transport rhombohedral (conversion
  cannot explain), or same-region strong-vs-strong conflict with no mechanism:
  a **fork to report** (STYLE rule 14) with the deciding follow-up
  (near-field imaging of the region; re-map through the encapsulant;
  the transport cross-checks in the base recipe). One modality being
  wrong is now the *hypothesis set*, not an embarrassment — list which
  specific misread each contract's hedges already allow.

**Step 5 — the call.** Output contract: the Step 4 table (every named
channel), per-region fused verdicts on the strength scale, the
registration artifact, named hedges (registration uncertainty, uncovered
channels, stage gap), and what-would-settle for every unreconciled row.
**A fused "cannot tell" or a well-evidenced disagreement is a successful
outcome; forcing concordance is a protocol violation.**

## Verify

- **Independence audit** (Step 1's precondition): confirm from the
  contracts' provenance that neither call cites the other's evidence.
- **Registration stress**: shift the registration by its stated
  uncertainty (over the anchor variants, when the uncertainty is a
  spread); any region whose conclusion flips — mechanism class,
  coverage label, or domain share — is reported as
  registration-limited, not classified. The stable part of a split row
  (e.g. a majority share) may still be classified.
- **Directionality audit**: every reconciled-by-conversion row names its
  risky step; every Raman-Bernal/transport-rhombohedral row is in unreconciled (no
  exceptions — this asymmetry is the recipe's one hard rule).
- **No-averaging audit**: no fused strength exceeds its strongest input
  except the concordant class; no per-device verdict exists unless all
  covered regions concur.

## Examples

*(our-measurement — mechanical lessons only.)*

- QC0426 case
  (`hera/docs/notes/2026-07-17-QC0426-raman-fusion/fusion/` + the
  correction in the archive README): initially fused as concordant-ABA;
  PI review then identified the Raman leg as gate-contaminated (post-fab
  map through graphite gates), and the rows were re-labeled
  **transport-dominant** with Raman as weak corroboration. Two lessons:
  (1) **fusion inherits its inputs' physics misses** — the admissibility
  step checks contract *form*, not physics; the base recipes' screens
  (here, the through-stack screen) are the only defense, and a
  concordance is only as strong as its weaker leg's validity domain.
  (2) Imagery-based stage inference is consistent-with at best — this
  run's "no visible gate overlay ⇒ pre-top-gate" revision was overturned
  by grower testimony (graphite gates are near-invisible optically);
  report a stage conflict as a fork, not a revision. What stands: the
  registration work (lead census, ±1.5 µm measured) and both returned
  findings.
- QC0426 pre-fab ladder
  (`hera/docs/notes/2026-07-25-QC0426-prefab-raman/`): three-stage map
  series (flake → stack → device) on one device — the Step 3
  multi-stage case. The registration chain to contact pairs runs flake
  video frame → stack imagery → marked-chip optical images → GDS; the
  flake↔stack link across pickup (flake tears into ribbons) is the
  registration-uncertainty driver.
- Synthetic four-class mechanics fixture
  (`hera/models/raman_stacking/dryrun/fusion/`): re-runnable regression
  covering all four mechanism classes and the audits — run it after any
  edit to this recipe.

## Next

- Unreconciled rows → price the deciding measurement before more
  argument; near-field imaging resolves what both far-field modalities
  cannot.
- Concordant mixed-domain maps → the fused domain picture (which pairs
  probe which stacking) feeds campaign planning in the transport
  recipe's Next section.
