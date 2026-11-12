**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Nothing in this directory
is ever an input to a measurement or offline-stage instance.

# Stacking campaign — run & lock index

Working names ("T1", "replication", …) live in this file only; lock
directories, file contents, and commit messages use session dates. Locks
that predate this convention keep their paths — this directory is
append-only (`prereg-protocol.md` §3).

## vti-02 (all runs: same device, same cooldown)

| Working name | Session date | Live model | Corpus | Lock dir | Offline stage |
|---|---|---|---|---|---|
| arm-1 original | 2026-08-21 | claude-fable-5 | `13b07e9` | `vti-02/` (prereg series) | fusion locked (`vti-02/fusion-verdict.md`); clean-env rerun planned → `vti-02-20260821-rerun/` |
| replication | 2026-08-22 | claude-fable-5 | `13b07e9` | `vti-02-20260822/` | fusion, clean-env (this phase) |
| T1 · no-corpus | 2026-08-23 | claude-fable-5 | `039b0f5` | `ablation-2026-08/vti-02/` (pre-convention) | fusion run 1 quarantined + run 2 scored, both locked |
| T2 · Opus, no-corpus | 2026-08-24 | claude-opus-5[1m] | `039b0f5` | `vti-02-20260824/` | fusion, clean-env (planned) |
| T3 · Opus, +corpus | 2026-08-25 | claude-opus-5[1m] | `13b07e9` | `vti-02-20260825/` | fusion, clean-env (planned) |

The Raman leg for every vti-02 offline stage is the human-authored
`vti-02/raman.md` (sha256 `4b5ed8c7…`, seal ledger `raman-hashes.md`),
taken as-is — no raw Raman data exists for this device, so there is no
HERA raman-read stage.

Note: the 2026-08-25 session's ana notebook is named `20260824_ana.ipynb`
(session-init artifact). Provenance headers key on the session directory,
never the notebook filename.

"Live model" is the tactical session's model. Session-init (`hera-session`)
runs separately, on its own model, with its own transcript in each
archive's `transcripts/` — cite the tactical jsonl in provenance headers.

## vti-01

| Working name | Lock dir | Offline stages |
|---|---|---|
| arm-1 | `vti-01/` (prereg series) | raman read + fusion locked; clean-env rerun planned → `vti-01-rerun/` |
| ablated offline pair | `ablation-2026-08/vti-01/` (pre-convention) | raman read + fusion locked |

## Governing documents

- `prereg-protocol.md` — the arm-1 blinded-series protocol
- `prereg-offline-stages.md` — clean-environment offline-stage procedure,
  scoring rule for the cross-arm comparison, rerun program (declared
  2026-08-27)
- `deviations.md` — every departure from protocol
- Ablation-series design + grading doc of record: Primer,
  `Sharpelab/HERA T1 no-corpus control - vti-02.md`
