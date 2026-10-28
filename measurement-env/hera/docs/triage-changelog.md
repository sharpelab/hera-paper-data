# Triage changelog + evaluation log

Append-only record of corpus fixes the triage loop has landed (or punted),
and a separate log of whether they actually took. Companion to
`triage-scoreboard.md` (per-session metrics) and `triage-workflow.md` (the
process). Chiron maintains both sections:

- **Step 7 (land):** append a **Changelog** entry per landed change that
  carries a `watch` or trigger — L2/L3 fixes, L1 burn-log entries
  (`watch` = does the failure class recur?), and L1 backlog/punt items
  (`unpunt-if` = their re-eval trigger). Pure bookkeeping (scoreboard /
  resolution-table rows, record-only notes) is not logged.
- **Step 1 (build queue):** check the new session against every prior
  Changelog entry — append an **Evaluation log** entry recording whether a
  landed fix held (`watch`) or a punted fix's trigger fired (`unpunt-if`).
  A regression or a fired trigger becomes a high-priority queue item.

This broadens the recurrence check past the STYLE burn log — the gap that let
`hera-watch-digest`, `nbcw-block`, and `blinded-r2-set` regress unnoticed
between rounds 1 and 2.

L1 burns live inline in STYLE (rules 2 / 11 / 12); they're represented here by
their paired fix entry's `watch` (cited `burn #N` / the burned value), not
duplicated as separate rows.

**Both sections are append-only.** Nothing here is ever rewritten — a fix's
current status is its latest Evaluation-log entry. (Why append-only: the
corpus lands via parallel subtasks rebasing onto `hera`; mutating past rows
invites the merge conflicts append-only avoids, and keeps "what landed"
immutable.)

**Round 1 was triaged *manually*** (the `session-notes-resolution` subtask,
2026-06-11) — those entries are tagged `by: manual` and back-filled from the
real resolution table in `hera/docs/vti/2026-06-10-live-session-log.md`. The
chiron-v0 blind dry run (`$HERA_DATA/triage-dryruns/2026-06-10-QC0426/`) was a
*test of chiron against that manual work*, not the record of what landed;
its diff slugs are reused here as stable `fix-id`s. From round 2 on, chiron
appends its own entries (`by: chiron`).

**Changelog entry fields:** `fix-id` · round · by · commit/ref · *status*
(`landed` | `punted`) · Change · Intent · Surface · **Watch** (landed: the
behavior a later session should show) or **Unpunt-if** (punted: the evidence
that revives it).

**Evaluation-log entry fields:** `fix-id` · checked-in (session) · Verdict
(`held` | `partial` | `regressed`, or for punts `still punted` |
`unpunted`) · Evidence · Follow-up.

---

## Changelog — round 1 (manual, 2026-06-11)

### Tooling & shims

**`nb-utf8-stdout`** · R1 · manual · `ef26959` · *landed*
- **Change:** force UTF-8 stdout/stderr on win32 in `nb` + `nb-collab` `main()`.
- **Intent:** kill the per-command `PYTHONIOENCODING` tax (cp1252 console crashes; item 2a).
- **Surface:** `tools/nb`, `tools/nb-collab`.
- **Watch:** agent runs `nb`/`nb-collab` without prefixing an encoding export.

**`nb-summary-exec`** · R1 · manual · `ef26959` · *landed*
- **Change:** `exec`/`ec` column in `nb summary` (`[n]` / `-` / blank for md).
- **Intent:** Gate A/B execution-count text in the prompt is now true as written (item 2b); stop the raw-JSON dive.
- **Surface:** `tools/nb`, `hera_tactical.md`.
- **Watch:** agent reads exec counts via `nb summary`, not `json.load`.

**`shims-no-sync` / `menv`** · R1 · manual · `20dc8d9` · *landed*
- **Change:** `--no-sync` on `nb`/`nb-collab` shims; new `menv` shim; all three prompts say `menv python -c '...'`; memory note scoped DEV-MACHINES-ONLY.
- **Intent:** repo shims match the rig hot-patch; retire the `uv run --project` incantation footgun; stop the `--no-project` leak (item 3).
- **Surface:** `tools/`, prompts, `subtask_agent/MEMORY.md`.
- **Watch:** agent invokes `menv python`; no bare `uv run --project`; no `--no-project` on rig.

**`nb-collab-discovery`** · R1 · manual · `ced24e4` · *landed*
- **Change:** `_server_alive()` probe skips dead jpserver candidates; `--server-url` alone looks up token; explicit `--token ''` honored (item 4).
- **Intent:** stop silent resolution to a dead server.
- **Surface:** `tools/nb-collab`.
- **Watch:** no ConnectionRefused / silent wrong-server during discovery.

**`hera-archive-rig-flag`** · R1 · manual · `604d2ca` · *landed*
- **Change:** `--rig {toploader,vti}` presets, `--device` override, `--no-data` (item 10).
- **Intent:** archive VTI sessions (chiron.md already documented `--rig vti`).
- **Surface:** `tools/hera-archive`.
- **Watch:** VTI sessions archive cleanly via the preset. *(R2 support log already flags the whitelist footgun — sync whole dir — as a follow-on.)*

**`cell-index-extension`** · R1 · manual · `53dd526` · *landed*
- **Change:** `jupyterlab-cell-index` labextension — 0-based model-order cell indices in the JL UI (item 6a; the proposed prompt content-anchor was *rejected* in favour of building this).
- **Intent:** operators locate the cell HERA cites without an index↔content map.
- **Surface:** `jupyterlab-cell-index` (vendored wheel), JL UI.
- **Watch:** cells cited by bare index without a content anchor / hand-rolled map.

### Prompts & working-style

**`nbcw-block`** · R1 · manual · `hera_tactical.md` L250 · *landed*
- **Change:** mandate `nb-collab wait` to block on a cell when the next decision depends on its result.
- **Intent:** stop end-turn-and-poll on measurement cells.
- **Surface:** `hera_tactical.md`.
- **Watch:** blocks measurement cells unprompted.

