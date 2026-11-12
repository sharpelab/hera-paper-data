# 2026-07-17 — QC0426 Raman read + Raman×transport fusion (e2e)

First end-to-end execution of the Raman fusion leg on a real device: two
fresh instances, each corpus-allowlisted, each blind to what it had to be
blind to.

## Inputs

- Raman data: grower-supplied WITec project
  (`$HERA_DATA/raman-qc0426/06_3LGr-device.wip`) — 532 nm; Spot1 + two
  20×20 µm hyperspectral scans (61×61 @ 13 s, 51×51 @ 11 s); two
  stage-registered video images; full spectral range −891…3652 cm⁻¹.
  In-fiber power 4–6 mW (at-sample unrecorded); acquired 2026-05-14/15.
- Transport contract: the locked 2026-07-16 capstone call
  (`../2026-07-16-QC0426-session-3/hera_scratch/call_draft.md`).

## Runs

- **`raman-read/`** — fresh instance, no sight of any transport result,
  executing `recipes/investigations/raman-stacking-id.md` via
  `models/raman_stacking/` (`load_wip`). Verdict: all mapped device
  regions **ABA (strong)** — single FWHM population 63.7 ± 0.7 cm⁻¹, no
  bimodality or walls; lineshape matches the ABA-3L reference panels at
  2.33 eV; **M-band cross-check concurs** (single M⁻ at 1746 cm⁻¹).
  Scan LA-002 found partial + defocused (weak/consistent-with only);
  Spot1 is bare substrate (uninformative). Stage read off the video
  images as post-fabrication-apparent.
- **`fusion/`** — second fresh instance executing
  `recipes/investigations/stacking-raman-transport-fusion.md` on the two
  locked contracts + device card. Registration by lead census on the
  video images: all 15 contacts placed in the stage µm frame (±1.5 µm
  measured); sr1/sr2 channel segments covered with ≥1.9 µm margin.
  **Fused: sr1 ABA (strong, concordant); sr2 ABA (strong, concordant);
  per-device ABA (strong)** — all covered regions concur. All four
  Verify audits pass.

## Findings beyond the verdict

- **Stage-stamp revision (fusion → Raman contract)**: the map is
  **pre-top-gate** (spine Raman-bright, no gate overlay in imagery), so
  top-gate deposition intervened between map and transport — harmless
  here (ABA is the conversion-stable endpoint; transport post-dates the
  step) but the fusion certifies the finished device only: pre-fab
  stacking, graphene under contact metal, and sub-0.4 µm slivers are
  outside both modalities' reach.
- **R2 box contamination (fusion → Raman contract)**: R2's edge clips
  the back-gate graphite tab (2D ≈ 2708 cm⁻¹ pixels are graphite, not
  trilayer); no fused row rests on R2.
- Residual fork: a 9th bottom-side lead's identity (B1-shifted end
  contact vs second gate lead) — evaluated under both indexings, no
  class flips.

## Grower answers (2026-07-17, Slack)

- **Stage: after final fab, before loading into the VTI** (grower). This
  supersedes the fusion run's imagery-based "pre-top-gate" inference —
  the top gate is graphite, near-transparent optically, so the absence
  of a visible gate overlay never implied pre-gate (the Raman read's
  original "post-fab-apparent" stamp was correct). Map→transport stage
  gap is loading + cooldown only: the concordance is stage-tight.
- **Power**: the in-file in-fiber values (4–6 mW) are the recorded laser
  power; at-sample conversion remains uncalibrated (hedge stands,
  reduced).
- **Pre-fab Raman maps of this flake exist** and are being sent — the
  deciding artifact for the pre-fab stacking question (flake was
  screened rhombohedral; post-fab both modalities read ABA).

## Correction (2026-07-18, PI review)

The post-fab map probes the **whole vertical stack — substantially the
graphite gates**, whose Bernal-like 2D superposes on the buried channel's
signal; the per-spectrum metrics cannot unmix them. Standings revised:

- `raman-read/` standalone verdict: **downgraded ABA (strong) →
  consistent-with-ABA, gate-contaminated** — the map's uniformity
  (63.7 ± 0.7 cm⁻¹) is as consistent with a uniform gate stack as with a
  uniform channel.
- `fusion/` per-region rows: **concordant → transport-dominant** —
  transport (in-situ, channel-selective) carries the device verdict;
  the Raman leg is weak corroboration at best. The registration work and
  returned findings stand.
- The **pre-fab map (incoming) is the load-bearing Raman evidence** for
  this device.

This burn produced the recipe's through-stack screen
(`raman-stacking-id.md` Verify). The `result.md` files are completed
records and are left as executed; this section governs.

Working `.npz` intermediates and video-zoom series were not archived;
regenerate via the scripts in each dir against the `.wip`.
