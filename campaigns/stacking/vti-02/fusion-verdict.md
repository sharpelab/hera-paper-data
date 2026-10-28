**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Prereg §5 step 2, fusion verdict. Verbatim `fusion-verdict.md` of the fresh-instance run (brief: `hera/docs/brief-vti-02-fusion.md`; run dir `$HERA_DATA/raman-vti-02-fusion/` — staged inputs, registration artifact `registration.png/.json`, `make_registration.py`, `nb-extract/`). Locked as produced; not edited.

---

# Fused stacking verdict — vti-02 (Raman × transport)

*Executed per `hera/recipes/investigations/stacking-raman-transport-fusion.md`
(bases: `tetralayer-stacking-fs-count.md` for transport — the device card's
material line is `4LGr`; `raman-stacking-id.md`, tetralayer+ section, for
Raman). Inputs: `inputs/transport-call.md` (locked, tetralayer Step 7),
`inputs/raman.md` (the device group's human-written Raman record),
`inputs/device_card.md`, `inputs/20260821_ana.ipynb` (parsed, not
executed — `nb_extract.py` → `nb-extract/`), `inputs/session_notes.md`.
Registration artifact: `registration.png` + `registration.json`
(`make_registration.py`).*

**Headline: no evidential fusion is possible for vti-02 — the Raman leg
fails admissibility on the evidence and coordinate axes, so the fusion
degrades to a consistency narrative. The only stacking-read region, sr1 =
B_1–B_2, carries the transport verdict unchanged: ABAB (Bernal), strong,
single-modality. No per-device verdict exists.** The Raman document's
rhombohedral lean is neither confirmed nor contradicted by this run: taken at
face value it would sit in the reconciled-by-conversion class (the allowed
direction, with named risky steps), not in unreconciled.

---

## Step 1 — Admissibility

**Transport (`transport-call.md`) — fusible.** Weight word per channel
(sr1: ABAB, strong); evidence list with run ids (5, 8, 10–15), frequencies,
(n, D) coordinates and side, Onsager overlays (ana cell 23), Luttinger
check, F_L-tone origin tests, LK masses; channel coordinates as a contact
pair (B_1–B_2, source T_0, drain B_3) resolvable on the device card's
contact map; seven named hedges; what-would-firm list; the protocol
statement is implicit in the contract form (hedged strong, not decisive).
The ana notebook cell 29 matches the locked text. Nothing returned.

**Raman (`raman.md`) — not fusible on three of four axes.** Assessed axis
by axis against the recipe's Step 1 and the Raman base recipe's Step 0/6:

| Axis | Required | `raman.md` supplies | Outcome |
|---|---|---|---|
| Weight word | strength-scale word per spot/region | "Lean: ABC … Strength: strong" (one flake-level lean) | present — but a weight word attached to no evidence is a bare verdict |
| Evidence list | FWHM / population means / wavelength / reference panel / morphology / cross-checks | none; "Flakemap / spectra files: not yet in hand — pending from Ben"; wavelength, power, spot size, date all "unknown" | **fails** |
| Coordinates | spot/region positions + mask/raster | none — the region is named only as "the rhombohedral domain … cut out"; no map window, no cut outline, no device-frame link | **fails** |
| Stage stamp | build stage + post-map step list | "pre-stacking, on parent flake"; post-map steps "stacking, anneal, cut, litho" (unordered, undated); internally conflicting (see Step 3 stage fork) | partial |

Per the recipe, "a bare verdict without evidence coordinates is not
fusible — return it to its recipe." The Raman leg is returned to
`raman-stacking-id.md` (its Step 0 table cannot be filled; its Step 6
contract cannot be produced from this document). For fusion it is
**uninformative on the evidence scale** — not weak, not consistent-with:
there is no feature-level evidence to grade. The author's "strong" is
testimony about data this run has not seen, and is not inherited. The
base recipe's own caps would apply even if the data arrived as described:
a single-wavelength map with N not independently stated, no power, no
spot size, pre-fab — strength capped until Step 0 is filled.

What the document *does* supply and this run admits: (i) a rhombohedral-
family lean for the parent-flake domain from which the device was cut;
(ii) the stage stamp (pre-stacking, parent flake); (iii) a post-map build
step list; (iv) the author's expectation that the cut region contains no
Bernal — an expectation about the device, not Raman evidence, carried as
the author's lean only.

**Independence precondition — PASS (provenance-based).** See Verify.
Evidential fusion is *not* granted — not because of independence, which
holds, but because the Raman leg is inadmissible; the outcome is a
consistency narrative by the brief's degrade rule.

## Step 2 — Spatial registration (artifact: `registration.png`)

Frame bridges actually available: the device card's contact map (pad
labels/numbers and arc order only — no µm), the ana notebook's geometry
(gate-stack thicknesses; the B_1–B_2 path topology: dual-gated channel plus
a TG-only series segment outside the graphite back-gate footprint, cell 15,
plus Si-doped contact regions, cell 21), and the positions `raman.md`
gives (none). No optical image, no GDS, no stage-registered video frame,
no cut outline. Anchors fit: **0**. The artifact is therefore topological:
it places sr1 on the contact topology and records that the Raman region
cannot be placed in any frame.

