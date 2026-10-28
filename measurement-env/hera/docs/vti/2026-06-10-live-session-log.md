# VTI live session log — QC0426 / hera-vti / 2026-06-10

Operator-side log of the first live HERA session on the VTI. Kept by the
support session (Zack's running commentary + infra observations) for
post-session review. The agent's own `session_notes.md` lives in the
measurement dir on dgg-vti; merge both when archiving.

Setup recap: dgg-vti, JL 8899 (`--collaborative`, measurement-env env),
session dir `~/VTI_local_data/zack/20260610-QC0426-hera-live/`, agent
`hera-vti` on `claude-fable-5[1m]` *(launched via bare `claude --agent
hera-vti "$(cat ./hera_session.md)"` — `--model` omitted; default model,
NOT explicitly pinned to fable[1m] — verify which model actually ran when
scoring)*. Operator: Qingrui at the rig. Zack supervising via RustDesk +
SSH. Preflight: RTC verified, nb-collab probe landed (cell id 5d5267f8).

Pre-session infra incidents (before agent launch, for completeness):

- **TOOLING — double JL launch wedged the collab layer.** Two server
  instances contended for `.jupyter_ystore.db` (WinError 32 lock on
  rotate), collab extension crashed, all 3 notebook kernels died in a
  restart loop, browser tab hung loading. Fix: taskkill the whole tree
  (NB: from Git Bash must use `powershell -c "taskkill ..."` — bare
  `taskkill /PID` gets MSYS path-mangled and silently no-ops), rm stale
  ystore, single relaunch. Runbook should warn against double launch and
  include the PowerShell form.
- **TOOLING — stale jpserver runtime files break nb-collab discovery.**
  Auto-discovery matched a dead 8889 server (stale runtime file, PID
  presumably recycled) → ConnectionRefused. Also: `--server-url` without
  `--token` is silently ignored (`if server_url and token:`), and a
  token-less server can never satisfy the override since token `""` is
  falsy. Fix applied: deleted all stale `jpserver-*.json` except the live
  one. nb-collab fix candidates: warn when --server-url given without
  --token; allow --token ''; probe candidate servers before resolving.

---

## Running log

- **18:0x TOOLING — `nb summary` has no execution counts.** Gate A/B
  verification per `hera_vti.md` says "nb summary shows execution
  counts" — it doesn't (confirmed in `src/tools/nb.py`); the agent had
  to dive into the notebook JSON to check whether setup/SAFETIES cells
  had run. Two fix candidates: (a) add exec-count column to `nb summary`
  (nb feature), (b) amend `hera_vti.md` gate A/B detection text to match
  reality. Note the toploader `hera_tactical.md` has the same claim
  ("nb summary shows zero outputs across setup cells") — check whether
  that one is also wrong.

- **FEEDBACK — operator pre-flight review of the measure nb.** Qingrui +
  Zack walked the deployed measure notebook cell by cell before running;
  Qingrui adjusted a couple of cells (capture the diff from the notebook
  later — it's the operator-trust signal for the template). He asked what
  HERA will actually do — specifically whether it will run the B-n maps
  at different fixed D. (The D-series fan plan is exactly the campaign
  shape; an operator independently anticipating the agent's arc before
  the agent states it is a good sign for plan legibility — check later
  whether HERA's stated arc matched his expectation.)

- **PROTOCOL — operator handoff mid-session.** Qingrui away ~30 min
  (possibly Aaron subbing in); Zack has permission to run, operating
  remotely via RustDesk. For this window the "hands at the rig" property
  of the operator contract is suspended — cheap cells (gate sweeps,
  density cuts; minutes, zero field) are low-risk, but a fan start
  commits a multi-hour magnet ramp with nobody physically present.
  Flagged to Zack at the time.

- **TOOLING — operator can't see cell indices in JL.** HERA cites cells
  by 0-based index (nb convention); JupyterLab displays no indices, so
  the operator can't locate "cell 18" without counting. Workaround used:
  `nb summary <nb>` in a JL terminal as the index↔content map. Fix
  candidates: (a) prompt amendment — cite indices with a content anchor
  ("cell 18 — the SAFETIES cell"), zero-cost, do this; (b) a JL
  cell-index extension or nb affordance later.

- **FEEDBACK — Zack: ana should probably be `edit_exec`.** Live take
  during baselines: ana's `edit_no_exec` policy makes the operator run
  pure-analysis cells (no hardware) that HERA promoted — friction with
  no safety payoff, since scratch is already exec and ana is not the
  hardware surface. Design-change candidate for the policy table
  (hera_vti.md + iris.md + launcher stamping). Flippable live by editing
  `nb.metadata.hera.policy` if wanted mid-session.

- **STATUS — gate-C baselines running** (quick checks, zero field;
  Zack operating during Qingrui's absence).

- **FEEDBACK — Qingrui (returned), via chat doc: Si optimization wanted.**
  "Usually at least we would like to try a few Si gate and find the
  optimal one. So we want some negative Si gate, so I would do at least
  −50 V as the safety." Two consequences: (1) `[VERIFY: k_2410 range]`
  resolved → validator widened to **[−50, +100] V** — synced to deployed
  + repo device card; operator to edit SAFETIES cell (SI_MIN → −50.0)
  and re-run; (2) campaign-shape input — an Si-optimization leg before
  or alongside the fan series; HERA should fold it into the arc.
  Full chat doc to be attached post-session.

- **TOOLING — agent prefixes `PYTHONIOENCODING=utf8` on every command.**
  HERA discovered Windows console encoding mangles unicode in python
  output and is paying a per-command workaround tax. Fix candidate: make
  it ambient — `export PYTHONIOENCODING=utf-8` in DGG's `~/.bashrc` (or
  setx machine-wide), and/or note in hera_vti.md's environment section.
  RESOLVED live: added to `~/.bashrc` on dgg-vti (new shells only).

- **INCIDENT — ana notebook kernel dies on boot; UNRESOLVED, deferred.**
  Symptom: ana cells do nothing; webui "kernel: connecting"; server log
  shows 4+ kernels dying with "restart failed" (16:45→17:04), each dying
  during boot (never reaches idle), incl. fresh REST-created sessions.
  Measure kernel (booted earlier) healthy throughout and running sweeps.
  Findings: (1) env churn — site-packages mutated 16:17/16:27, right
  before deaths began; `tools/nb` and `tools/nb-collab` shims run
  `uv run --project` WITHOUT `--no-sync`, so every agent nb/nb-collab
  call can re-sync the env; patched both shims on the rig (+ final
  `uv sync` to settle; repo copies need the same patch — land later).
  (2) BUT a fresh kernel still died post-patch, and a manual
  `ipykernel_launcher` boot from the session dir runs clean (no .py
  shadowing in cwd) — so churn isn't the whole story; root cause open.
  Zack's call (17:1x): STOP debugging — protecting the live run beats
  fixing ana. Workaround: HERA analyzes via local python + hera_scratch/
  files, appends un-executed record cells to ana. Revisit post-session
  (also explains why scratch-nb execution may be unavailable — same
  kernel-boot path; agent's edit_exec on scratch is moot until fixed).

- **TOOLING — agent analyzes via `uv run --no-project --with numpy`,
  not the measurement env.** Provenance: committed agent-memory
  (`subtask_agent/MEMORY.md:37`) recommends the pattern for dev-machine
  worktrees; it leaked to the rig context via the repo. Accidental
  upside: no project sync → no env churn (see kernel incident). Cost: no
  `sweep`/`hera.analysis` loaders → hand-rolled TSV/metadata parsing,
  against the prompt's own warnings. Relay sent: use
  `uv run --no-sync --project ~/measurement_env python`. Post-session:
  bake `--no-sync` into hera_vti.md, land shim patches, scope the memory
  note to dev machines.

- **FEEDBACK/DESIGN — fridge utilization is the missing metric (Zack).**
  HERA serializes: sweep → read docs → analyze → decide → land next cell,
  leaving the fridge idle between runs. Measured live at first three
  runs: **42% utilization** (14/34 min), gaps 3.7 + 5.6 min, then a
  10+ min idle stretch while it read docs. Relay sent: overlap thinking
  with sweeps; land contingent next-cells with go/no-go conditions in
  the markdown; read during sweeps, not during idle. Post-session items:
  (a) `hera-utilization` tool (timeline + gaps + score from
  `data/*/metadata.json`) — easy and correct beats each agent
  hand-rolling it; (b) hera_vti.md working-style amendment ("price idle
  time; keep a cell queued"); (c) consider surfacing the score in the
  session-notes protocol so it's tracked per session.
  Positive observation alongside: run metadata discipline is excellent —
  recipe slugs (`gate-current-sanity-check`, `trilayer-stacking-id`) +
  fully structured comments on every run.

  **Metric refinement (Zack, follow-up):** attribute idle time. Time
  with a runnable agent cell landed-and-waiting (operator running other
  cells, reviewing, or away) counts AS utilized from the agent's side —
  the agent-attributable idle is only: fridge not measuring AND no
  un-executed agent proposal pending. Score ≈ agent-idle / session-span,
  separate from raw fridge utilization (both useful: raw = ops metric,
  attributed = agent metric). Instrumentation needed to compute it:
  (a) `nb-collab append` should stamp `metadata.hera.appended_at` on
  cells (one-line tool change); (b) cell execution timestamps — enable
  JL's execution-timing recording (`recordTiming`) in the deployed
  settings so run-vs-land latency is reconstructable. Build after the
  session.

- **MILESTONE — first Landau-fan proposal landed (est. 1 h 40 m);
  Qingrui tagged in to review/run.** Gates + baselines behind it; the
  wall-clock estimate in the proposal = the "price everything" style
  rule working. Supervisor check at the time: confirm the estimate
  includes the initial magnet ramp (0→start-field at ~0.137 T/min ≈ up
  to ~1 h if starting from 0 to 8 T) — if not, true commitment is ~2.5 h.

- **MILESTONE detail — HERA's fan handoff message (verbatim highlights),
  scoring notes:**
  - "Both watchers are running in the background — one confirms the fan
    starts writing (run 3), the other blocks on the cell itself." →
    within-turn background watchers (data-dir + `nb-collab wait`);
    resourceful, consistent with the no-autonomous-polling rule
    (in-turn, not scheduled).
  - Staged mid-fan plan: ~20–25 min (≈8 B-rows) partial re-form from TSV
    → abandon/continue call; mid-fan model-chain overlay (sr1/sr2 + sr3
    as Rxy, "single global density rescale allowed"); post-fan Verify
    (decimation, B-row subsetting, superposed-fan alternative, lever-arm
    quantization). → the brief's decision points, made concrete, with
    the forward model in primary position.
  - "fan cell is idx 37, ~1 h 40 m estimate (possibly ~2 h 25 m if the
    ramp is slower than the prior campaign's row overhead suggests; the
    first rows will tell us which)" → bracketed estimate with a stated
    self-calibration plan. And the fan runs 0→8 T from where the magnet
    sits — **no initial ramp at all; ramp amortized into the slow axis**
    — "ends with the magnet at 8 T, which is fine for a follow-up
    densified fan coming back down." Textbook never-re-traverse +
    next-move field planning. Supervisor's ramp concern: answered
    pre-emptively.
  - Operator-addressed close ("Qingrui — … Run it when ready."). Minor
    nit: cites "idx 37" without a content anchor (see earlier TOOLING
    entry on cell indices).

- **POST-SESSION plan (Zack):** pull the full measurement dir + session
  log with the existing archive script (`hera-archive`) and review.
  NB: hera-archive is toploader-pathed (`<user>/<device>_toploader`,
  ssh target toploader) — check/adapt for dgg-vti +
  `VTI_local_data/zack/20260610-QC0426-hera-live` before relying on it.

- **FEEDBACK (positive, Zack) — mid-run check-in behavior is the win.**
  Happy with HERA planning the ~20–25 min early-analysis checkpoint on
  the 1.5–2.5 h fan, with an explicit adjust/abandon path if the early
  rows are washed out. This is the highest-value form of the mid-fan
  decision point: at 1.2 K wash-out was the reference campaign's known
  failure mode, so an early call saves hours of fridge time. Design
  validation for incremental-row disk reads + the priced abandon/continue
  fork; carry this pattern into the recipe/prompt as a norm for any
  sweep > ~30 min.

- **STATUS — first mid-fan checkpoint underway** (~the planned 20–25 min
  mark). Standard-looking inspection ops: partial TSV re-form, row
  counts, etc.

- **REVIEW ITEM — helper extraction pass over the agent transcript.**
  During the archive review, mine HERA's Bash/python one-liners for
  recurring operations worth promoting into documented helpers
  (`hera.analysis` additions or small CLIs): candidates expected —
  partial-fan re-form from a live TSV (row-windowed Rxx(n,B) matrix),
  "how many B-rows landed" progress probe, utilization calc, exec-count
  check via notebook JSON (the `nb summary` gap), model-chain overlay
  plotting. Each hand-rolled-twice operation is a tool candidate; each
  tool removes a class of convention mistakes (gain division, schema
  keys) by construction.

- **DESIGN IDEA (Zack) — live data digest for agent monitoring.**
  A tool that watches an in-progress run dir and digests incoming data
  to stdout — e.g. `hera-watch data/3`: one line per landed B-row (row
  idx, B, n-window, per-channel Rxx stats with gain applied, rows/min,
  ETA) — so HERA can attach a Claude Code background monitor to it
  instead of hand-rolling watcher loops. Evidence of need: HERA built
  two ad-hoc watchers for the fan unprompted. Adoption test: build it,
  document it in the prompt's tools section, and see whether the agent
  *actually reaches for it* next session vs rolling its own — usage
  decides whether it stays. (Digest-to-stdout also keeps token cost
  flat: agent reads summaries, not TSV rows.)

- **DESIGN IDEA (Zack) — Slack integration for operator notification.**
  HERA should be able to ping the operator (checkpoint verdicts, "cell
  landed, run when ready", sweep done, anomaly flags) instead of relying
  on them watching the terminal/notebook — directly serves the
  utilization metric by cutting operator-latency on handoffs. Natural
  shape: a small `hera-notify` CLI (channel/DM + message) the agent can
  call, with house rules in the prompt (notify on: proposal landed +
  idle rig, checkpoint verdicts, run completion, anomalies; never spam).
  measurebot already does alerts — check whether its Slack plumbing is
  reusable before building new. Per agent-memory: test pings go to
  Zack's IDs only, never Aaron's.

- **CHECK (Zack asked) — forward-model usage + n-coverage, from synced
  data (runs 0–4, via sync-measurements.sh/titan):**
  - Model: USED, directly (`fan_partial.py` imports `ll_spectrum.SWMcC`
    + `crossing_model.ml_trajectories`; chain overlay raw +
    background-divided), and decisively — session_notes records the
    model *rejecting* the chain interpretation of run 3's second ray
    family ("in-window chains would need rescale ~2") after the family
    survived decimation + B-subsetting. First live validation of the
    landau-fan Verify flow (its own RECIPE FIX entry says no changes
    needed).
  - n-coverage: confirmed narrow — run-3 fan n −0.4→+4.0e12 (121 pts) vs
    reference fans' ~6× wider gate range; priced trade (full width ≈
    10+ h vs 1 h 40 m). Review: was the window rationale stated in the
    proposal cell? Hole side (~unsampled) — physics question for the
    brief agent on e–h asymmetry in the fingerprint.
  - Run 4 = promised densify fan, 8→6 T come-down (n 0.3–3.2e12,
    201 pts) — never-re-traverse held across moves.
  - From HERA's session_notes: (a) `nb cells` UnicodeEncodeError on
    cp1252 console = root cause of the PYTHONIOENCODING habit — fix in
    nb.py (force UTF-8 stdout on Windows); (b) ANOTHER template leak,
    same class as Si=+50: stale meas_config `comments` ("B-n sweep at
    D=+0.5 … source current on 33") from prior campaign/stripped
    proposal — it overrode per-run and flagged the drain-contact
    conflict; (c) missing re-entry-baseline recipe slug — it improvised
    tags under existing slugs.

- **SESSION NOTE (Zack) — permissions change for HERA, probably bypass
  by default; small discussion wanted.** Tension: permission prompts tax
  the operator and the utilization metric, and they're rubber-stamps for
  the read/analyze surface (click-through training = alarm fatigue). But
  the operator watches the *notebook*, not HERA's terminal — so the CC
  permission layer is effectively the only gate on non-notebook actions
  (shell on a shared lab PC: other users' data under VTI_local_data,
  taskkill, ssh, git). Options: (a) full bypass + strengthened
  shared-PC blast-radius section in the prompt; (b) mined allowlist
  (today's transcript via /fewer-permission-prompts) auto-allowing the
  analysis surface, prompts retained for destructive/network/system
  classes; (c) bypass + an OS-level sandbox/user account later. Support
  session lean: (b) first, escalate to (a) if prompts remain frequent.

- **DESIGN (Zack) — introduce fridge/cryostat cards alongside device
  cards.** Rig-level facts get their own card (per fridge: VTI,
  toploader, pink…): magnet driver + ramp/limits/blocking semantics,
  thermometry + heater, **safe temp/B envelope** (e.g. max sample T for
  temp sweeps, T-at-field limits, He consumption/hold time), sweep API
  stack, instrument inventory, known quirks. Structural consequence:
  hera_vti.md's "VTI rig conventions"/magnet-discipline section
  migrates into the VTI card → the agent prompt becomes
  fridge-agnostic (protocol only), and the layer model completes:
  prompt = protocol, rig card = machine, device card = sample,
  brief = campaign, recipes = method. Gate B grows a rig-envelope leg
  (T/B limits validated like gate validators — today temperature has NO
  home in any safety check). Proposed location:
  `hera/rig-cards/{EXAMPLE,VTI,toploader}.md`, deployed next to
  device_card.md in the measurement dir.

- **SPAWN — `qswitch-prefan-recipes` subtask (fable, base hera@069a5e6).**
  Scope: encode the pre-fan campaign stage as recipes (contact
  characterization/optimization, CNP finding, gate range-finding VTI
  variant if needed, `reentry-baseline`) + QSwitch driver integration
  for automated contact switching (evaluate vendored
  `vti_drivers/QSwitch.py` vs qcodes-contrib QDevil). Outputs: recipes +
  driver; proposes plan to Zack before writing. Invariant set: contact
  truth stays in `measurement_config`/metadata when switching is
  automated.

- **MILESTONE (from the paper-reading subtask) — the session-notes
  feedback loop closed; on the record.** The live session's
  `session_notes.md` (11 tagged entries: RECIPE FIX / PROTOCOL /
  TOOLING) fed corpus amendments that landed on `hera` within ~24 h of
  being written by the agent mid-session:
  - `a8275ab` — presence-vs-pattern restatement of the finite-D crossing
    caveat (**the rule that misled HERA live**), series-path/mosaic
    caveat on CNP-vs-D, and creation of `hera/recipes/STYLE.md`
    (epistemics style guide for agent-executed recipes, with a burn
    log; this incident is entry #1).
  - `069a5e6` — recipe-vs-STYLE review fixes: ambiguous-CNP middle
    branch, N_M=0 vertical-series conditioning + confounds,
    strength-scale verdicts.
  - `f14db9a` — from the aliased run-3 fan (notes entries on wrong
    row-overhead and B-resolution): both-axes design-time Nyquist guard
    + full fan cost model in `landau-fan.md`, STYLE rules 11
    (rig/device-agnostic recipes) and 12 (design-time guards; calibrate
    constants, don't inherit), burn-log #2.

  Loop mechanism: agent writes tagged session notes → post-session
  triage → recipe/STYLE amendments citing the session.

  **Open question (Zack) — how to strengthen the loop.** Candidate
  shape: a standing post-session triage step giving every tagged entry
  an explicit disposition (recipe-fix / STYLE / eng-backlog / wontfix),
  latency tracking (note → landed amendment; derivable from note
  timestamps vs git dates), and HERA proposing the recipe diff itself
  in-session as a session_notes attachment. Support-session view: the
  `session-notes-resolution` subtask spawned tonight IS the triage
  prototype — its required resolution table (item → ruling → change) is
  the disposition record; if it works, formalize it as a standing step
  in `hera/docs/session-archiving.md` (triage before archive closes).
  In-session diff proposals are cheap to allow and keep the human gate:
  RECIPE FIX entries may carry a proposed diff; triage applies, edits,
  or rejects — never auto-applied.

- **STATUS — campaign endgame: temp sweep being finalized with Qingrui.**
  The session's last measurement will be a temperature sweep. Note the
  live irony for the rig-card design entry above: **no artifact today
  encodes the VTI's safe T/B envelope** — whatever max-T / B-at-T
  constraints Qingrui states in this discussion are exactly the future
  `hera/rig-cards/VTI.md` content; capture them from the chat doc rather
  than letting them evaporate.

- **STATUS/MILESTONE — HERA's pre-temp-sweep rig questions** (to
  Qingrui, before landing cells): (1) T-control ownership — Lakeshore
  heater loop vs manual vaporizer/needle valve; offers a ±50 mK
  settle-and-verify block but "don't want to fight your control loop";
  (2) He economics at 25 K, with a priced fallback ("cap the ladder at
  ~15 K, still discriminating, ratio 1.9"); (3) thermometry offset
  Lakeshore-vs-sample, "LK fits inherit T errors linearly." All three
  are rig-card content the corpus doesn't hold — the agent independently
  hitting the same gap as the rig-card design entry. Spawned
  `vti-doc-rig-questions` subtask to answer 1+3 from the lab's VTI
  Google Doc (citations required; rig-envelope facts harvested as
  VTI rig-card seed); humans own #2.

- **RESOLVED — rig questions 1+3 answered (vti-doc-rig-questions
  subtask; landed hera@4162879).** Q1: closed-loop on LS335 input A
  sample-mount heater; needle valve/vaporizer operator-only; agent's
  settle-and-verify compatible (read-only). PID/heater-range = TODO in
  the lab doc itself. Q3: no documented LS-vs-sample offset —
  uncharacterized gradient, ask operator; sensor accuracy ±6–9 mK
  (10–20 K) per the Cernox cal packages the subtask harvested into
  `hera/vti/cernox-cal/` (with the field-error table: ~tens of mK at
  10 K @ 6 T). Open: which serial is on input A (`INCRV? A` once the
  rig is free). Rig-card seed material: substantial. Also note the lab
  doc's own gaps (PID TODO, stale sensor suffix) — the rig card will be
  *better* than the lab doc on day one.

- **RESOLVED (runbook caveat) — nohup'd JL survives SSH-channel death.**
  The launching SSH client (backgrounded locally 2026-06-10 16:16) was
  reaped >24 h later; probe confirmed the 8899 server uninterrupted
  (same PID, kernels live, activity seconds old). The runbook's
  "launch from a local window for survival" caution can be downgraded
  to a note; SSH launch is fine on this box.

- **TOOLING/INCIDENT — HERA used the wrong magnet read API (Zack: "not
  its fault, the API is bad").** Driver autopsy confirms: FastBi1K5 has
  no correct field-read surface — `get_field()` returns *commanded
  current* × T_per_A (`GET:I:?`), not measured field; the
  instantaneous-sample readback (`GET:I:SAMPLE:?`) is commented-out dead
  code; `status()` issues six redundant queries; `mag` is a bound method
  with a spoofed `.full_name`, not a qcodes Parameter. Fix (driver now
  vendored in `src/drivers/`, ours to clean): proper qcodes Instrument
  with a single `field` Parameter (get = real readback, set = blocking
  ramp, documented semantics), back-compat aliases for the rig
  notebooks, and a note in the VTI rig card on which SCPI path is truth.
  AGREED (Zack): add a **scaled read Parameter for the current field**
  (qcodes `ScaledParameter`/`Parameter(get_cmd=...)` over the current
  readback × `T_per_A`) — fp-able in sweeps and unambiguous, distinct
  from the set-point.
  Route: driver work → `qswitch-prefan-recipes` subtask (owns drivers)
  or a follow-up driver-cleanup item in the triage queue; consider
  upstreaming to dgglab/VTI-drivers after a rig smoke test.

- **DESIGN (long-term, Zack) — automate the VTI heat-up stage.** The
  warm-up for the temperature sweep was manual and fraught: per the lab
  doc (rig-questions answer), only the LS335 sample-heater loop is
  closed-loop — vaporizer/needle valve are hands-on-rig, so reaching and
  holding elevated T is operator craft, not procedure. Full automation
  needs: actuation or a documented setpoint procedure for the
  vaporizer/needle-valve side, LS335 loop orchestration (PID/heater
  range — currently TODO even in the lab doc), the safe T/B envelope
  (rig card), and settle/verify primitives the agent can call. Plan:
  **talk to Bingcheng (VTI czar)** — owns the rig knowledge; his answers
  seed both the rig card and the automation scope. Long-term item; park
  in eng-backlog after the Bingcheng conversation shapes it.

- **TOOLING (fixed live) — Shift+Enter in Alacritty-on-rig inserted a
  literal `\r` instead of newline.** Root cause: the provisioned
  `alacritty.toml`'s Shift+Return binding was double-escaped
  (`chars = "\\u001B\\r"` = 8 literal chars in TOML). Fixed in place
  (single-escaped → real ESC+CR, hot-reloaded; .bak existed). If the
  provisioning for these rig terminals is scripted/templated somewhere,
  fix it at the source too — same bug will reappear on the next rig.
  → spawned `alacritty-provisioning-fix` subtask: reads the lab-pc-setup
  wiki page, fixes the escaping at the provisioning source (suspect:
  `setup-lab-pc.ps1` here-string layering), sweeps other `chars` entries
  for the same class, verifies rendered output bytes.

- **REVIEW ITEM — possible leak: the starting Si = +50 V choice.**
  Run 0 already carried Si=+50 V. Candidate provenance: the deployed
  meas_config skeleton and/or device card both mention +50 V (run-80
  fan) and +95 V (cut/gatemap) from the *reference campaign* — HERA may
  have inherited +50 as a default rather than deriving or asking, i.e.
  prior-campaign choices steering the blinded session through the
  template side door. To review in the archive: trace +50 V's provenance
  through deployed artifacts (meas_config cell, card, brief), and check
  whether HERA's notebook markdown treats it as a given or a decision.
  Interacts with Qingrui's later Si-optimization input (negative values
  wanted) — if +50 was a silent inheritance, the blinding protocol needs
  a "operational defaults are also information" pass. "be extremely
  careful… it's not worth messing up the run to fix the ana nb now."
  Support-side debugging on the rig during an active sweep should
  default to read-only; process kills / session creation / env syncs are
  run-endangering interventions that need explicit clearance. Bake into
  the support-session playbook.

---

## Resolution log (post-session triage, 2026-06-11)

Item-by-item triage with Zack (`session-notes-resolution` subtask);
each row records the ruling and the concrete change/commit. HERA's own
`session_notes.md` items are folded into the same queue.

| # | Item | Ruling | Change / commit |
|---|------|--------|-----------------|
| 1 | Rescue uncommitted artifacts from `vti-live-readiness` worktree (this log + Si device-card widening) | **Apply** | Log landed at `hera/docs/vti/`; QC0426 card Si row → [−50, +100] V, `[VERIFY]` resolved |
| 2a | `nb`/`nb-collab` UnicodeEncodeError on cp1252 console (root cause of HERA's per-command `PYTHONIOENCODING` tax) | **Apply** | `sys.stdout/stderr.reconfigure(encoding="utf-8")` on win32 in both tools' `main()`; rig `~/.bashrc` export stays as belt-and-suspenders |
| 2b | `nb summary` lacks execution counts (gate A/B text in hera_vti.md claimed it; HERA dove into raw JSON) | **Apply** (nb feature, not prompt retreat) | `exec` column in `cmd_summary` (`[n]` / `-` / blank for md); prompt claim now true as written; smoke-tested on the session measure nb |
| 3 | Env-churn cluster: shim `--no-sync` patches (applied live on rig, not in repo); `uv run --project` incantation in prompts (token tax + footgun — Zack); agent-memory `--no-project` note leaked to rig context | **Apply, with new `menv` shim** (Zack: prompt incantations are a footgun; shim it) | `tools/nb`+`nb-collab` get `--no-sync` (matches rig patch); new `tools/menv` shim + install.sh entry; all three prompts (vti/tactical/iris) now say `menv python -c '...'`; explicit-sync policy added to preflight runbook; MEMORY.md note scoped DEV MACHINES ONLY |
| 4 | nb-collab server resolution: stale jpserver-*.json matched a dead server (ConnectionRefused); `--server-url` without `--token` silently ignored; token `''` impossible | **Apply** | `_server_alive()` probe (3s `/api/status`) skips dead candidates with a stderr warning; `--server-url` alone now looks up the token by URL (errors with a hint instead of falling through); explicit `--token ''` honored |
| 5 | Runbook lacks guard rails for the pre-session incidents (double launch → ystore contention → kernel restart loops; MSYS-mangled taskkill; stale runtime files) | **Apply** (Zack: launch via `menv`) | Runbook §4: launch line now `nohup menv jupyter lab ...` (no implicit sync); launch-precondition probe; recovery procedure (powershell-form taskkill /F /T, rm stale ystore, rm stale jpserver-*.json, single relaunch) |
| 6a | Operator can't locate "cell 18" — JL shows no indices; prompt-anchor workaround proposed | **Build now** (Zack: show indices in the UI instead — better and cheaper for everyone; prompt-anchor text rejected) | `jupyterlab-cell-index` subtask spawned (frontend-only labextension, model-order indices, windowing-safe, vendored wheel); local perf+functionality verification before deploy; eng-backlog entry tracks it |
| 6b | Mid-run checkpoint was emergent, not required — highest-value behavior of the day | **Apply** | "Checkpoint long sweeps" working-style bullet (sweeps > ~30 min: stated checkpoint + priced continue/adjust/abandon fork) in hera_vti.md + hera_tactical.md |
| 6c | Idle-time pricing norm ("keep a cell queued"; 42% measured utilization) | **Punt — unresolved** (Zack: right direction, too strong for now) | eng-backlog: re-evaluate after `hera-utilization` tooling lands and sessions are scored |
| 7 | ana policy: `edit_no_exec` makes the operator run pure-analysis cells — friction, no safety payoff | **Apply — flip to `edit_exec`** (delete included; shared-kernel caveat punted) | Policy tables + prose in hera_vti.md and iris.md; `templates/vti_ana.ipynb`, `templates/toploader_ana.ipynb`, `hera/templates/QC0426/20260610_ana.ipynb` metadata + header text. Hardware contract unchanged (measure append-only, operator-run) |
| 8a | `hera-utilization` scoring tool (raw + agent-attributed) | **Punt** (Zack) | eng-backlog entry (paired with 6c — re-evaluate together once sessions are scored) |
| 8b | Utilization instrumentation: nb-collab timestamps + JL `recordTiming` — unrecorded timing is lost forever; round 2 needs it recording | **Subtask** | `session-metrics-instrumentation` spawned (base hera@908a83c) |
| 8c | `hera-watch` live run-dir digest (HERA hand-rolled two watchers unprompted) | **Subtask** (adoption-test framing: round 2 usage decides if it stays) | `hera-watch` spawned (base hera@908a83c) |
| 6a′ | (update) JL cell-index extension | **Done** | `jupyterlab-cell-index` subtask landed on hera (53dd526): prebuilt vendored wheel, model-order indices, testbed harness for local verification |
| 9 | `hera-notify` Slack integration | **Apply here** (measurebot plumbing confirmed reusable — no new integration) | `src/tools/hera_notify.py` + `tools/hera-notify` shim + pyproject script + install.sh; house rules in hera_vti.md Tools (brief names the operator key; fixed event list; no default recipient by design). Tested live: DM to ZACKG from dev box ✅. Also fixed stale "edit-only on ana" line (item 7 leftover). Rig config (`~/.config/measurebot/.env` on dgg-vti) → maintenance window |
| 10 | `hera-archive` is toploader-pathed | **Apply — generalize** (`--rig {toploader,vti}` preset, `--device` override, `--no-data`) | Adapted + ran for real: `hera/docs/notes/2026-06-10-QC0426-session/` (notebooks, card, brief, session_notes, hera_scratch, HERA transcript; data skipped — titan mirror has it). Review items unblocked |
| 11 | Permissions for HERA: bypass vs mined allowlist | **Hard bypass, default for claude on both rigs** (Zack; overrides support-session lean) | Launch commands get `--dangerously-bypass-permissions` (hera_vti.md, hera-session.md phase 7, runbook §8); shared-PC blast-radius bullet added to hera_vti.md "What you do not do" (the prompt is now the only gate); runbook documents the `~/.claude/settings.json` `defaultMode: bypassPermissions` rig default |
| 12a | Blinding leak: Si=+50 silently inherited (research verdict: 3 channels — brief VERIFY framing, card run-80 citation, reference pack anchored at +50) + stale meas_config comments | **Apply — new round-2 set with the fix baked in** (Zack: new card + new nb set for round 2) | `hera/templates/QC0426-round2/`: stripped device card (physical truth + rounded-inward outer box; QSwitch `[PREFLIGHT]` ?s until bring-up), scrubbed `measure.ipynb` (fence-framed SAFETIES, skeleton meas_config `<SET PER RUN>`, QSwitch placeholder cells), fresh `ana.ipynb` (edit_exec); operator-side truth sheet `round2-safeties-sheet.md`; preflight §2 updated |
| 12b | Estimate bias: actuals ~+7% over even upper brackets (optimistic-floor anchoring) | **Apply** | "Price everything" bullet: derive from measured overhead, cite the calibrating run, headline = realistic case |
| 12c | Coverage trade stated internally only; hole side never acknowledged | **Apply** | nb-collab proposal-cell requirements: state the coverage trade on the page (what's excluded, why, price of full coverage) |
| 12d | Helper candidates (partial-fan re-form, gain-applied resistance grids, per-column SdH FFT — 6-8 hand-rolls each) | **Continuation → hera-watch subtask** (same domain, warm) | Done: `hera.analysis.{fan_grids,resistance_grids,sdh_fft}` landed (1bfbdbf), bit-exact vs scratch outputs; gain model unified into hera.analysis |
| — | Rig/fridge cards design (layer-model completion; T/B envelope safety home) | **Punt → backlog** (Zack: right design, not round-2-blocking) | eng-backlog: "Fridge/rig cards — complete the layer model" (incl. chat-doc T/B envelope capture as VTI seed) |
| 13a | Classical-Hall trap: Rxy value-match masquerades as plateau confirmation (run-3 near-miss) | **Apply** | trilayer-stacking-id Verify: flatness (dRxy/dn ≈ 0), never value-match |
| 13b | Densify-without-terminator: run 4 resolved zero new minima (unbounded "ragged → densify" prescription) | **Apply** (compressed to a stopping rule after discussion) | Step-4 densify branch: no-new-minima → stop; α-fork needs plateaus or density anchor, not grid |
| 13c | SdH-FFT two-pocket method found structure no arc-hunting surfaced (run 5) | **Apply** | Hunt discriminator #5: per-column FFT in 1/B, f₁+f₂=f_tot signature, window-sensitivity caveat; cites `hera.analysis.sdh_fft` |
| 13d | FFT forensics spiral: 3 extraction schemes, conflicting slopes, manufactured confidence | **Apply** (recipe-generic → STYLE, not the recipe) | STYLE rule 14 (extraction-sensitive claims are forks) + burn-log entry 3 |
| 13e | Vertical-candidate adjudication "worked but was close"; no worked negative in Examples | **Apply** | trilayer-stacking-id Examples: anomaly E3 worked rejection (four-count kill) |
| 13f | Si setpoints quoted in recipe Examples — same channel the provenance trace convicted | **Apply** (Zack: setpoints are calibrated, not recipe content) | Examples scrubbed (cite `measurement_config`/notebook index instead); STYLE rule 11 gains the setpoints-are-calibration-data exception, Si=+50 as the burn. 60 s/row datum + aliasing validation: record-only (rig data → future VTI rig card) |
| 14 | Scratch notebook unused — HERA wrote scripts in `hera_scratch/` all session | **Retire the scratch nb** (Zack) | hera_vti.md: policy table row removed, workflow bullet now scripts-based; round-2 kit ships no scratch nb |
| 15 | Ana-kernel boot-death incident (UNRESOLVED from the live session) | **RESOLVED — autopsied live 2026-06-11** (fridge in benign warm-up; Zack cleared rig work) | Root cause: the surviving JL server's **spawn context is poisoned** (server in an orphaned job object; pre-16:17 kernels broke away and live; every new kernel since dies < 3 s, silent — reproduced today via REST). Disk env, kernelspec, and the server's env vars all verified healthy (kernel boots fine with the server's exact env from a fresh process). **Env-churn correlation downgraded to coincidence** (16:17 sync vs ~16:18 launch-session close). Fix: server restart from a local console at the maintenance window (checklist #5); runbook §4 gains the symptom→fix note + throwaway-kernel post-launch test |
| 16 | Strengthen the session-notes feedback loop (the log's open question; this triage was the prototype) | **Apply — formalize** | `session-archiving.md` gains "Resolution triage — the standing post-session step": merged queue, human-ruled dispositions, table-in-the-log, maintenance-window checklist, in-session proposed diffs (never auto-applied), operational-defaults hygiene check |

### Rig-side maintenance checklist (post-session window, in order)

All deferred rig writes from this triage; each needs the rig free:

1. dgg-vti: `git pull` in `~/measurement_env` (brings shim patches, menv,
   hera-notify, cell-index wheel, prompt changes) + `scripts/install.sh`
2. dgg-vti: `uv sync` (no live kernels!) — picks up jupyterlab-cell-index
   + hera-notify entry point; then the runbook §1 import smoke test
3. dgg-vti: `~/.config/measurebot/.env` (copy from toploader, fix/confirm
   operator user IDs) — enables hera-notify
4. dgg-vti + toploader: `~/.claude/settings.json` →
   `{"permissions": {"defaultMode": "bypassPermissions"}}` (merge, don't
   clobber)
5. dgg-vti: restart JL 8899 **from a local console** per runbook
   recovery procedure, clean stale ystore/jpserver files — this IS the
   ana-kernel fix (autopsy 2026-06-11, resolution row 15: the surviving
   server's spawn context is poisoned; new kernels die at birth). After
   relaunch, run the throwaway-kernel spawn test, not just /api/status
6. toploader: `git pull` + `install.sh` at its next natural window (gets
   the same tools; nothing urgent)
