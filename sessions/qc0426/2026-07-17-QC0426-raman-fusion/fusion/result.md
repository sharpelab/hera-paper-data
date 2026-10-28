# QC0426 — fused stacking verdict (Raman × transport)

Executed 2026-07-17 per `hera/recipes/investigations/stacking-raman-transport-fusion.md`.

Inputs:
- **Transport contract** (locked 2026-07-16): `hera/docs/notes/2026-07-16-QC0426-session-3/hera_scratch/call_draft.md` — sr1 (T3–T4) ABA strong; sr2 (B4–B5) ABA strong; sr3 (T5–B6) Hall density scale only.
- **Raman contract** (locked 2026-07-17): `/tmp/qc0426-raman-read/result.md` + `provenance.md` — R1/R2/R3 ABA strong at stage S; no ABC resolved anywhere mapped.
- **Device card**: `hera/docs/notes/2026-07-16-QC0426-session-3/device_card.md` — contact labels, arc ordering, wired configuration.
- **Registration source**: the two stage-registered video images inside `/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip` (per-pixel µm grids, same stage frame as the scan position grids). Used for registration only; no spectral re-analysis.

---

## Step 1 — admissibility

Both contracts are fusible: weight words (strong/weak/consistent-with), explicit evidence tables, and coordinates (transport: named contact pairs; Raman: stage-µm region boxes + stage stamp). Neither is a bare verdict.

**Independence audit (precondition) — PASS.**
- Transport call locked 2026-07-16 during a transport campaign with no Raman data on disk; the `.wip` file was received 2026-07-17 (Raman provenance), i.e. *after* lock — transport could not have seen Raman. The contract text contains no optical/Raman evidence; every evidence row is quantum-oscillation/Hall.
- Raman call produced 2026-07-17 by a fresh instance from the grower's file, with no sight of any transport result (provenance + tasking). Its only mention of transport is in "what would firm it", as a *future* arbiter — it cites no transport evidence, no wiring, no session data.
- No cross-citation in either direction → **evidential fusion** (not a consistency narrative).

Caveat recorded: the Raman *data* predate transport, but the Raman *analysis* postdates it by one day; independence rests on the provenance assertion that the analyst saw no transport result. Accepted.

## Step 2 — spatial registration

**Artifact: `registration_artifact.png`** (video image v003 in the stage µm frame with contact labels, transport channel segments, Raman region boxes, scan windows, Spot1). Supporting: `v003_seg.png` (gold/stack segmentation), `v003_full.png`, `v000/v003` zoom series, `registration.npz`.

### Method
The device card gives labels and arc ordering (T = top arc L→R; B = left side then bottom L→R) but no µm coordinates. Registration was built by lead census on the video images (gold / stack-blue color segmentation, connected components, arm-crossing cuts):

- **Top arc: exactly 7 ohmic leads** (6-lead fan + 1 right-side lead), each landing on one of 7 upper mesa arms → **T1…T7, L→R**. An 8th top lead (big top-left) lands on a dark graphite-colored tab, not on mesa material → gate lead (back-gate graphite tab; corroborated by blue-shifted 2D ≈ 2708 cm⁻¹ pixels there in the Raman metric maps — graphite, not trilayer).
- **Bottom: exactly 8 fan leads**, each landing on one of 8 lower mesa arms → **B1…B8, L→R** (primary indexing). B1's lead exits the chip on the left side, matching the card's "left side then bottom L→R". A 9th wide left lead lands on a stack-colored strip joining the mesa's left end — identity unresolved (**fork**: B1-shifted end-contact vs. second gate lead); both indexings evaluated below.
- Spine centerline (fit, rms 0.44 µm): y = −0.367·x − 1.913 (stage µm); spine thickness ≈ 2.3 µm; contact pitch ≈ 2 µm.