| Channel | Pads | Transport | Raman overlap | Coverage | Note |
|---|---|---|---|---|---|
| sr1 = B_1–B_2 (source T_0, drain B_3) | 12–04 (29 → 27) | ABAB (strong) | not placeable | **uncovered** | registration-limited: `raman.md` asserts in prose that the whole device is the isolated rhombohedral domain — "covered" if that were established; it is not (no map, no outline, no device image) |
| rest of flake ("the cut region") | — | not probed (sr2/sr3 n.c.) | asserted (whole region) | n/a — no transport read | Raman-asserted only |

**Registration uncertainty: unbounded** (no frame bridge links the Raman
region to the device). **Domain scale: unknown** for this flake (µm-scale
domains are typical — Lui 2011 via the Raman base recipe, N = 3
statistics, citation). Uncertainty ≫ domain scale ⇒ coverage is at best
partial even if the assertion were accepted; with no position at all,
coverage cannot be established ⇒ **uncovered** (brief rule; no
interpolation, no reconstruction). Two further coverage-relevant facts
from the transport side: the sr1 footprint includes a TG-only series
segment and Si-doped contact regions (regions outside the graphite
back-gate footprint), so "the channel" is itself a composite whose
sub-regions the Raman leg could not have resolved even with a map.

## Step 3 — Temporal registration

Stage stamp: pre-stacking, on the parent flake; acquisition date unknown;
measurement 2026-08-21/22. **Stage fork** (reported, not resolved — QC0426
lesson, fusion recipe Examples): `raman.md` states "no Raman at any later
stage" and "before stacking", yet also "the rhombohedral domain survived
the cutting process" and "some spectra look like noise due to the laser
cutting" — the latter two read as Raman taken *after* the laser cut. Stage
S is therefore either S_A (pre-cut parent flake) or S_B (post-cut,
pre-pickup parent flake); both are pre-stacking and pre-metal, so the
downstream risk table is the same except for whether the cut is bracketed
by Raman evidence.

Post-map steps (from `raman.md`'s list, order and dates not recorded;
risk tiers per the fusion recipe, laser cut per the Raman base recipe's
converter list):

| Step | Risk tier | Region relevance | Status |
|---|---|---|---|
| Laser cut (isolating the domain) | laser heating — documented converter at the ~10 mW scale; a cutting laser exceeds mapping power by orders of magnitude; heat-affected zone at the cut edges | cut edges = the device perimeter, i.e. near the contact/channel edges | post-map under S_A; bracketed by Raman under S_B ("survived") — stage fork |
| Stacking (hBN pickup / transfer) | transfer/pickup (2nd tier; armchair-direction pickup documented converter) | whole flake | post-map under both stages; pickup direction not recorded |
| Anneal | chemical+bake / clean thermal (3rd–4th tier; adsorbate chemistry + bake is the documented converter) | whole flake | post-map; conditions unknown |
| Litho (contacts: T_0, B_1, B_2, B_3 + dead pads; top gate — material not stated on the card) | **metal deposition on/near region — top tier** (Geisenhof: walls move by µm) | contacts land on the flake edge adjacent to the sr1 channel; top gate, if metal, lies directly on the channel | post-map |
| Cooldown + campaign | clean thermal | all | — |

No map exists at a later stage, so no differencing is possible; the
risk-class inference above is the only temporal evidence. Directional
rule in force: documented conversion is rhombohedral → Bernal only. A
post-fab map through the graphite back gate (and a possibly-metal top
gate) would be capped at consistent-with for the buried channel by the
base recipe's through-stack screen — `raman.md` is right that no
later Raman could carry the call on this device as built.

## Step 4 — Per-region fusion table

