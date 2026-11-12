**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Ablation-series lock (no-corpus offline stages); design + grading: Primer doc "HERA T1 no-corpus control - vti-02.md". Locked as produced; not edited.

# vti-02 — fused stacking verdict (Raman × transport, 2026-08-24)

Fusion of the locked transport call (session 2026-08-23/24) with the device
group's Raman/fab record. Method: the transport leg was verified against the
ana notebook (final-call cell matches `transport-call.md` verbatim; each cited
evidence line was checked against the stored per-run reads and figures —
archived under `artifacts/`, see below). The Raman leg was assessed on what the
document itself carries; its verdict wording was treated as an input to weigh,
not a conclusion to inherit.

## 1. Per-channel table

One wired pair this cooldown: **sr1 = B_1–B_2** (source T_0 → drain B_3).

| Channel | Transport | Raman | Fused | Basis for the fused row |
|---|---|---|---|---|
| sr1 (B_1–B_2) | **ABAB (Bernal), strong.** Five convergent lines: R_CNP(D) ×14 rise then saturation at ≈3.4 kΩ (not insulating); D-symmetric response 0.85–0.90 over the reachable ±window; 4-fold LL fan with ν=±4-first and non-monotonic ν=0 (crossings at ≈2.4 / 7.2 T) at D≈0; 2-fold-split fan with monotonic ν=0 at D−D0≈+0.20; meV-scale activation gaps (Δ≈1.8 meV at +0.28 V/nm). Evidence chain verified in `inputs/20260823_ana.ipynb` and figures. | **ABC lean; weak as evidence about this channel.** Attaches to the **pre-stacking parent-flake stage** (with internal stage ambiguity — hedge H2). The record's own "strong" qualifies that stage, not the finished device: no spectra or map in hand ("pending"), instrument/date unknown, laser-cut noise admitted, and the record itself names stacking/anneal/cut/litho as ABC→ABA conversion risks postdating the read. | **ABAB (Bernal), strong** — for this channel as built and measured. Carried alongside it, unharmonized: a **well-evidenced disagreement with the pre-fab expectation** ("cut region contains no ABA"). | Transport is a direct, current, multi-signature measurement of exactly this region; the Raman ABC is a stale prior at a different build stage with no inspectable data, and by its own framing is "not ground truth". The ABC→ABAB tension does not indict either leg: conversion during fab, spatial mismatch, or an erroneous original read are all live, and the inputs cannot distinguish them (§2, §4). Concordance is not forced: the fusion does **not** conclude the parent flake wasn't ABC, and does **not** confirm the "no ABA in the cut region" expectation — transport contradicts that expectation for the one region it can see. |

No other named channel exists: T_1–T_4 dead as provided, sr2/sr3 not
connected, no Rxy pair. The rest of the device is **cannot tell — unmeasured**
by both legs (Raman has no post-stack coverage; transport has no probe).

## 2. Spatial / temporal correspondence

**Spatial: the two legs cannot be placed on one coordinate frame.**
`raman.md` carries no map, no coordinates, no optical image; no frame bridges
(optical, GDS, build-step list) were supplied; the parent-flake URL is not an
input. The device card gives pad labels and wiring only — no physical geometry
tying B_1–B_2 to any location on the parent flake. The sole spatial link is
the fab record's narrative claim that the rhombohedral domain was cut out and
became the device region. **Cost to the fusion:** (a) "channel was ABC and
converted during fab" cannot be separated from "channel never overlapped the
mapped ABC domain" — so the transport ABAB cannot be read as evidence about
conversion, and the Raman ABC cannot localize where ABC might survive; (b) ABC
surviving elsewhere in the device (under dead contacts, outside the B_1–B_2
region) is neither supported nor excluded by anything in the inputs.

**Temporal: known ordering, unknown dates, with one internal inconsistency.**
Raman acquisition date is unknown; stage is stated as pre-stacking. Transport
is firmly dated (2026-08-23 20:27 → 2026-08-24 11:16, close-out clean). Between
the two sit stacking, anneal, cut, and litho — each named by the Raman record
itself as an ABC→ABA conversion risk. The record is additionally inconsistent
about where the cut falls: the header lists the cut as *postdating* the read,
while the findings ("the rhombohedral domain survived the cutting process",
"some spectra look like noise due to the laser cutting") require *post-cut*
spectra. Whether "survived the cut" is Raman-evidenced or assumed cannot be
determined from the inputs. **Cost:** the number of conversion-risk steps
between the last Raman evidence and transport is itself uncertain (3 or 4),
and the one fab-stage survival claim the record makes cannot be graded.

