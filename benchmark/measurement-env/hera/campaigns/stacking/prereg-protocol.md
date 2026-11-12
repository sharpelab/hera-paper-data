# Arm 1 preregistration protocol — blinded device series

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** This document carries
the campaign frame (`hera/blinding.md`); it must never appear in a
deployed kit or an agent-visible reference list.

*Draft until frozen. This document becomes binding when it is committed
and the freeze tag (§3) is cut — both before the first series device
cools. It defines what the tag covers; cutting the tag (targeted at the
post-capstone-2 triage crank) is a separate act. Design rationale lives
in `hera-paper/notes/arm1-blinded-validation.md`; this doc declares, it
does not argue.*

## 1. Endpoints

- **Primary**: per device, a region-resolved stacking call per the output
  contract of `hera/recipes/investigations/trilayer-stacking-fs-count.md`
  (Step 7, all five parts). That contract is the pre-declared scoring
  rule; it is not restated here. **"Cannot-tell with reasons" is a valid
  outcome and is scored as such** — under the contract, a confident call
  without feature-level evidence is the protocol violation, not the hedge.
- **Secondary**: the HERA Raman-fusion verdict (§5 step 2), Aaron's
  adjudication (§5 step 3), and per-device run metrics per
  `hera-paper/notes/run-metrics-spec.md` (wall-clock, interventions,
  interrupted runs, token cost).
- **Framing**: the reported metric is **concordance** among transport
  call, fusion verdict, and adjudication — not accuracy. Raman is
  imperfect ground truth; a disagreement with a traceable evidence
  divergence is a result, not a failure.

## 2. Device flow

- Eligible: fresh Raman-screened rhombohedral-candidate devices that
  function at cooldown (gates up, credible contacts).
- **Every eligible device enters, in cooldown order. No selection** by
  either party at any stage.
- Series size: capped at 3–4 devices; the series ends at the cap or when
  device stock is exhausted, whichever comes first. A device that dies
  mid-investigation is reported as such, not silently replaced.

## 3. The freeze

One git tag on this repo covering, as deployed:

- the corpus (recipes, docs, models),
- the session brief template,
- the device-card template,
- the agent prompts (tactical, session-init, fusion),
- replay suite v1 (per `hera/docs/benchmark-plan.md`, 2026-07-16 update:
  frozen before capstone results are read; rides this tag).

Nothing under the tag changes mid-series. Tag target: the post-capstone-2
triage crank — after the Raman-for-stacking reference and the
fusion/adjudication recipe land, since anything the fusion step uses must
be under the tag.

**`hera/campaigns/stacking/` is outside the frozen surface**: it is the
series' append-only audit trail and grows during the series. Nothing
already committed here is ever amended.

## 4. The blind

- Zack (operator) is blind to each device's Raman results until that
  device's transport call locks, and blind to all *other* devices' Raman
  for the whole series.
- Aaron is the shield: holds the sealed Raman documents, assigns device
  aliases, issues each device's intake facts — the values the kit is
  built from (see `aaron-shield-instructions.md`).
- Every deployed kit passes the per-session checklist in
  `hera/blinding.md` before the session goes live.

## 5. Per-device sequence

**Locking mechanism** (applies to every "locked" below): an artifact is
locked when it is committed to `hera/campaigns/stacking/<alias>/` on the
`hera` branch — the commit supplies the timestamp, the branch history the
ordering audit. Sealed content is locked by proxy: the file stays with
Aaron; its sha256 is committed to `hera/campaigns/stacking/raman-hashes.md`.
Unsealing = committing the file itself, which must match the logged hash.

**Pre-series (step 0)**: Aaron commits each per-device Raman document's
sha256 to `raman-hashes.md` before device 1 cools. Zack sees hashes,
never content.

Then, per device (files under `<alias>/`):

1. **Transport call locked** (`transport-call.md`). E1 HERA runs the
   investigation to a defensible conclusion; the Step-7 call is locked.
2. **Fusion verdict locked** (`raman.md`, then `fusion-verdict.md`).
   Aaron unseals that device's Raman document — commits it, hash verified
   against `raman-hashes.md`. A **fresh HERA instance** — no session
   context — receives the archived artifacts (locked call, ana notebook,
   session notes) plus the Raman document, and produces a fused verdict.
   Locked before Aaron writes or reveals anything; the fusion instance
   never sees Aaron's views.
3. **Adjudication locked** (`adjudication.md`). Aaron — having seen the
   locked transport call and his own Raman document, and **not** the
   fusion verdict — writes his adjudication with calibrated strength
   vocabulary. Locked.
4. **Unseal and compare** (`comparison.md`). All three verdicts read side
   by side; concordance recorded. Nothing upstream is edited after this
   point.

## 6. Publication commitment

Published regardless of outcome: every device in the series, every
transport call, every fusion verdict, every adjudication, every run
metric, every deviation. No device or call is dropped from the report.

## 7. Deviations register

Any departure from this protocol — a mid-series change to anything under
the tag, a sequence break, a blind breach, a kit found leaking after
deploy — is recorded (what, when, why) in
`hera/campaigns/stacking/deviations.md` and published with the results.