**`checkpoint-long-sweeps`** · R1 · manual · `3c30416` · *landed*
- **Change:** "Checkpoint long sweeps" working-style bullet — sweeps > ~30 min state a checkpoint + priced continue/adjust/abandon fork (item 6b; the day's highest-value emergent behavior).
- **Intent:** make the emergent mid-run check-in a norm.
- **Surface:** `hera_tactical.md`.
- **Watch:** agent states a mid-run checkpoint in the proposal cell for long sweeps. *(Comes under test once a >30 min sweep lands.)*

**`wallclock-constants`** · R1 · manual · `0c5c05b` · *landed*
- **Change:** wall-clock section — traverse-dominated formula + measured constants (0.137/0.092 T/min, ~60 s/row fine) as recalibratable priors (item 16).
- **Intent:** price sweeps from measured overhead, not inherited guesses.
- **Surface:** `hera_tactical.md` (constants' home until rig cards exist).
- **Watch:** agent re-calibrates turnaround from its own first sweeps before pricing.

**`bypass-permissions`** · R1 · manual · `8521c65` · *landed*
- **Change:** `--dangerously-bypass-permissions` is the standing rig default; blast-radius bullet added (item 11). *(You overrode the dry-run/support lean for a mined allowlist.)*
- **Intent:** the prompt is the only gate; stop the per-command permission tax.
- **Surface:** prompts, runbook, `~/.claude/settings.json` rig default.
- **Watch:** sessions launch under bypass; no permission-prompt friction.

**`ana-policy-edit-exec`** · R1 · manual · `9257b07` · *landed*
- **Change:** flip ana-notebook policy `edit_no_exec` → `edit_exec` (item 7).
- **Intent:** drop pure-analysis-cell toil; measure-notebook contract untouched.
- **Surface:** prompts + ana templates.
- **Watch:** agent executes its own analysis cells; operator only runs measure cells.

### Recipes & STYLE (physics)

**`presence-vs-pattern`** · R1 · manual · `a8275ab` · *landed*
- **Change:** finite-D crossing *presence* vs *pattern*; series-path caveat (burn #1).
- **Intent:** stop discarding finite-D arcs as "not ABA evidence"; never call ABC from CNP-vs-D growth alone.
- **Surface:** `recipes/investigations/trilayer-stacking-id.md`, STYLE.
- **Watch:** finite-D arcs get model-overlaid; CNP-vs-D claimed "consistent-with", not "device is ABC". *(burn #1 — a presence rule worded as a blanket rule discarded pattern evidence; STYLE rule 2.)*

**`landau-fan-cost-nyquist`** · R1 · manual · `f14db9a` · *landed*
- **Change:** B-axis Nyquist guard + full fan cost model incl. traverse (burn #2); STYLE rules 11–12.
- **Intent:** fan grids checked on both axes at design time; pricing includes traverse.
- **Surface:** `recipes/measurements/landau-fan.md`, STYLE.
- **Watch:** grids Nyquist-checked both axes; row overhead calibrated from own sweeps. *(R2: re-check when n_max changes — a follow-on PROTOCOL note.)*

**`trilayer-hall-flatness`** · R1 · manual · `a8275ab`/`069a5e6` · *landed*
- **Change:** Verify demands plateau *flatness* (dRxy/dn≈0), never Rxy value-match (item 13a; run-3 near-miss).
- **Intent:** kill the classical-Hall confirmation trap.
- **Surface:** `trilayer-stacking-id.md` Verify.
- **Watch:** plateau claims cite flatness, never a value coincidence.

**`trilayer-densify-floor`** · R1 · manual · `069a5e6`/`d05de13` · *landed*
- **Change:** step-4 densify stopping rule — no-new-minima ⇒ stop; α-fork needs plateaus or a density anchor, not grid (item 13b).
- **Intent:** terminate the unbounded "ragged → densify" prescription.
- **Surface:** `trilayer-stacking-id.md` step 4.
- **Watch:** densification stops on no-new-minima rather than refining indefinitely.

**`trilayer-sdh-fft`** · R1 · manual · `d05de13` · *landed*
- **Change:** discriminator #5 — per-column FFT in 1/B, f₁+f₂=f_tot signature, window-sensitivity caveat (item 13c).
- **Intent:** surface two-pocket structure arc-hunting misses.
- **Surface:** `trilayer-stacking-id.md`; cites `hera.analysis.sdh_fft`.
- **Watch:** agent reaches for per-column FFT for two-frequency questions.

**`style-burn3-extraction-forks`** · R1 · manual · `069a5e6`/`d05de13` · *landed*
- **Change:** STYLE rule 14 (extraction-sensitive claims are forks) + burn-log entry 3 (item 13d).
- **Intent:** when a claim flips under extraction params, report the fork + deciding measurement; stop refining.
- **Surface:** `recipes/STYLE.md`.
- **Watch:** flip-under-params claims are reported as forks, not chased.

**`trilayer-E3-rejection`** · R1 · manual · `d05de13` · *landed*
- **Change:** worked *rejected* vertical-candidate Example (run-4 anomaly E3, four-count kill) (item 13e).
- **Intent:** a negative worked example in Examples.
- **Surface:** `trilayer-stacking-id.md` Examples.
- **Watch:** N_M=0 / vertical-series candidates pattern- + confound-checked.

**`blinded-r2-set`** · R1 · manual · `9304c3f`+`f14db9a` (STYLE 11) · *landed*
- **Change:** stripped round-2 device card + scrubbed notebooks; STYLE rule 11 + setpoints-are-calibration exception, Si=+50 as the burn (items 12a/13f).
- **Intent:** keep operating defaults + scoring framing out of agent-visible files.
- **Surface:** `templates/QC0426-round2/`, device card, STYLE.
- **Watch:** no setpoints / round-N / "replication" framing visible to the agent.

**`estimate-discipline`** · R1 · manual · `ebaf1e7` · *landed*
- **Change:** "price everything" from measured overhead, cite the calibrating run, realistic headline; state the coverage trade on the page (items 12b/12c).
- **Intent:** kill the ~+7% optimistic-floor anchoring; surface the excluded hole side.
- **Surface:** `hera_tactical.md`, nb-collab proposal-cell requirements.
- **Watch:** every proposed sweep carries a measured-overhead estimate + coverage trade.

### New recipes (qswitch-prefan subtask)

**`reentry-baseline`** · R1 · manual · `b33ce42` · *landed*
- **Change:** Gate-C re-entry baseline recipe gets its own slug + procedure (item 23).
- **Surface:** `recipes/device-init/reentry-baseline.md`.
- **Watch:** Gate C runs the slug, not improvised tags.

**`cnp-and-dline-calibration`** · R1 · manual · `c54f44e`+`d3656ee` · *landed*
- **Change:** CNP fit → capacitance ratio → D-line designer recipe, with axis-orientation clause.
- **Surface:** `recipes/device-init/cnp-and-dline-calibration.md`.
- **Watch:** ran as written in R2 (it did — produced c_bg/c_tg≈1.31; two-tier provenance written back).

**`contact-survey-2t`** · R1 · manual · `8a3c401`+`0a40c49` · *landed*
- **Change:** per-pair 2T characterization recipe (mux- or hand-switched), bring-up-record precondition, reference density, re-wire hygiene.
- **Surface:** `recipes/device-init/contact-survey-2t.md`.
- **Watch:** ran as written; RECIPE FIX deltas = its next iteration. *(R2 generated the current-bias/4T delta — a real evaluation.)*

**`gate-range-finding` (+VTI variant)** · R1 · manual · `7d13331`+`f8e5da5` · *landed*
- **Change:** gate range-finding base recipe + first STYLE-13 rig variant; watch-and-interrupt operator fast-path.
- **Surface:** `recipes/device-init/`.
- **Watch:** evidence-based narrowing inside the outer box. *(R2 punted range-finding to R3 — not yet exercised.)*

### Instrumentation & new tools

**`session-metrics-appended-at`** · R1 · manual · `8d0fc2a` · *landed*
- **Change:** stamp `metadata.hera.appended_at` on nb-collab-inserted cells + JL `recordTiming` (item 8b).
- **Intent:** capture land/run timing — unrecorded timing is lost forever; round 2 needs it.
- **Surface:** `tools/nb-collab`, deploy.
- **Watch:** R2 measure notebook carries `appended_at` stamps + `data/*` start/end times.

**`hera-watch-digest`** · R1 · manual · `b693e7c` · *landed*
- **Change:** `hera-watch` live run-dir digest — per-row gain-divided view + ETA (item 8c, explicit adoption-test framing).
- **Intent:** stop HERA hand-rolling watchers; incremental reads mid-sweep.
- **Surface:** tool + `hera_tactical.md`.
- **Watch:** agent reaches for `hera-watch` on data-writing cells.

**`hera-notify`** · R1 · manual · `ef07e5d` · *landed*
- **Change:** Slack pings via measurebot — fixed event list, operator key named in brief (item 9).
- **Intent:** notify on proposal-landed-while-idle + run-completion.
- **Surface:** `tools/hera-notify`, prompt Tools section.
- **Watch:** agent calls `hera-notify` on the specified events.

**`hera-analysis-helpers`** · R1 · manual · `1bfbdbf` · *landed*
- **Change:** `hera.analysis.{fan_grids,resistance_grids,sdh_fft}` (item 12d; bit-exact vs scratch; gain model unified).
- **Intent:** retire 6–8 hand-rolls each.
- **Surface:** `src/hera/analysis.py`.
- **Watch:** agent imports the helpers instead of re-deriving fan/resistance/FFT grids.

### Process

**`scratch-nb-retire`** · R1 · manual · `d4d78ab` · *landed*
- **Change:** retire the scratch notebook; scripts-based workflow; round-2 kit ships none (item 14).
- **Surface:** prompts, templates.
- **Watch:** no scratch-notebook references; scratch work in `hera_scratch/` scripts. *(R2 support log flags a leftover dated tombstone in the prompt — a follow-on scrub.)*

**`session-notes-proposed-diffs`** · R1 · manual · `hera_tactical.md` (item 22) · *landed*
- **Change:** session-notes protocol — RECIPE FIX entries may attach a proposed diff (triage applies/edits/rejects).
- **Surface:** `hera_tactical.md`.
- **Watch:** agent attaches diffs to RECIPE FIX notes where cheap.

**`resolution-triage-standing-step`** · R1 · manual · `a7d6c82` · *landed*
- **Change:** formalize resolution triage as the standing post-session step (item 16) — later superseded by the `chiron` agent (`013df99`).
- **Surface:** `docs/session-archiving.md`, `chiron.md`.
- **Watch:** every session gets a resolution table + scoreboard row.

### Punted / backlog (round 1)

**`idle-court-norm`** · R1 · manual · — · *punted*
- **Change (proposed):** prompt norm — queue-ahead, don't leave the fridge idle while thinking (items 6c/8a).
- **Intent:** raise fridge utilization without a per-rig framework.
- **Surface:** `hera_tactical.md` (if revived).
- **Unpunt-if:** `hera-utilization` shows HERA-court idle above threshold on a real session (behavioral norm needs measurement, not a lean).

**`hera-utilization`** · R1 · manual · `0ff62ce` (design only) · *punted*
- **Change (proposed):** raw + HIL-adjusted fridge-utilization scoring tool (item 8a; design doc, not built).
- **Intent:** measure the idle-norm's premise; score sessions.
- **Surface:** `src/tools/hera_utilization.py` (when built).
- **Unpunt-if:** a stamped session exists to validate HIL against — **now satisfied** (R2 is fully stamped; see eval log).

**`rig-cards`** · R1 · manual · — · *punted → since landed*
- **Change (proposed):** complete the layer model with rig/cryostat cards (T/B envelope safety home).
- **Intent:** give machine facts a home; rig prompt goes fridge-agnostic.
- **Surface:** `hera/rig-cards/`.
- **Unpunt-if:** round-2-blocking or bandwidth frees — **fired**: landed in round-2 prep (`25b5866`, VTI card + rig-agnostic `hera_tactical`).

**`lakeshore-single-poller`** · R1 · manual · eng-backlog · *backlog*
- **Change (proposed):** one poller process per shared instrument; kernel + Grafana both read from it.
- **Intent:** kill the two-masters VISA contention (the Grafana logger vs the measurement kernel killed a run; the workaround cost the lab telemetry).
- **Surface:** infra (Lakeshore first; magnet readback same audit).
- **Unpunt-if:** two-masters contention recurs / before the next temperature campaign.

**`queue-preflight-recipe`** · R1 · manual · eng-backlog · *backlog*
- **Change (proposed):** `device-init/queue-preflight.md` — per-cell precondition asserts, state chaining, halt-on-failure, park-cell exemption, estimate-vs-actual log line per link.
- **Intent:** standardize the assert-precondition pattern that converged live (cf. `silent-preconditions`).
- **Surface:** `recipes/device-init/`.
- **Unpunt-if:** unattended overnight chains need it (round-2+ overnight segments).

**`nbcollab-watch-mode`** · R1 · manual · eng-backlog · *backlog*
- **Change (proposed):** `nb-collab watch <notebook>` — event-stream new-cell/output/file events; make `wait`'s silent timeout loud.
- **Intent:** replace shell-sentinel monitoring duct tape (one false fire + one silent `nb-collab wait` timeout during the long fan).
- **Surface:** `tools/nb-collab`.
- **Unpunt-if:** monitoring-sentinel friction or a silent `wait` timeout recurs.

## Changelog — round 1.5 (round-2 prep, 2026-06-12 → 06-15)

*The corpus fixes that landed between round 1's triage and round 2, during
round-2 prep — human/subtask-driven (`by: manual`), not a chiron crank.
Round 2 (2026-06-14) tested the ones that landed before it; the 06-15 items
are first tested by round 3.*

### Drivers & safety

**`magnet-mag-param`** · R1.5 · manual · `9d50c3b` · *landed*
- **Change:** `FastBi1K5.mag` is a real qcodes Parameter — `mag()` reads the measured field (readback × `T_per_A`), `mag(target)` keeps blocking-ramp set.
- **Intent:** the live session asked for exactly this (`get_field()` correction).
- **Surface:** `src/.../drivers` (VTI).
- **Watch:** agent uses `magnet.mag()` for field readback. *(R2: used; landau-fan delta now prefers `mag` over `get_field`.)*

**`max-field-14T`** · R1.5 · manual · `5f4b4c7` · *landed*
- **Change:** driver `max_field_T` 13.5 → 14.0 per the magnet-limit ruling; limit + provenance in the VTI rig card.
- **Intent:** make the 14 T cap reachable through `mag()`; driver and card agree.
- **Surface:** driver + `rig-cards/VTI.md`.
- **Watch:** session caps set below 14 T; no ValueError below the stated cap.

**`gate-leakage-interrupter`** · R1.5 · manual · `5714993`+`5f01866` · *landed*
- **Change:** `LeakageDetector` + `k2400_leakage_guard`; gate-leakage-survey rewritten as a single dI/dV-interrupter recipe.
- **Intent:** trip at leakage onset, not against an operating limit.
- **Surface:** `sharpelab_nb`, `recipes/device-init/gate-leakage-survey.md`.
- **Watch:** gate sweeps run under the interrupter guard. *(Blocklisted in R2; first real test in R3 if gates are swept.)*

**`qdac-gate-support`** · R1.5 · manual · `a444757` · *landed*
- **Change:** `QDac2` driver + `bring_up_qdac_gate` + VTI template wiring.
- **Surface:** drivers, VTI template.
- **Watch:** QDAC gates bring up via the helper, not hand-rolled.

### Prompts & working-style

**`silent-preconditions`** · R1.5 · manual · `74128bb` · *landed*
- **Change:** working-style norm — cells whose first action is expensive/stateful (field move, heater write, long sweep) open with a cheap preflight block (read assumed state, print expected vs actual, stop on mismatch).
- **Intent:** operationalize the emergent precondition behavior; the persistent-switch incident is the burn a one-line check would have caught. Marked ablatable scaffold.
- **Surface:** `hera_tactical.md`; rig card names per-rig hazards + cheap reads.
- **Watch:** agent opens stateful cells with a preflight read. *(R2: agent ran precondition cells reading field — partial/held.)*

### Recipes & cards

**`rig-cards-vti`** · R1.5 · manual · `25b5866`(+`ef6cd6d` toploader) · *landed*
- **Change:** rig-card schema + VTI card; `hera_tactical` goes rig-agnostic (machine facts move to `rig_card.md`); absorbs persistent-switch hazard, 0.092 T/min datum, LS335 two-masters quirk, envelope cut, settle datum.
- **Intent:** complete the layer model — machine facts have one home (the `rig-cards` punt firing).
- **Surface:** `rig-cards/`, `hera_tactical.md`.
- **Watch:** agent reads machine facts from `rig_card.md`, not the prompt; no rig constants in the prompt.

**`recipe-tail-fixes`** · R1.5 · manual · `e3c337e` · *landed*
- **Change:** trilayer beat-exclusion Verify (intermod damps with m_A+m_B); landau-fan measured-vs-bare ramp pricing; temperature-dependence stability-criteria settles (not absolute targets).
- **Intent:** fold the round-1 session-tail RECIPE FIX notes into the corpus.
- **Surface:** `recipes/investigations/trilayer-stacking-id.md`, `recipes/measurements/{landau-fan,temperature-dependence}.md`.
- **Watch:** beat-damping exclusion used; ramps priced from measured rate; settles framed as stability criteria.

### Tooling, runbook, process

**`install-retire-stale-copies`** · R1.5 · manual · `183be43` · *landed*
- **Change:** `install.sh` retires stale agent *copies* (not just symlinks) by frontmatter name — Git Bash installs are copies.
- **Intent:** stop superseded prompts (`hera.md`/`hera-vti.md`) surviving on rig PCs.
- **Surface:** `scripts/install.sh`.
- **Watch:** re-run after a rename leaves no stale agent prompt on the rig.

**`rtc-tab-runbook`** · R1.5 · manual · `ee5f01b` · *landed*
- **Change:** recovery procedure gains step 0 — close all RTC tabs before relaunch; prefer hard kill (stale-tab ydoc merge duplicated cells).
- **Surface:** `docs/.../preflight-runbook.md`.
- **Watch:** relaunch closes tabs first; no cell-duplication on restart.

**`chiron-agent`** · R1.5 · manual · `013df99`(+`c074d43`,`f003d47`,`d266775`) · *landed*
- **Change:** Chiron (`hera-triage`) — the standing post-session self-improvement agent; supersedes the manual `session-notes-resolution` step.
- **Intent:** close the feedback loop automatically with the human gate at step 4.
- **Surface:** `hera/chiron.md`, `docs/triage-workflow.md`.
- **Watch:** post-session triage runs as chiron; this changelog + the scoreboard get appended. *(R3 is its first real crank.)*

### Backlog (round 1.5)

**`worked-example-ab`** · R1.5 · manual · eng-backlog · *backlog*
- **Change (proposed):** A/B whether close-to-home worked examples calibrate or anchor — queue the three held-out QC0426-specific examples (LK mass split + beat exclusion; VTI measured-vs-bare traverse; post-heating base-shift burn) and/or ablate existing ones across fixtures.
- **Intent:** decide the run-proximity rule (generic rules landed; device/rig-specific anchors held out as too close to home).
- **Surface:** recipe Examples (`trilayer-stacking-id`, `landau-fan`, `temperature-dependence`).
- **Unpunt-if:** post-round-2 — batch several for statistical power.

---

## Changelog — round 3 (chiron, 2026-06-16)

*First real chiron crank. Triaged the 2026-06-14 QC0426/VTI session; landed on
`hera` via `subtask/triage-r3-integration`. Tooling fixes came from chunked
subtasks; the hera-watch long-run work came from a `/subtask` (Zack in the
proposal loop).*

### Recipes, STYLE & cards

**`blinding-conventions`** · R3 · chiron · `aaa8184` · *landed*
- **Change:** new `hera/blinding.md` — agent-visible artifacts carry the
  science, never the campaign frame (round/session identity, replication/
  benchmark language, operating setpoints); round identity stays scorer-side.
- **Surface:** `hera/blinding.md`, `session_template.md`.
- **Watch:** no "round N"/"replication"/prior-cooldown framing in agent-visible
  files; chiron's scope-hygiene grep clean. *(Fixes the `blinded-r2-set`
  regression — STYLE rule 11 class; same as Si=+50.)*

**`landau-fan-vti`** · R3 · chiron · `6c9ee7b` · *landed*
- **Change:** VTI variant — `magnet.mag` (blocking ramp, no pre-settle),
  `calc_gate_voltages` sig, `async_station`, `hera-notify`, measurement-
  dominated cost. fp-LS335 hazard left to the rig card (rule 13).
- **Surface:** `recipes/measurements/landau-fan-vti.md`.
- **Watch:** VTI fans run under the variant; no `time.sleep(600)` pre-settle;
  n-points trimmed (not B coarsened) for the high-n Nyquist floor.

**`contact-survey-bias-mode`** · R3 · chiron · `9f4e905` · *landed*
- **Change:** step-3 conditional — current-bias rigs pin I at `I_bias`, so 2T
  current ranks aliveness/localization only; resistance + CNP need 4T.
- **Surface:** `recipes/measurements/contact-survey-2t.md`.
- **Watch:** current-bias survey claims aliveness only, defers ranking to 4T.

**`dwell-from-tau`** · R3 · chiron · `fc46836` + `2c1c849` + `5e98061` · *landed*
- **Change:** STYLE rule 12 settling floor (`dwell ≳ k·τ`, derive-by-default,
  bend knowingly per Aaron) + VTI card lock-in note + preflight τ-record step +
  contact-survey dwell clause; burns moved to the bottom (#5 Si=+50, #6 dwell).
- **Surface:** `STYLE.md`, `rig-cards/VTI.md`, `preflight-runbook.md`, `contact-survey-2t.md`.
- **Watch:** dwells derived from measured τ, not bare seconds; τ recorded at
  bring-up. *(Aaron to workshop the exact wording.)*

**`fan-nyquist-nmax`** · R3 · chiron · `b9a58f9` · *landed*
- **Change:** landau-fan step 1 — re-run the Nyquist check on `n_max` change;
  never inherit a ΔB across fans.
- **Surface:** `recipes/measurements/landau-fan.md`.
- **Watch:** Nyquist re-checked when n_max grows; high-n floor bought by
  trimming n, not coarsening B. *(burn #2 follow-on; partial recurrence this session.)*

### Prompts

**`prompt-watch-ranking`** · R3 · chiron+/subtask · `a1c51a1` + `12dff88` · *landed*
- **Change:** hera-watch is the default monitor for data-writing cells;
  `nb-collab wait` reserved for the start-gate + non-data; `--source-file` for
  shell-hostile cell source.
- **Surface:** `hera_tactical.md`.
- **Watch:** agent backgrounds `hera-watch --next --follow` on sweeps; uses
  `nb-collab wait` only at the start-gate; file-based source for backtick/`$()` cells.

**`prompt-scrub`** · R3 · chiron · `2d0ff33` + `d007c6b` · *landed*
- **Change:** remove dated changelog asides + the scratch-notebook reference
  entirely (talk only about `hera_scratch/`).
- **Surface:** `hera_tactical.md`.
- **Watch:** no date-stamped asides / "scratch notebook" phrasing in the prompt.

### Tooling

**`hera-watch-longrun`** · R3 · /subtask · `a1c51a1`(+feat) · *landed*
- **Change:** `--follow` (no deadline, for backgrounding) + `--next`/`--wait-start`
  (arm before the run dir exists); 570s default kept for foreground safety.
- **Surface:** `src/hera/watch.py`, `src/tools/hera_watch.py`.
- **Watch:** a backgrounded watch runs a multi-hour sweep to completion without
  re-arming; `--next` blocks from cell-proposed through completion. *(unpunts `nbcollab-watch-mode`.)*

**`nb-collab-wait-loud`** · R3 · chiron · `efc827d` · *landed*
- **Change:** `wait` timeout prints a loud stderr line + distinct exit.
- **Surface:** `src/tools/nb_collab.py`.
- **Watch:** a `wait` timeout is never mistaken for completion.

**`nb-error-render`** · R3 · chiron · `a26738e` · *landed*
- **Change:** `nb cells --outputs` renders error `ename`/`evalue`/`traceback` (ANSI-stripped).
- **Surface:** `src/tools/nb.py`.
- **Watch:** agent reads tracebacks via `nb`, not hand-rolled raw-JSON `.ipynb` parsing.

**`nb-collab-source-file`** · R3 · chiron · `991f2e7` + `12dff88` · *landed*
- **Change:** documented `--*-file`/stdin (verbatim, no shell substitution); root
  cause was bash command-substituting inline backtick/`$()` args.
- **Surface:** `.claude/commands/nb-collab.md`, `hera/nb-collab/README.md`, `hera_tactical.md`.
- **Watch:** no dropped backtick paths; agent uses file-based source for special chars.

**`hera-archive-whole-dir`** · R3 · chiron · `d5422b1` · *landed*
- **Change:** whole-session-dir mirror (rsync, tar fallback) replacing the
  enumerated whitelist; `rig_card.md` + arbitrary new files now archive.
- **Surface:** `tools/hera-archive`, `docs/session-archiving.md`.
- **Watch:** `rig_card.md` archives; nothing silently dropped. *(rsync transport
  untested on a real rig → maint. checklist.)*

**`ana-data-path`** · R3 · chiron · `229f739` · *landed*
- **Change:** ana templates resolve `./data` from the notebook's `_dh`, not kernel cwd.
- **Surface:** `templates/*_ana.ipynb` (5 notebooks).
- **Watch:** ana loaders work without hardcoded absolute paths.

**`tau-snapshot-warm`** · R3 · chiron · `d4b87aa` · *landed*
- **Change:** VTI measure template reads `time_constant()`/`filter_slope()` in
  lock-in setup → warms the qcodes cache so τ lands in the run snapshot.
- **Surface:** `templates/vti_measure.ipynb`.
- **Watch:** VTI run metadata `instruments` snapshot has non-null τ/slope.

**`brief-slack-slot`** · R3 · chiron · `35ae44d` · *landed*
- **Change:** session-brief template gains an Operator Slack key slot.
- **Surface:** `session_template.md`.
- **Watch:** deployed briefs name the operator key; `hera-notify` has a recipient.

### Backlog (round 3)

**`recipe-dwell-sweep`** · R3 · chiron · `d4381df` · *backlog* — align bare step
dwells (gatemap, silicon-backgate-survey, …) to the settling floor.
**Unpunt-if:** cleanup-mode pass.

**`mcp-trim`** · R3 · chiron · `317bdb3` · *backlog* — disable unused default
MCPs in the rig launch config (~233k context, mostly fixed overhead).
**Unpunt-if:** focused-environment review / next session.

**`tau-snapshot-update`** · R3 · chiron · `592f5d9` · *backlog* — Option A
(`inst.snapshot(update=True)` in measureme) behind Option B.
**Unpunt-if:** snapshot fidelity needed on instruments where reads are cheap.

**`style-burn-split`** · R3 · chiron · `7c61063` · *backlog* — split the burn
log out of STYLE (now 251 lines, 1 over budget).
**Unpunt-if:** STYLE crosses ~250 / burn log > 10 entries — **now satisfied; deferred to cleanup mode.**

**`nb-collab-guard`** · R3 · chiron · `3e2042d` · *backlog* — ablate the
shell-hostile prompt note via a better `--help` / inline-source guard.
**Unpunt-if:** guard built → delete the prompt note.

---

## Evaluation log

**`idle-court-norm`** · checked R2 (2026-06-14) · *still punted*
- **Evidence:** `hera-utilization` unbuilt; raw fridge utilization computed (43%) but no HIL / court split yet, so the threshold isn't evaluable.
- **Follow-up:** none — remains punted; re-check once `hera-utilization` lands.

---

### Checked R3 (2026-06-14 QC0426 / VTI — chiron's first real crank, 2026-06-16)

*Step-1 changelog audit of the 2026-06-14 session against every prior entry
whose `watch`/`unpunt-if` touches it. Two snapshot corrections up front: the
support log's "hera-watch 0 adoption" and "no hera_scratch" findings are both
**file_id-17 snapshots** — the full transcript shows 31 `hera-watch` calls and
17 scratch scripts (first at ~25% through). Those fixes **held**; the support
log captured the session before the agent switched media.*

**`blinded-r2-set`** · checked R3 · *regressed*
- **Verdict:** regressed — same-class leak as the Si=+50 burn it was built to fix.
- **Evidence:** "round 2" / "replication from a cooled start" / "2026-06-01
  cooldown" framing ships in the agent-visible deployed templates
  (`device_card.md:1,3`; measure/ana nb headers) and the agent propagated it
  (device-card write-back "Session findings — round 2"). STYLE rule 11 class.
- **Follow-up:** **high-priority R3 queue item (L3)** — neutralize round-N
  template framing; round identity lives scorer-side only. NB: agent *reasoning*
  stayed blind (explicitly refused `compare_qc0426.py` on isolation grounds,
  transcript L899) — the leak is in the kit, not agent-introduced.

**`landau-fan-cost-nyquist`** (burn #2) · checked R3 · *partial / regressed*
- **Verdict:** partial — design-time Nyquist guard skipped on the second fan.
- **Evidence:** ΔB=0.1 T reused for the high-n firming fan (file_id 21) without
  re-running the check at n_max=10 → 1.5 rows/period (under the ≥2 floor); the
  undersampled corner is exactly where a spurious high-n second pocket appeared
  (killed post-hoc for B≥4 T). Conclusion not compromised; the guard didn't fire
  at design time. Agent self-logged it (PROTOCOL note).
- **Follow-up:** R3 queue item — "re-run Nyquist on n_max change" in landau-fan
  (the follow-on this entry already flagged). **Recurrence count +1.**

**`nbcw-block`** · checked R3 · *partial*
- **Verdict:** partial — adopted, but not unprompted on the first cell.
- **Evidence:** agent ran run-0 (measurement cell) by ending its turn and
  polling; operator asked for `nb-collab wait`; adopted runs 1+ (5 calls,
  transcript L140/156/171/220/263). Prompt reads "use it when…", not imperative.
- **Follow-up:** R3 queue item — make measurement-cell blocking the default and
  rank `hera-watch` vs `nb-collab wait`.

**`hera-watch-digest`** (item 8c adoption test) · checked R3 · *held*
- **Verdict:** held — the adoption test passed.
- **Evidence:** 31 `hera-watch` invocations (first L292), reached for after the
  `nb-collab wait` 10-min timeout on the 19-min gate map. (Support-log "0
  adoption" was a file_id-17 snapshot.)
- **Follow-up:** R3 tooling item — 570 s default `--timeout` forces a dozen+
  re-arms on the 3.5 h fan (the real friction, not non-adoption).

**`checkpoint-long-sweeps`** · checked R3 · *held*
- **Verdict:** held — first real >30-min-sweep test.
- **Evidence:** agent stated + read a mid-run checkpoint on the 3.5 h D=0 fan
  (`fan_checkpoint.py`, ~45 min in, transcript L646).

**`wallclock-constants` / `estimate-discipline`** · checked R3 · *held*
- **Verdict:** held — round-1's ~+7% optimism pattern did not recur.
- **Evidence:** recalibrated ~0.74 s/pt from run 0 (rig-card default 1.2);
  estimates accurate-to-slightly-conservative (35-min survey + 3.5 h fan both
  within budget); no systematic optimism in the estimates-vs-actuals roll-up.

**`presence-vs-pattern`** (burn #1) · checked R3 · *held*
- **Evidence:** fan arcs model-overlaid (ABA chain region measured, not
  discarded); CNP-vs-D claimed "consistent-with mixed," ABC withheld until fans.

**`style-burn3-extraction-forks`** (rule 14) · checked R3 · *held*
- **Evidence:** spurious high-n second pocket reported + killed as a rule-14
  fork (vanished for B≥4 T → sub-onset artifact, "tested+killed").

**`trilayer-hall-flatness`** · checked R3 · *held* — Hall classical, no plateau
value-match claimed.

**`trilayer-sdh-fft`** · checked R3 · *held* — per-column SdH-FFT used (0/69
two-pocket across the clean window).

**`scratch-nb-retire`** · checked R3 · *held (behavior) / partial (prompt)*
- **Evidence:** scratch-first adopted (17 `hera_scratch/` scripts; support-log
  "no scratch" was a file_id-17 snapshot). BUT the prompt still carries the dated
  retired-scratch-notebook tombstone (`hera_tactical.md:114-115`) + a dated
  ana-policy note (L133-134).
- **Follow-up:** R3 queue item — scrub the changelog asides from the live prompt.

**`silent-preconditions`** · checked R3 · *held* — stateful cells opened with
preflight reads (magnet field read before the fan).

**`magnet-mag-param`** · checked R3 · *held* — `magnet.mag()` used for readback;
the landau-fan VTI delta prefers it over a `get_field`/`mag.field` form.

**`rig-cards-vti`** · checked R3 · *held* — agent read machine facts from
`rig_card.md`; the data-isolation audit confirms no prompt-embedded rig constants
were needed. (Side finding: `rig_card.md` is **not archived** — `hera-archive`
whitelist miss; queued tooling item.)

**`hera-notify`** · checked R3 · *held (not a regression)*
- **Evidence:** 0 calls, but the deployed brief omitted the operator's Slack key
  (`SLACK_USER_QCAO` was in dgg-vti's `.env`, unreferenced) — the tool had no
  recipient. Prompt adherence was correct (agent grepped, found none, did not
  ping — transcript L1316/1323).
- **Follow-up:** R3 queue item against the **brief/kit**, not the prompt: the
  session-brief template needs a Slack-key slot. Do **not** score as adoption.

**`lakeshore-single-poller`** (backlog) · checked R3 · *unpunted*
- **Verdict:** trigger fired — two-masters contention recurred.
- **Evidence:** data/19 fan killed at row 2 (~7 min) by `VI_ERROR_TMO` on
  `KRDG? A` — agent put `s.fp(heater.sample_temperature)` in the per-point loop
  despite the rig card's two-masters warning; landau-fan step 6 says "fp
  temperature(s)" with no VTI delta. Re-ran clean (file_id 20) with T removed.
- **Follow-up:** immediate mitigation = landau-fan VTI "don't fp the LS335"
  delta (R3 recipe item); the infra single-poller fix stays backlog but is now
  **before-next-temperature-campaign** live.

**`nbcollab-watch-mode`** (backlog) · checked R3 · *unpunted*
- **Verdict:** trigger fired — silent `wait` timeout + monitor friction recurred.
- **Evidence:** `nb-collab wait` hit its silent ~10-min internal timeout on the
  19-min gate map (returned `status: timeout`); `hera-watch`'s 570 s default
  `--timeout` then forced a dozen+ re-arms across the 3.5 h fan.
- **Follow-up:** R3 tooling items — long/background `hera-watch` timeout; loud
  `wait` timeout; `hera-watch` against not-yet-started cells.

**`hera-utilization` / `idle-court-norm`** · checked R3 · *still punted*
- **Evidence:** R2 is a fully-stamped session (the `hera-utilization` unpunt-if,
  now satisfied), but the tool is still unbuilt, so HIL court-utilization isn't
  computed and the idle-norm premise stays unevaluated.
- **Follow-up:** unchanged — build `hera-utilization`; re-check the idle-norm
  against its output.

---

## Changelog — round 4 (chiron, 2026-06-16 QC0426 / VTI, first autonomous E1)

### Prompts
**`e1-regrant`** · R4 · chiron · `2336d9b` · *landed* — re-entry to E1 needs a
fresh explicit grant after any E0 drop. **Watch:** HERA does not resume
autonomous execution post-drop without a grant.
**`consent-ramp-step`** · R4 · chiron · `2336d9b` · *landed* — a gate driver's
ramp `step`/`inter_delay` is consent-gated. **Watch:** HERA does not change
ramp granularity without operator consent.
**`no-hand-roll-analysis`** · R4 · chiron · `2336d9b` · *landed* — reach for
`hera.analysis` helpers + `open_run` before hand-rolling load/reshape/FFT.
**Watch:** HERA uses the helpers and `open_run`, not inline re-derivation or
substring run-lookup. *(Top token lever this session — 50× json.load, 40×
detrend, 17× rfft hand-rolled.)*
**`ana-raw-first`** · R4 · chiron · `2336d9b` · *landed* — ana plots raw before
interpretation. **Watch:** each run's ana shows raw then analysis.

### Cards
**`vti-2d-perpoint`** · R4 · chiron · `5fecd01` · *landed* — VTI card: 2D D=0
multimegasweeps ~2.0–2.5 s/pt (vs ~1.2 1D). **Watch:** long-sweep estimates
priced from the right per-point; no recurring optimism.
**`qc0426-card-r3-base`** · R4 · chiron · `6203240` · *landed* — device card
rebased on the blinding-scrubbed R3 card + graphite back gate + contact map
(drain T7→B7). **Watch:** no round-N framing in the card; CNP kept out for
blinded runs.

### Templates
**`si-gate-inter-delay`** · R4 · chiron · *landed* — QC0426 measure template sets `k_2410.volt.inter_delay = 0.01` (Si gate dV/dt pacing, dielectric safety; Zack owns the value). **Watch:** Si ramps are paced; no bus jam / dielectric-stress recurrence.

### Tooling (landed via subtasks)
**`watch-mode-hardening`** · R4 · subtask · `56464bd` · *landed* — hera-watch `wait_for_next_run` latch (fixes `--next` on 2nd+ runs) + line-flushing emit (the block-buffer was the real `--next` "stall"); nb-collab `wait --follow` + default 570→1800 s + loud timeout. Resolves the `nbcollab-watch-mode` / `hera-watch-longrun` regressions. **Watch:** a backgrounded `--next --follow` runs a multi-hour 2nd+ sweep to completion with live per-row digests. **Rig deploy:** re-run `install.sh` (loud `wait` timeout bit silently only because the deployed copy was stale).
**`gate-calibration-helper`** · R4 · subtask · `a69be95` · *landed* — `GateCalibration` + `luttinger_frequency` in `hera.analysis` (A-2). **Watch:** sessions construct one calibration object instead of re-typing n(Vtg,Vbg) / `n·h/4e` per cell.

### Deferred to Aaron (recipes — drafted, held for the science pass)
**`fs-count-validity-ceiling`** / **`sdh-detrend-highmr`** /
**`contact-survey-span-anchor`** / **`reentry-linecut`** · R4 · chiron ·
`9239f4b` (record in `aaron-handoff.md`) · *deferred* — chiron-drafted, held for
Aaron's recipe science pass. **Unpunt-if:** Aaron's recipe review lands.

### Backlog (round 4)
All in `hera/docs/eng-backlog.md` §2026-06-16. **Unpunt-if:** cleanup-mode pass
or the named trigger. Items: `k_bg.volt()` GET halving; nb-collab ana insert;
hera-notify multi-recipient; agent-cell operator visibility; sweep progress-bar
spam; out-of-band E1 safety monitor; people roster; E-1 discussion mode;
cost/token breakdown; large-GPIB-ramp software guard; bring-up lock-in-sens
check (strengthens `bias-precheck`).

---

### Checked R4 (2026-06-16 QC0426 / VTI — first autonomous E1 session, 2026-06-17)

*Step-1 changelog audit of the 2026-06-16 session against every prior
`watch`/`unpunt-if`. Round label R4 = chiron's 2nd real crank (R3 = the
2026-06-14 crank); the live campaign calls this session "round-3" — date is
authoritative. Two snapshot scares refuted up front: the support log's
"B7-death repeats the T7 kill" and any "high-|n|+Si deterministically kills
contacts" reading — the full transcript shows B7 surviving the identical
condition end-to-end (T7 was a one-off marginal contact).*

**Regressions / fired triggers (high-priority queue items):**
- **`brief-slack-slot`/`hera-notify`** (K-1) · *fix held / adherence miss* — the
  wiring fix held (other notifies delivered); HERA did **not fire** the grant-ack
  / re-grant notify the prompt already lists, so the operator got no ping on E1
  entry. Not-sent, not a delivery/wiring regression. → record-only + watch HERA
  fires grant-ack/re-grant notifies next E1.
- **`nbcollab-watch-mode`** · *unpunted (re-fired)* — silent `nb-collab wait`
  570 s timeout (snake + F(n) fan, ≥2×); `hera-watch --next --follow` stalls on
  2nd+ runs; `--follow` block-buffers stdout (forced a redundant ScheduleWakeup
  heartbeat scaffold). → watch-mode /subtask.
- **`hera-watch-longrun`** · *regressed* — backgrounded-to-completion-without-
  re-arm failed (the `--next` stall). → same /subtask.
- **`nb-collab-wait-loud`** · *regressed* — timeout silent again; possible stale
  rig install of the loud-exit fix. → verify shipped (maint re-install).
- **`estimate-discipline`/`wallclock-constants`** · *partial* — per-sweep recal
  good, but headline estimates ~40–60% optimistic; root cause is the per-point
  default, not the magnet ramp (card has settle+speed). → `vti-2d-perpoint`.

**Held:** `blinding-conventions` (exemplary — deferred card write-back mid-
session); `fan-nyquist-nmax`/burn #2 (**recurrence streak broken** — finer-B,
not coarsen); `landau-fan-vti`; `lakeshore-single-poller` (BL-1, temp ban
honored, `fp` only on k_bg.curr/sr.X); `contact-survey-bias-mode`;
`checkpoint-long-sweeps`; `presence-vs-pattern` (burn #1); `trilayer-hall-
flatness`; `trilayer-sdh-fft`; `style-burn3-extraction-forks` (rule 14);
`silent-preconditions`; `magnet-mag-param`; `rig-cards-vti`;
`reentry-baseline`; `cnp-and-dline-calibration`; `max-field-14T`;
`recipe-tail-fixes`; `nbcw-block` (reframed under E1); `ana-data-path`.

**Partial:** `dwell-from-tau` (τ recorded + reasoning τ-aware, dwells still
stated as bare seconds); `prompt-watch-ranking` (hera-watch default held, the
`--next` form failed → direct-dir fallback); `tau-snapshot-warm` (verifiable
only at archive).

**Still punted:** `idle-court-norm` / `hera-utilization` (unbuilt; token
numbers captured — ~907k peak); `worked-example-ab`; R3 backlog
(`recipe-dwell-sweep`, `mcp-trim`, `tau-snapshot-update`, `style-burn-split`,
`nb-collab-guard`). `mcp-trim` leaning toward firing (~907k context) but the
cause is single-context-no-compaction + inline-analysis, not MCP overhead.

---

## Changelog — round 5 (chiron, 2026-06-17 QC0426 / VTI)

*Second autonomous (E1) session; first run of the reworked
`trilayer-stacking-fs-count` investigation → strong ABA call. Aaron kept the
operator-side log (`vti/2026-06-17-live-session-log.md`); science items routed
to his pass, protocol/tooling to the crank.*

### Process

**`corpus-style`** · R5 · chiron · `63aa67b` · *landed*
- **Change:** `hera/CLAUDE.md` gains "Corpus Style" + "Editing the corpus"
  (terse, point-don't-restate, prefer-deleting, don't-edit-completed-records);
  `chiron.md` gains a "No editorializing" rule pointing at it + mandating it be
  carried into every subtask/agent brief.
- **Intent:** make minimal-diff the default for *all* corpus editors, not just
  chiron — over-editorializing is chiron's own recurring burn (R4 acc ~20%).
- **Watch:** corpus diffs (chiron, subtasks, delegated agents) land minimal; no
  restated hazards, no edits to completed records.

### Recipes & cards

**`fp-temperature-rigcard`** (R-2) · R5 · chiron · `997521b` · *landed*
- **Change:** `gate-current-sanity-check` drops hardcoded `s.fp(temperature)`,
  defers the fp list to the rig card (landau-fan-vti pattern); VTI card note
  made imperative ("do not poll the LS335 per-point").
- **Surface:** `recipes/device-init/gate-current-sanity-check.md`, `rig-cards/VTI.md`.
- **Watch:** no per-point LS335 poll in VTI sweeps; recipes don't hardcode a
  temperature fp. *(Fixes the run-0 kill; `lakeshore-single-poller` infra fix
  still backlog.)*

### Tooling

**`nbcollab-append-execute`** (T-1) · R5 · chiron · `45f3b9c` · *landed*
- **Change:** `nb-collab append --execute` runs the last appended code cell by
  the id the append just created (shared live-kernel path with `execute-cell`;
  policy-gated before any cell lands). Prompt + docs point HERA at it.
- **Surface:** `src/tools/nb_collab.py`, `hera_tactical.md`, nb-collab docs.
- **Watch:** agent uses `append --execute`; no wrong-cell from a stale on-disk
  `[-1]`.

### Spawned as /subtask (propose-first)

- **`hera_template_dedup`** (R-1 + dc205 aliasing) — kill per-round/per-device
  template forks; generate the deployed nb + gate aliases from the device card.
  Motivated by the dropped Si `inter_delay` fix and the rediscovered dc205
  fast-axis. **Lands-if:** subtask proposal approved + implemented.
- **`hera_measure_closeout`** (A-5) — reusable close-out/shutdown function in the
  measure nb.
- **`k2400_ramp_behavior`** (A-6) — investigate the BG K2400 non-blocking-ramp report.
- **`hera_progress_bar_spam`** (A-7) — investigate progress-bar output bloating
  HERA's context (supersedes the R4 backlog stub).

### Backlog / deferred

- **`dc205-no-get-drive`** (P-4.1) · backlog — DC205 set-only drive can't ramp;
  fix the drive. **Unpunt-if:** template-redesign subtask or cleanup.
- **`e0-after-run`** (A-8) · backlog (design) — auto-drop to E0 on run completion?
- **aaron-handoff (2026-06-17)** · deferred — fs-count ceiling (2nd), density/field
  over-range vs recipe, bias-current guidance, high-B sens, GateCalibration
  adoption, SdH detrend (2nd), resistance÷current FYI. **Unpunt-if:** Aaron's pass.

### Subtask landings (folded in as they complete)

**`progress-bar-collapse`** (A-7) · R5 · subtask · `fcef889` · *landed*
- **Change:** `nb`/`nb-collab` read tools run-length-collapse consecutive
  identical rendered outputs (threshold 3). RTC persists one `display_data`
  per `sweep.progress` update (one measure cell held 3302), bloating HERA's
  `nb cells --outputs` read (166.8 KB → 2.5 KB on the worst cell). Live bar and
  the sweep package are untouched; source-side cadence fix backlogged.
- **Surface:** `src/tools/nb.py`, `src/tools/nb_collab.py`.
- **Watch:** `nb cells --outputs` on a measure cell stays compact; no
  per-sweep-point output spam in HERA's reads.

**`measure-closeout`** (A-5) · R5 · *deferred to backlog* — no bandwidth this
round; requirement captured in eng-backlog (2026-06-17). **Unpunt-if:**
bandwidth / cleanup.

**`template-dedup`** (R-1 + P-4.2 aliasing) · R5 · subtask · `19ef0c0` · *landed*
- **Change:** retired the per-round/per-device notebook forks for a single
  carry-forward source — `templates/base/VTI_measure.ipynb` + `base/ana.ipynb`,
  device facts in `metadata.hera.slot` cells filled from the device card. The Si
  `inter_delay` fix re-lands on the raw `k_2410` cell (carries forward); gate
  aliases (`k_tg = dc205_volt`, …) built from the card wiring. `hera-mksession`
  args `<template> <rig>` → `<rig> <device>`.
- **Surface:** `hera/templates/base/`, `tools/hera-mksession`, `tools/hera-session.md`.
- **Watch:** new sessions deploy from the base + device card; Si `inter_delay`
  pacing present without a manual re-add; the DC205 top-gate alias is set up at
  session start, not rediscovered live. Slot auto-fill is a queued hera-session
  TODO (operator hand-validates until then).
- **Follow-on:** SRS_DC205 driver subtask kicked off to close the `k_tg.volt` vs
  `dc205_volt` asymmetry (the P-4.1 `dc205-no-get-drive` backlog item).

**`k2400_ramp_behavior`** (A-6) · R5 · *held open, not this cut* — Zack keeps the
investigation running; lands a later cut. **Unpunt-if:** subtask completes.

### Checked R5 (2026-06-17 QC0426 / VTI, 2026-06-18)

*Step-1 audit of the session against every prior `watch`/`unpunt-if`. Aaron's
support log reconciled against the transcript: his mid-session "not dividing by
current" and "didn't up sensitivity" reads were both either refuted (the ana
template + `resistance_grids` divide by measured current) or self-corrected live
(sr0 re-ranged after the run-3 abort).*

**Regressions / fired triggers (high-priority):**
- **`si-gate-inter-delay`** · *regressed* — the round-4 template (`6a3fa74`) was
  re-forked fresh after the fix (`df14eec`) and dropped `k_2410.volt.inter_delay`;
  the deployed kit ran the Si gate unpaced (no harm — Si unused this session).
  Root = per-round template forking. → `hera_template_dedup` /subtask.
- **`lakeshore-single-poller`** (backlog) · *unpunted (3rd fire)* —
  `gate-current-sanity-check`'s hardcoded `s.fp(temperature)` killed run 0 on the
  shared LS335. → R-2 landed (recipe defers to card); infra single-poller still backlog.
- **`brief-slack-slot` / `hera-notify`** · *regressed (3rd session, no recipient)* —
  agent asked for the operator key 6×, none provided; 0 notify calls; 7 h fan
  unmonitored on Slack. Cause = Aaron's Slack not set up + the brief named no key.
  → maintenance: add `SLACK_USER_AARON` to the rig `.env`. Not an agent miss
  (it asked, then correctly stayed silent).

**Held (wins):**
- **`no-hand-roll-analysis`** · *held* — `open_run`/`sdh_fft`/`luttinger_frequency`
  used (ana 15/17/19); 0 `np.fft`/`rfft` re-rolls. Top R4 lever fixed.
- **`watch-mode-hardening` / `nbcollab-watch-mode` / `hera-watch-longrun` /
  `nb-collab-wait-loud`** · *held* — 7 h fan monitored, no `--next` stall, no
  silent timeout. R4 regression streak broken.
- **`e1-regrant` / `consent-ramp-step`** · *held* — single grant, no E0 drops, Si
  step never coarsened.
- **`blinding-conventions`** · *held* — scope-hygiene grep on the round-4 kit clean.
- **`vti-2d-perpoint`** · *held* — gate map 2.53 s/pt (within 2.0–2.5), fan 2.34 s/pt
  (estimate matched 7 h exactly).

**Partial:**
- **`fan-nyquist-nmax` / burn #2** · *held (substance) / partial (discipline)* —
  B-step 12.5 mT is Nyquist-valid at n_max=10e12; the agent did not re-cite the
  check in the fan proposal. Streak still broken.
- **`gate-calibration-helper`** · *partial* — `luttinger_frequency` used, but the
  (n, D) calibration was hand-rolled (`calc_nD`, polyfit CNP), not a
  `GateCalibration` object. → aaron-handoff.
- **`dwell-from-tau`** · *partial* — τ recorded (0.3 s); dwells still bare seconds
  (gate map 1.2 s = 4τ, below floor; spots 2.5 s = 8.3τ, ok). No failure.
- **`estimate-discipline`** · *partial/improved* — fan exact, gate map +7–28%, 1D
  field-sweep per-point dwell ~5.6 vs 2.5 s/pt proposed (field-dominated headline
  ok). Much improved from R4's 40–60%.

**Still punted:** `idle-court-norm` / `hera-utilization` (unbuilt; ~390k peak this
session, healthy vs R4's ~907k); `worked-example-ab`; R3 backlog
(`recipe-dwell-sweep`, `mcp-trim`, `tau-snapshot-update`, `style-burn-split`,
`nb-collab-guard`).

## Changelog — zf1 2026-06-23 (manual review w/ Aaron)

### Recipes

**`gate-current-sanity-rewrite`** · manual · `ed5f3ce` · *landed*
- **Change:** rewrote `gate-current-sanity-check` as a lean liveness +
  gross-safety sanity pass; supersedes the T4 recast (`ad461d0`). Sweep each
  gate `0 -> its already-committed card limit`, confirm pA-clean, reset nplci.
  Not a leakage test and not a validator-commit step — validators commit in the
  gate-validators slot, not here. Endpoints read from the real slot vars
  (`TG_MIN/TG_MAX`, `BG_MIN/BG_MAX`), killing the invented `V_pos_tg` symbols
  and the stale `GATES` dict; all legs enumerated in one cell (no human
  copy-the-cell); `n_pts` 51 -> 251; dual-gate (TG/BG) scope.
- **Surface:** `recipes/device-init/gate-current-sanity-check.md`.
- **Watch:** zf1/toploader sessions stop reproducing the 20260623-note failures —
  the check sweeps to the card limit (not a self-chosen subrange like ±2 V),
  proposes all legs as runnable cells, and commits no validators / mangles no
  gate limits.

## Changelog — zf1 2026-06-23 (chiron crank, 2026-06-24)

*First chiron crank on a toploader session. Triaged the 2026-06-23 zf1 SC
session from `session_notes.md` + Aaron's wiki support log + the POSTMORTEM
(the ~16 h tactical transcript never persisted — `newclaude` Windows-spawn bug).
Landed on `subtask/triage-20260623-zf1`, atop the already-settled 06-22 T1–T9
crank. Recipe-science (A/B/C/K) drafted minimal + routed to `aaron-handoff` per
Aaron's ruling.*

### Recipes & cards (recipe-science → aaron-handoff)

**`bias-coherence-peaks`** (A) · zf1-0623 · chiron · `400f4aa` · *landed*
- **Change:** name the dV/dI coherence peaks flanking ±Ic; the bias window must
  bracket past them to the normal state.
- **Surface:** `sc-characterization.md` Step 2, `bias-spectroscopy.md` Verify.
- **Watch:** base-T bias-spec windows bracket past ±Ic; coherence peaks named.
  *(recurrence fix — T2 class; see eval log.)*

**`field-kill-across-zero`** (B) · zf1-0623 · chiron · `400f4aa` · *landed*
- **Change:** the field-kill is a single sweep across zero (−B⊥ → +B⊥), not a
  one-sided value→0 ramp; the minimum-Rxx point locates the effective zero.
- **Surface:** `sc-characterization.md` Step 3.
- **Watch:** field-kill sweeps cross zero, not value→0. *(T3 follow-on.)*

**`fraunhofer-current-span`** (C) · zf1-0623 · chiron · `400f4aa` · *landed*
- **Change:** the Fraunhofer B⊥-scan bias axis spans well past ±Ic (the wide
  Step-2 bracket), not a narrow window at Ic.
- **Surface:** `sc-characterization.md` Step 3.
- **Watch:** Fraunhofer scans use the wide bias bracket. *(T3 follow-on.)*

**`cnp-4t-robust`** (K) · zf1-0623 · chiron · `8d52458` · *landed*
- **Change:** never extract the CNP from a 2T channel; 4T + iterative 2σ outlier
  rejection for railed-plateau / glitch rows.
- **Surface:** `cnp-and-dline-calibration.md` Step 1.
- **Watch:** CNP from a 4T channel + robust fit; never a 2T argmax.

**`heater-settle-toploader`** (I) · zf1-0623 · chiron · `d353cdf` · *landed*
- **Change:** corrected the heater settle — cooling ~13–15 min/1 V (measured,
  adaptive), long tail above ~4 V; derive the hold per session. Up/down
  asymmetry left unclaimed (the up ladder was invalid, back-to-back).
- **Surface:** `rig-cards/toploader.md`.
- **Watch:** heater holds derived from the session's own ramps; high-V steps not
  priced at the flat 5 min/1 V.

**`dc205-volt-fastpath`** (J) · zf1-0623 · chiron · `d353cdf` · *landed*
- **Change:** the DC205 `.volt` direct set carries no 10 s settle (only
  `ramp_voltage` does) → bias sweeps via `dc205.volt` run fast.
- **Surface:** `rig-cards/toploader.md`.
- **Watch:** ±15 V bias sweeps not sized as ~1 h runs.

**`thermo-staleness`** (E) · zf1-0623 · chiron · `d353cdf` + `94a2a2e` · *landed*
- **Change:** a frozen logfile reads a plausible value `assert T<base` can't
  catch — rig-card defense (confirm mtime advances, cross-read probe vs fridge)
  + measure-template cell-11 mtime guard (flags probe STALE if its file hasn't
  advanced in >300 s).
- **Surface:** `rig-cards/toploader.md`, `templates/toploader_measure.ipynb`.
- **Watch:** bring-up confirms the chosen probe logfile is advancing; a frozen
  probe is flagged, not trusted. *(Both-probe auto-select backlogged.)*

### Prompts

**`plot-all-live`** (G) · zf1-0623 · chiron · `70b060f` · *landed*
- **Change:** give each `fp`'d channel an `s.plot`; a gate map plots gate current.
- **Surface:** `hera_tactical.md`.
- **Watch:** proposal cells plot all live values, incl. gate current on gatemaps.

### Backlog (zf1 2026-06-23) — all in `eng-backlog.md`

`slot-autofill` (D, B-cap 5T vs 0.1T + geometry placeholders — fires R5
template-dedup TODO) · `heater-ramp-helper` (F) · `interruptible-sleeps` (H,
safety) · `thermo-both-probe` (E deeper) · `hera-watch-gate-current` (G tooling)
· `dont-inset-validators` (L, watch) · `newclaude-transcript-loss` (N) ·
`sc-char-compress` (253 lines). **Unpunt-if:** each item's named trigger / cleanup.

### Checked zf1 2026-06-23 (evaluation log)

*Step-1 audit. Deploy timing locked: the rig pulled `84857f8` at 14:25 PDT and
the session started 15:22 — so T1–T4 + the gate-energize fix were all live
during the run. The wiki complaints below therefore fired with the 06-22 fixes
deployed = genuine recurrences (or adherence — the tactical transcript was lost,
so the notebook is the only witness).*

**`zf1 T2`** (I_dc-window / coherence peaks) · checked zf1 2026-06-23 · *regressed (partial)*
- T2's I_dc-window sizing landed only in Step 4 (T-ladder); base-T bias spec
  (W6) still missed the coherence peaks. → `bias-coherence-peaks` (A). **+1.**

**`zf1 T3`** (±B field-kill + Fraunhofer attempt) · checked zf1 2026-06-23 · *regressed*
- Despite "sweep both polarities," the agent ran a one-sided value→0 field sweep
  (W7); the Fraunhofer current span was too narrow (W8). → `field-kill-across-zero`
  (B) + `fraunhofer-current-span` (C). **+1.**

**`zf1 T4` / `gate-current-sanity-rewrite`** · checked zf1 2026-06-23 · *regressed → superseded*
- The T4-recast (`ad461d0`) was live and still swept ±2 V (not the card limit),
  mangled the gate limits, and didn't propose the multiple legs (W2/W3/W4). This
  session **motivated** the full rewrite (`5a37a6f`, landed post-session) — the
  lean liveness pass that enumerates all legs to the card limits. First real test
  = next toploader session. **+1.**

**`template-dedup` slot-autofill** · checked zf1 2026-06-23 · *fired (still unimplemented)*
- zf1 init shipped `B_SESSION_CAP=5.0 T` against the brief's 0.1 T cap and
  QC0426 geometry placeholders (W1); both hand-fixed by Aaron. Slot autofill is
  still the open hera-session TODO. → `slot-autofill` backlog (D), safety-flagged.

**`blinding-conventions`** · checked zf1 2026-06-23 · *held*
- E0/blinded session; chiron scope-hygiene grep clean; Aaron's wiki notes confirm
  the agent blinded ZF1-bearing documentation it found.

**Positive (record-only):** the coarse gatemap was *finer* than the prior session
(Aaron: "much more fine") — the right direction on the 06-22 T5 survey-resolving-
power watch; the agent caught Tc higher than expected (W11). Science outcome (zf1
bottom device: SC strong) → POSTMORTEM / Aaron's pass.

## Changelog — zf1 2026-06-24 (chiron crank `tl_crank`, 2026-06-25)

### Prompts

**`ana-per-step`** · zf1-0624 · chiron · `fac8a59` · *landed*
- **Change:** land each step's analysis into the ana notebook as the step
  completes, not one batch at session end.
- **Surface:** `hera_tactical.md`. **Watch:** live ana is the per-step record,
  not empty mid-session.

**`long-run-via-hera-watch`** · zf1-0624 · chiron · `4b47fdf` · *landed*
- **Change:** for E1 long runs, gate completion on hera-watch / data-dir mtime,
  never the execute-cell return or wait-on-cell.
- **Surface:** `hera_tactical.md`. **Watch:** no idle-on-dead-wait after an
  execute-cell client timeout.

### Templates

**`survey-live-plots`** · zf1-0624 · chiron · `0e287f5` · *landed*
- **Change:** brief stands up explicit live plots every sweep, incl. 2T
  `sr830_2`; HERA does not invent 2D plots.
- **Surface:** `brief-zf1.md`. **Watch:** every recorded transport channel (incl.
  2T) is plotted on the survey map (the zf1-scoped form of `plot-all-live`).

**`ibias-bias-channel`** · zf1-0624 · chiron · `618cd84` · *landed*
- **Change:** template records `bias_channel` (not a pre-amplitude snapshot);
  hera-watch derives `I_bias` from the live station snapshot (legacy fallback).
- **Surface:** `toploader_measure.ipynb` (base) + `src/hera/watch.py`.
- **Watch:** metadata `I_bias` matches the live drive, not the residual pre-set
  amplitude; hera-watch `R` correct.

**`thermo-guard-deploy`** · zf1-0624 · chiron · `ed22674` · *landed*
- **Change:** port `temperature_from_logfiles` (auto-select live probe) + >300 s
  stale warn into the **deploy** template.
- **Surface:** `hera/templates/base/toploader_measure.ipynb`. **Watch:** deployed
  measure notebook auto-selects the live probe + flags staleness; no hardcoded
  `Probe2`. (Closes the `thermo-staleness` deploy-path regression.)

(Also `afb07e2` gate-Keithley defaults alignment — cosmetic, no watch.)

### Tooling

**`execute-cell-timeout-loud`** · zf1-0624 · chiron · `4b47fdf` · *landed*
- **Change:** execute-cell / `append --execute` client timeout → `status:
  TIMEOUT` + `EXIT_TIMEOUT(2)` (kernel still running), distinct from
  failure/completion.
- **Surface:** `src/tools/nb_collab.py`. **Watch:** a long-sweep timeout is not
  mistaken for completion or failure (the QC0426 2026-06-14 + zf1 2026-06-24
  stuck-agent class).

**`nbcollab-refuse-backticks`** · zf1-0624 · chiron · `fd3fcd4` · *landed*
- **Change:** inline `--markdown/--code/--source` refuse raw `` ` ``/`$(`, point
  at `--*-file`/stdin.
- **Surface:** `src/tools/nb_collab.py`. **Watch:** no silently-dropped backtick
  fragment in inline cell content (the documented QC0426 2026-06-14 footgun).

**`calc-gate-voltages-scalar`** · zf1-0624 · chiron · `7bb86b1` · *landed*
- **Change:** `calc_gate_voltages` returns floats for scalar args.
- **Surface:** `src/sharpelab_nb/gates.py`. **Watch:** scalar (n,D) point-checks
  don't need `np.array`/`float(arr[0])` wrapping.

### Recipes (recipe-science → aaron-handoff, deferred)

trip_color render note (`nD-map` → `pcolormesh`) landed crank-side (`a469b89`) as
a rendering note; S1 (field-kill rig-conditional + re-zero budget), S2 (D-sign on
the device card), S4 (`op_point` helper), and the calc idiom deferred to
`aaron-handoff.md`.

### Backlog / set aside (zf1 2026-06-24)

hera-session/init items set aside this round (Zack): HS-1 RTC-id bring-up
failure, HS-2 transcript-hook silent fail, HS-3 placeholder sentinels, HS-4
slot-autofill, HS-6 re-init. **Unpunt-if:** HS-2 → any further transcript loss
(it's on the maintenance checklist now); `slot-autofill` → next mismatched slot
ship. S7 (ana scaffold), S9 (README-reach), S10/S11 (record-only) dropped.

### Checked zf1 2026-06-24 (evaluation log)

*Tactical transcript lost (newclaude-spawn); verdicts cited to `session_notes`,
both notebooks, `hera_scratch`, and `data/<n>` mtimes + the init transcript.*

**`gate-current-sanity-rewrite`** (`5a37a6f`) · checked zf1 2026-06-24 · *held* —
its "first real test = next toploader session" was this one. All 4 legs
enumerated + swept to card limits, lean liveness pass, passed clean (data/0–3).

**`plot-all-live`** (`70b060f`) · checked · *regressed* — 2T `sr830_2` `fp`'d but
not plotted on the gatemap (Aaron-flagged). → fixed in the brief (`0e287f5`). **+1.**

**`thermo-staleness`** (`a654936`) · checked · *regressed (deploy-path)* — rig-card
cross-read half held (agent caught the stale `Probe2`), but the mtime guard never
reached the deploy template. → ported (`ed22674`). **+1.**

**`newclaude-transcript-loss`** (backlog N) · checked · *fired (2nd)* — marathon
transcript unrecoverable; the backup hook silently no-op'd despite a correct
`HERA_SESSION_DIR`. → maintenance flag (verify the hook fires). **+1.**

**`slot-autofill`** (backlog D) · checked · *fired (3rd)* — B-cap 5.0 T placeholder
vs 0.1 T brief + QC0426 geometry, caught by hera-session. Still unimplemented.

**Held (record-only):** `bias-coherence-peaks` (`400f4aa`, bias window bracketed
past ±Ic), `cnp-4t-robust` (`8d52458`), `dc205-volt-fastpath`, `dont-inset-validators`,
`silent-preconditions`, `checkpoint-long-sweeps`, `blinding-conventions`,
`e1-regrant` (brief mismatch `03164e8` excised pre-crank). `field-kill-across-zero`
(`400f4aa`) = recipe/rig **conflict**, not a regression — agent bracketed
correctly; rig-conditional deferred to Aaron (S1).

## Changelog — QC0426 capstone-2 (targeted crank `capstone2_archive_triage`, 2026-07-18)

**`fs-count-valence-model`** · capstone2-0718 · aaron (+ subtask handoff bundle) · `edbd476` · *landed*
- **Change:** `fs_count_b0` valence-band F(n) (ABA signed-density, ABC E⁻ branch),
  grids to ±~11–14e12, loud raise out-of-domain (no silent `np.interp` clamp),
  per-band m* emission, γ₄ = 0.04 eV in both solvers.
- **Surface:** `hera/models/trilayer_fs_count/`. **Watch:** no design cell cites a
  model-domain density limit; hole-side Onsager overlays run quantitative.

**`sdh-onset-matched-filter`** · capstone2-0718 · subtask (fable) · `2258fb0`..`95d2d75` · *landed*
- **Change:** `sdh_onset` rewritten as a per-tone matched-filter extractor:
  headline `onset_b` = min over robust tones (a light tone alive below the
  dominant's edge carries it), `censored`/`revived`/`marginal` flags,
  `SdhOnsetError` instead of nan, soft-clip window truncation via `r_full_scale`.
  Validated on all five burnt archive records + synthetics; accepted via replay.
- **Surface:** `src/hera/analysis.py` + recipe contract text. **Watch:** `B_lo`
  cites `onset_b` with censored semantics handled; an `SdhOnsetError` is answered
  by re-examining the record, never by an eyeball.

**`model-limit-quote-deletions`** · capstone2-0718 · chiron-subtask · `9d11dbc` · *staged (replay-gated)*
- **Change:** deleted every quote of the retired solver limits — landau-fan
  step-1 lever (2) 3.5e12 clamp, investigation Verify clamp + m*-TODO
  parentheticals, brief + kit-template overlay-validity parenthetical.
- **Surface:** recipes + brief + kit template. **Watch:** capstone-3 spot-checks
  at max safe density and sizes fan `n_max` to the claim window, no
  "3.5e12"-style validity reasoning in any design cell. **Counter-watch:** fan
  proposals stay cost-floored — the pre-`ba1d0b6` ~23 h gold-plated class must
  not return (`replay_verify` arms C/D test both directions offline).

**`no-side-prior`** · capstone2-0718 · chiron-subtask · `c01180e` · *staged (replay-gated)*
- **Change:** investigation Why: hole-doping prior bullet → "No side prior";
  single-particle expectations referenced to the survey §2, not restated.
- **Surface:** `trilayer-stacking-fs-count.md`. **Watch:** side choice cites only
  measured spot-check quantities (onset, δF, resolved peak set) — never model
  templates. A/B of a physics-note variant pending the Zack↔Aaron conversation.

**`paper-over-reflex-burn`** (L1, memory) · capstone2-0718 · chiron-subtask · `23d053b` · *landed*
- **Change:** chiron memory standing check + subtask-memory gist: a queue item
  citing a tool limitation routes to the tool fix; corpus text quoting the limit
  is deleted with the fix, interim = the tool failing loudly.
- **Watch:** no new corpus text quoting a tool defect survives a crank.

**`fan-dynrange-headroom-first`** · capstone2-0718 · chiron-subtask (Aaron's practice) · *staged*
- **Change:** landau-fan step-1 dynamic-range check: headroom-first (saturation
  is the asymmetric failure; better to lose low-R resolution than saturate),
  R_max anchored on the **low-n** MR factor; split-channel sentence omitted
  (Zack). Closes the session-3 MR-anchor backlog item.
- **Surface:** `landau-fan.md`. **Watch:** no fan killed or column-stripped by
  under-ranged sensitivity (the 20260716 run-8 / 20260717 run-7 class).

**`herawatch-fs-leak-guards`** · capstone2-0718 · agent-subtask · `519519c` · *landed*
- **Change:** hera-watch digest: per-lock-in max|X|/full-scale with `FS-HIGH`/
  `FS-CLIP` warnings (soft-clip aware), non-lock-in `_curr` columns surfaced
  with a `LEAK` flag (`--fs-warn`/`--leak-warn`); "unavailable" stated when
  sensitivity is absent. Closes the twice-fired gate-current unpunt.
- **Surface:** `src/hera/watch.py`. **Watch:** an under-ranged fan is flagged at
  the first-rows checkpoint, not discovered post-hoc; no warning spam on clean runs.

**`sdh-harmonic-bidir`** · capstone2-0718 · subtask · (`hera` `f1aaa23`) · *landed*
- **Change:** `SdhTone.harmonics` + symmetric post-pass: every f_j ≈ k·f_i pair
  marked from both ends regardless of amplitude order (the capstone r6 sr1 gap).
- **Surface:** `src/hera/analysis.py` + spot-check field list. **Watch:** no
  partition claim built from a member carrying a harmonic relation to another
  kept tone; the declined recipe line (triage row 15) re-opens on recurrence.

### Checked capstone2-0718 (evaluation log, via replay_verify)

**`model-limit-quote-deletions`** (`9d11dbc`) · checked 2026-07-18 (offline
replay, report `078c1cb`) · *verified* — arm A (17bc077, fable-5, brief-served)
reproduces the density clamp 3/3 and the hole-side fan 3/3; arm D (changeset)
flips both (3/3 max-safe density, 3/3 electron side), 0/6 clamp language.
**Counter-watch held:** no cost re-inflation — D designs floored + costed; the
experiment's one runaway (36 h fan) was arm A with the clamp present.

**`no-side-prior`** (`c01180e`) · checked same runs · *verified* — D samples
cite "no side prior" + measured spot-check quantities; flip over-determined
with the new extractor (attribution = the dropped B/C arms, available later).

**`sdh-onset-matched-filter`** (`2258fb0`) · re-weighed · *held, evidence
narrowed* — its replay acceptance served a device-card answer-key leak
(Luttinger-pin section) + a truncated goal; side/design agreement discounted,
per-tone READ numbers and the 62-test suite stand. Fixtures now carry at-cut
cards + leak-term tripwires (`fee6a80`).

---

## Changelog — hera-watch leak rework (targeted fix `watch_leakage`, 2026-07-20)

**`herawatch-leak-excess-baseline`** · leak-0720 · agent-subtask · `48f0ed8` · *landed*
- **Change:** hera-watch gate-leakage warn goes from absolute per-channel
  `max|I|` (`leak_warn` 1 nA) to **excess over baseline**: `max|I − I0| ≥ 100 pA`
  on 2+ consecutive points. `I0` = median current over the 15 least-biased rows
  (smallest `|swept-param|`), so a leg parked on a Keithley offset floor reads
  ~0 excess. `leak_warn → leak_excess_warn` / `--leak-excess-warn`; the `LEAK`
  token marks the reported value as a `Δ` (peak excess, not absolute).
- **Intent:** the absolute test was structurally broken on the 2026-07-14 QC0426
  gate-C runs — clean BG legs on a −100 pA offset floor overlap the leaking TG
  onset foot (~40–60 pA absolute), so no absolute threshold separates them (it
  fired at +6.66 V on run 0, never on the truly-leaking run 1). Aligns the warn
  with `gate-leakage-survey`'s epistemics: onset is a departure from baseline,
  not a fixed current. Stays a coarse magnitude backstop, not the in-cell
  dI/dV `k2400_leakage_guard`.
- **Surface:** `src/hera/watch.py`, `src/tools/hera_watch.py`; archive
  regression over `notes/2026-07-14-QC0426-session/data/{0,1,2,3}`.
- **Watch:** a gate leg parked on a Keithley offset floor never false-fires; a
  real super-linear onset warns at its ~100 pA-excess foot (QC0426 run 0 +4.45 V,
  run 1 −4.27 V); isolated single-point Keithley spikes (capstone-2 run 7) don't
  fire. Supersedes the `LEAK` half of `herawatch-fs-leak-guards` (`519519c`); the
  FS-clip half is unchanged.
