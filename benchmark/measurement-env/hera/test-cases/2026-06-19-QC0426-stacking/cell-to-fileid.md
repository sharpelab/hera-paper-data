# Cell ↔ file_id map — QC0426 stacking (session-3, 2026-06-19)

Human aid, not served. Fixture indices == source indices (notebook cropped from
cell 0). The cut is at index 45 (inclusive); cells 46–47 (the Landau fan) are the
answer key.

| cell | what | file_id |
|---|---|---|
| 35 | Step 1a — 1D CNP locator (TG sweep) | `data/0` |
| 37 | Step 1b v1 — 0 T gate map (died on LS335 per-point read) | (no saved dir) |
| 41 | Step 1b v2 — 0 T TG–BG gate map | `data/1` |
| 43 | Step 3a — SdH spot check, HOLE (n=−5e12) | `data/2` |
| 45 | Step 3b — SdH spot check, ELECTRON (n=+5e12) — **latest at cut** | `data/3` |
| 46–47 | Step 4 — Landau fan, electron D=0 (**post-cut answer**) | `data/4` |

Allowlist for the `after-sdh-spot-checks` frontier: `data/[0,1,2,3]`. `data/4`
(the fan) is the leak.