| Channel | Transport verdict + strength (now) | Raman verdict + strength + stage | Fused verdict + strength | Mechanism class |
|---|---|---|---|---|
| **sr1 = B_1–B_2** | **ABAB (strong)** — light/heavy pair at 0.21/0.77·F_L on the ABAB Onsager curves across n = 1.35–3.06 × 10¹², Luttinger sum closed at one global scale 0.93, F_L tone read as inter-block breakdown (B-window, grid-change, LK), beat exclusion decisive; hedges (i)–(vii) | rhombohedral-family lean, author-asserted "strong"; **inadmissible — fails evidence + coordinates axes (uninformative for fusion)**; stage: pre-stacking, parent flake, date unknown, stage fork S_A/S_B | **ABAB (strong)** — transport-only; no fused upgrade; stage = now (2026-08-22, in situ) | **Single-modality** (Raman leg uninformative/uncovered for the channel). Consistency narrative: at face value the pairing Raman-rhombohedral (stage S) / transport-Bernal (now) is the *allowed* direction and Step 3 names top-tier risky steps (contact metal deposition; plus pickup, anneal, laser cut) — it would classify reconciled-by-conversion, "converted (consistent-with), step: contact metallization"; it is **not** an unreconciled conflict. Recorded as narrative only — conversion is not asserted. |
| rest of flake ("the cut region", as `raman.md` resolves it; no coordinates) | — (no pair wired; sr2/sr3 n.c.) | rhombohedral-family lean, author-asserted "strong"; inadmissible (as above); as of stage S only — a rhombohedral Raman read does not propagate to measurement time | **no fused verdict (uninformative)** | Single-modality (Raman), with the Raman leg inadmissible: no verdict stands on the strength scale for this region |

**Per-device verdict: none.** Only one region carries a transport read;
the Raman leg is inadmissible; the transport contract itself states the
flake may host other domains. The author's "expect the cut region to
contain no ABA" is an expectation, not a covered-region concurrence.

### sr1 — the hypothesis set if `raman.md` is taken at face value

Listed so the deciding follow-ups can be priced; none is weighed here,
because the Raman leg supplies nothing to weigh.

1. **Conversion during fabrication** (rhombohedral → Bernal; allowed
   direction): named risky steps above — contact metal at the channel
   edge (top tier), hBN pickup, anneal, laser cut (under S_A). The
   author's own framing ("each an ABC→ABA conversion risk") agrees.
2. **Raman misread**: uniaxial strain mimics the broad/asymmetric 2D
   signature; layer-number (a terrace) raises FWHM; the tetralayer
   Bernal-vs-rhombohedral split needs the within-map two-population
   structure; none of the base recipe's screens (strain-mimic, terrace,
   through-stack, absence-resolvability) can be audited without the
   spectra. The laser-cut "noise" spectra are a data-quality flag the
   author raises.
3. **Registration**: the sr1 footprint (channel + TG-only series segment
   + contact regions) may lie partly or wholly outside the mapped
   rhombohedral domain — the cut outline vs the domain wall is not
   recorded; a µm registration error on µm domains flips a label.
4. **Transport misread**: the transport contract's hedges allow an ABCA
   *minority* domain contributing to the F_L tone (hedge vii), one pair
   only (i), the series-segment tone (v), the mass-ratio shortfall (ii),
   pentalayer untested (vi). They do **not** allow a sole-ABCA read of
   sr1: a resolved 0.21·F_L branch has no ABCA parent, and the sub-F_L
   fundamentals dominate.

## Step 5 — The call

**Per-region fused verdicts (strength scale):**

- **sr1 = B_1–B_2: ABAB (Bernal) — strong; single-modality (transport,
  now).** No fused upgrade and no fused downgrade: the Raman leg
  contributes no admissible evidence either way.
- **Rest of flake: no verdict (uninformative).** Raman-asserted
  rhombohedral at a pre-stacking stage, inadmissible; transport-uncovered.
- **Per-device: none.**

**Registration artifact:** `registration.png` (+ `registration.json`,
regenerated by `make_registration.py`). Topological only; 0 anchors;
uncertainty unbounded; coverage of sr1 uncovered (registration-limited).

**Named hedges:**

- **Raman inadmissibility** is the binding constraint: no spectra, no map,
  no metrics, no wavelength/power/spot size/date. The author's "strong" is
  not an evidence-scale strength.
- **Registration uncertainty unbounded** vs an unknown (µm-typical) domain
  scale — sr1 coverage is uncovered; any covered/partial label would be
  registration-limited.
- **Stage gap**: acquisition date unknown; four post-map interventions of
  which at least one is top-tier (contact metal), plus a **stage fork**
  (pre-cut vs post-cut Raman) internal to `raman.md`.
- **Uncovered regions**: everything outside sr1 has no transport read;
  sr1 itself is a composite footprint (dual-gated channel + TG-only
  series segment + Si-doped contacts) that no far-field map resolves.
