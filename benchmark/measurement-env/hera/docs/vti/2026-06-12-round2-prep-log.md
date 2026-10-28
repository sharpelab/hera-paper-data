# VTI round-2 prep log — 2026-06-12

Operator-side log of round-2 preparation (successor to the
`vti-live-readiness` support session; round-1 record:
`2026-06-10-live-session-log.md`). Tagged entries as events happen; feeds
the same post-session/post-prep triage loop
(`hera/docs/session-archiving.md`).

Day plan (Zack's order): rig/fridge cards (sub-subtask) → QSwitch
preflight (interactive) → deploy accumulated `hera` changes to dgg-vti
(maintenance-window gated) → this log throughout.

---

## Running log

- **STATUS — branch state at start of prep.** Local `hera` at `a67c647`,
  **ahead of `origin/hera` by 2** (`a67c647` session-log update,
  `15857f4` ABA roadmap) — the round-2 preflight's "[Zack] push `hera`"
  release valve must carry these. Submodules: measureme `9b98548`
  (post-sharpelab_nb-removal — the pointer the import smoke test
  guards), measurebot `8a6ecb4`.

- **GAP — Qingrui's temp-sweep-constraints chat doc never landed.** The
  round-1 log says "full chat doc to be attached post-session"; it is
  not in the repo or the session archive
  (`hera/docs/notes/2026-06-10-QC0426-session/`). It is the seed for
  the VTI rig card's safe-T/B envelope (temperature still has NO safety
  home in any artifact). Asked Zack to supply it for the rig-cards
  work.

- **SPAWN — `magnet-field-param` subtask (base hera@a67c647).** Zack's
  call: the magnet-API fix gets its own subtask, now, integrated into
  round 2 (rides the round-2 deploy). Scope: `magnet.mag` becomes a
  real qcodes Parameter — `mag()` reads the current field as a scaled
  param (readback × `T_per_A`), `mag(target)` keeps the blocking-ramp
  set semantics; read-truth verdict (`GET:I:?` vs dead-code
  `GET:I:SAMPLE:?`) documented for the future VTI rig card; back-compat
  aliases; fake-transport unit tests. Carved OUT of the rig-cards
  scope (one owner for driver code; card documents the result).

- **LANDED — `magnet-field-param` → hera@9d50c3b** (+ `3f3a26f` LF
  normalization): FastBi1K5 `mag` is now a real qcodes Parameter with a
  measured-field get. Convergent validation from the session tail:
  HERA's own session_notes (06-12 ~00:10) independently logged
  "`magnet.mag()` getter not implemented; operator corrected to
  `get_field()` live" — the live session asked for exactly the fix that
  landed. Follow-through: recipes/templates that say "use
  `get_field()` for readback" can now prefer `mag()`.