### Registration uncertainty
- v000 ↔ v003 absolute-frame feature offset, measured by cross-correlation: **(−1.2, +1.0) µm** — the stage/video registration reproducibility. Scan-grid ↔ video residual from spine-outline comparison ≲ 1 µm. **Adopted uncertainty: ±1.5 µm.**
- Against the domain scale: the Raman map is **uniform** (single FWHM population 63.7 ± 0.7 cm⁻¹ across all 543 credible px, no walls) over its full ~16 µm mapped extent, so the effective domain scale is the whole window ≫ 1.5 µm. A ±1.5 µm shift cannot change which Raman verdict overlays any channel. (Had the map contained µm-scale domains, ±1.5 µm ≳ domain scale would have forced "partial" — stated per recipe.)

### Contact coordinates (stage µm; junction = arm ∩ spine centerline)

| Contact | Lead tip (x, y) | Spine junction (x, y) | Role (wired) |
|---|---|---|---|
| T1 | (−1.9, +6.4) | (−4.3, −0.3)* | — |
| T2 | (−0.6, +5.8) | (−2.11, −1.14) | source |
| T3 | (+1.2, +5.4) | (−0.18, −1.85) | sr1+ |
| T4 | (+3.4, +4.8) | (+1.83, −2.58) | sr1− |
| T5 | (+5.4, +4.0) | (+3.52, −3.20) | sr3 (Hall) |
| T6 | (+7.4, +3.5) | (+5.25, −3.84) | — |
| T7 | (+9.6, +2.6) | (+6.9, −4.4)* | — |
| B1 | (−7.3, −6.3) | (−6.27, +0.38) | — |
| B2 | (−5.2, −7.1) | (−4.72, −0.18) | — |
| B3 | (−3.5, −7.7) | (−2.85, −0.87) | — |
| B4 | (−1.4, −8.4) | (−1.16, −1.49) | sr2+ |
| B5 | (+1.1, −9.2) | (+0.78, −2.20) | sr2− |
| B6 | (+3.4, −10.0) | (+2.75, −2.92) | sr3 (Hall) |
| B7 | (+5.7, −10.9) | (+4.96, −3.73) | drain |
| B8 | (+8.4, −12.1) | (+5.6, −4.0)* | — |

\* geometric estimate (arm fit unreliable); not load-bearing — no wired role.

Internal consistency checks on the assignment: Hall pair T5–B6 junctions sit nearly opposite across the spine (Δx = 0.8 µm) ✓; both Rxx segments lie inside the source→drain span T2 (−2.11) → B7 (+4.96) ✓. The alternate T-indexing (top-left lead = T1) also passes these checks but requires the right-side lead — which lands on mesa-blue material — to be a gate (would short to channel): disfavored. The alternate B-indexing (wide-left = B1) puts part of sr2 outside the current path, mildly inconsistent with sr2's strong SdH signal: disfavored. Primary indexing carries a ±1 residual ambiguity on both arcs; its effect is bounded below.

### Coverage classification (per transport channel)

| Channel | Segment (stage µm) | Raman coverage | Margin to R1 box edge |
|---|---|---|---|
| sr1 (T3–T4) | spine (−0.18, −1.85) → (+1.83, −2.58) | **covered** — inside R1 (ABA strong) | ≥ 1.9 µm |
| sr2 (B4–B5) | spine (−1.16, −1.49) → (+0.78, −2.20) | **covered** — inside R1 (ABA strong) | ≥ 2.0 µm |
| sr3 (T5–B6) | spine cross-section x ≈ 2.8–3.5 | **covered** — inside R1 | ≥ 1.3 µm |
| current injection at T2/B7; graphene under all contact metal | arm tips / under gold | **uncovered** (Raman-dark under metal) — no fused claim; neither contract claims these | — |

Index-shift variants: T-alt sr1 = (−2.11 → −0.18) and B-alt sr2 = (−2.85 → −1.16) both remain inside R1 (min margin 1.37 µm). No interpolation used anywhere; uncovered stays uncovered.

## Step 3 — temporal registration

