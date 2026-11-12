# HERA engineering backlog

Items surfaced during HERA exploration that aren't HERA itself — sharp edges, doc gaps, small fixes worth tracking but not blocking the main thread.

## sharpelab_nb sharp edges

Surfaced 2026-05-05 during the source-skim pass for `hera/docs/sharpelab-nb-reference.md`. All four are user-facing gotchas, not internal cleanup.

- [ ] **`Yokogawa7651` is write-only.** No parameter readback from the instrument; voltage cache is empty after kernel restart, and ramp methods raise `RuntimeError` unless `set_voltage_cache()` is called or `start=` is passed explicitly. Sharpest gotcha in the package. Source: `src/sharpelab_nb/drivers/`. Mitigation candidates: auto-prompt for current voltage on first ramp; persist cache to disk; document loudly in the driver class docstring.

- [ ] **`autorange_sr830s` silently no-ops** if `|phase| < 160°`. Phase drift during a sweep stops autoranging with zero warning. Source: `src/sharpelab_nb/autorange.py`. Mitigation: emit a one-line warning when the phase guard skips a lock-in; surface in `Status` output.

- [ ] **`plot_hysteresis` unconditionally loads `[file, file+1]`** — no guard. Calling on the last run of a dataset raises. Source: `src/sharpelab_nb/plotting.py`. Mitigation: check existence of `file+1` and raise a clear error, or fall back to single-run plot.

- [ ] **`temperature_from_logfile` hardcodes column index `-3`** with no validation; assumes Lakeshore log format never changes. Source: `src/sharpelab_nb/thermometry.py`. Mitigation: parse by header on first read, cache the column index per logfile.

## Ship `sharpelab_nb.sc` Ic-extraction helpers

Surfaced 2026-06-21 (zf1 toploader session). `bias-spectroscopy.md`'s Verify imports `from sharpelab_nb.sc import extract_critical_current` / `map_ic_dome`, but the `sc` module doesn't exist → `ModuleNotFoundError`. Not blocking — HERA hand-extracted Ic (threshold crossing on smoothed dV/dI); the recipe now flags the import "not yet shipped — extract by hand".

- [ ] **Ship `sharpelab_nb/sc.py`: `extract_critical_current` / `map_ic_dome`.** Pure and device-agnostic — take physical dV/dI (Ω) + the bias-current axis; the caller resolves channels/gains per the device card. `extract_critical_current(idc, dVdI, threshold, smooth=...) -> (ic_neg, ic_pos)`: first threshold crossing out from zero on each polarity, smoothed; **return `np.nan` (not the sweep edge) when a polarity never crosses**, so "range too short → Ic is a lower bound" stays detectable. `map_ic_dome(...)` applies it per slow-axis row. Center on the zero-bias minimum to absorb the ~1–5 nA instrumental offset. Lands in the `measureme`/`sharpelab_nb` submodule (Zack). Source: `bias-spectroscopy.md` Verify.

## hera-classify prefix is below Gemini cache minimum

Surfaced 2026-05-06 during the toploader smoke test. The classifier's stable prefix (system instruction + glossary + output prefs + device card + 5-channel exemplar PNGs + exemplar JSON) totals ~3.4k tokens — under the 4k token minimum Gemini 2.5 Flash requires for `CachedContent`. Every call hits `429 RESOURCE_EXHAUSTED ... TotalCachedContentStorageTokensPerModelFreeTier limit=0, requested=3375` (free-tier shape) and falls back to inline. The fallback works fine and inline cost is ~$0.001/call at human pace, so this is cosmetic — but the architecture's main efficiency claim isn't currently realized.

- [ ] **Bulk the prefix above 4k tokens or accept inline.** Two paths: (a) accept inline as the steady state and remove the cache machinery (less code, no false expectation); (b) add a second exemplar (RPL10 dataset has annotated scans at 24/26/138/220/279) and/or enrich the glossary to push the prefix above 4k, which would let cache actually engage on a paid tier. Free tier has cache-storage limit=0 regardless, so (b) only pays off if we move off free. My lean: (a) for now since cost is negligible; revisit if (i) we go paid for other reasons or (ii) we want to share the prefix across many concurrent classify calls. Source: `src/hera/providers/gemini.py:_create_cache`, `src/hera/prompt.py:build_stable_prefix`.

## Device-card updates belong in close-out, not mid-run

