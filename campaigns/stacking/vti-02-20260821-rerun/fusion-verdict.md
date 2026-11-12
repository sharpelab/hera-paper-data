**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Campaign lock (clean-environment rerun of the 2026-08-21 fusion, per the `prereg-offline-stages.md` rerun program). Verbatim `fusion-verdict.md` of the fresh-instance run (brief: `hera/docs/brief-vti-02-20260821-fusion-rerun.md`; run dir `$HERA_DATA/raman-vti-02-20260821-fusion/`). Inputs byte-identical to the arm-1 fusion's staged set except the disclosed SCORER-banner strip (deviations.md, 2026-08-22 entry recorded 2026-08-27). CONCORDANT with the locked original (`vti-02/fusion-verdict.md`): same verdict (ABAB Bernal, strong, single-modality), same admissibility findings, same consistency-narrative posture — per the prereg disclosure rule, reported in the supplement. The prereg-series verdict of record is unchanged. Locked as produced; not edited.

# vti-02 — fused Raman × transport stacking verdict

*Fusion run 2026-08-27, per
`hera/recipes/investigations/stacking-raman-transport-fusion.md`, transport
base `tetralayer-stacking-fs-count.md` (device card material line: 4LGr),
Raman base `raman-stacking-id.md`. Inputs: the five files under
`inputs/` named in the brief. Offline analysis; ana notebook parsed, not
executed.*

## Headline

**sr1 (B_1–B_2): ABAB (Bernal) — strong, transport-only.** The Raman leg
is inadmissible as a fusion contract (axes below), so the fusion degrades
to a consistency narrative for that leg: the face-value disagreement
(pre-fab attested ABC vs. in-situ ABAB) lies in the **allowed conversion
direction** and has multiple named risky steps available, but conversion
is **not established** — mis-registration and a Raman misread remain
open co-explanations. No per-device verdict exists; regions outside the
sr1 footprint are **cannot tell** at measurement time. That is the
successful outcome here, not a failure.

## Step 1 — admissibility

**Transport leg — admissible.** `inputs/transport-call.md` is a complete
tetralayer Step 7 output contract: weight words ("ABAB (Bernal) —
strong"), a feature-level evidence list (f₁ = 6.2 T, f₂ = 21.8 T, fan
branches on the ABAB Onsager curves, Luttinger sum at one global scale
0.93 ± 0.03, F_L-tone origin discrimination, LK masses with beat
exclusion, degeneracy audit), named coordinates (channel sr1 = B_1–B_2,
source T_0, drain B_3; (n, D) coordinates per tone), hedges, and a
what-would-firm list. Verified against the ana notebook: the call cell
(cell 29) is byte-identical to the contract body
(`artifacts/ana_inventory.md`).

**Raman leg — not admissible as a contract; admitted as attested
testimony.** `inputs/raman.md` assessed against the `raman-stacking-id`
output contract, axis by axis:

| Axis | Status |
|---|---|
| Weight words | Present in form ("Lean: ABC … Strength: strong") — but a *lean*, and per both base recipes a confident call without feature-level evidence is a protocol violation; the wording is assessed, not inherited |
| Evidence list | **Fails.** No spectra, no FWHM/lineshape metrics, no wavelength, no reference panel — "Flakemap / spectra files: not yet in hand" |
| Positions / region mask | **Fails.** No spot or domain coordinates of any kind; the domain exists only as prose |
| Acquisition metadata (Step 0) | **Fails.** Instrument, wavelength, power, spot size all unknown; acquisition date unknown |
| Stage stamp | Present qualitatively (pre-stacking, on parent flake) but **internally inconsistent**: the header says the cut postdates the read, while the findings ("survived the cutting process", "some spectra look like noise due to the laser cutting") imply post-cut spectra. Reported as a stage fork (QC0426 lesson: fork, not revision) |

Fusible weight of the Raman leg: **ABC, consistent-with at best**
(attested; the document's own "strong" is unsupported by anything in
hand — no metadata caps at weak, no data at all caps below that). Per
the fusion recipe, a bare verdict without evidence coordinates is not
fusible; per the brief, the fusion **degrades** rather than returns:
consistency narrative + coverage caps below.

**Independence audit (Step 1 precondition) — pass, with one hedge.**
Neither contract cites the other's evidence. The transport contract,
session notes, and the full ana notebook (sources + outputs greped,
`artifacts/ana_inventory.md`) contain no reference to Raman, the parent
flake, or an ABC prior — the only ABC/ABCA vocabulary is the tetralayer
recipe's own template language. `raman.md` references only pre-fab
facts, no transport. The two calls also *disagree*, which is itself
inconsistent with either leg shaping the other toward concordance.
Hedge: `raman.md` is undated, so its independence rests on content, not
on a timestamp.

