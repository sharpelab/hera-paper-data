**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.**

# Pre-registration — offline-stage procedure and scoring

Declared 2026-08-27 (this file's first commit is the declaration time),
before the 2026-08-22 session's fusion or any subsequent offline stage ran,
and before any rerun outcome was known. Rulings: Zack (operator).

## Uniform clean-environment procedure

Every remaining offline stage (raman read or fusion) launches as:

- a fresh headless instance (`claude -p`), cwd = a fresh, isolated run dir
  under `$HERA_DATA` (`/data/sharpelab/hera-data/`), no Agent-tool wrapper —
  the brief is the entire prompt;
- operating rules folded into the brief (a "Working rules" section: uv-only
  Python, write only under the run dir, corpus read-only, no git, no URL
  fetch, parse-don't-execute notebooks, final-report shape);
- isolation additions relative to the 2026-08-21 procedure: the run dir's
  parent is not an input (sibling dir names leak existence metadata);
  harness-injected environment/project context is not an input — disclose
  in the provenance line if seen; the "never read" list names third-party
  reads/leans on either modality's call explicitly (the 2026-08-21 brief
  carried this only in the provenance-line requirement); and notebooks are
  JSON-parse only (the `nb`-tool affordance the 2026-08-21 wrapper allowed
  is withdrawn, matching the 2026-08-23 brief);
- explicit `--model` on the launch line; a machine-readable launch record
  (`--output-format json`) captured beside the run dir.

Exposure rule (unchanged from the 2026-08-23 fusion precedent): if the
verdict's provenance discloses an exposure, quarantine the run, reset the
run dir to inputs-only, rerun once; the clean run is scored regardless of
outcome, declared before the rerun's verdict is read.

## Per-arm settings

- **Model tracks the arm**: fable sessions get fable offline stages
  (`claude-fable-5[1m]`), opus sessions get opus (`claude-opus-5[1m]`).
- **Brief design tracks the corpus condition**: +corpus arms use the
  recipe-pointing brief form (method lives in the corpus; per
  `brief-vti-02-fusion.md`); no-corpus arms use the contract-hoisted,
  method-withheld form (per `brief-vti-02-20260823-fusion.md`). No other
  design changes per arm — in particular, no added hedging or steering
  for arms whose transport call is known to the operator to be wrong.
- **The staged transport call is the ana notebook's final cell** (the final
  call). Earlier blind calls, where they exist, are recorded in the staged
  file's provenance header, not staged as the call.

## Scoring rule for the cross-arm comparison

For the cross-arm (corpus × model) comparison, the scored offline artifacts
are the **clean-environment runs** — including reruns of stages originally
executed under the Agent-tool launch frame, which injects the launching
repo's git status (branch, commit subjects) into the instance's context.
The prereg-series locked verdicts are unchanged and remain the verdicts of
record for the prereg series; they are reported alongside.

Existing frame-sensitivity datum: the 2026-08-23 fusion's exposed run 1 and
clean run 2 returned identical verdicts.

Rerun program (queued after the missing offline stages complete):

- vti-02 2026-08-21 fusion → lock at `vti-02-20260821-rerun/`
- vti-01 raman read + fusion → lock at `vti-01-rerun/`

Rerun briefs are the original briefs with only the uniform-procedure deltas
(Working-rules fold-in, the two isolation additions, run-dir substitutions).

## Disclosure plan

Declared outcome-blind: if the clean-environment reruns are concordant with
their locked originals, the launch-frame leak, the reruns, and the
concordance are reported in the supplement, and the main text carries the
uniform clean-environment results. If any rerun is discrepant with its
original, the discrepancy is promoted to the main text and both results are
reported.

## Rerun-program clarification — vti-01 stage chaining (ruled 2026-08-27)

The vti-01 rerun is the end-to-end pipeline: the rerun fusion consumes the
**rerun read's** contract (`result.md` → `inputs/raman-contract.md`, with
its provenance and region raster), exactly as the original pipeline
chained. The alternative (pinning the fusion to the original locked
`raman-contract.md`) was considered and rejected. Ruling: Zack,
2026-08-27 — recorded while the rerun read was in flight, before its
verdict was read by anyone.

## vti-01 rerun disposition + pinned diagnostic (ruled 2026-08-27)

- The chained vti-01 rerun fusion is **discrepant-in-part** with the
  locked original: all stacking verdicts and strengths identical; the
  mechanism-class column diverged (original: sr1/sr3
  reconciled-by-conversion; rerun: all channels uncovered →
  single-modality, the stricter registration reading). Per the disclosure
  rule, promoted to the main text; both results reported. Ruling: Zack,
  2026-08-27.
- **Pinned diagnostic fusion** (this section is its pre-declaration): one
  additional clean-environment fable fusion consuming the ORIGINAL locked
  raman contract set (the byte-identical files the original fusion
  consumed) with the same constant legs, under the rerun brief form. It
  isolates upstream-contract shape from fusion-instance registration
  judgment. Post-hoc diagnostic — labeled, reported, **not scored**; the
  scored rerun remains the chained run per the chain ruling above.
  Ruling: Zack, 2026-08-27, recorded before the diagnostic launched.
