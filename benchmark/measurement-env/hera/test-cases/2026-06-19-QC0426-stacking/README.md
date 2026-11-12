# QC0426 stacking — replay fixture (VTI, 2026-06-19 session-3)

A HERA replay fixture frozen from QC0426's stacking campaign (trilayer graphene,
VTI). Cut after the electron SdH spot check, before the Landau fan.

**Why this fixture exists.** It is the layer-B (decision) half of verifying the
SdH/fan analysis fix: at the `after-sdh-spot-checks` frontier, does the agent
**design the Landau fan without the two acquisition faults** the as-run fan
carried (clipping from under-ranged fixed sensitivity; under-settling from a
shaved fast-axis dwell)? Run `hera-replay` from a worktree at the pre-fix commit
(`82883a9`) vs the post-fix commit (current `hera`) and compare the proposed
fan — the recipe lever is `landau-fan.md` (burn #7 worst-corner dynamic-range
guard + burn #8 fast-axis settling, absent pre-fix).

## Frontier

- **`after-sdh-spot-checks`** (cut 45) — see `frontiers/after-sdh-spot-checks.md`
  and `ground_truth/after-sdh-spot-checks/`.

## Source

Cropped from `hera/docs/notes/2026-06-19-QC0426-session-3/20260619_measure.ipynb`
(cells 0–45, outputs preserved). Fixture indices == source indices.

## Per-run modality (allowlisted data)

| file_id | modality | cell |
|---|---|---|
| 0 | 1D CNP locator (TG sweep) | 35 |
| 1 | 2D 0 T TG–BG gate map | 41 |
| 2 | 1D SdH spot check, hole | 43 |
| 3 | 1D SdH spot check, electron (**latest**) | 45 |

`data/4` (the Landau fan) is the answer key — not served. See `cell-to-fileid.md`.
