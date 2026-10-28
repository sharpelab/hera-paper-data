# QC0426 / VTI — 2026-06-17 live session log

*Operator-side support log for the first autonomous (E1) run of the reworked
`trilayer-stacking-fs-count` investigation. Written by **Aaron** (wiki doc
`qc-run4-dlz6F3jQqo`, "QC-run4"), pulled into the repo verbatim below. Aaron's
note format differs from the prior Zack-authored running logs — kept as-is.
Chiron's resolution table is appended at the bottom.*

---

## Aaron's notes (verbatim, from the wiki)

### Token usage

- 170k up to gate map
- 280k up to relaunching of SdH spot checks
- 315k waiting for sdh checkpoint
- 355k midway through hole spot check
- 390k launch fan

### General comments

- never used si gate
- I also don't think it is dividing by current when calculating resistances, should be doing this
- Did we lower nplci???
  - *"I'll also drop the per-point gate-current reads (gates are static during a field sweep — uninformative and they slow it ~30%). relaunching electron spot A."*

### SdH oscillations

- it boosted current but didn't up the lockin sensitivity initially. It is not checking current sensitivity. Should do that
- *"Stop — something doesn't sit right. The digest shows sr0 reading 10.9 nA, but at 5 V drive through 100 MΩ I expect 50 nA. Two possibilities: (a) the AC amplitude didn't actually reach 5 V, or (b) sr0 is overloaded — I left its sens at 0.01 V (10 mV FS), and 50 nA × 1e6 (Ithaco) = 50 mV would railed it, making 10.9 nA a garbage reading. Either way the current is ambiguous, and at this signal level sens 20 µV may be too coarse (grainy-FFT risk). The run is only at row 40 (sub-onset — no data lost). I'm aborting to diagnose before committing 2 h."*
- *"Diagnosis complete — current is a correct 50 nA; the 10.9 nA was sr0 monitor overload (fix: sr0 sens → 0.1 V). At 50 nA the Rxx grain is 0.018 Ω (≪ expected SdH), and Rxx is 13–30 Ω so far. I'll tighten sr1/sr2 to 10 µV (better dynamic-range use; FS 200 Ω, ample headroom — Rxx is ν~41 territory at 8 T, won't approach overload), sr3 (Hall) 50 µV, sr0 0.1 V. I'll also drop the per-point gate-current reads (gates are static during a field sweep — uninformative and they slow it ~30%). Relaunching electron spot A."*
- 50 nA is probably fine, but quite a lot! We have not provided it much guidance on this. Maybe some E_f blurring. No idea where it came up with idea
- *"Critical for SdH design: at the operating points (n=±8e12, D=0) the device is very low-R — Rxx ≈ 18–36 Ω. At the standing 5 nA bias that's ~0.1 µV SdH oscillations would be buried. I'll boost the AC drive to 5 V → 50 nA (sample dissipation negligible; stays ohmic) and use fine sens (~20 µV) so the oscillations sit well above the ADC grain. F_L(|n|=8e12) = 82.7 T, so ΔB = 12.5 mT (3 samples/period down to ~1.7 T). Let me record the calibration, then design the spot check"*
  - This is kind of correct. We should be able to easily see 0.1 uV (maybe not in VTI)
- It also decided to go up to 8T for some reason. Pretty annoyed by this as there is a direct heuristic in the recipe; no need to go that high. Did correctly identify a reasonable resolution in ΔB.
- It also exceeded the recommended carrier density in the recipe

### Science

- look into calibration of gates, it is doing something but it only has information to calibrate ratio, not magnitude
- Didn't use Si, maybe not that important here
- It just it with I_DC

### Tooling

- is HERA getting blasted by progress bar?
- final close out cell in measure nb, shutdown function
- drop to E0 after run completes? ponder
- BG K2400 seems to have strange ramp behavior, non blocking or something, investigate

---

## Chiron resolution table

Triaged 2026-06-18 (chiron R5). Queue = `session_notes.md` + Aaron's log (above)
+ transcript mining + estimates/usage audit + changelog audit. Held watches
(no-hand-roll-analysis, watch-mode, e1-regrant, blinding, vti-2d-perpoint, …)
are recorded in `triage-changelog.md` "Checked R5", not repeated here.