- **ENVELOPE (Aaron, via Zack) — safe T/B: essentially NO constraints
  in the normal working window.** Some consideration needed at very
  high fields/temps; the historical caution was convention ("just
  wasn't commonly done"), not physics — students were cautious, but
  slightly elevated temps/fields are operationally fine. This
  supersedes the cautious framing inherited from round-1 chat. Seeded
  to the `rig-cards` subtask verbatim (provenance cited; numeric edges
  of "very high" are `[VERIFY]` with Bingcheng).

- **SPAWN — `rig-cards` subtask (base hera@9d50c3b).** Two-stage per
  Zack: stage 1 = schema (`hera/rig-cards/EXAMPLE.md` + interactions
  note vs device cards) → Zack reviews solo and with companion device
  cards → stage 2 = VTI + toploader cards + the hera_vti/hera_tactical
  prompt migration. Branched on top of the magnet fix, so the
  read-truth verdict is citable.

- **ARCHIVE — round-1 final pull complete** (`hera-archive --rig vti
  --device QC0426 --no-data zack/20260610-QC0426-hera-live
  2026-06-10`; round 1 confirmed concluded, hera session closed; data
  skipped — titan mirror). Refresh delta over the 06-11 archive, all
  uncommitted in the round2-prep worktree pending commit approval:
  measure nb +1116 lines (ladder/E3 session tail), ana nb touched,
  transcript +294 lines, 2 new `hera_scratch/` files (`lk_extract.py`,
  `run16_e3.png`), device card +1 row, session_notes +5 entries (below).

- **FLAG — B-field session cap was amended live to |B| ≤ 14.0 T**
  (device-card delta, 2026-06-11, operator approval Qingrui/Aaron;
  "a cap, not an endpoint"; SAFETIES re-committed). Interactions to
  resolve before round 2: (a) the driver's own `max_field_T = 13.5`
  raises ValueError below the stated cap — 14.0 in a SAFETIES cell is
  unreachable through `mag()`; which number is the magnet's actual
  rating? (b) the round-2 stripped card's outer safety box presumably
  still says 8 T — does the amendment propagate? Rig-card content
  either way.
  **RESOLVED 2026-06-12 (rig-cards subtask):** (a) magnet limit ruled
  **14.0 T** (Zack; device cards set session caps below it) — driver
  `max_field_T` bumped 13.5 → 14.0, limit + provenance live in
  `hera/rig-cards/VTI.md` (Magnet). (b) the round-2 card's 8 T outer
  box stands as that session's cap; no propagation implied.

- **TRIAGE QUEUE — five new session_notes entries from the session
  tail** (post-06-11-triage; feed the standing resolution loop):
  1. PROTOCOL: persistent-switch heater bit ladder attempt 1 — add
     "confirm persistent-switch state before any first-action-is-a-
     field-move cell" to VTI preflight (rig-card / recipe leg).
  2. RECIPE FIX: trilayer-stacking-id — LK mass-split + beat-exclusion
     Verify method (beat damps with m_A+m_B; light coexisting mass =
     pocket). Plus rig datum: VTI closed-loop settles 2–5 min, not
     toploader's 10–20 (rig card).
  3. TOOLING: `mag()` getter — RESOLVED by 9d50c3b (above).
  4. PROTOCOL: post-heating base 1.21 → 1.32 K; cooldown thresholds
     should be stability criteria, not absolute targets; ask Bingcheng
     re restoring pre-heating needle-valve flow.
  5. PROTOCOL: E3 post-mortem — never classify dispersion from < ~8
     B-rows spanning ≥ 1.5 T; log "dispersion undetermined". (Also
     earlier tail entry: measured ramp rate 0.092 T/min at 0.02 T
     steps, not bare 0.137 — landau-fan-vti pricing fix.)

- **PROBE (read-only) — dgg-vti deploy-readiness state.** Rig repo
  HEAD `2388dcf` (early in the post-session wave — behind local hera
  by ~25 commits); local mods exactly the two sed-patched shims
  (`tools/nb`, `tools/nb-collab`, 1 line each) — `git checkout --
  tools/ && git pull` resolves as planned. `~/.bashrc`
  PYTHONIOENCODING export present (keep). `~/.claude/settings.json`
  has NO permissions key — bypassPermissions merge still owed. JL 8899:
  measure kernel alive and touched today (12:48Z, 1 connection) —
  awaiting QC confirmation before shutdown; **wrinkle: two OTHER
  users' kernels live on our 8899 server** (`qingrui/temp/A25_041_ana`,
  `bsuo/NF03A2/.../measurement.ipynb`, both idle since 06-10 23:16Z,
  0 connections) — the planned server restart kills those too; fold
  into the QC/operator confirmation.

- **DESIGN (Zack) — preflights in cells; operationalize lightly, mark
  as ablatable.** Round-1 behavior not captured in any artifact:
  proposed cells whose first action is expensive or stateful (field
  move, heater write, long sweep) should OPEN with a cheap preflight
  block — read the state the cell assumes (field readback, persistent-
  switch state, base T), print expected vs actual, stop before the
  expensive action on mismatch. Evidence from the tail: HERA already
  did this emergently (precondition cells reading field), and the
  persistent-switch incident (ladder attempt 1) is the burn a one-line
  check would have caught. Operationalize LIGHTLY — a prompt norm, not
  a framework — and note explicitly that it's scaffold: ablation
  candidate as HERA gets more autonomous. Interaction: the rig card is
  the natural home for *which* stateful hazards exist per rig and the
  cheap read for each (flows to the `rig-cards` schema).

