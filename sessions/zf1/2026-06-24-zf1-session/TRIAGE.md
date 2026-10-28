# Triage resolution — zf1 2026-06-24 (toploader) · crank `tl_crank` (2026-06-25)

Post-session crank for the zf1 SC-characterization marathon
(`aaron/20260624-3-zf1`). Note streams folded: agent `session_notes.md`,
Aaron's wiki notes (`20260624-zf1`), durable-artifact mining (the tactical
transcript was lost — see maintenance flag), and the changelog audit.

Landed via `subtask/tl_crank` (ff-merge to `hera`, no push). One fix per
subtask, reviewed and folded.

## Resolution table

| # | Item | Ruling | Change / commit |
|---|---|---|---|
| 1 | ana written one late batch (live record empty most of session) | apply (subtask) | `hera_tactical` land-ana-per-step · `fac8a59` |
| 2 | gate-Keithley template drift vs Aaron's snippet | apply (subtask) | base template `_setup_k2400` defaults commented · `afb07e2` |
| 3 | survey gatemap didn't plot 2T (Aaron) | apply — **scoped to the brief** | brief: explicit live-plot block incl. `sr830_2` · `0e287f5` |
| 4 | execute-cell 570s timeout < long sweep; stale-YDoc hang (~25min idle) | apply (subtask) | timeout → loud `EXIT_TIMEOUT(2)`; tactical gates long-run completion on hera-watch · `4b47fdf` |
| 5 | nb-collab inline `--markdown/--code` backticks → shell substitution drops fragments | apply (subtask) — **refuse** | `_reject_inline_substitution` on raw `` ` ``/`$(` · `fd3fcd4` |
| 6 | meas_config `I_bias` snapshotted before drive set → metadata ×25 wrong | apply (subtask) | template records `bias_channel`; hera-watch derives from live snapshot · `618cd84` |
| 7 | `calc_gate_voltages` returns `(1,)` arrays; `float()` errors (2 hardware-safe failures) | apply (subtask) | scalar args → floats · `7bb86b1` (recipe idiom hunk pulled → Aaron) |
| 8 | "stop using trip color in plots" (Aaron) = `tripcolor` rendering | apply (subtask) — Zack's call | `nD-map` render note → `pcolormesh`; crop term retired · `a469b89` |
| 9 | thermo staleness guard never reached the deploy template (changelog regression) | apply (subtask) | port `temperature_from_logfiles` + >300s warn into `hera/templates/base/` · `ed22674` |
| 10 | brief E1-vs-"E0 throughout" mismatch (surfaced live) | already fixed — verify | `03164e8` (pre-crank); canonical brief single-homed on E1 |
| S1 | sc-char Step 3 "sweep across zero" vs toploader never-cross-zero; magnet re-zero budget | defer → Aaron | recipe-science; `aaron-handoff.md` |
| S2 | D-sign anchoring (Aaron: D *is* anchored; card carries no D-sign) | defer → Aaron | device-card fact; `aaron-handoff.md` |
| S4 | `op_point(n,D)` helper (CNP-anchor block hand-retyped 6× w/ magic constants) | defer → Aaron | `aaron-handoff.md` |
| R | `calc_gate_voltages` call idiom now that scalars return floats | defer → Aaron | `aaron-handoff.md` |
| — | ana scaffold cells left dead; README-not-reaching-agents (meta); "field-kill not most decisive" (no misread found); estimate wall/token under-model | record-only / ignore (Zack) | — |
| HS-1..6 | hera-session / session-init issues (RTC-id bring-up failure; transcript-hook silent fail; placeholder sentinels; slot-autofill; re-init) | set aside this round (Zack) | maintenance flag below; backlog |

## Maintenance-window checklist (rig-side — on Zack's go, after he pushes `hera`)

1. Toploader rig: `cd ~/measurement_env && git pull` (after `hera` is pushed).
2. `scripts/install.sh` (re-installs agent prompts + shims; picks up the
   nb-collab behavior change, template fixes, prompt norms).
3. Sanity-check the new nb-collab behavior on the rig: execute-cell client
   timeout now exits 2 (`TIMEOUT`, kernel still running); inline `--markdown`/
   `--code` refuse raw backticks (point at `--*-file`).
4. **HS-2 — the marathon transcript's raw jsonl was never written; recovered
   manually via `/export`.** Claude Code never persisted this session's
   conversation jsonl (`~/.claude/projects/<proj>/<id>.jsonl` absent; only
   `scratchpad/`, `tasks/`, `session-env/`, `file-history/` under the session
   id). Root cause surfaced when `/export` failed with `EEXIST: mkdir
   '…/20260624-3-zf1'` — Claude Code does a **non-recursive `mkdir` of the
   (already-existing) session dir** and bails, so every transcript-persist
   attempt silently gave up all session. The backup hook therefore had nothing
   to copy (both `~/.hera/transcripts/` + `$SESSION_DIR/.transcripts/` empty) —
   the bug is **upstream of the hook**. Recovered the conversation by running
   `/export <path-outside-the-session-dir>` while the terminal was still open
   (archived as `transcripts/9ceaffa3-marathon-export.md`, rendered markdown, not
   raw jsonl). **Fix still needed** (the recovery was luck — the session happened
   to still be open): the mkdir must be recursive/idempotent so the jsonl
   actually lands; verify on the rig. 2nd consecutive near-loss.
5. (Open) repo-root `templates/toploader_measure.ipynb` (launcher copy) vs
   `hera/templates/base/` still diverge — full dedup remains backlogged.