## 3. Named hedges

- **H1 — testimonial Raman.** No spectra, map, or acquisition metadata in
  hand; the ABC identification cannot be quality-checked (2D-mode line-shape
  assignment near laser-cut damage is exactly where such reads fail).
- **H2 — stage ambiguity inside raman.md.** Header (cut postdates read) vs
  findings (post-cut spectra implied) conflict; see §2.
- **H3 — no frame bridge.** Channel-to-domain overlap is asserted by the fab
  narrative, not verifiable from the inputs.
- **H4 — stage gap.** Every step between Raman and transport is a named
  ABC→ABA conversion risk, so the ABC/ABAB disagreement cannot, by itself,
  indict either measurement.
- **H5 — single-channel transport.** Only B_1–B_2 is probed; a stacking-domain
  boundary or residual ABC anywhere else in the device is invisible this
  cooldown (no second pair, no Rxy).
- **H6 — transport residuals.** ABCB with accidentally compensated asymmetry
  is excluded by LL phenomenology (4→2-fold evolution, ν=0 crossing pattern),
  not by symmetry alone; D reachable only to +0.32 / −0.13 V/nm, T ≥ 1.17 K;
  n, D are on the session's own calibration (c_bg/c_tg = 0.71, n = 0.82·n_geo).
- **H7 — verdict-wording discipline.** The Raman record's "strong" lean was
  re-scoped to the stage it attaches to, per the fusion contract; it was not
  inherited as device-stage strength.

## 4. What would settle it

The sr1 stacking row itself is settled at strong by transport; what remains
open is the ABC↔ABAB tension (where the pre-fab ABC went) and the unmeasured
remainder of the device:

- **Obtain the Raman map + spectra + acquisition metadata from Ben** (listed
  as pending). This converts H1/H2 directly: grades the original ABC
  assignment, fixes the acquisition stage, and gives coordinates.
- **A frame bridge**: pre/post-cut optical images and the GDS placed on the
  Raman map, locating the B_1–B_2 channel within (or outside) the mapped
  rhombohedral domain. Converts H3 and separates "converted" from "never
  overlapped".
- **Raman on parent-flake offcuts/remnants** (post-cut, never stacked), if
  they exist: isolates the cut step's conversion effect from
  stacking/anneal/litho. Post-fab Raman on the device itself is off the table
  per the record (no exposed layer after gating).
- **Next warm-up: repair/rebond T_1–T_4 or rewire sr2/sr3** to probe a second
  region and an Rxy pair. Converts H5 — a second region either reproduces
  Bernal phenomenology or finds the missing ABC.
- **Extended transport window** (−D beyond −0.13 V/nm via a rewired gate box;
  T < 1.17 K) to tighten the ABCB-compensation and small-gap exclusions (H6).
- **A sister device from the same parent flake**, if any exists, measured by
  either modality: discriminates "original Raman read wrong" from "conversion
  during this device's fab".

## Artifacts

Evidence figures extracted (not executed) from `inputs/20260823_ana.ipynb`;
regeneration script `artifacts/extract_figures.sh`:

- `artifacts/cell020_out1.png` — run 3 coarse gate map, single CNP ridge, coarse R_CNP(D)
- `artifacts/cell024_out1.png` — run 4 R_CNP(D) saturation, peak width, D-symmetry ratio
- `artifacts/cell028_out3.png` — run 6 fan at D≈0: 4-fold ν lines, ν=0 dips ≈2.4/7.2 T
- `artifacts/cell032_out2.png` — run 7 fan at D−D0≈+0.20: 2-fold split, monotonic ν=0
- `artifacts/cell035_out2.png` — runs 8–18 T ladder + Arrhenius, meV-scale gaps

Each figure was checked against the corresponding notebook read and the final
call's numbers; no discrepancies found.

## Provenance

Inputs received, in full and nothing else: `inputs/transport-call.md`,
`inputs/raman.md`, `inputs/20260823_ana.ipynb` (parsed, not executed),
`inputs/session_notes.md`, `inputs/device_card.md`. No prior fusion attempt,
draft, or verdict for vti-02 was seen; no third-party read, lean, or reaction
to either modality's call was seen. No web fetches or searches (the
parent-flake URL in `raman.md` was not accessed); no repository or notes
directory was read. Fusion produced 2026-08-24 by a fresh instance from these
inputs alone.