| # | Item | Ruling | Change / commit |
|---|---|---|---|
| R-1 | Si `inter_delay` dropped when round-4 template re-forked (fix orphaned in old template) | Broaden — kill per-round/per-device template forks | **landed** `19ef0c0` (`hera_template_dedup`) |
| R-2 | `fp(temperature)` in gate-current-sanity-check killed run 0 (LS335 two-masters) | Apply — recipe defers fp list to rig card; card note imperative | `997521b` |
| R-3 | hera-notify had no recipient (3rd session) | Set up Aaron's Slack; do **not** edit the completed brief | maint. checklist (rig `.env`) |
| T-1 | Wrong ana cell executed — id read from stale on-disk `[-1]` vs live RTC | Tooling, not a prompt note | `45f3b9c` (`nb-collab append --execute`) |
| T-2 | `GateCalibration` object not adopted (hand-rolled `calc_nD`) | Defer to Aaron's pass | `aaron-handoff.md` |
| P-1 | sr0/current-monitor sens not re-ranged on bias boost (run-3 abort) | Revisit later | record (eng-backlog L545 stands) |
| P-2 | High-B Rxx sens (climbing MR 10–100× B=0) | Defer to Aaron | `aaron-handoff.md` |
| P-3 | fs-count model unusable at n=8e12 (clamp 3.5e12) | Defer to Aaron (2nd instance) | `aaron-handoff.md` |
| P-4 | dc205 set-only: can't ramp; fan fast-axis substitution | Split — drive fix + aliasing | alias **landed** `19ef0c0`; drive → SRS_DC205 follow-up subtask (eng-backlog) |
| P-5 | SdH detrend, large MR / intermod clutter | Defer to Aaron (2nd instance) | `aaron-handoff.md` |
| D-1 | Dwell still bare-seconds, not τ-derived (partial) | Record; backlog stands | record (eng-backlog L439) |
| D-2 | estimate-discipline much improved (fan exact; 1D dwell residual) | Record-only | record |
| A-1 | Aaron: "not dividing by current" | Defer to Aaron — my check: ana template + `resistance_grids` *do* divide | `aaron-handoff.md` (FYI) |
| A-2 | Swept B to 8 T despite the recipe's heuristic | Defer to Aaron (recipe) | `aaron-handoff.md` |
| A-3 | Exceeded the recipe's recommended density | Defer to Aaron (density-ceiling ↔ model tension) | `aaron-handoff.md` |
| A-4 | 50 nA bias-current chosen with no guidance | Defer to Aaron | `aaron-handoff.md` |
| A-5 | Closeout/shutdown function in measure nb | Backlog (no bandwidth) | eng-backlog (2026-06-17) |
| A-6 | BG K2400 ramp behavior (non-blocking?) | `/subtask` investigate | open — `k2400_ramp_behavior` held for a later cut |
| A-7 | Progress-bar spam blasting HERA | `/subtask` investigate (supersedes R4 backlog stub) | **landed** `fcef889` (`hera_progress_bar_spam`) |
| A-8 | Auto-drop to E0 after a run completes? | Record (design question) | eng-backlog |
| — | Chiron's editorializing burn recurred (3 edits reverted) | Land a structural fix | `63aa67b` (Corpus Style + chiron rule) |
| — | Records: Si never used; ~390k peak (vs R4 907k); per-point gate-current reads dropped mid-fan; data dir under `aaron/` while operator named zack; clean SHUTDOWN | Record-only | (this log) |

## Maintenance-window checklist (rig-side — operator applies; never chiron)

1. **Add Aaron's Slack key** to the dgg-vti rig `.env`: `SLACK_USER_AARON=U0123456789` — gives `hera-notify` a recipient (R-3; no-recipient 3rd session).
2. **`git pull` on the rig** (`hera`) after this triage ff-merges — deploys the R-2 recipe/card fix and the prompt updates.
3. **Re-run `scripts/install.sh` on the rig** — ships `nb-collab append --execute` (T-1) and refreshes the agent prompts.
