# vti-02 — fused stacking verdict (Raman × transport)

*Executes `hera/recipes/investigations/stacking-raman-transport-fusion.md`
against the locked transport call (`tetralayer-stacking-fs-count.md`
Step 7) and the device group's Raman record. Offline analysis; no rig.
Step 5 output contract.*

**Headline.** The fusion **degrades to a single-modality read plus a
consistency narrative**: the Raman leg fails the recipe's Step-1
admissibility gate on the evidence and coordinate axes, and supplies no
frame bridge of any kind, so no registration transform exists and every
channel is **uncovered**. The one live channel's fused verdict is
**ABAB (strong)** and is carried **entirely by transport** — no upgrade,
no concordance claimed. The two documents are nonetheless *compatible*:
rhombohedral-at-stage-S → Bernal-now is the permitted conversion
direction and Step 3 names four unretired risky steps, one of them metal
deposition on the measured channel. That compatibility is recorded as a
narrative, not classified as a mechanism, because the Raman leg is not
fusible. **No per-device verdict is issued.**

---

## Step 1 — admissibility

### Transport leg — admissible

`transport-call.md` is byte-identical to ana-notebook cell 35, the final
cell (checked programmatically: `artifacts/nb_checks.txt`, 7171 chars
each, `identical=True`). It carries every element Step 1 requires:

| Axis | Status |
|---|---|
| Weight word | ✅ "channel B_1−B_2: **ABAB (strong)**", on the STYLE scale |
| Evidence list | ✅ tones with frequencies, reproducibility counts (18/18), (n, D) coordinates, density side, B-window, δF, dual model overlay, Luttinger check |
| Coordinates (which contact pair/channel) | ✅ `sr1`, B_1−B_2, resolvable to bond pads 12/04 via the device card |
| Hedges / what-would-firm / status | ✅ all present, six named hedges |
| Stage | ✅ in-situ on the finished device, 2026-08-24/25 |

Its own recipe's criterion for *strong* — "two branches on the ABAB
curves **and** the F_L-tone origin passed" — is met on the face of the
contract (evidence (a)+(c) and (b) respectively). Fusion checks contract
**form**, not physics (QC0426 lesson 1); the transport leg's validity
domain and hedges are inherited wholesale into every row below.

### Raman leg — **not fusible** (returned to `raman-stacking-id.md`)

`raman.md` is assessed against that recipe's Step 6 five-part contract,
axis by axis. Its own verdict wording is an input assessed here, not a
conclusion inherited.

| Axis (`raman-stacking-id.md`) | Status | Detail |
|---|---|---|
| **Weight word** | ⚠️ present but unsupported | "Lean: ABC / Strength: strong". A *lean* labelled *strong* with no feature-level evidence anywhere in the document. |
| **Spot/region coordinates** | ❌ **fails** | No spot positions, no (x, y), no region label mask or raster, no map, no image. One prose region only: "the cut region". This is the axis Step 1 names as disqualifying: *"a bare verdict without evidence coordinates is not fusible — return it to its recipe."* |
| **Evidence list** (metrics with spectral coordinates) | ❌ **fails** | No 2D FWHM, no population means, no skew/ratio/r², no lineshape, no reference panel, no morphology, no cross-checks. The underlying files are "not yet in hand — pending from Ben". |
| **Step-0 acquisition metadata** | ❌ **fails** | Wavelength, laser power, spot size, map step, spectral resolution, raw-vs-processed and acquisition date are all recorded as unknown. Per Step 0 these missing fields *cap* achievable strength; the recipe's own line is "data lacking metadata supports at most **weak** calls", and a lone read with no same-flake reference supports at most **consistent-with**. |
| **Stage stamp** | ✅ ordinal only | "pre-stacking, on parent flake" — the load-bearing part is present. Date unknown, so the stage gap is ordinal, never elapsed. |
| **Layer count** (recipe Step 1, "layer count before stacking") | ❌ absent | `raman.md` never states N. The device is tetralayer (`device_card.md`). FWHM grows with N, so an unstated N is an unscreened confound; the trilayer-specific numbers in the Raman recipe are N = 3 facts and only the *family-level* rule (rhombohedral-family FWHM > Bernal-family at every N) transfers. |
| **Mandatory Verify screens** | ❌ none run | Strain-mimic screen (mandatory before any ABC verdict from width alone), terrace screen, tool gates, mixed-spectrum decomposition, excitation-transfer ban — none documented. |
| **Absence claim** ("expect the cut region to contain no ABA") | ❌ fails resolvability | STYLE rule 4 / the recipe's "absence claims cite resolvability": no coverage, spot/step vs domain scale, power, or surface statement is given, and no post-cut read exists. The outcome available is "not resolved", never "absent". |
| **What-would-firm-it** | ⚠️ implicit only | "pending from Ben". |