**Registration revises the Raman stage stamp.** The Raman contract stamped stage S = "post-fab (apparent, unconfirmed)". The registration evidence says **post-etch + post-contact-metallization but pre-top-gate**: the channel spine is Raman-bright with a clean, un-attenuated trilayer spectrum (spine amplitudes ≈ arm amplitudes) and no gate overlay is visible over the mesa in either video image — yet the transport device (2026-07-16) is gated by `k_tg` through 15.6 nm hBN. A top-gate layer was therefore added to the channel *after* the map. (Top hBN was already present at map time — hBN E₂g observed.) **Returned finding to the Raman contract** — this partially answers its pending build-stage question.

Build steps between map (2026-05-14/15) and transport (2026-07-16), tagged by conversion risk (recipe ordering: metal deposition on/near region > transfer/pickup > chemical+bake > clean thermal):

| Step | Risk class | On/near sr1+sr2? |
|---|---|---|
| Top-gate fabrication over the channel (metal deposition if metal TG — highest class; transfer/pickup if graphite TG; which is undocumented) | **highest / second** | **directly over both** |
| Bonding / packaging (undocumented) | moderate-low (off-mesa) | near contacts |
| Cooldown to 1.2–1.3 K | clean thermal (lowest) | yes |

Directionality: documented conversion runs **ABC→ABA only**. Both calls read ABA, so the intervening risky step cannot have created a false agreement: an ABA region at map time stays ABA through any later processing, and transport confirms ABA after the step. The gap's real cost is scope, not validity: **neither modality constrains the pre-fabrication stacking** — contact metallization (the highest-risk converter) preceded even the Raman map.

## Step 4 — per-region fusion

| Channel | Transport verdict (2026-07-16) | Raman verdict (stage: pre-TG post-contacts, 2026-05-14/15) | Coverage | Fused verdict | Mechanism class |
|---|---|---|---|---|---|
| **sr1 (T3–T4)** | ABA — **strong** (two-pocket FS {f_ML, f_BL} at ±6e12, n-tracked partition, grid-change robust) | R1: ABA — **strong** (2D lineshape match + M-band cross-check at 2.33 eV) | covered | **ABA — strong (concordant, cross-modal)** | **Concordant** — band structure read electrically and optically; strongest class this recipe produces |
| **sr2 (B4–B5)** | ABA — **strong** (same pair both densities; partition-consistent fan columns) | R1: ABA — **strong** | covered | **ABA — strong (concordant, cross-modal)** | **Concordant** |
| sr3 (T5–B6, Hall) | no stacking verdict (density scale n_Hall/n_gate = 1.02–1.10, consistent) | R1: ABA — strong | covered | ABA — strong, **Raman-only** at this cross-section | n/a — single-modality (transport row carries no stacking claim; not counted as concordant) |
| under-contact graphene; outside scan windows | no claim | unmapped / Raman-dark | uncovered | **no claim** | — |

Corroborating uniformity concordance (not a verdict row): transport's "no mosaic signature" (identical SdH template on both regions, ridge fits agree to 0.08%, F_L tone tests as breakdown not an ABC singleton) matches Raman's "no domains, no walls anywhere in the mapped area" — two independent null results on the same mixed-domain hypothesis.

**Per-device verdict (permitted: all covered regions concur):** **QC0426 is ABA (Bernal) — strong — over everything either modality can see**: both transport channels and the entire Raman-mapped exposed mesa (spine + all arms). Scope limits in hedges.

## Verify

