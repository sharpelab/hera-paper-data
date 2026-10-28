# Arm 1 — shield & adjudicator instructions (Aaron)

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** This document carries
the campaign frame (`hera/blinding.md`); it must never appear in a
deployed kit or an agent-visible reference list.

*You are the unblinded side of the arm-1 series: you hold the Raman
ground truth, prepare the blinded kits, and adjudicate. Zack must not
learn any Raman content — or anything about the composition of the device
set — until each device's calls are locked. Full protocol:
`prereg-protocol.md`; these are your duties only. Everything you lock is
a commit to this directory (`hera/campaigns/stacking/`) on the `hera`
branch — git supplies the timestamp and ordering.*

## Before the series (once)

- [ ] Write **one Raman document per device**. Each must contain:
  - where the **full raw Raman data** lives (the project/map files, e.g.
    WITec `.wip` — acquisition metadata rides along in-file), plus your
    per-spot reads (ABA / ABC / mixed / unclear),
  - **spot locations** mapped onto the device geometry (optical image
    with marked spots, or coordinates) — the fusion step reconciles Raman
    spots against transport contact pairs spatially, so location is
    load-bearing,
  - your overall per-device lean, with a strength word,
  - acquisition date.
- [ ] Seal them: keep the files on your machine only. Commit each file's
  `sha256sum` output to `raman-hashes.md` here, **before the first device
  cools**. Name files by wafer/device ID — nothing Raman-derived. Don't
  edit a file afterward: an edited file no longer matches its hash and
  voids that device's seal.
- [ ] Reveal nothing about the pool: not the device count beyond the
  agreed 3–4 cap, not the expected mix of stackings.

## Per device, at intake

- [ ] Assign a neutral alias — no hint of stacking, screening result, or
  ordering by promise. The alias↔device mapping stays with you until that
  device unseals.
- [ ] Fill the intake fact sheet: copy
  `hera/templates/stacking-campaign/intake-facts.template.md` and
  form-fill every field (limits, caps, geometry, wiring, contact map) —
  no prose beyond the listed fields.
- [ ] Run the two greps in the fact sheet's header before sending — Zack
  reads the sheet raw, so a frame word in it has leaked before any
  downstream check.
- [ ] Send the fact sheet to Zack. He instantiates the kit from the
  frozen templates and runs the blinding checks
  (`hera/templates/stacking-campaign/README.md`). The fact handoff is
  the blind's cut point; every step after it is runnable by either side.

## Per device, adjudication

- Wait for Zack's confirmation that **both** the transport call and the
  HERA-fusion verdict are locked. Do not open `<alias>/fusion-verdict.md`
  — you adjudicate blind to it.
- Read: `<alias>/transport-call.md` + your own Raman document for this
  device (this device's only).
- Write: your adjudication — per-region where the evidence supports it,
  every judgment carrying a strength word (decisive / strong / weak /
  consistent-with / uninformative), evidence cited. Raman is not
  automatically right: where the modalities disagree, say which you
  believe and why.
- Lock it: commit `<alias>/adjudication.md`. Only then are the three
  verdicts compared.

## Never, while the series runs

- Reveal any Raman content — spectra, reads, leans — before that device's
  transport call is locked.
- Hint at the composition of the device set ("this one's the interesting
  one", how many ABC, ordering by promise).
- Confirm, deny, or visibly react to any HERA call mid-series.
- Open a fusion verdict before your adjudication for that device is
  locked.
- Discuss series devices' stacking anywhere Zack can see it.