**Ruling.** The Raman leg carries a stage stamp and a weight word and
nothing else. It fails Step 1 on **coordinates** and on **evidence**, so
it is **not fusible** as written. Assessed on what it does contain, the
strongest grade its own recipe would license is **consistent-with (ABC,
as of stage S)** — and even that is generous, since the document
presents no feature-level evidence at all and its recipe calls a
confident call without feature-level evidence a protocol violation. For
the Step-4 table the leg enters as **uninformative** (not fusible),
with the consistent-with reading carried in the narrative.

What is *not* being said: nothing here impugns the read Ben actually
made. The claim is narrower and entirely about admissibility — the
evidence for it is not in the input set, so this fusion cannot weigh it.

---

## Independence audit (Step 1 precondition, and Verify #1)

**Direction 1 — was transport shaped by Raman? No, on the record.**
A keyword scan of all 36 ana-notebook cells (`scripts/nb_checks.py` →
`artifacts/nb_checks.txt`) finds **zero** occurrences of "Raman",
"rhombohedral", "pre-fab", "parent flake" or any equivalent; the same
scan over `session_notes.md` and `transport-call.md` returns only the
device-independent template term "ABCA" used as a transport template
name. The transport leg's evidence is entirely in-session (runs 5–8).

*Residual R1 (named hedge).* `transport-call.md` discloses that one
clause of the **superseded** blind call (cell 30) is redacted at
staging because "it references material outside this session", declared
not load-bearing. Its content is unverifiable by me. Three facts bound
the risk: it sits in the **adjacent-N** bullet (N = 3 vs N = 4), an axis
orthogonal to Bernal-vs-rhombohedral; it is in the cell the locked call
**supersedes**; and the blind call already read ABAB (consistent-with)
before run 8 — a rhombohedral prior, had it been in sight, would have
pulled the other way. Risk of contamination: low, not zero.