- **DEPLOY — non-kernel column executed on dgg-vti** (hera pushed by
  Zack at 10 commits; kernel work held for QC's device-grounding
  window). Done: shim sed-patches reverted via `git checkout --
  tools/`, `git pull --ff-only` to `a864b28`, submodules at
  measureme `9b98548` / measurebot `8a6ecb4`, `scripts/install.sh`
  (new shims hera-watch/menv/hera-notify + hera-vti agent prompt
  installed), `~/.claude/settings.json` merged with
  `defaultMode: bypassPermissions`, `~/.config/measurebot/.env`
  copied from toploader. hera-notify smoke-tested to ZACKG via
  `menv python -m tools.hera_notify` (console-script entry point
  registers at the maintenance-window `uv sync`; shim works after
  that). Still parked for the window: `uv sync`, import smoke tests,
  JL 8899 restart + throwaway-kernel test + recordTiming check,
  round-2 session dir.

- **GAP — measurebot .env has no key for Qingrui.** Toploader's .env
  (now on dgg-vti) carries ASHARPE/BSUO/IZHENG/ZACKG only; the round-2
  brief must name the operator's Slack key for hera-notify. Need
  Qingrui's Slack member ID → add `SLACK_USER_QCAO` (both rigs,
  ideally).

- **DEPLOY — hera-notify operator key.** QC's Slack ID (U0123456789)
  added as `SLACK_USER_QCAO` to `~/.config/measurebot/.env` on dgg-vti
  AND Zack's dev box. (Toploader still lacks it — add at its next
  window.) The round-2 brief can now name `QCAO` as the operator key.

- **QSWITCH KIT — bring-up notebook built + wiring plan encoded.**
  `hera/templates/QC0426-round2/qswitch_bringup.ipynb`: runnable form
  of qswitch-smoke-test.md, one section per step with expected outputs
  and stop conditions inline; config cell holds the maps with
  placeholder asserts (silent-preconditions style); policy
  `edit_exec` — full control (Zack's call: the bring-up is
  interactive, operator at the rig for the hardware steps; a live
  claude session drives/extends it directly via nb-collab). Wiring plan from Zack
  encoded in nb banner + round-2 device card: device → Fischer, F1 =
  all contacts → QSwitch's single Fischer input (lines 1–24), F2 =
  gates → front panel alongside instrument BNCs. New safety concept:
  **reserved gate taps** — gate-occupied front-panel taps must never
  be routed to a contact line (config-cell assert + card `[PREFLIGHT]`
  marker). Open for the physical preflight: which taps gates occupy;
  that gate drive is unaffected by relay ops. Also fixed the card's
  swapped map semantics (lines = contact→line, breakouts = port→tap,
  matching `contact_mux`).