## Step 2 — spatial registration

Artifact: **`artifacts/registration-vti-02.png`**, record:
`artifacts/registration-vti-02.md`, generator: `scripts/registration.py`.

No metric frame bridge exists in the input set (no map coordinates, no
optical image, no GDS; ana notebook geometry is electrical only). The
registration is the topological chain: parent flake → attested ABC
domain → cut region (claimed ⊂ domain) → stack/fab → contact frame →
sr1. **Metric anchors: 0; registration uncertainty: unbounded; domain
scale: unknown.** Uncertainty ≳ domain scale at every link, so:

- **sr1 (B_1–B_2): Raman coverage at best partial** — recorded as
  *attested-covered, metrically unverifiable*; domain composition under
  the footprint unresolved.
- **All other device regions: transport-uncovered** (sr2/sr3 n.c.; T_1–T_4
  dead).

No interpolation performed.

## Step 3 — temporal registration

Raman stage: pre-stacking on the parent flake (post-cut per the findings
text; ordering forked, above). Build steps between map and the
2026-08-21 measurement, by conversion-risk class (converter list,
`raman-stacking-id.md`); conversion runs rhombohedral→Bernal only:

1. **Litho / metal-contact deposition** — on the device region by
   definition (contacts on the channel); highest class — anisotropic
   strain moves walls by µm (Geisenhof).
2. **Laser cutting** — local heating at the cut perimeter, which bounds
   the entire device region; the document itself flags cutting-damaged
   spectra.
3. **Stacking / hBN pickup + transfer** — documented converter (armchair
   pickup, Yang).
4. **Anneal** — chemical + bake class (Zhang).

Only one map stage exists, so no map differencing is available; risk-class
inference is the only temporal evidence. Every risk class is present:
a genuine pre-fab ABC region measuring Bernal today is fully consistent
with the documented conversion physics. `raman.md` itself concedes the
frame: "each an ABC→ABA conversion risk."

## Step 4 — per-region fusion table

| Region / channel | Transport | Raman | Fused | Mechanism class |
|---|---|---|---|---|
| **sr1 = B_1–B_2** (source T_0, drain B_3) | **ABAB (Bernal) — strong** (in-situ, 2026-08-21) | ABC — attested, **consistent-with at best** (document claims strong; evidence, position, metadata axes all fail); stage: pre-stacking, date unknown; coverage: attested-covered → at best partial | **ABAB — strong** (= transport input; no fused upgrade) | **Single-modality (transport)** — Raman leg inadmissible. Consistency narrative: the face-value ABC→ABAB disagreement is in the allowed direction and **consistent-with conversion** (named risky steps: contact metal deposition on the region; laser cutting at the region perimeter; hBN pickup; anneal). Reconciled-by-conversion is *unavailable as a class* (it requires two standing calls); mis-registration (device not actually within the ABC domain) and a Raman misread (strain mimic — unscreenable without spectra) remain open co-explanations. **Not unreconciled** — no Raman-Bernal vs transport-rhombohedral, no strong-vs-strong conflict survives admissibility |
| **Device region outside the sr1 footprint** (the only region `raman.md` resolves is the whole cut region, undelimited) | uncovered (sr2/sr3 n.c., T_1–T_4 dead) | ABC — attested, consistent-with at best, same failed axes; stage-locked | **Cannot tell** at measurement time. As of the pre-stacking stage: ABC (consistent-with, attested) — a rhombohedral Raman verdict does **not** propagate forward across risky steps | **Single-modality (Raman, stage-locked, degraded)** |

No split/share sub-rows: with zero metric registration no share picture
can be constructed (stated, not interpolated). No per-device headline:
covered regions do not concur and most of the device is uncovered.

## Step 5 — the call

- **sr1 (B_1–B_2): ABAB (Bernal) — strong.** Transport-only; carries all
  of the transport contract's own hedges (one contact pair / mosaic;
  mass-ratio weakness; δF = 3.1 T; hole side geometry-limited; ABCA
  minority domain in the F_L tone not excluded; ABCB "not supported" on a
  citation-grade template — and note the Raman ABCB blind spot could not
  have helped there even with data in hand).
- **Rest of device: cannot tell** (now). ABC (consistent-with, attested)
  as of pre-stacking only.
- **Registration artifact**: `artifacts/registration-vti-02.png` (+ `.md`).