- **Independence audit — PASS** (Step 1): no cross-citation; lock order + provenance exclude both directions of contamination.
- **Registration stress — PASS, no class flips.** Shifting registration by ±1.5 µm (each axis): sr1/sr2 segment margins to the R1 box are 1.9–2.3 µm > 1.5 µm — both stay covered/inside. Combined worst case (±1 index shift **and** full +1.5 µm y-shift) moves the B-alt sr2 endpoint 0.13 µm past R1's box edge — into the inter-arm/R2 area, which carries the *same* ABA-strong verdict from the same uniform map: coverage class and mechanism class unchanged. No region is registration-limited at the class level; the ±1 contact-index ambiguity is reported as a residual fork that does not touch any conclusion.
- **Directionality audit — PASS.** No reconciled-by-conversion rows exist (none invoked; the named risky step in Step 3 is *not* used as reconciliation). No Raman-ABA/transport-ABC rows exist. The one hard rule is unexercised but checked.
- **No-averaging audit — PASS.** Every fused strength equals its stronger input (concordant class only); no strength was averaged or inflated beyond "strong". The per-device verdict exists only because all covered regions concur (sr1, sr2 concordant ABA; sr3 Raman-only ABA; no contrary region).

## Step 5 — the call

**QC0426, fused: ABA (Bernal), strong, concordant across independent physics** — on sr1 (T3–T4) and sr2 (B4–B5) individually, and per-device across all Raman-covered + transport-probed area. No disagreement of any class; no unreconciled rows; nothing was forced — the concordance is the measured outcome, not an assumption.

### Named hedges

1. **Registration basis**: contact labels rest on lead-counting against the card's arc ordering (7 top / 8 bottom, exact match) — there are no lithographic fiducials or grower-labeled images. Residual ±1 index ambiguity on each arc and the wide-left-lead identity fork remain; bounded above — no variant changes any fused row.
2. **Stage gap / scope**: the Raman map is pre-top-gate; TG fabrication (highest-risk converter, directly over the channel) intervened before transport. Harmless to the concordance (ABA is the conversion-stable endpoint, and transport post-dates the step), but **pre-fabrication stacking is unconstrained by both modalities** — an originally-ABC flake converted during contact metallization is indistinguishable in this fusion.
3. **Uncovered area**: graphene under all contact metal and outside the two 20×20 µm windows carries no claim; sub-spot (< ~0.4 µm) ABC slivers are invisible to Raman, and transport bounds them only insofar as no mosaic/singleton signature appeared in the channels.
4. **Inherited from base contracts** (not re-litigated): transport — no LK mass split (blocklisted), qualitative hole-side Onsager overlay, D_offset = 0 unexamined; Raman — single wavelength (2.33 eV), N = 3 from fabrication records, at-sample power unrecorded (caps the "no ABC resolved" claim), instrument-inflated absolute FWHM (used morphologically only).
5. **R2 box contamination (returned finding to the Raman contract)**: R2's box edge (x ≲ −7.5, y ≈ 3–4.5) clips the back-gate graphite tab — the blue-shifted 2D (~2708 cm⁻¹) pixels there are graphite, not trilayer. R2's ABA-strong verdict stands on its arm pixels; recommend trimming R2 to x ≥ −7. No fused row rests on R2.

### What would settle / firm (no unreconciled rows — all optional strengtheners)

- Grower confirmation of the build timeline (map stage, TG material/date) — retires the stage-stamp revision from "apparent" to documented.
- Grower's pad-map or a labeled image — retires the ±1 indexing fork.
- LK mass per branch (transport) and a red-excitation/ULF Raman point — the base recipes' own firming steps.
- s-SNOM only if sub-spot ABC slivers ever matter; nothing in either dataset motivates it.

---

## Files (all in /tmp/qc0426-fusion/)

- `result.md` — this contract
- `registration_artifact.png` — **the Step 2 artifact**: v003 video image, stage frame, contact labels T1–T7/B1–B8, sr1/sr2/sr3 segments, source/drain, Raman region boxes R1–R3, scan windows, Spot1
- `v003_seg.png` — gold / stack-blue color segmentation used for the lead census
- `v003_full.png`, `v003_mesa/top/bottom/topL/topR/botL/botR/leftlead.png`, `v000_*.png` — zoom series
- `registration.npz` — spine fit, tips, junctions (arrays)
- `reg1_zoom.py` … `reg4_register.py` — rerunnable registration scripts