Surfaced 2026-06-19 (QC0426 round-5 triage). `hera-mksession` re-copies the
**clean** canonical `templates/<device>/device_card.md` each session, so every
in-run device-card write is **archival-only** — it does not carry to the next
session (round 5 re-established the (n,D) calibration from scratch; it didn't
inherit round 4's). Two problems with writing the card during the run: (1) the
agent spends tokens authoring a *results* section into a card whose stated job
is **physical truth** (wiring, hardware, safety, provided config); (2) round 4
wrote "QC0426 = ABA (Bernal), strong" and round 5 wrote "QC0426 = ABC
(rhombohedral), strong" — a non-decisive, here *contradictory*, interpretive
call lodged in the truth card. Both are duplicated in `session_notes.md` + the
ana notebook + the wiki, which are the right homes.

- [ ] **Move device-card mutation out of the live run into a close-out step.**
  During the run the card is read-mostly. At session close-out, a bounded pass
  writes back only *measured device facts worth re-reading* (confirmed
  addresses, channel health, and — if we decide calibration should carry
  forward — the (n,D) calibration). **Never** the interpretive stacking call /
  strength verdict; those stay in notes/ana/wiki. Open sub-decision: should the
  per-cooldown (n,D) calibration carry forward (persist the closed-out card as
  the next session's prior) or be re-established each cooldown? If carry-forward
  is wanted, solve it *without* dragging the science call along. Touches the
  tactical/iris prompts (drop the in-run card-write step) and hera-session /
  mksession (the close-out write-back).

## Recipes lack post-hoc analysis blocks

Surfaced 2026-05-05 while drafting `hera/hera_tactical.md`. The device-init recipes describe what a human should watch for on the **live Qt plot** (e.g. "gate current stays in picoamps, nA roll-off is breakdown") and one cites a concrete threshold (`gate-leakage-survey` mentions `5e-11 to 8e-11 A` for the abort callback) — but none describe how to verify pass/fail **post-hoc from disk**, which is HERA's only path since it can't see the live plot.

- [ ] **Add `## Verify` section to each recipe.** Code-shaped block(s) showing how to load the saved sweep (`<notebook_dir>/data/<file_id>/{data.tsv, metadata.json, plot.png}`), compute the recipe's pass/fail criteria (e.g. `np.abs(df['k_tg.curr']).max() < 1e-9`), and either green-light advancement or hand back to the human. Source: every recipe in `hera/recipes/{device-init,measurements}/`. Mitigation: a one-pass amendment after the first live HERA tactical session surfaces the actual analysis idioms the agent reaches for. Pairs with the agent prompt's `Bash + Read + local Python` section, which currently carries the file-layout knowledge by itself.

## HERA-prefilled session template

- [ ] **HERA-flavored measurement template.** A variant of `templates/toploader_measure.ipynb` that ships HERA conventions pre-filled: mandatory `add_comment` patterns at sweep boilerplate, header text hints toward recipe slugs, any HERA-specific hooks. Users start a HERA-mode session from this template instead of the bare one. Probable home: `templates/toploader_measure_hera.ipynb`. Open: how the GUI launcher exposes the choice (per `src/gui/toploader_launcher.py`'s "create new run" flow).

## Show cell indices in the JupyterLab UI

Surfaced 2026-06-10 (VTI live session). HERA cites cells by 0-based index
(nb convention); JupyterLab displays no indices, so the operator can't
locate "cell 18" without counting — workaround that session was `nb summary`
in a JL terminal as the index↔content map. Triage 2026-06-11: prompt-side
content anchors ("cell 37 — the fan cell") judged inferior; Zack wants the
indices visible in the UI — better and cheaper for everyone.

- [ ] **Surface 0-based cell indices in JL** — candidates: existing
  extension if one exists, a ~50-line local labextension, or CSS
  counter hack on `.jp-Cell` (counters can't skip markdown cells, so the
  CSS route likely miscounts vs nb's code+md indexing — verify before
  shipping). Must match `nb`'s indexing exactly (all cells, 0-based) or
  it's worse than nothing. Deploy: both rigs + Zack's browser profile.

## Fridge/rig cards — complete the layer model

The rig-card layer landed 2026-06-12 (EXAMPLE/README/VTI/toploader cards
under `hera/rig-cards/`, deployed as `rig_card.md`; the prompt is now
machine-agnostic, renamed `hera_tactical.md`).

- [ ] Still to collect from Bingcheng (VTI czar): envelope edge
  numbers, heat-up/cool-down procedure, exception ownership — answers
  land on the VTI card (see round2-preflight rig-rules item).

## Session archives don't belong in the repo long-term

Surfaced 2026-06-11 while archiving the first VTI live session
(`hera/docs/notes/2026-06-10-QC0426-session/`, 11 MB with the agent
transcript). Archives are committed to the repo today (toploader
precedent) — fine while there are few, but they're data, not code, and
the repo will bloat as sessions accumulate.

- [ ] **Move session archives to the measurement-data tree** (titan
  mirror / `dgglab-measurements`-style location), keep only the session
  *notes/log* docs in the repo, and point `hera-archive` at the new
  destination. Migrate existing `hera/docs/notes/*-session/` archives
  when the destination exists.

## Idle-time pricing norm (utilization) — punted, too strong for now

Surfaced 2026-06-10: HERA serialized sweep → read → analyze → land next
cell; measured 42% fridge utilization over the first three runs. Drafted
working-style bullet ("price idle time; keep a runnable next-cell landed
with go/no-go conditions") punted at 2026-06-11 triage: right direction,
too strong as a hard norm — risks queue-for-the-sake-of-queue cells and
operator pressure. Revisit with data once `hera-utilization` (raw +
agent-attributed) exists and a couple more live sessions are scored.

- [ ] **Re-evaluate after utilization tooling lands** — pair the metric
  with a softer prompt nudge (read/analyze during sweeps, not during
  idle) and judge against measured scores, not vibes.

## Validator persistence prompt (tactical)

Surfaced 2026-05-05. When the human tightens validators live via `k_tg.volt.vals = validators.Numbers(-7, 6)`, the change lives in the kernel only — kernel restart drops it. The `GATES["k_*"]["limit"]` in cell 1 has to be edited separately to survive. Nothing in the recipe or tactical's protocol prompts the human to do this; tonight Isaac knew to do it but the agent didn't help.

- [ ] **Tactical should prompt for the cell 1 `GATES` update** when it observes a live-validator tightening that doesn't have a corresponding cell 1 edit. Nb-collab can't edit cell 1 directly (append-only), so this is either (a) a markdown reminder cell appended to the notebook, (b) a recipe step that runs an override cell at every kernel re-init, or (c) a follow-up cell that re-asserts the validator after cell 1+9 run from a fresh kernel. Pairs with the iterate-then-bless gate above.

## Mid-session prechecks → recipes

Surfaced 2026-05-05. Tactical drafted two precheck cells on the fly that aren't in any recipe today: a bias precheck (cell 18: `amp = sr830_1.amplitude(); ...`) before the first sanity-check, and a lock-in state diagnostic (cell 25) when the post-119 readouts looked stuck. Both are reusable and small.

- [ ] **Promote to named recipes** under `hera/recipes/device-init/`:
  - `bias-precheck` — verify lock-in excitation amplitude, time constant, sensitivity are sane before any current-channel reads. `## When`: before the first `gate-current-sanity-check` of a session, or after any lock-in reconfiguration.
  - `lockin-state-check` — diagnostic for stuck or saturated lock-in readouts. Polls reference state, sensitivity, overload flags. `## When`: when sweep readouts look frozen or all channels return identical values.
  
  Both are short; should be 30-line recipe files with the cell-shape captured. The post-session notebook cells 18–19 and 25 are the source material.

## FastBi1K5 driver follow-ups

Surfaced 2026-06-12 during the magnet-API incident fix (`mag` is now a
qcodes Parameter — get = measured averaged readback × T_per_A, set =
blocking ramp; see the VTI rig card's magnet section).

- [ ] **Abort / interrupt handling.** Interrupting a cell mid-`field()`
  leaves the supply ramping to the stale target; recovery is calling
  `field()` again with a new target. Wants a `stop()` / ramp-to-here
  primitive — design together with the UPS/measurebot safety integration
  down the line (power-loss handling shares the same "park the magnet
  safely" machinery). The non-blocking ramp mode (`start_field_ramp` /
  `wait_for_ramp`) added no stop.

## VTI drivers review follow-ups (full-directory pass)

Surfaced 2026-06-12, review pass over `src/drivers/` after the FastBi1K5
rework. Round-2-blocking items went straight into the round-2 SAFETIES
cell (instrument-level `k_tg.voltage.vals` fence; temperature setpoint
typo-guard caps); these are the rest.

- [ ] **SRS_DC205: step-size-aware ramp.** `ramp_voltage` always issues
  50 serial `VOLT` writes + sleeps regardless of step size, and the
  round-2 template's `dcbias` routes every fast-axis sweep point through
  it — likely ~0.2–0.5 s/point of pure overhead at 115200 baud. Fix:
  `points = max(2, ceil(|Δ|/dV))` with a chosen dV granularity. Biggest
  single sweep-speed lever in the directory; held back from round 2 to
  avoid changing sweep timing at deploy time. Pairs with the
  SRS_DC205 ↔ sharpelab_nb unification (drivers README).
- [ ] **Lakeshore_335: split the `*_power` set_cmds.** They embed
  `\r\n` mid-string (`'OUTMODE 1,3,0,0 \r\n MOUT 1,{:.4f}'`) to smuggle
  two commands into one write, second with a leading space — works by
  accident if it works. Split into two writes (needs a method set_cmd,
  not a format string). Also: PID loop config still TODO; `off()` prints
  instead of raising on an unknown heater name.
- [x] **async_station: persistent thread pool.** Resolved by retiring
  `drivers.async_station` and moving the VTI onto `sweep.AsyncStation`,
  which reuses one executor per sweep and batch-reads SR830 X/P via `snap()`.
- [ ] **AMI_420 `mag()` needs the FastBi1K5 treatment before that rig
  matters.** Two real hazards: (1) bare `except Exception` retry loop
  that re-sends the setpoint on any error; (2) the done-poll only checks
  `state() == 'RAMPING'`, so `QUENCH DETECTED` exits as if the ramp
  completed. It already has a true field readback (`FIELD:MAG?`) — port
  the mag-as-Parameter pattern plus fault-aware polling.
- Reviewed, no action: `Lakeshore_218`, `AMI_1700`, `Terranova_906A`
  (trivial read-only drivers); `QSwitch` (recent fork, live rig history,
  exercised via `contact_mux` tests).

## SRS_DC205 dedup / driver-dir consolidation

Surfaced 2026-06-14 (`dedup_drivers` subtask — scoped, then deferred for
time). Findings recorded so the work isn't re-derived; nothing changed yet.

- [ ] **Consolidate the one shared driver, `SRS_DC205`.** It is the *only*
  overlap between `src/drivers/` (VTI) and `src/sharpelab_nb/drivers/`
  (toploader); every other file in each dir is rig-specific and stays put.
  The two SRS copies are **not interchangeable**:
  - VTI `drivers/SRS_DC205.py` — rate-based ramp (`ramp_rate=5` V/s mutable
    attr, 50 pts), no post-ramp settle, `VOLT {}`. **Every** committed
    `ramp_voltage`/`ramp_rate` caller is a VTI notebook
    (`k_tg.ramp_rate=2; k_tg.ramp_voltage(vg)`); `ramp_rate` exists only on
    this copy, so VTI must keep it.
  - toploader `sharpelab_nb/drivers/srs_dc205.py` — fixed-duration ramp
    (100×0.01s), mandatory `sleep(10)` for ΔV>0.1, `Ints(0,2)` range
    validator, `VOLT {:.7f}`, ctor kwargs. **No committed code instantiates
    or ramps it** — toploader templates only `import` the symbol; its
    divergent semantics are dead code in-repo.
  - Canonical home = `src/drivers/` (its README already declares it the
    source of truth / intended single package). `sharpelab_nb.drivers`
    becomes a re-export shim so `from sharpelab_nb.drivers import SRS_DC205,
    Yokogawa7651` and `sharpelab_nb/__init__.py` keep resolving with zero
    template edits. Windows case-collision (`SRS_DC205.py` vs
    `srs_dc205.py`) blocks naive co-location — a real merge, not a `git mv`.
  - Three resolutions, pick one at pickup: **(A, recommended)** collapse onto
    the VTI driver — one file/class, VTI byte-unchanged, drop toploader's
    dead fixed-duration/settle path; needs Zack's nod that no *live*
    toploader notebook ramps SRS. **(B)** preserve both, relocate the
    toploader copy into `drivers/` under a case-distinct filename — zero
    behavior change, but keeps two same-named classes. **(C)** one
    parametrized driver with a ramp-mode flag — cleanest end state, most code
    + re-validation, overkill given (A)'s dead path. Optional under (A): port
    toploader's `{:.7f}` + `Ints(0,2)` into the VTI file (avoids
    `VOLT 1e-07`; harmless but re-touches a rig-validated driver).
  - **QDAC collision watch:** the `qdac_support` subtask may edit the same
    re-export `__init__.py` files (`src/drivers/__init__.py`,
    `src/sharpelab_nb/drivers/__init__.py`); whoever lands second rebases.
  - Subsumes the "Pairs with the SRS_DC205 ↔ sharpelab_nb unification"
    side-note on the step-size-aware-ramp item above.

## VTI launcher GUI (à la toploader)

Surfaced 2026-06-11. The VTI session is brought up entirely by hand via the preflight runbook (clone, `uv sync`, manual `jupyter lab` launch line, kernel bring-up). The toploader has a tkinter launcher GUI (`src/gui/toploader_launcher.py`) that handles run creation, JupyterLab start/stop, worker management, and aggregate health. A VTI equivalent would fold the runbook's manual steps into the same launcher pattern.

- [ ] **Build a VTI launcher GUI modeled on the toploader's.** Just capturing the item for now — scope it later.

## gate-range-finding base ↔ gate-current-sanity-check convergence

Surfaced 2026-06-11 (STYLE review of the new device-init recipes); held for
the authoring subtask, which completed without it — now unowned. The
toploader's `gate-current-sanity-check` is the same core activity as
`gate-range-finding` step 1 (and carries the live-tested failure-mode
catalog the base recipe leans on by reference). Two living documents
covering one activity will drift.

- [ ] **Rewrite `gate-current-sanity-check` as `gate-range-finding-toploader`**
  (STYLE rule 13 variant: declared base, deltas with forcing rig facts,
  obsolescence condition). Decide the failure-mode catalog's home
  explicitly — likely the base's preconditions/Examples, since both rigs
  already lean on it. Until then the base's header note is the only guard
  against divergence.

## Fold the dI/dV interrupter (`gate-leakage-survey`) into `gate-range-finding`

Surfaced 2026-06-16 (the `leakage_check_after` zero-read guard work). The
interrupter is not a separate activity from range-finding — it is an
**automated method for range-finding Step 1**: the `LeakageDetector` trips
at the leakage *foot* automatically, replacing the manual endpoint-walk and
the Step-7 "watch-and-interrupt" operator fast-path. `gate-leakage-survey`
also **restates** the shared tail: its Cell C (commit validators + device-card
mirror + HERA handshake) ≈ base Step 3, and its Cell B (opposed-corner verify)
≈ base Step 2 (four-corners, narrower). Three living documents
(`gate-range-finding`, `gate-current-sanity-check`, `gate-leakage-survey`)
over one core activity will drift. Distinct from the convergence entry above:
that axis is rig variant (toploader); this axis is **method** (manual walk |
watch-and-interrupt | dI/dV interrupter) within one base.

**Sequencing gate:** `gate-leakage-survey` is DRAFT / not-yet-beta-tested, and
both it and the base gate supersession on *"once beta-tested, this supersedes
the manual range-finding."* The VTI interrupter beta-test is staged but unrun.
Do not promote the interrupter into the primary recipe ahead of its own gate
unless the folded step is tagged `[BETA]`.

- [ ] **After the VTI beta-test passes:** fold the interrupter into
  `gate-range-finding` Step 1 as a third method option (default stays the
  manual walk; interrupter is the opt-in automated path); collapse Cell B/C
  into the base's Step 2/3; retire `gate-leakage-survey.md` (content absorbed,
  the rectangle/opposed-corner argument moved into Step 2's prose). Keep the
  `k2400_leakage_guard` / `run_after` registration idiom (`partial` pins
  `i_col`) as the worked cells.
- [ ] **Before then (optional drift-guard):** make `gate-leakage-survey`'s
  Cell B/C reference the base's Step 2/3 instead of restating them, and tighten
  the cross-links, so the two don't diverge while both are live.

## Toploader rig-card holes to fill before next run

Surfaced 2026-06-12; the two-prompt unification it tracked landed the same
day (rig-card work). Residual:

- [ ] Fill the toploader card's "not documented" holes with the operator
  (magnet ramp/limit/blocking semantics, base T, heater topology, envelope
  ruling) before the next toploader session.

## Disable claude.ai connectors on the toploader rig PC

Surfaced 2026-06-22. Done on dgg-vti (VTI): `"disableClaudeAiConnectors": true`
in `~/.claude/settings.json` drops the claude.ai Gmail/Drive/Calendar connectors
ambiently — a shared rig box shouldn't expose the personal account they're tied
to (verified live: `claude mcp list` → none; `--strict-mcp-config` does *not*
work for account connectors). Toploader still exposed.

- [ ] Apply the same one-key merge to the toploader's `~/.claude/settings.json`
  (don't clobber) next maintenance window. Retire when a lab account lands.

## LS335 sample-loop PID tuning session (Bingcheng)

Surfaced 2026-07-15 (QC0426 VTI session 2, LK ladder v1–v5); ruled to
backlog 2026-07-16 (Zack + Aaron). Loop 1 PID was never tuned: upward
steps overshoot ~+1.4 K, recovery is bath-limited (~0.015 K/min toward
the vaporizer floor), tolerance-settling can't pass below ~20 K.
Interim: hover acceptance (temperature-dependence VTI variant) +
set_both ratio dropped 0.99 → 0.95 (more cooling headroom — watch
heater power / mount→device gradient).

- [ ] **Rig session with Bingcheng: tune loop 1 PID** (autotune or
  manual; plant varies with T / He flow / needle valve → likely zone
  settings across 1.5–50 K). Scope `ratio` in the same session — PID
  and the vaporizer floor are coupled knobs. Success = tolerance-
  settling passes at ≤ 20 K; then delete hover acceptance from the
  recipe variant and the overshoot figures from the rig card (their
  obsolescence condition). Pairs with the Lakeshore_335 "PID loop
  config still TODO" note in the drivers-review section above.

## Single-poller architecture for shared instruments (Lakeshore first)

Surfaced 2026-06 live session (HERA retro, issue 6 / suggestion 5): VISA
contention between the Grafana logger and the measurement kernel killed a
run; the workaround (pause the logger) cost the lab telemetry for the
entire heated period. Two masters on one instrument is an architecture
bug that will recur on any logged instrument.

- [ ] **One poller process per shared instrument; all consumers read from
  it** (kernel reads cached values via a local endpoint or file; Grafana
  scrapes the same). Lakeshore is the proven offender — fix before the
  next temperature campaign. Same pattern audit for the magnet readback.

## Queue-preflight recipe (unattended chains)

Surfaced 2026-06 live session (HERA retro, suggestion 6). The
assert-precondition pattern converged on live — state chaining between
queued cells, halt-on-failure, deliberately NO asserts on the park/safe
cell — worked and should be standard rather than re-invented per session.

- [ ] **Write `device-init/queue-preflight.md`** (or a measurements/
  pattern doc) capturing the cell shapes: per-cell precondition asserts,
  state chaining, halt semantics, the park-cell exemption, and the
  estimate-vs-actual log line per chain link. Run-2 desirable: round 2's
  overnight segments will queue unattended.

## nb-collab first-execute-cell failure — RESOLVED by Phase 1 (2026-07-18)

Surfaced 2026-07-17 (capstone-2 bring-up). First id-addressed command after
a notebook opens failed `cell id not found` (retry worked). Root cause:
**stale `jpserver-*.json` server selection** — the agent resolved to a
wrong/dead server via the unauthenticated `/api/status` probe. Spec at
`hera/nb-collab/sync-resolution-spec.md`.

- [x] **Phase 1 (deterministic server resolution) — landed 2026-07-18, the fix.**
  `_server_alive` probes authenticated `/api/sessions` (not the public
  `/api/status`, which a stale wrong-token file passed); `_resolve_server`
  dedupes candidates, prefers newest jpserver mtime, returns the first that
  authenticates. Unit + Windows e2e (zack-win11-vm) verified.
- **Phase 1.5 (content barrier) / Phase 2 (Layer-4 server extension): not
  planned.** The spec's hypothesized sync-freshness race could not be
  reproduced on zack-win11-vm across escalating conditions (single cold
  client, warm-browser + agent, 60- and 250-cell notebooks, 8× concurrent
  cold-room connects — 0/247 lookups missed). Called a misdiagnosis of the
  stale-server bug; revisit only if a first execute-cell fails again on a
  clean single-server resolve.

## nb-collab watch mode (event stream)

Surfaced 2026-06 live session (HERA retro, suggestion 9): the agent's
monitoring layer was shell-sentinel duct tape all session — one false
fire, one silent `nb-collab wait` timeout during the long fan.

- [ ] **`nb-collab watch <notebook>`**: stream new-cell / output / file
  events (long-poll or websocket on the RTC doc), replacing ad-hoc
  sentinel loops. Should also fix `wait`'s silent-timeout default
  (timeout must be loud).

## Worked-example A/B: do close-to-home examples calibrate or anchor?

Surfaced 2026-06-12 (recipe-tail-fixes subtask): three QC0426-specific
additions were deliberately held out of the run-2 corpus as too close to
home — (a) trilayer-stacking-id worked two-frequency close (the split LK
masses + light-mass beat exclusion, session-tail entry 06-12), (b)
landau-fan measured-vs-bare traverse worked example (the VTI rates), (c)
temperature-dependence stability-criteria burn citation (the post-heating
base-shift incident). The generic rules landed; the device/rig-specific
anchors did not. Open question: do such examples *calibrate* the agent
(better priors, faster adjudication) or *anchor* it (expecting those
masses/rates/shifts on the next device)? The corpus already carries
counterparts (the E3 worked rejection, the toploader wall-clocks) that
could be ablated for the reverse arm.

- [ ] **Evaluate post-round-2**: queue the held-out examples (and/or
  ablate existing worked examples) and A/B across fixtures or sessions —
  batch several so the comparison has power; record which direction
  behavior moves per example, not just net. Good to do, not urgent.

## Merge the two trilayer forward-model dirs

Surfaced 2026-06-16 (ABA/ABC FS-count promotion). The corpus now has two
trilayer forward-model dirs: `models/aba_trilayer/` (the Landau-fan crossing
model, backing `trilayer-stacking-id.md`) and `models/trilayer_fs_count/` (the
B=0 FS-count + Onsager + high-field Streda model, backing
`trilayer-stacking-fs-count.md`). They overlap — `trilayer_fs_count/ll_sequence.py`
already imports `aba_trilayer/ll_spectrum.py` as a sibling, and both carry the
same SWMcC/Datta parameterization. Kept separate at promotion (different
investigations, and FS-count adds ABC content `aba_trilayer` lacks).

Update 2026-07-16 (blinding unlink for the capstone run): `ll_spectrum.py`
(the shared SWMcC core) now lives in `models/trilayer_fs_count/`; the QC0426
crossing *analysis* (README / FUTURE_WORK / compare / validate /
crossing_model) moved to `docs/vti/aba-trilayer-qc0426/` (scorer-side) so the
agent-visible models tree carries no device results. Largely resolves this
item; remaining:

- [ ] **Fold the (future) ABC-LL model into `models/trilayer_fs_count/`**
  next to the shared core when it lands; keep campaign comparisons
  scorer-side (`docs/vti/`).
## Recipe-sweep: align step-level dwells to the STYLE settling floor

Surfaced 2026-06-14 (QC0426/VTI triage, item R-3). STYLE rule 12 now states
the settling floor (`dwell ≥ k·τ`); `contact-survey-2t`, `landau-fan`,
`field-sweep-1d`, and `gate-leakage-survey` already tie dwell to τ or a settle
diagnostic, but a few recipes still carry **bare prescriptive dwells** in their
step text (not Examples, which may keep historical provenance-tagged values):

- [ ] `gatemap.md` step 6 / §examples — `slow_delay=3, fast_delay=1` as a
  recommended literal; add "or `k·τ`, whichever is larger" per the settling
  floor.
- [ ] `silicon-backgate-survey.md` steps 1/3 — `fast_delay=1` literals; same
  fix.
- [ ] Sweep the rest of `recipes/measurements/` + `device-init/` for bare
  `delay=`/`fast_delay=` in **step instructions** and reference rule 12.
  Low-priority cleanup; the STYLE rule + the burned recipe (`contact-survey-2t`)
  are the load-bearing fixes. Good cleanup-mode fodder.

## Split the burn log out of STYLE.md as it grows

Surfaced 2026-06-14 (QC0426/VTI triage, item R-3 pass). STYLE.md is at ~236
lines (budget ~250) and the burn log is ~6 entries and growing one or two per
session; the rules stay tight (burns moved to the bottom, pointers inline) but
the file will cross budget on burns alone.

- [ ] When STYLE crosses ~250 (or the burn log passes ~10 entries), **split the
  burn log into its own file** (`recipes/STYLE-burns.md` or `recipes/burns.md`),
  leaving STYLE.md the tight rules + `(burn log #N)` pointers that resolve to the
  split file. Keep the numbering stable (entries are referenced by number from
  rules and the changelog). Cleanup-mode work; the inline pointers already make
  the rules readable without the stories, so this is mechanical when the size
  forces it.

## Instrument snapshot stores time_constant / filter_slope as None

Surfaced 2026-06-14 (QC0426/VTI triage, item T-8; root-caused by the anakit
subtask). A run's `metadata.json` `instruments` snapshot has `time_constant`
and `filter_slope` keys but `null` values, so the lock-in τ is not recoverable
from disk (hurts reproducibility + post-hoc settling checks). Root cause:
`lib/measureme/sweep/sweep.py:381` builds the snapshot as `inst.snapshot()`,
which defaults to `update=False` → QCoDeS serializes **cached** values; during
a run only `X` is `get()`-ed, so `time_constant`(`OFLT?`)/`filter_slope`(`OFSL?`)
are never queried and their cache stays `None`.

Two fixes (Zack's lean: **B is good, but it's not free on every instrument** —
needs per-instrument consideration of read cost before adopting):

- [ ] **Option B (preferred, when reads are cheap): warm the cache at
  bring-up.** A `srN.time_constant(); srN.filter_slope()` read in the measure-
  notebook lock-in setup cell populates the cache so the run snapshot captures
  it — this is the *same read* the R-3 τ-record bring-up step already asks for,
  so the two fold together. **Caveat: on instruments where a parameter read is
  slow or perturbs state, an unconditional read-every-param at bring-up is not
  free** — scope it to the lock-in τ/slope, not a blanket snapshot warm. Lives
  in `templates/*_measure.ipynb` (measure-notebook contract → human ruling).
- [ ] **Option A (complete fix, heavier): `inst.snapshot(update=True)` in
  measureme**, optionally with a `params_to_skip_update` allowlist. Fixes every
  param but forces a hardware get of *all* of them at sweep init — exactly the
  read-cost concern above, rig-wide. Submodule change; defer behind B.

## 2026-06-16 QC0426 session — backlog

Surfaced in the first autonomous (E1) session; triaged to backlog.

- [ ] **`k_bg.volt()` GET halves on every call.** Each interactive read returns half the previous (get-side-effect; not RC/time). Swept data logs setpoints and is unaffected, but interactive BG readback is untrustworthy. Source: Keithley 2400 / `k_bg` driver. Mitigation: fix the get path; until then trust setpoints, not reads.
- [ ] **nb-collab ana notebook lacks insert-at-index.** append / edit-cell / delete-cell only → can't retrofit a raw-before-analysis cell in order without a destructive rebuild. Operator wants insert access on ana. Source: nb-collab.
- [ ] **hera-notify is single-recipient.** Want a group-thread target and/or multiple mentions in one call. Source: hera-notify + the brief Slack-key slot.
- [ ] **Agent-executed cells don't reflect in the operator's JupyterLab tab.** `nb-collab execute-cell` under E1 doesn't visibly show the cell running in the operator's open view. Operator-side visibility gap.
- [ ] **Sweep progress bar bloats the stored notebook.** `sweep.progress` updates via `update_display(display_id=…)`; under RTC/jupyter-collaboration each update persists as a new `display_data` output (~1 HTML div per sweep point → notebook-file and ydoc-room bloat; one QC0426 cell held 3302). Executor-independent: the browser overwrites in the UI, but the saved model appends for operator- and HERA-run cells alike. HERA read tools now collapse it (`nb` / `nb-collab`); the source-side fix wants a coarser update cadence and/or a non-inline live-progress surface (e.g. a popup window). Source: `lib/measureme/sweep/progress.py`.
- [ ] **Out-of-band E1 safety monitor (design).** Independent watchdog for gate leakage / magnet quench / sample heating during autonomous runs, separate from the agent's own checks (augment hera-watch or a new layer).
- [ ] **People roster for the agent (design).** Short who's-who (name + one-line background) of the people HERA interacts with. Filled offline; must be blinding-safe.
- [ ] **E-1 discussion-only mode (design).** A mode below E0: discussion only, no proposing/running.
- [ ] **Cost/hr + token-burn breakdown.** This session: ~907k peak context (14 h single context, no compaction), 2.03M output tokens. Want cost/hr at API pricing + a where-did-tokens-go breakdown. Ties to utilization (above) and mcp-trim.
- [ ] **Lock-in sensitivity check at bring-up** (strengthens *Mid-session prechecks → recipes* / `bias-precheck`). Sens left at 2 mV default digitized few-kΩ signals coarsely → coarse data (files 0–4) until reset to 200 µV. Setup/VERIFY should check `sens ≈ I_bias × R_target`. Rig card also lacks the amp/lock-in spec (see aaron-handoff card gaps).

## 2026-06-17 QC0426 session — backlog

- [ ] **DC205 drive has no get → can't ramp.** `dc205_volt` (TG) is set-only, so `s.ramp(dc205_volt, …)` misbehaves; park via a plain set. Fix the drive so ramp works (or the template/setup wraps it safely). Source: SRS_DC205. (Aliasing into the template is the `hera_template_dedup` subtask.)
- [ ] **Drop to E0 after a run completes? (design).** Aaron's open question — whether HERA should auto-revert to E0 when an autonomous run finishes rather than holding E1. Decide the policy.
- [ ] **Measure-nb close-out / shutdown function.** A reusable end-of-session function (+ a final measure-nb cell) that parks the rig quiescent: lower excitation, ground device contacts via `mux.park()` (managed lines only — preserve Si standing closures), gates/field to 0. The 2026-06-17 SHUTDOWN (`session_notes.md`; `hera_scratch/shutdown.py`) is the worked example. (Was the `hera_measure_closeout` /subtask — deferred for bandwidth.)
- [ ] **Switch the working branch to `master`; sweep `hera`-branch references.** The repo develops on a `hera` working branch. When it becomes/merges to `master`, review every reference to the `hera` branch and update it — `aaron-handoff.md`, `chiron.md` / `triage-workflow.md` ("land on hera"), `scripts/install.sh`, session-archiving docs, and any tooling that assumes the branch name.

## ContactMux: fail, don't ramp, on a live managed line

Surfaced 2026-06-18 (QSwitch transient readiness). The QSwitch manual requires switching at V=0/I=0; ContactMux soft-grounds its own managed lines but doesn't check the user's sources.

- [ ] **`ContactMux.select`/`park` should refuse (raise) when a managed line carries nonzero voltage — never auto-ramp.** Design TBD.

## QSwitch settle/transient: make it a recipe (was the VTI smoke-test doc)

Surfaced 2026-06-18. `hera/docs/vti/qswitch-smoke-test.md` (QSwitch bring-up + buffer-trace `settle_s` calibration) was deleted — a rig-specific procedure doc is the wrong home. Content is in git history; origin is Bingcheng's CF01B1 buffer-trace method (cells 41–46).

- [ ] **Write `recipes/measurements/switch-transient-characterization.md`** — the rig-agnostic buffer-trace settle/transient procedure (scoped in `campaign-readiness-qswitch-transient.md`). The recipe is the method's home; the device card carries per-cooldown bless status.

## QSwitch ethernet control needs a UDP driver (fw 2.0)

Surfaced 2026-06-18. QSwitch firmware 2.0 changed ethernet comms from **TCP/IP to UDP** (port 5025); VISA can't be used over LAN (USB/serial still VISA) — see `docs/manuals/qswitch/QSwitch_FW2.0_extended_release_notes.pdf`. Confirmed live: a raw UDP query to the VTI switch returns IDN/state. The VTI switch now has a **static IP `192.168.0.11`** (UDP:5025), set + verified 2026-06-18; USB (ASRL, per-cooldown — ASRL4 this cooldown) is the working control path today. `drivers.QSwitch` and the latest `qcodes_contrib_drivers` (0.25.0) are both `VisaInstrument` (VISA/TCP only, **no UDP**), so neither controls the switch over ethernet; the only UDP implementation is QDevil's standalone `qdac2-tools/src/qswitch.py` (`UdpConfig` + `socket.SOCK_DGRAM`).

- [ ] **Add a UDP transport to `drivers.QSwitch`** (preferred — keeps `ContactMux`, the device-card mux vocabulary, and recipes unchanged): port QDevil's `UdpConfig`/`SOCK_DGRAM` path so the driver takes an IP and speaks UDP, VISA still for USB. Alternative: adopt QDevil's `qswitch.py` wrapper and adapt `ContactMux` onto it. Own branch; nothing blocks today (USB works).
- [ ] **VTI rig card QSwitch block**: add the static ethernet IP + the "VISA=USB-only, LAN=UDP-driver" caveat. Do with the driver work.

## Session-brief template (`session_template.md`) prose pass

Surfaced 2026-06-18 (card-EXAMPLE cleanup). The campaign-layer template
escaped the prose pass that trimmed the rig/device EXAMPLEs; same fat.

- [ ] **Trim `hera/session_template.md`.** The "Cards" section re-enumerates
  each card's contents ("gate stack, hBN thicknesses…"; "magnet, thermometry,
  envelope…") — restating what it points to; cut to "read both before
  proposing." Drop the leftover `CC`-ism (line ~31, "since CC is rooted here")
  — the tactical prompt now says "Working directory". Tighten the verbose
  `hera-notify` field guidance (it restates the prompt). Also decide the
  naming/pedagogy: it's a blank fill-in form named `_template`, while the
  rig/device layers are filled-in `EXAMPLE.md` worked examples.

## Retire `trilayer-stacking-id.md` (deprecated)

Surfaced 2026-06-20. `recipes/investigations/trilayer-stacking-id.md` (the Datta
fan-crossing approach) is superseded by `trilayer-stacking-fs-count.md`
(FS-counting, the one live sessions use) and is now front-matter-marked
deprecated. It's still cross-referenced from live surfaces, so it can't be
deleted yet — re-home each reference, then remove the file.

- [ ] **Single-gated path** — `trilayer-stacking-fs-count.md:27` defers the
  single-gated (D ∝ n) case to id.md. Fold that into fs-count (or a dedicated
  note) so nothing live depends on the dead file.
- [ ] **Examples cross-ref** — `trilayer-stacking-fs-count.md:273` points at
  id.md's Examples for the QC0426 fan run-ids / D values.
- [ ] **STYLE.md cites** — `recipes/STYLE.md` references id.md for the step-5
  output contract (~line 91) and two burn-log entries (~186, ~220). Re-point
  step-5 to fs-count's output contract; the burn-log can keep the historical
  name but note the recipe is retired.
- [ ] **device-init cites** — `cnp-and-dline-calibration.md:169` and
  `reentry-baseline.md:99` reference id.md's channel-triage step; re-point to
  fs-count step 2.
- [ ] **Delete** `trilayer-stacking-id.md` once the above land.

## Shared/synced home for the fixture binary layer + replay run artifacts

Surfaced 2026-06-20 (SdH/fan replay A/B/C/D). `$HERA_DATA` (default
`/data/sharpelab/hera-data`) + `link-data.sh` already keep the fixture binary
layer (`data/`, `images/`, `runs/`, `*.ipynb`) out of git and the convention is
live (the b1c2 fixture's `data/` symlinks into it). **But `$HERA_DATA` is local**
(Zack's `/data` nvme), not shared/synced — so a collaborator on another machine
gets the git text layer (`frontiers/`, `ground_truth/`) but **not** the data or
the replay run outputs, and cannot reproduce a fixture or read a run's
`result.json`/`output.md`. These artifacts are large but **important and shared**
(benchmark inputs + experiment results).

- [ ] **Decide a shared/synced home for the fixture binary layer + replay runs.**
  Candidates: the titan/dgglab measurements tree (already the measurement-data
  sync target), a synced volume, or rclone/git-LFS over `$HERA_DATA`. Must let a
  collab pull a fixture's `data/` + a run's `result.json`/`output.md` on another
  machine. Pairs with `link-data.sh` (point its destination at the shared store)
  and the "Session archives don't belong in the repo" item above.

## nD-sweep preflight: validator-clip fraction is hand-rolled

Surfaced 2026-06-21 (zf1-run1 triage). Designing a rasterized (n,D) sweep, the
agent hand-rolled the same preflight twice (`hera_scratch/nd_design.py`,
`nd_design2.py`): `raster.rasterize` → `calculate_gate_voltages` with the
*device's* geometry → clip against the committed validators and report the
out-of-box fraction (`in-validator: X/Y, clipped Z%`). `sharpelab_nb` ships
`plot_raster_preview` (the path/figure) and `sanitize_tg_bg` (the clip), but
nothing reports the clip *fraction* against the committed validators — a
HERA/session concept neither lab-shared helper models.

- [ ] **(watch) Validator-aware nD-sweep preflight.** A hera helper (couples to
  committed validators → hera, not sharpelab_nb): rasterize → gate-convert
  (device dtg/dbg/ep) → report % of points outside the validators before
  committing the sweep. Watch: recurs whenever a rasterized nD-map is proposed;
  promote from watch if it fires again. Source: zf1-run1
  `hera_scratch/nd_design.py`.

## `cap-ratio-calibration` vs `cnp-and-dline-calibration` — decide and reconcile

Surfaced 2026-06-21 (zf1-run1 triage). The corpus references
`cap-ratio-calibration` in ~9 files as a calibration step, but no recipe by
that name exists; the implementing recipe is `cnp-and-dline-calibration.md`
(its output already refines the cap ratio from the CNP slope). Worse, the
references are inconsistent: some mean "the cap-ratio extraction
`cnp-and-dline-calibration` does today" (one such site fixed in
sc-characterization Step 1), while `cnp-and-dline-calibration.md` L157 calls
`cap-ratio-calibration` a *"still deferred"* **independent** recipe. So a
blind rename would clobber the intentional deferred-recipe references.

- [ ] **Decide (1) vs (2), then reconcile all sites.** (1) `cap-ratio-calibration`
  is a real planned recipe → keep the forward-refs but mark it deferred/unwritten
  somewhere central so it doesn't read as a broken link. (2) It's a loose alias for
  the extraction `cnp-and-dline-calibration` already does → standardize the
  remaining ~8 sites on `cnp-and-dline-calibration`, drop the "deferred" framing.
  Recipe-semantics call (Aaron's domain). Sites: `nD-map.md` (7), `landau-fan.md`
  (4), `gatemap.md` (2), `silicon-backgate-survey.md`, `cnp-and-dline-calibration.md`,
  `extending-the-corpus.md`, `campaign-readiness-2504.06972{,-workstream}.md`.

## 2026-06-20 zf1-run1 session — backlog

Tooling notes from the zf1-run1 wiki notes (8NbxR877nE), not corpus-worthy as
recipe/card edits.

- [ ] **No DC-bias-current instrument alias for `dc205_1`.** The DC current bias
  (dc205_1 through the 100 MΩ → ±150 nA) has no named alias to slot into the
  measure config, so the agent wires it ad hoc. Wants a template/config alias for
  the DC-current-source role. Source: zf1-run1. Related: the `dc205_volt` get/ramp
  + `hera_template_dedup` aliasing items above (different role: that's VTI TG-gate
  drive; this is toploader DC current bias).
- [ ] **Silence JupyterLab warnings in cell outputs.** JL/deprecation warnings
  land in the cell outputs the agent reads, burning tokens and adding noise. Filter
  them at the notebook/kernel level (warnings filter in a setup cell, or a JL config).
  Source: zf1-run1.
- [ ] **`snap` chokes on a trailing-minus number.** `ValueError: could not convert
  string to float: '154.764-'` — a sweep/`snap` read hit a trailing-sign number
  format it can't parse. Find the producer (instrument readout format) and make the
  parser tolerant (or normalize the string). Source: zf1-run1.
- [ ] **Session-note helper tool.** A small helper to append a timestamped entry to
  `session_notes.md` — enforce append-only, stamp the time for free. Tool candidate;
  the agent hand-appends today. Source: zf1-run1. (Pairs with the note-stream
  conventions Chiron consumes.)
- [ ] **Monitor + shutdown safety layer (incl. UPS).** UPS monitoring isn't wired
  on toploader ("ups shit is missing") — fold it into a broader **monitor +
  shutdown** concern rather than a standalone gauge: power-loss/UPS, the
  out-of-band gate-leakage/quench/heating watchdog, and the close-out/shutdown park
  share one "keep the rig safe unattended" machinery. Source: zf1-run1. Ties
  together the OOB E1 safety-monitor + measure-nb close-out/shutdown items above
  and the FastBi1K5 UPS/measurebot-integration note.

## (punt) Blinding leak: shared recipe Examples name the device under blind

Surfaced 2026-06-21 (zf1-run1 triage). zf1 is b1c2 under blind. The
`gate-current-sanity-check.md` failure-mode catalog cites the b1c2 cell-26
grounded-short **by name**, and the agent surfaced "the b1c2 precedent on this
rig" in its Gate C reasoning — connecting zf1→b1c2 and defeating the blind.
General mechanism: any agent-visible recipe Example (or crop) that names a
device leaks once that device is re-run under a blinded alias. Blinding
integrity is L3 (Aaron's call).

- [ ] **(punt) Decide blinding policy for named-device Examples.** Re-evaluate
  **before the next blinded campaign** (trigger): either scrub/alias device
  names in agent-visible recipe Examples + crops for devices that may be re-run
  blinded, or accept the leak as out-of-scope. Source: zf1-run1
  `gate-current-sanity-check.md` L172 (names b1c2); `hera_scratch/gateC_md.md`.

## Agent adherence: bypassed an available rule (instruction-following)

Surfaced 2026-06-22 (zf1 toploader session, T1 triage). An adherence gap
distinct from a corpus gap: the toploader rig card states the heater takes a
mandatory equilibration hold after every ≤1 V step ("5 min for a full 1 V
step", direction-agnostic). On warm-up the agent ramped 1→6 V with `sleep(60)`
and rationalized it as "slow delay correct only on the way down." The rule was
present, unambiguous, and at the right layer.

The `temperature-dependence.md` step-4 pointer (added this triage) addresses
the recipe framing that *invited* the misread, but the gap is not explained by
a missing instruction.

- [ ] **Review this instruction-following failure.** One-off, or a pattern of
  rules losing to recipe framing under token pressure? Decide whether it
  warrants a mechanism (e.g. surfacing the governing card rule for the recipe
  in play at preflight) or is acceptable as occasional. Source: 2026-06-22 zf1,
  T1.

## gate-current-sanity-check: finish the range-finding → validation rewrite

Surfaced 2026-06-22 (zf1 toploader, T4 triage). The recipe was redesigned from
a combined liveness + range-finding "iterate-then-bless" loop into a
**validation of already-known gate limits** (sweep `0 → known limit` per gate +
the dangerous corners, expect no leakage; liveness kept). Landed this pass:
`## What`, the `## When` preconditions, Cell A endpoint + iteration loop, and the
leakage failure-catalog row. Remaining:

- [ ] **In-file cleanups still reading as range-finding:** `## Why` (rewrite to
  the reaffirm framing; drop "set from observed safe range" + the ungrounded
  parenthetical); the geometry-ceiling line ("don't walk `|v_endpoint|`");
  failure-catalog row 3 action ("unground the device" — it's a contact short, not
  ungrounding); Cell B comment/intro ("established by Cell A iterations" /
  "confirmed safe range"); HERA handshake ("the discovered ranges"); `## Next`
  first bullet; `## Examples` (narrate the range-finding history — reshape or trim).
- [ ] **Cell A corners mechanism:** corner legs currently pin the non-swept gate
  by hand-editing the park ramp (guided by a comment). Decide whether a cleaner
  `park` field in the edit-block is worth it.
- [ ] **Re-point downstream** to send the *establishing*/blessing role to
  `gate-range-finding`: `gatemap.md`, `nD-map.md`, `silicon-backgate-survey.md`,
  `gate-range-finding.md`, `device-cards/EXAMPLE.md`, `gate-leakage-survey.md`,
  `session_template.md`.
- [ ] **Reconcile the two convergence backlog items** (gate-range-finding ↔
  sanity-check; fold-leakage-survey-into-range-finding) with this split — they
  proposed merging sanity-check *into* range-finding; this splits them the other
  way.

## Agent should account for survey resolving power up front

Surfaced 2026-06-22 (zf1 toploader, T5 triage). A coarse survey map is correct
— the issue is the agent treated its limited resolving power as an afterthought.
The run-2 survey stepped BG at 0.1 V (≈0.83×10¹¹ cm⁻²), coarser than the
predicted SC arc width (~0.5×10¹¹), so a narrow arc could thread between grid
points and be missed; the agent only flagged this late. Not a recipe/gatemap
edit (a coarse survey is intended) — it's a reasoning habit: when sizing a
survey, state up front what feature width it can and can't resolve, and what
could be missed.

- [ ] **Decide where to instill "account for resolving power up front."**
  Candidates: a working-style / prompt nudge (size a sweep against the feature
  you're hunting; state what it cannot resolve before running), or a
  survey-design checkpoint. Relates to the "HERA samples less fine than Aaron"
  tendency (noted same session, not yet logged separately).
- [ ] **(watch) Linecut coverage non-exhaustive (T6).** Run-3 linecuts found the
  candidate, but the D-spacing between "a few" cuts is unconstrained — a narrow
  arc can sit between them. Same habit, linecut axis. **Watch the next run**: if
  non-exhaustive linecuts miss the candidate, promote to a fix (exhaustive
  D-coverage as the default in `sc-characterization` Step 1).

## (watch) Agent carries prior bounds as point estimates

Surfaced 2026-06-22 (zf1 toploader, T9 triage). The `sc-characterization` Step 1
prior is a bound — `|D| ≳ 0.5 V/nm` — but the agent restated the candidate
region as `D ≈ −0.5 V/nm` (a point), dropping the "or beyond." The truth landed
at D ≈ −0.65 (consistent with the bound, not the point). Not a recipe gap (the
prior is stated correctly as `≳`); an agent-faithfulness habit, adjacent to the
over-specificity / blinding theme.

- [ ] **(watch) Carry prior inequalities faithfully** — don't collapse a `≳`/`≲`
  bound into a `≈` point estimate. Watch for recurrence; promote to a
  prompt/working-style nudge if it repeats. Source: 2026-06-22 zf1, T9.

## 2026-06-23 zf1 toploader triage (chiron)

From the zf1 SC session (session_notes + wiki support log + POSTMORTEM). Items
not landed this crank, with triggers.

- [ ] **Generate measure templates from rig/device/brief cards** (full form of
  the device-card→slot autofill R5 `hera_template_dedup` left as a hera-session
  TODO). Two failure classes drive it: (a) slot-fill placeholders ship stale —
  zf1 init shipped `B_SESSION_CAP = 5.0 T` against a brief cap of **0.1 T**
  (safety-adjacent) and ana geometry `t_tg=15.6e-9, t_bg=12e-9` (QC0426's) vs
  the zf1 card's 23.6/20 nm, both caught by Aaron at init — the kit must not
  ship a brief-violating B-cap; (b) the base templates hardcode the instrument
  roster outside the slot system entirely (lock-in lists, Keithley roles, the
  State-capture cell's param list — grown again by the 2026-07-19 close-out
  work), all of it really rig-card + device-card data. Generate the notebook
  from the card layers at session creation instead of hand-maintained
  carry-forward cells. **Unpunt-if:** any slot ships mismatched again /
  hera-session slot work / the next template surface addition.
  Source: 2026-06-23 zf1, W1; 2026-07-19 measure-closeout subtask.
- [ ] **Heater ramp helper** — a simple "ramp T from A→B with a progress print"
  function (open-loop heater drive; the operator hand-rolled settle ladders all
  session). **Unpunt-if:** next heating campaign / cleanup. Source: W9.
- [x] **Interruptible sleeps for instrument-bound loops** (safety) — `nb-collab
  interrupt` did **not** stop the Tc ladder (runs 26, 27 completed after the
  interrupt). Resolved 2026-07: root cause was `_interruptible` swallowing the
  caught SIGINT after a graceful sweep wind-down (the zf1 cell built a fresh
  AsyncStation per rung, so the per-station raise-on-reuse guard never fired);
  `sweep`/measureme sweeps re-raise as KeyboardInterrupt after the writer
  closes, and UPS graceful shutdown propagates as InterruptedError after
  parking — an enclosing cell loop dies instead of starting the next sweep.
  Source: W12, session_notes.
- [ ] **Thermometry both-probe auto-select + staleness detector** — the cheap
  mtime guard landed (measure template cell 11 + rig card); the deeper fix needs
  both probe logfiles in `TOPLOADER.temp_logfiles` so bring-up can read both and
  auto-select the advancing one, plus a "T identical to N decimals across N runs"
  flag. **Unpunt-if:** thermometry work / cleanup. Source: W10, session_notes
  (root cause of the stale-T abort).
- [ ] **hera-watch: surface fp gate-current channels** — the digest shows only
  the mc lock-in channels (sr1/2/3), not the fp'd `k_*_curr` columns, so the
  leakage half of a gatemap/liveness run is invisible (had to open_run the TSV).
  Add max|I| per row when gate-current channels are present. **Unpunt-if:** next
  gatemap/liveness session / cleanup. Source: session_notes TOOLING.
- [ ] **(watch) Don't inset committed validators** — agent inset the gatemap
  0.2 V inside the device-card validators out of ad-hoc leakage caution; Aaron
  overrode (the committed validators ARE the known-safe envelope; range-finding
  was blocklisted precisely because it's established). One incident → watch for
  recurrence before a STYLE/prompt rule. Source: 2026-06-23 zf1 FEEDBACK, W3.
- [ ] **`newclaude` Windows tactical-spawn left no transcript** (data-loss) — a
  ~16 h tactical session wrote no `.jsonl` anywhere on the rig (whole-disk
  verified; `.claude.json` cwd showed `history=0`). Triage worked from notes
  only. Add a post-launch check that the spawned tactical session actually wrote
  a transcript before the operator commits to it. **Unpunt-if:** any session
  again leaves no transcript. Source: POSTMORTEM.
- [ ] **(cleanup) `sc-characterization.md` over budget** — 253 lines (~250
  budget) after this crank's Step 2/3 strengthening. Compress at next cleanup
  pass. **Unpunt-if:** cleanup mode. Source: 2026-06-23 growth control.
- [ ] **Snapshot non-followed but relevant values at run start (T, Si)** —
  sweep's `_init_metadata` snapshots only followed instruments, so `meas_config`
  carries cell-run-time reads for `sample_temperature:` (logfile, no instrument)
  and `Si (V)` (dc205, when parked/not followed) — stale if the cell isn't
  re-run after a change (×125 R bug was this class, via frozen `bias_voltage`).
  Add a run-start hook (cf. `run_afters`) or an always-snapshot list so these
  are captured JIT like followed instruments. Same gap, correct-direction
  example: `bias_channel` resolves I_bias from the drive lock-in's snapshot,
  so a run that doesn't follow sr1 gets an *absent* I_bias (fallback:
  `hera-watch --bias`) rather than a stale one — an always-snapshot list would
  close that hole too. **Unpunt-if:** measureme/sweep work, or a stale-Si/T
  value corrupts an analysis. Source: 2026-07-14 QC0426 session_notes TOOLING.

## Branded launcher exe for the rig GUIs (tray identity)

Surfaced 2026-07-15 during the pink deployment. The Qt launchers run under the
venv's python, so Windows attributes their tray icon to "Python" in the
notification-area settings. `SetCurrentProcessExplicitAppUserModelID`
(landed in `gui/qt/base_launcher.py`) may fix the label on newer Windows
builds — check the pink result before investing further. The console-window
half of the problem is handled in-process: `base_launcher.run()` hides its
own freshly-allocated console (uv's venv `pythonw.exe` is a console-subsystem
shim — astral-sh/uv#19226 — and a `wscript` wrapper got eaten by CrowdStrike
on the Stanford-managed pink PC; shortcut targets the console `python.exe`,
Run: Minimized).

- [ ] **If AUMID doesn't rebrand the tray label**: build a PyInstaller
  "frankenstub" per rig — a minimal `console=False` exe (built on the rig
  with the venv's own interpreter via `uvx pyinstaller`, version-file
  FileDescription "measurement-env-<rig>", `assets/measurement-env.ico`)
  that points `sys.path` at the live venv + repo and calls the launcher's
  `main()` in-process, so the branded process owns the tray icon while the
  code stays git-pull fresh. Prior art for the packaging: zeeref's
  `ZeeRef.spec` / `installer.iss`. Half-day of Qt-plugin-path fiddling —
  and test against CrowdStrike early: unsigned PyInstaller onefile exes are
  classic EDR bait, so onedir + local build may be required. Retire when
  astral-sh/uv#19226 is fixed.

## VTI 20260714.2 session sharp edges

Surfaced 2026-07-14/15 (QC0426 VTI session). Workarounds exist for all four;
none blocking.

- [x] **`hera.analysis.sdh_onset` nans on narrow records and multi-tone flips.**
  Resolved 2026-07-18 by rewrite (subtask sdh_onset_fix): root cause was the
  unpadded per-window FFT (5.6 T bins → empty or leakage-filled SNR noise bands
  for tones ≲30 T: nan, or SNR≈10¹⁵ and the record edge returned as "onset"),
  compounded by the argmax-median consensus failing on multi-tone records and
  per-dominant-tone semantics (capstone run 6: heavy tone's edge returned while
  light-tone content ran from ~1.5 T). Now nested-scan tone ID + per-tone
  Gaussian matched filter with an analytic noise floor; `onset_b` = min over
  robust tones; raises `SdhOnsetError` instead of nan; censored / marginal /
  near-residual disclosure via `summary()`; `r_full_scale` soft-clip truncation
  (the 2026-07-17 unflagged-clip note, same module). Pinned by
  `tests/hera/test_sdh_onset_archives.py` against all three archives and
  accepted via `hera-replay` on frontiers at both burnt decisions
  (`hera/test-cases/2026-07-{16,17}-QC0426-sdh-onset-replay/`).

- [x] **`hera-watch` 2D digest labels the megasweep slow axis `None`**
  (`row 0/61 None=-3`). Resolved: `build_model` reads the singular
  `slow_param`/`fast_param` megasweep keys alongside the plural
  multimegasweep ones; a missing name omits the label instead of printing
  `None=`.

- [x] **`run.col()` raises on duplicate columns when the swept param is also
  fp'd** (e.g. `k_2400_tg_volt` at indices [1, 3]). Resolved: `col()` returns
  the first occurrence (the planned/setpoint instance, matching
  `summarize_run`/`FanGrids.grid`) with a warning naming the indices;
  `col_at` still selects the readback. The `col_indices`/`col_at` idiom is
  gone from the recipe Verify blocks.

- [x] **Mid-run reads are positional-only** — resolved: `open_run` maps
  names from `metadata.json` (on disk from sweep start), tolerates the
  in-flight TSV's partially-written trailing row and the zero-row window,
  and `Run.complete` / `summarize_run`'s "in flight" status distinguish a
  live run from a truncated one. No TSV header added.

## Corpus own-error-rate: mechanism claims need verification tiering

Surfaced 2026-07-16 (capstone-prep triage). The 20260714.2 session notes
carried a confident wrong mechanism ("2D per-point cheaper — row-batched
readback"); triage nearly enshrined it on the rig card. The *phenomenon*
was measured; the *mechanism* was invented; the two traveled as one fact,
and operator skepticism was the only backstop. A 3-minute dt-decomposition
of the archived TSVs settled it (Keithley NPLC, not batching).

- [ ] **Tag mechanism vs phenomenon** in note-stream conventions + STYLE:
  measured phenomenology and inferred mechanism get distinct markers; a
  mechanism without a verifying artifact is a fork to report, not a fact.
- [ ] **Chiron: re-derive mechanisms from archived data when cheap** before
  landing them on cards — make the dt-decomposition-style check a standard
  triage step. Homes: `chiron.md` triage procedure + `hera/CLAUDE.md`.

## Triage crank friction: make the full crank always-runnable

Surfaced 2026-07-16 (Zack). Anti-accretion machinery exists (file budgets,
cleanup steps) but the full crank often isn't run: it's slow, and a rerun
targeted at one fix area forces wading through everything else that
surfaces. Accretion wins by default whenever the crank is skipped.

- [ ] **Targeted crank mode**: scope a rerun to a named fix area without
  surfacing the full queue; keep the full crank for scheduled passes.
  Goal: zero remaining reasons to skip the crank.

## Recipe-form compliance experiment (giga-paragraph vs checklist)

Surfaced 2026-07-16. landau-fan step 1 as dense prose gets better step
compliance than a checklist rewrite (prior hera-replay experiment: Opus
skipped steps in list form) — but the prose also carries an output
contract ("state the computed N_B, N_n, wall-clock"), so form and
contract are confounded. Hypothesis: required emissions carry the
compliance (skipping becomes visible), not prose density; bullets read
as menus.

- [ ] **hera-replay A/B across forms, same content**: (a) the
  giga-paragraph as-is, (b) bulleted checklist, (c) checklist with a
  per-step output contract — each step must emit its computed artifact,
  (d) numbered steps (ordinals imply sequence and completeness), ±
  contract. Score step compliance per arm across several fixtures for
  power. If (c)/(d) match (a), rewrite the giga-paragraphs
  human-readable with contracts — resolves the growth-vs-compliance
  tension.

## Synthetic / simulated device backend (benchmark bed + in-run tool)

Surfaced 2026-07-16 (benchmark discussion; extends Zack's prior thinking).
Two candidate backends for full-campaign runs without rig time: (a) a
**scan bank** — very-high-resolution scans of a real device, future runs
simulated by resampling; (b) a **physics simulator** (the forward models
generalized) serving a fictional device with ground truth by construction
(stacking, masses, onset chosen at build time). Either enables repeatable
end-to-end campaigns per model — statistics instead of anecdotes — and a
bed for protocol/safety probes (planted consent-gated situations,
blocklist temptations, blinding leaks; measure uptake). Prior art:
`models/trilayer_fs_count/`, the fan-vision-synthetics work.

- [ ] **Pick/sequence the backends**; a DummyInstrument-style rig serving
  either behind the normal sweep call surface.
- [ ] **Simulator as a HERA tool** (Zack): beyond benchmarking, the
  simulator joins the in-run toolbox — fit a hypothesis, generate
  predictions, compare against the next sweep.

## VTI 20260716 session-3 deferred items

Surfaced 2026-07-16/17 (QC0426 VTI session-3, stale-brief stacking
rehearsal; pre-freeze review 2026-07-17). Ruled backlog — none blocking
the capstone rerun.

- [x] **`landau-fan` step-1 dynamic-range rule: the MR anchor is
  n-dependent.** Resolved 2026-07-18: the dynamic-range check is now
  headroom-first (saturation is the asymmetric failure) and anchors on
  the low-n MR factor.
- [x] **Investigation overlay bullet: conduction-band-only domain.** Resolved
  2026-07-18 the other way: the model fix (edbd476 — valence band, extended
  grids, loud out-of-domain) retired the domain limit itself; the 3.5e12/e-only
  quotes were deleted from landau-fan step 1, the investigation Verify, and the
  brief + kit template instead of adding a clause.
- [x] **VTI rig card T_e reconcile** — moved to
  `hera/docs/vti/vti-rig-backlog.md` (rig work for Bingcheng, with the
  6.1 K derivation; card untouched for now).

## Replay regression-test ladder (corpus CI)

Surfaced 2026-07-18 (fs-count quote-deletion replay, report
`hera/docs/notes/2026-07-18-fs-count-quote-deletion-replay.md`). The
experiment supplies seed patterns for a standing corpus regression bed,
cheapest first:

- [ ] **Corpus lint**: grep agent-visible surfaces at commit time for
  tool-limit-shaped text (numeric validity quotes, model-domain numbers) —
  the paper-over class, mechanically.
- [ ] **Decision probes**: cheap single-frontier replays (brief-served,
  production model) pinned to burnt decisions — density, side, n_max —
  run per crank against the current corpus.
- [ ] **Sensitivity-paired fixtures / sim-device sessions**: the heavier
  rungs; pairs with the existing "Synthetic / simulated device backend"
  item above.