**Named hedges**

1. **Raman leg evidence not in hand** — the entire Raman column rests on
   an undated, uninstrumented attestation; flakemap/spectra "pending from
   Ben".
2. **Registration unbounded** — attested-covered only; conversion vs.
   geometry vs. misread underdetermined for the sr1 disagreement.
3. **Stage fork** — `raman.md` internally inconsistent on whether the
   read pre- or post-dates the laser cut.
4. **Layer count at map time unestablished** — `raman.md` never states N
   of the parent flake or that it was confirmed before the stacking
   read; tetralayer identity comes from the device card. A terrace or
   N-misassignment at map time is an unscreened alternative for the
   "domain".
5. **Mosaic** — one wired pair; the flake may host other domains; the
   transport call is one region's.
6. **Sub-spot blindness** (structural, stated every time): even a genuine
   pre-fab ABC read cannot exclude sub-spot Bernal slivers.

**What would settle the degraded/disagreeing rows**

- **Ben's flakemap + spectra + acquisition metadata** (wavelength, power,
  spot size, date, cut ordering): re-run `raman-stacking-id` Steps 0–6
  properly — restores the evidence and position axes, enables the
  strain-mimic and terrace screens, and could upgrade the sr1 row to
  reconciled-by-conversion (or expose a misread).
- **Optical images of stack/device + GDS**: metric registration of the
  cut region onto the contact frame — decides conversion vs. geometry
  for the sr1 narrative.
- **Second R_xx pair** (operator rewiring at the breakout): cross-region
  transport — tests the mosaic hypothesis and whether any region still
  measures rhombohedral.
- Transport's own firming list (cleaner pair for the QH-ray pin; longer
  1/B record for the φ² mass split; hole side on a fully dual-gated
  path).
- Post-fab optical checks on the finished device would be through-stack
  weak at best (buried channel under gates) — near-field/re-map applies
  to unprocessed sibling material, not this channel.

## Verify — the four audits

1. **Independence** — **pass** (Step 1 above): no cross-citation either
   way; verified over the full notebook text; hedged only by the missing
   `raman.md` date.
2. **Registration stress** — **pass, with the narrative
   registration-limited.** With zero anchors the stress runs over the two
   limiting topological variants (sr1 inside vs. outside the attested ABC
   domain). The sr1 fused verdict (ABAB, strong) and its class
   (single-modality transport) are invariant — transport is in-situ on
   the channel. What flips is only the *consistency narrative's
   mechanism* (conversion ↔ geometry), which is therefore reported as
   registration-limited, not classified. The row-2 coverage label
   (uncovered transport) is registration-independent.
3. **Directionality** — **pass.** The only disagreement is
   Raman-rhombohedral (attested) vs transport-Bernal — the allowed
   direction, with risky steps named (metal deposition, laser cut,
   pickup, anneal). No reconciled-by-conversion row was claimed (class
   unavailable without an admissible Raman leg — its precondition, two
   standing calls, is enforced, and its named-step requirement would have
   been met). No Raman-Bernal/transport-rhombohedral row exists.
4. **No-averaging** — **pass.** Fused strength (strong) equals the
   strongest input (transport); no concordant upgrade claimed; the
   degraded Raman leg was not blended in; no per-device verdict issued.

## Provenance line

Received exactly the brief's input set —
`inputs/transport-call.md`, `inputs/raman.md`, `inputs/device_card.md`,
`inputs/session_notes.md`, `inputs/20260821_ana.ipynb` (parsed as JSON,
never executed) — plus, from the corpus,
`recipes/investigations/stacking-raman-transport-fusion.md`,
`tetralayer-stacking-fs-count.md`, and `raman-stacking-id.md`. I saw
**no prior fusion attempt, draft, or verdict for this device, and no
third-party view, lean, or reaction to either modality's call**. The
parent-flake URL in `raman.md` was not fetched; nothing under
`/data/sharpelab/hera-data/` outside this run directory was listed or
read; no other `hera/` directories, archives, or communications were
accessed. Harness-injected environment context (user identity, today's
date 2026-08-27, platform info; the directory is not a git repository so
no git context existed) was used only to date this document. A bundled
chart-styling skill reference supplied the figure palette — no device
information in it.

## Artifacts

- `fusion-verdict.md` — this file
- `artifacts/registration-vti-02.png` / `.md` — Step 2 registration artifact + record
- `artifacts/ana_inventory.md` — notebook cell inventory, call-cell byte-check, independence/geometry greps
- `scripts/parse_ana.py`, `scripts/registration.py` — regenerators
