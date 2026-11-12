# QC0426 capstone-2 (2026-07-17) — triage log

Targeted crank (subtask `capstone2_archive_triage`, 2026-07-18): archive +
Aaron's two flags worked to root cause, plus the judicious session-notes
sweep. Archive: `hera/docs/notes/2026-07-17-QC0426-capstone-2/`
(provenance `17bc077`, clean). Aaron ruled the run **insufficient as a
capstone**; capstone-3 to follow.

Root cause (both flags, one defect): `fs_count_b0`'s solver limits
(|n| ≲ 3.5e12 grid edge, conduction band only) were quoted as "validity"
on four agent-visible surfaces; in this run the quotes steered three
consecutive design decisions — spot-check density ±3.0e12 (measure cell
39, "kept under the FS-model's 3.5e12 overlay clamp"), side = hole (the
electron ML is invisible at 3e12; wins the ±6e12 head-to-head,
20260714.2), fan n_max = −3.5e12 of −6.4 reachable (cells 43/44). The
first triage draft proposed additional clauses; ruled the other way —
fix the tool, delete every quote (chiron memory: "Paper-over reflex").

## Resolution table

| # | Item | Ruling | Change / commit |
|---|---|---|---|
| 1 | Archive capstone-2, commit alone | done | `6b39599` (landed) |
| 2 | A1: hole side chosen again (Aaron) | not a side-choice-rule failure — model fix + quote deletions; no new side-choice prose | model `edbd476` (Aaron) + `9d11dbc` + `c01180e` (staged, replay-gated) |
| 3 | A2: narrow fan gate range (Aaron) | recipe text drove it (lever-2 clamp); delete, don't reword | `9d11dbc` |
| 4 | Spot-check density suppression (mined; cell 39) | same root, covered by the deletions | `9d11dbc`; watch on capstone-3 |
| 5 | Triage's own Diffs A/B (add clauses) | withdrawn — paper-over reflex; burn recorded | memory `23d053b` |
| 6 | Hole-side prior bullet (Why) | delete; physics stays in survey §2; A/B of a physics-note variant pending Zack↔Aaron | `c01180e` (staged) |
| 7 | S3: `sdh_onset` per-dominant-tone + nan classes (backlog refire) | tool rewrite (fable subtask), accepted via replay | `2258fb0`..`95d2d75` (landed) |
| 8 | S1: hera-watch gate-current channels (unpunt fired 2×) + S4: in-flight soft-clip | subtask proposed; pending go | — |
| 9 | S2: `settle_s` ownership line, VTI card | proposed with the T_e item; pending Aaron | — |
| 10 | VTI card T_e (~8 K) vs session-3 fitted T_e0 = 6.1 K | to VTI rig backlog (Bingcheng): careful characterization; card unchanged; not HERA-linked | `hera/docs/vti/vti-rig-backlog.md` |
| 11 | Device-card calibration carry-forward for capstone-3 | ruled no — capstones include calibration, as the blinded runs will | — |
| 12 | Verify model + onset fixes offline | `replay_verify` subtask running (arms A–D incl. cost-floor counter-metric) | — |
| 13 | nb-collab first-command sync race | Phase 1 subtask running (deterministic server resolution) | — |
| 14 | Metrics draft row | drafted (`hera-paper/analysis/drafts/`); HAND-CHECK fields flagged, caveat "insufficient as capstone" (Aaron) | — |

| 15 | sdh_onset follow-up: partition-claim recipe line (subtask suggestion) | declined — restates the Why harmonic screen + STYLE rule 14; re-open if a harmonic-tainted partition claim recurs after bidirectional `harmonic_of` | — |
| 16 | sdh_onset follow-up: bidirectional `harmonic_of` | fresh subtask; landed to `hera` | `f1aaa23` tip |
| 17 | hera-watch guards: soft-clip %FS + gate-current columns + leak flag | subtask; reviewed, landed to triage branch | `519519c` |
| 18 | Replay verification of the changeset | **discriminating pass** — arm A reproduces both burnt decisions, arm D flips both, 0/6 clamp language, no gold-plating regression (the one 36 h runaway was arm A *with* the clamp). Density burn is fable-modal / opus-invisible; the brief parenthetical, not recipe text, drove it | report `078c1cb` |
| 19 | sdh_onset acceptance evidence (2258bf0) | re-weighed per replay finding: device-card Luttinger-pin leak tainted side/design agreement; per-tone READ numbers + the 62-test suite stand | record-only |
| 20 | Replay methodology (production-model burn controls, brief-served frontiers, at-cut cards, regression ladder) | chiron memory + backlog seed | — |

Maintenance window (rig-side, before capstone-3): pull + `install.sh`;
regenerate the QC0426 kit (`hera-mkkit`) so the deployed brief drops the
overlay-validity parenthetical. Zack syncs by hand.