**Direction 2 — was the Raman document shaped by transport?**
`raman.md` is **undated**, so its authoring time relative to the
2026-08-25 transport call cannot be established. Its framing ("Pre-fab
prior, not ground truth"; "each an ABC→ABA conversion risk") is
hedge-forward and would, if written post-hoc, bias *toward* the
transport result rather than manufacture a disagreement — its ABC lean
rests on pre-stacking data either way.

*Residual R2 (named hedge).* Undated Raman document; authoring order
unestablished.

**Audit outcome: PASSES with residuals R1 and R2 named.** Independence
is not the binding constraint here — admissibility is. Note the recipe's
own consequence for a failed independence check (degrade to a
consistency narrative) is reached anyway, by the other route.

---

## Step 2 — spatial registration (binding artifact)

**Artifact:** `artifacts/registration-frame.png` (figure) +
`artifacts/registration.json` (machine-readable census, coverage labels,
stress result). Regenerated by `scripts/registration.py`.

**Frame-bridge census — what was actually supplied:**

| Bridge the recipe asks for | Supplied? |
|---|---|
| Stage-registered video images inside the Raman files | ✗ (no Raman files at all) |
| Marker-frame optical images | ✗ |
| Device GDS | ✗ |
| Raman spot/region coordinates, mask or raster | ✗ |
| Flake or cut outline | ✗ |
| Hall-bar geometry (L/W) | ✗ — `session_notes.md` flags its absence on the device card |
| Ana notebook spatial content | ✗ — electrical geometry only (keyword scan, `artifacts/nb_checks.txt`) |
| Device-card pad table | ✓ **ordinal only** — labels, bond pads, and the convention "T = top arc L→R, B = left side then bottom L→R" |
| Build-step list | ✓ prose, undated (see Step 3) |

**Metric anchors available: 0.** No transform — rigid or otherwise —
can be fitted, because the Raman side has no coordinates to anchor. The
recipe's multi-anchor / non-rigid-strain machinery has nothing to act
on.

**Registration uncertainty: unbounded / undefined.** Not a large number
— *no* number. Against the domain scale (unknown for this flake; the
literature expectation for exfoliated multilayer graphene is µm-scale
domains, Lui 2011 via `raman-stacking-id.md`), an unbounded uncertainty
exceeds any µm-scale domain trivially, which is the condition under
which the recipe caps coverage at *partial* at best.

**What the frame does establish:** the ordinal ring of pads around the
mesa (T_0 alive on the top arc; B_1 alive on the left side; B_2, B_3
alive along the bottom; T_1–T_4 dead), the wired four-terminal pair
B_1−B_2, and the T_0→B_3 drive path crossing a strictly larger
footprint. Order is evidence; position, spacing, and mesa outline are
not, and the figure says so on its face.

**Coverage labels:**

| Channel | Raman coverage | Why |
|---|---|---|
| `sr1` : B_1−B_2 (pads 12–04) | **uncovered** | No Raman region can be placed on the footprint. |
| T_0→B_3 drive path (pads 29–27) | **uncovered** | Same; and no stacking read exists on this path for either leg. |
| sr2, sr3 (n.c.); T_1–T_4 (dead) | n/a — no channel | Why no mosaic test exists this cooldown. |

**The most generous reading, and why it does not change the label.**
Grant that the device flake *is* the cut piece, so the channel lies
inside "the cut region" by construction. The row is limited identically,
because the quantity that matters is not containment in the cut piece
but the **domain composition of the B_1−B_2 footprint** — and the cut
was made against a domain boundary that was never mapped, with no
post-cut read to check it. Step 2's own clause covers this case: a
covered footprint whose domain composition is unresolved "limits the row
the same way". Uncovered stays uncovered; no interpolation.

---

## Step 3 — temporal registration

Full artifact: `artifacts/temporal-registration.md`. Summary:

- **Stage S** = pre-stacking, bare parent flake, **date unknown** →
  stage gap is ordinal only.
- **Maps at multiple stages: none** → differencing unavailable; risk-class
  inference is the only instrument.
- **Through-stack status: gate-clean and stack-clean.** The screen that
  burned QC0426 does not trigger here. This is the Raman leg's one
  methodological strength — and its mirror: the gate-clean stage is the
  one furthest from the finished device.
- **Post-map steps, by risk class:** (1) **laser cut** isolating the
  domain — laser heating is a documented converter at the ~10 mW scale
  while safe mapping is ≤ 1 mW [citation, Zhang LSA 9 174], and cutting
  is orders above that, applied along the retained piece's whole
  perimeter; `raman.md` itself reports spectra looking like noise from
  the cutting. (2) **hBN pickup / stacking** — converts along armchair,
  preserves along zigzag [citation, Yang NL 19 8526]; alignment
  undocumented. (3) **anneal** — adsorbate chemistry + bake [citation,
  Zhang NC 4 2074]; parameters undocumented. (4) **litho + metal contact
  deposition** — top of the ladder, walls move by µm [citation,
  Geisenhof AANM 2 6067], and here the metal lands on the ends of the
  measured channel: the strain source is *on* the region. (5) cooldown
  and gating — low.
- **Directionality:** rhombohedral (S) → Bernal (now) is the **permitted**
  direction. Not a conflict. Also not evidence: a rhombohedral verdict
  does **not** propagate forward in time.

---

## Step 4 — per-region fusion table

| Channel / region | Transport verdict + strength | Raman verdict + strength + stage | Fused verdict + strength | Mechanism class |
|---|---|---|---|---|
| **`sr1` : B_1−B_2** (pads 12–04) — the only live four-terminal pair | **ABAB (strong)**, in-situ 2026-08-24/25, electron side, D ≈ 0, \|n\| ≤ 3.1×10¹² | **uninformative** (not fusible: no coordinates, no evidence, no metadata). Document's own wording "ABC, strong (lean)"; at most **consistent-with (ABC)** on what it contains. Stage: pre-stacking parent flake, date unknown. Coverage of this channel: **uncovered** | **ABAB (strong)** — transport-carried, no upgrade | **Single-modality** (Raman leg inadmissible *and* uncovered). Consistency note: under the counterfactual of an admissible Raman leg this row would classify **reconciled-by-conversion** — direction-legal, with four risky steps named — never *unreconciled*. |
| **R_cut** — "the cut region" (`raman.md`, prose; the only region the Raman document resolves) | **not registrable to this region** — containment of B_1−B_2 asserted by construction, never verified; domain composition unresolved | **uninformative** as evidence; **consistent-with (ABC)** as of stage S at most; rhombohedral verdicts do not propagate to measurement time | **cannot tell** — registration-limited | **Single-modality**, and blocked: the only leg with a claim on this region is the inadmissible one, and its direction of error is the one that cannot propagate forward |
| **T_0→B_3** (pads 29–27), two-terminal drive/drain path | **uninformative** — no four-terminal stacking read on this path; footprint strictly larger than B_1−B_2 | **uninformative**; coverage **uncovered** | **uninformative** | **Single-modality** with neither leg informative — i.e. no fusible content |
| sr2, sr3 (n.c.); T_1–T_4 (dead) | no channel | no channel | — | n/a — the reason no mosaic test exists |

**Per-region fused verdicts, on the strength scale**

- **B_1−B_2: ABAB (strong)**, tetralayer Bernal with symmetry-allowed
  inter-block magnetic breakdown, valid on the electron side at D ≈ 0
  and single field polarity — the transport contract's validity domain,
  inherited unchanged. Fusion adds **no** strength: the second modality
  contributed nothing weighable to this row.
- **R_cut: cannot tell.** A reasoned "cannot tell" is a successful
  outcome under both this recipe and the Raman base recipe.
- **T_0→B_3: uninformative.**
- **Device-level: no verdict.** One region covered, mosaic untestable
  (one live pair), R_cut unregistered. The no-averaging audit forbids a
  per-device headline here, and so does the transport contract's own
  "one region, no mosaic test" hedge.

**Consistency narrative (the degraded product, stated as such).** The
two documents are compatible. Ben's pre-stacking read says the parent
flake carried a rhombohedral domain that was cut out; the finished
device's one measurable channel reads Bernal; the transition
rhombohedral→Bernal is the documented direction and four unretired
converter-class steps sit between the two observations, the last of them
metal deposition on the channel itself. Conversion is therefore the
**leading** consistency hypothesis — but it is *not* classified as
reconciled-by-conversion, because that class consumes an admissible
Raman contract and this one failed Step 1. The competing hypotheses are
live and unranked by this input set:

1. **Conversion** — the domain was rhombohedral at stage S and converted
   during cut / pickup / anneal / metal deposition.
2. **The isolation never held** — "expect the cut region to contain no
   ABA" is an absence claim with no resolvability statement and no
   post-cut read; the cut may simply not have excised what it was aimed
   at, since the domain boundary was never mapped.
3. **The Raman read itself is unevidenced in this input set** — no
   spectra, no metrics, no metadata, no strain-mimic or terrace screen;
   uniaxial strain reproduces both the broadening and the asymmetry that
   read as ABC, and an unstated layer count leaves a terrace step as the
   first alternative hypothesis for any wall.
4. **Sub-spot / sub-channel geometry** — domains below the spot size are
   structurally invisible to Raman, and one Rxx pair cannot see a mosaic.

Nothing in the input set separates these. Neither modality is wrong; the
device group's expectation (build an ABCA device) is simply not
confirmed by the one channel that can be measured, and the *reason* is
not determined.

---

## Verify — the four audits

| Audit | Outcome |
|---|---|
| **Independence** | **PASS with residuals.** No transport cell, note, or contract cites Raman evidence (36/36 cells scanned, `artifacts/nb_checks.txt`). Residual R1: one redacted clause in the *superseded* blind call, on the adjacent-N axis, content unverifiable. Residual R2: `raman.md` undated, authoring order relative to the transport call unestablished. |
| **Registration stress** | **PASS as a limit statement, and it binds.** With 0 anchors there is no transform to shift: any geometry-dependent conclusion flips under an arbitrary displacement. Every row whose conclusion depends on where the Raman region sits is therefore reported as **registration-limited, not classified** — the R_cut row explicitly. The `sr1` row is **stable** under the stress: its fused verdict is transport-carried and transport's footprint is the channel by definition, so no Raman displacement can move it. |
| **Directionality** | **PASS.** No reconciled-by-conversion row was issued (conversion appears only in the consistency narrative — and the four risky steps are named there regardless). No Raman-Bernal / transport-rhombohedral row exists anywhere in the table: the pairing runs rhombohedral(S) → Bernal(now), the permitted direction. The recipe's one hard rule is not engaged. |
| **No-averaging** | **PASS.** No fused strength exceeds its strongest input: the single graded row is ABAB (strong) = transport's own grade, with no upgrade and no concordant class claimed (the legs do not agree — they name different stackings at different times, and one is inadmissible). No per-device verdict is issued; the covered regions do not all concur, because only one region is covered at all. |

---

## Named hedges

- **H1 — registration is unbounded, not merely coarse.** 0 metric
  anchors, no transform, no scale. Every coverage label is "uncovered"
  by construction, and no µm-scale statement about domain walls versus
  the channel footprint is available at any confidence.
- **H2 — the stage gap is ordinal and the risk ladder is unretired.**
  Raman acquisition date unknown; four converter-class steps between
  map and measurement, the highest-risk one (metal deposition) landing
  *on* the measured channel. None of the four can be sized from the
  input set.
- **H3 — the Raman leg's "strong" is not supported by anything in the
  document.** No metrics, no spectra, no acquisition metadata, no
  region mask, files not in hand, mandatory screens not run. This
  fusion grades that leg **uninformative** for fusion purposes and
  **consistent-with (ABC) at stage S** at the most generous reading.
- **H4 — internal ambiguities in the Raman contract.** The header's step
  order ("stacking, anneal, cut, litho") conflicts with the body's
  cut-then-stack narrative; "some spectra look like noise due to the
  laser cutting" sits beside "no further Raman was performed"; and "the
  rhombohedral domain survived the cutting process" has no post-cut read
  behind it.
- **H5 — layer count is unstated on the Raman side.** 2D FWHM rises with
  N, so an unstated N leaves a thickness terrace as the first
  alternative hypothesis for any domain wall. The device is 4L; only
  the family-level rule (rhombohedral-family FWHM > Bernal-family at
  every N) transfers from the recipe's N = 3 numbers.
- **H6 — independence residuals R1 (redacted clause) and R2 (undated
  Raman document)**, as above.
- **H7 — the transport leg's validity domain is inherited wholesale.**
  Electron side only (hole side gate-window-limited to −0.97×10¹² and
  reported unmeasured, not null); D ≈ 0; single field polarity with ~1%
  R_xy admixture and no ±B symmetrisation; the absolute density scale
  resting on the Δν = 4 assignment of the lowest LL ray (a consistency
  argument, load-bearing for the 1.05 rescale); Luttinger sum closing in
  39 of 57 columns with 13 columns testable for the breakdown
  discrimination; **the decisive per-branch LK mass split not
  measured**; one region, no mosaic test.
- **H8 — ABCB is not excluded.** [our-reasoning from the two base
  recipes; citation-grade — no validated ABCB transport model exists.]
  ABCB is also a two-Fermi-surface template, its discriminator is the
  *shape* of the light branch and the per-branch mass — exactly the
  decisive test the transport leg did not run — and on the Raman side a
  Bernal-family FWHM call at N = 4 cannot exclude ABCB either. It is
  weakly disfavoured here by the device's non-insulating CNP (R_xx
  locally *minimal* at neutrality, the band-overlap semimetal shape,
  against ABCB's intrinsic ~9 meV gap) — but CNP character is
  consistent-with at most and is forbidden as a standalone stacking
  read. A rhombohedral pre-history makes a mixed order a live member of
  the hypothesis set rather than an exotic one.
- **H9 — fusion inherits its inputs' physics misses.** Step 1 checks
  contract *form*; the base recipes' screens are the only defence
  (QC0426 burn). Here the Raman leg has no physics to screen, and the
  transport leg's screens are its own — this fusion re-ran neither.

---

## What would settle it

*Per degraded / cannot-tell row. There are no unreconciled rows; the
rows that fail to reach a fused upgrade fail for admissibility and
registration reasons, and these are what fix them.*

**Row `sr1` : B_1−B_2 — to convert the single-modality read into a real fusion**

1. **Make the Raman leg fusible** (returns it to `raman-stacking-id.md`):
   the actual spectra/map files from Ben plus the Step-0 metadata table —
   excitation wavelength, at-sample power, spot size, map step, spectral
   resolution, raw-vs-processed, acquisition date. Then Steps 2–4 of that
   recipe: per-pixel metrics, the two-population split with thickness
   populations masked first, the strain-mimic and terrace screens, and a
   **region label mask/raster** shipped alongside the prose.
2. **Make registration possible**: an optical image of the finished device
   showing the flake and the pad frame, plus the cut outline (or the
   device GDS). Any one of these converts 0 anchors into a fittable
   transform; two or more give the anchor-variant spread the recipe's
   stress audit wants.
3. **Firm the transport leg where its own hedges are open**: per-branch
   LK masses (`temperature-dependence-vti`, Flavor B — expect ≈ φ² ≈ 2.6×;
   this also closes H8/ABCB), ±B symmetrisation, and the hole side if the
   −0.3 V top-gate limit is conservative rather than physical.

**Row R_cut — to decide whether conversion actually happened**

4. **Near-field imaging (s-SNOM) of the channel region** — resolves the
   domain walls neither far-field modality can see, and is the recipe's
   named deciding measurement. This is the single highest-value item if
   the question "did our ABCA domain survive fabrication?" matters to the
   group.
5. **Re-map through the encapsulant** on the finished device, read
   against the through-stack screen (weak at best for a buried channel
   under graphite — expect consistent-with, not a call).
6. **A build-stage Raman ladder on the next device** — flake → post-cut →
   post-stack → pre-gate — which converts risk-class inference into
   differenced evidence and would have made this fusion decidable.

**Row T_0→B_3 / device level**

7. **A second Rxx pair** (operator rewiring at the breakout; T_1–T_4 are
   dead) — the only route to a mosaic statement, and the precondition
   for any per-device verdict.

---

## Artifacts

| Path | What |
|---|---|
| `artifacts/registration-frame.png` | Step-2 registration artifact (figure): ordinal pad frame, wired channel, the unlocalisable Raman region, no scale bar because no metric frame exists |
| `artifacts/registration.json` | Step-2 artifact (machine-readable): frame-bridge census, anchor count, coverage labels, stress result |
| `artifacts/temporal-registration.md` | Step-3 artifact: build-step ladder with conversion-risk classes, through-stack status, directionality |
| `artifacts/nb_checks.txt` | Admissibility + independence evidence: cell-35 ↔ `transport-call.md` byte identity; keyword scan of all 36 cells |
| `artifacts/nb_index.txt` | Ana-notebook cell index (parse-only) |
| `scripts/registration.py` | Regenerates the Step-2 artifact |
| `scripts/nb_checks.py`, `scripts/nb_index.py`, `scripts/nb_cell.py` | Notebook parsing (never execution) |

---

## Provenance

Received and used: this session brief; the fusion recipe
`hera/recipes/investigations/stacking-raman-transport-fusion.md`; its two
base recipes `tetralayer-stacking-fs-count.md` (routed by the device
card's `4LGr` material line) and `raman-stacking-id.md`;
`hera/recipes/STYLE.md`; and the five supplied inputs
(`transport-call.md`, `raman.md`, `20260824_ana.ipynb` — parsed as JSON,
never executed —, `session_notes.md`, `device_card.md`). Paper-level
claims are quoted **as carried in the recipes**, with the recipes'
provenance flags; `hera/docs/papers/` and
`hera/docs/raman-public-data.md` were not opened, and no model code was
run. I did not fetch the parent-flake URL in `raman.md` or any other URL.

I saw **no prior fusion attempt, draft, or verdict for vti-02**, and **no
third party's read, lean, or reaction to either modality's call**. I did
not list, glob, or read anything under `/data/sharpelab/hera-data/`
outside this run directory, and no sibling directory name reached me.

Harness-injected context disclosure (received, not used as evidence):
the session harness supplied the user's email address, today's date
(2026-08-27), a statement that the working directory is not a git
repository, platform/OS strings, a memory-directory path that embeds
this run directory's own name, and lists of available tools, skills and
agent types. A `ls -la` of the run directory printed a `..` entry (the
parent's inode metadata) with no sibling names. None of this bears on
either modality's call, and none was used in the analysis.

*Fused by an offline HERA analysis instance, 2026-08-27. Analysis only —
no rig, no notebook execution, no writes outside this run directory.*