- **Through-stack**: any future Raman on the finished device reads
  through the graphite back gate (and the top gate) — capped at
  consistent-with for the buried channel (base recipe screen).
- **Transport hedges inherited**: one contact pair (mosaic caveat);
  ABCA minority domain not excluded; hole side unmeasured; mass ratio
  below the φ² expectation; N = 4 supported, pentalayer untested.
- **Independence** rests on the documents' stated provenance and
  absence of cross-citation (Verify), not on sealed/locked timestamps for
  the Raman side.

**What would settle (every unreconciled/uncovered row — here both rows):**

1. **Ben's Raman data** — flakemap/spectra files with wavelength, power,
   spot size, step, date, plus the parent-flake image with the cut outline
   and a device-frame optical image (or GDS): run `raman-stacking-id.md`
   Steps 0–6 on it (tetralayer section), then re-run this fusion with a
   real registration. This is the cheapest item and the one that converts
   the narrative into an evidential row.
2. **Ben's stage testimony** — whether the map preceded or followed the
   laser cut; litho sequence and top-gate material; pickup direction.
3. **Second R_xx pair on the flake** (operator rewiring at the breakout;
   transport contract item 4) — the in-situ cross-region check that
   directly tests "no ABA anywhere in the cut region".
4. **Near-field imaging (s-SNOM)** of the device region through the hBN —
   resolves domain geometry now, below the Raman spot, where both
   far-field modalities are blind; the only measurement that can
   distinguish hypotheses 1 and 3 above.
5. The transport contract's own firming list (longer 1/B record for the
   φ² mass split; hole side on a fully dual-gated pair; QH ladder on a
   clean pair).

The fused outcome — a single-modality strong transport verdict with the
Raman leg returned to its recipe — is a successful outcome of this
protocol. Concordance was not forced; neither was a conflict manufactured
from an unevidenced lean.

---

## Verify audits

- **Independence audit — PASS.** `transport-call.md` (E1 session
  2026-08-21/22, corpus `13b07e9`) cites only transport-native evidence
  (runs 0–15, FFTs, Onsager overlays, LK ladder); the ana notebook and
  session notes contain no mention of Raman, of Ben's record, or of a
  stacking prior — the session ran on the device card alone, which carries
  no Raman content. `raman.md` cites no transport result and predates the
  cooldown by construction (pre-fab record; its one post-fab statement is
  that no later Raman exists). Neither document references the other.
  Caveat carried as a hedge: the Raman record is undated and unsealed, so
  independence is provenance-and-content-based, not timestamp-based.
- **Registration stress — coverage label registration-limited; no class
  flip.** Uncertainty is unbounded, so any covered/partial label for sr1
  would flip under the stress shift; "uncovered" is the floor and does not
  flip. The mechanism class (single-modality) is fixed by Step 1
  admissibility, not by the coverage label, and is stable under any
  shift. The consistency-narrative class (reconciled-by-conversion at face
  value) would also not flip to unreconciled under any registration,
  because it is set by verdict direction, not geometry; under a shift that
  places sr1 outside the domain it would become reconciled-by-geometry —
  still not a conflict.
- **Directionality audit — PASS.** Zero reconciled-by-conversion rows
  exist (the class is invoked only inside the consistency narrative, and
  there it names its risky step: contact metallization, top tier). No
  Raman-Bernal / transport-rhombohedral row exists. Bernal → rhombohedral
  conversion was never invoked.
- **No-averaging audit — PASS.** sr1's fused strength (strong) equals its
  single informative input; no upgrade was taken (class is not
  concordant). No strength was assigned to the Raman leg beyond
  uninformative. No per-device verdict was produced. Nothing was blended.

## Provenance

Received: `inputs/transport-call.md`, `inputs/raman.md`,
`inputs/device_card.md`, `inputs/20260821_ana.ipynb`,
`inputs/session_notes.md`; corpus reads limited to
`hera/recipes/investigations/stacking-raman-transport-fusion.md`,
`tetralayer-stacking-fs-count.md`, `raman-stacking-id.md`,
`hera/recipes/STYLE.md`, `hera/models/raman_stacking/README.md`, and the
synthetic fixture `hera/models/raman_stacking/dryrun/fusion/`; the brief
`hera/docs/brief-vti-02-fusion.md`. No URL fetched (the parent-flake link
in `raman.md` not followed). No prior fusion attempt, draft, or verdict
for vti-02 was seen; no third-party view of the transport call was seen;
no session archive, email, chat, or wiki was read. `transport-call.md`
carries a "not for agent view" header — it is admitted here by the brief
as the locked transport contract. No exposure to forbidden material
occurred.
