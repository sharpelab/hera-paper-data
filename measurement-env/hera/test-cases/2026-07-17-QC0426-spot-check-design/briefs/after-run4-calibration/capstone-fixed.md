<!-- variant: capstone-fixed | corpus-faithful to post-deletion refs (arm C/D)
     The campaign sections of the archived capstone-2 session brief
     (docs/notes/2026-07-17-QC0426-capstone-2/hera_session.md), verbatim,
     with the autonomy/grant/VERIFY protocol sections stripped (moot in an
     Identical to capstone-live.md minus the Tool overlay-validity
     parenthetical, matching what the fixed corpus (e92c157) generates from
     brief-QC0426 / the kit template. Serve to post-deletion refs only. -->

# Brief

## Campaign goal

**Determine the stacking order of QC0426 (trilayer graphene): ABA (Bernal) vs ABC
(rhombohedral)** — an independent, evidence-cited, region-resolved call (or a
calibrated "cannot tell"), per the governing investigation's output contract.

## Recommended recipes

The expected arc:

- `investigations/trilayer-stacking-fs-count.md` — the **governing investigation**
  (Fermi-surface counting at D ≈ 0): the decision procedure, the Verify suite, and the
  output contract. It orchestrates the measurement recipes below.
- `device-init/cnp-and-dline-calibration.md` — the CNP location and (n, D) calibration,
  **found fresh this session** (the device card carries no CNP).
- `measurements/sdh-spot-check.md` — the cheap fixed-(n, D) SdH frequency-content check
  that precedes the fan: it pins the onset, the tone frequencies, the B-step, and which
  side (hole/electron) gives cleaner SdH.
- `measurements/landau-fan.md` (the VTI variant takes precedence).
- `measurements/gatemap.md`.
- `measurements/temperature-dependence.md` (the VTI variant takes precedence — its
  guard set is mandatory for every elevated-T segment). The investigation's LK
  mass split (Verify) is in-arc, not a detour.

The rest of the corpus is available, not forbidden; off-arc composition with stated
rationale is encouraged under your scope rules (> ~30 min off-arc gets the detour
flag). The **contact configuration is provided and hardwired** (device card) — no
contact survey is in the arc, and there is no mux to reroute with: a dead provided
contact is an operator rewiring problem — flag it, don't detour.

**Tool:** the FS-count forward model (`hera/models/trilayer_fs_count/fs_count_b0.py`)
is the primary arc-reader, per the investigation's Verify.

## Blocklist

- `device-init/gate-leakage-survey.md`
- `device-init/gate-range-finding.md` (+ `-vti` variant)
- `device-init/silicon-backgate-survey.md`

"Range-finding" here is the leakage / gate-range **survey** class — it does **not**
restrict `cnp-and-dline-calibration` or CNP / (n, D) location.

## Session arc

Gate C (a cheap liveness check on the provided contact configuration — first-session
branch, no designated references), then the investigation ladder per
`trilayer-stacking-fs-count.md`, to the call in the ana notebook.