- **DEPLOY/INCIDENT — maintenance window executed; stale-tab RTC merge
  duplicated cells.** Window sequence ran clean: JL 8899 tree killed
  (PID 21536, the round-1 poisoned server), ystore + runtime json
  wiped, `uv sync` (cell-index wheel installed, hera-notify entry
  point registered), import smoke tests all pass (sharpelab_nb from
  repo src; gates + ContactMux + QSwitch + FastBi1K5), relaunch from
  RustDesk local console. THEN: ana nb re-grew every code cell as an
  appended block (40 cells vs the morning archive's 26), measure
  showed the same in-UI — root cause: browser tabs from the old
  session reconnected after the ystore wipe and jupyter-collaboration
  merged their stale ydocs into the rebuilt rooms. Fix: tabs closed,
  hard-kill (NOT graceful — avoids flushing the borked room state to
  disk), ystore re-wiped, ana truncated on disk with a
  verify-pure-duplicates guard (Zack's verification outputs kept),
  measure disk verified md5-identical to the archive (its dupes never
  hit disk), relaunch. Runbook recovery procedure gains step 0 (close
  all RTC tabs first; prefer hard kill); round-2 preflight restart
  item cites it. Post-relaunch verification: throwaway-kernel spawn
  test PASS (25 s alive, no restarter loop in log — the round-1
  poison signature is absent), recordTiming default True, ana 26 /
  measure 73 cells. Also noted: the OLD 8890 server was already dead
  (qingrui + bsuo kernels had migrated to 8899; killed with the
  window — flagged to QC), and its stale jpserver-16400.json was
  removed with the sweep.

- **REVIEW + REDEPLOY — rig cards landed (hera@25b5866); rig updated.**
  Reviewed the rig-card wave: layer model + tie-break rule sound; VTI
  card cross-checks clean against kernel-compat, cernox INDEX, Aaron's
  envelope ruling, and the session tail (it absorbed the
  persistent-switch hazard → Silent preconditions, closing triage
  item 1; 0.092 T/min measured-ramp datum; LS335 two-masters quirk).
  Read-truth settled: `GET:I:?` IS measured current (~41 ms lag) — the
  incident entry's suspicion of commanded-current was wrong. 14.0 T
  ruling propagated driver+card+template. Prompt unified as
  `hera-tactical` (hera_vti.md deleted, old toploader prompt parked).
  Rig redeploy: pull → 25b5866, install.sh, driver unit tests 35 pass.
  BUG found live: install.sh's stale-agent retire only trusted
  symlinks — on Git Bash installs are copies, so hera.md/hera-vti.md
  survived on dgg-vti (removed by hand); install.sh now also retires
  regular files whose frontmatter names a shipped agent (toploader
  would have hit the same). Loose ends flagged: iris.md still
  toploader-flavored (unify item), toploader rig card pending.

- **RIG ANSWERS (Bingcheng/Qingrui via Zack, during rewiring) + NVRAM
  read.** (1) Envelope early cut: consideration zone = simultaneously
  >~10 T and >~15 K → rig card. (2) He: closed-loop system, no session
  budget constraint → rig card (replaces the state-the-He-trade
  guidance). (3) Needle valve: no restore needed post-round-1 ("just
  took a while") — triage item 4's Bingcheng half RESOLVED; the
  stability-criteria-over-absolute-thresholds recipe half still open.
  (4) Heat-up/cool-down procedure: promised after QSwitch bring-up.
  (5) `INCRV?` read (LS335 GPIB0::10, kernel-free): input A = curve
  23 = X225149 (cernox INDEX resolved); input B = curve 21 whose
  header ALSO says X225149 — load anomaly, unresolved, B control-only
  so bounded impact → rig card + INDEX.

- **WIRING (in progress, maps NOT final).** Images received
  (IMG_9515 device photo: circled breakout-box indices per pad,
  F1/F2 tags, TG=13/F2, Si 11/26; IMG_9516 table: 13 F1 rows breakout
  → fischer, 5 arrowed F2/gate rows). MID-STREAM REVISION
  (Zack): not enough front-panel BNCs for all instruments → some
  voltage sources get wired into the QSwitch **IN** (line side);
  Bingcheng to deliver a config covering QC's full manual repertoire
  without replugs. HOLD encoding until that config lands. Flagged:
  sources-on-lines is outside `contact_mux`'s model (lines = device
  contacts, taps = instruments) — routing source→contact joins two
  LINES via a shared tap; expect a ContactMux extension, and the
  reserved-taps guard inverts (source lines must never close onto a
  lock-in tap unintentionally). Review BC's config against the driver
  before any relay moves.

- **WIRING — contact map drafted + encoded (T6 pending).** Zack-guided
  OCR of the wiring images converged: circled photo numbers = cable
  conductor indices; the five F2-riding pads (T1, B1, B2, TG, BG) are
  shorted onto spare F1 conductors at the breakout; **F1 fischer index
  = QSwitch line**; breakout-box indices abstracted away. Map encoded
  in the round-2 device card (T1–T7/B1–B8 + gates TG→12, BG→2,
  Si→16/11) and pre-filled into the bring-up nb config cell
  (`GATE_LINES` never managed; collision assert). Open from BC: T6
  (pad F1-02) line; BNC 1–8 tap map; IN-side source map. QSwitch
  diagram (from Zack) sharpened the model: tap !9 = per-line series
  relay to a second 24-pin IN connector (1:1, no cross-routing) →
  gate sources likely ride IN pins of their gate lines; !0 is
  default-closed SOFT ground (resistor) so reset() dumps gates
  resistively. ContactMux extension shape: `gates={name: line}`
  excluded from managed set, !9 closures held outside select/park.

- **SPAWN — `recipe-tail-fixes` subtask (base hera@25b5866).** The
  four rig-independent triage items: trilayer-stacking-id (LK
  mass-split + beat-exclusion Verify; E3 coarse-B dispersion rule),
  landau-fan (measured-vs-bare ramp pricing via rig-card constants),
  temperature-dependence (stability criteria over absolute targets).
  Rig-card settle datum (2–5 min closed-loop) added here instead —
  rig fact, not recipe content.

- **WIRING FINAL (QC's routing slide) + BRIEF RESTRUCTURE.** QC
  produced the routing deck (slide 1 = annotated device photo with
  line assignments; slide 2 = QSwitch diagram): **T6 = line 12**
  resolved; **TG/BG hardwired** (not through the QSwitch — the
  earlier TG→12/BG→2 shorts were undone, freeing 12 for T6 and 2
  entirely); **Si rides lines 16/11 with standing closed relays**
  (keep-closed requirement; only gate the switch touches); BNC taps
  1–8 = sr1.V1/V2, sr2.V1/V2, sr3.V1/V2, sr1.amplitude (AC source),
  sr0.V1×−1e6 (AC current). The sources-on-lines ContactMux extension
  is unnecessary — existing driver model fits; Si handled by
  exclusion from the managed set; `qsw.reset()` hazard rescoped to
  "drops Si's standing closures". Card + bring-up nb updated to
  final. **Round-2 brief restructured as two phases** (Zack's design):
  phase 1 prep & characterize (device-init chain, new surface) with a
  six-item exit contract (incl. exit report in ana + operator go) →
  phase 2 classify (the replication). Zack's design stance, on the
  record: human gates are likely permanent even as autonomy grows —
  the *owners* (strategic vs tactical) may change; round 2
  deliberately tests the gate pattern.

- **QSWITCH PHASE-1 (code-eval) — serial forensics; switch identified
  as UNPLUGGED.** Worked the bring-up nb live in
  `zack/qswitch_testing/` (NOT the session dir — testing is its own
  context; future session dir naming: `zack/<date>-QC0426`, no
  "round2"). §0–§1 pass; §2 connect chase resolved by PnP
  enumeration: ASRL7 = DC205 (IDN'd at 115200, s/n 20500514), ASRL8 =
  Terranova 906A gauge (held by the VSCode influx-logger kernel —
  correctly, permanently), and the QSwitch is a **Microchip VID_04D8
  USB-CDC ghost at COM3 — not connected** (USB/power, QC to
  reconnect; expect ASRL3 back). **"Port wanders" lore debunked** —
  the 06-11 ASRL7/8 scan was the residents with the switch already
  unplugged; Windows pins the port to the instance. §1 guidance
  rewritten (nb template + testing copy + card). TOOLING items logged:
  (a) nb-collab created a second session for the same notebook
  (backslash vs forward-slash path) — executes land on a different
  kernel than a browser tab attaches to; needs path normalization;
  (b) execute-cell warns to install `jupyter_kernel_client`; (c)
  failed qcodes connects leave the instrument name registered —
  retry cells need `Instrument.close_all()`. Discovered en route: QC's
  own JL lives at port 8888 now (system Python, console-launched
  06-11 — the jpserver-16400.json I swept this morning was ITS live
  runtime file, not a corpse; harmless but discovery for his server
  now needs a restart or manual token).

- **PARKED (Zack) — VTI temperature-monitoring investigation.** Second
  candidate task raised today: investigate the VTI temperature
  monitoring situation and plan improvements. Zack: too large a change
  before round 2 — deferred. Adjacent to the existing
  heat-up-automation backlog item (round-1 log; Bingcheng-the-czar
  conversation shapes both). Candidate eng-backlog entry post-round-2.
