# VTI live session log — QC0426 / hera-tactical / 2026-06-14

> **SCORER / SUPPORT-SIDE — not for agent view.** Same quarantine posture
> as `round2-safeties-sheet.md` and `round2-scorecard.md`: this log embeds
> the deployed safety limits and the scorecard's re-derivation targets.
> Do not cite it in any agent-visible doc; the agent prompt's
> data-isolation rules are the fence.

Operator-side log of the **round-2** live HERA session on the VTI (the
replication-from-cooled-start run). Kept by the support session (Zack's
running commentary + infra observations) for post-session review. The
agent's own `session_notes.md` lives in the measurement dir on dgg-vti
(`20260614-QC0426/session_notes.md`); **merge both when archiving** — that
file is primary for the agent's reasoning, this one carries support-side
commentary and ground-truth scoring the agent cannot see.

**Setup recap:** dgg-vti, JL 8899 (`--collaborative`, measurement-env
env), session dir `~/VTI_local_data/zack/20260614-QC0426/` (synced to
`~/sharpelab/dgglab-measurements/vti/zack/20260614-QC0426/` via
`sync-measurements.sh`/titan). Agent **`hera-tactical`** (round-1's
`hera-vti`, renamed in the post-session install), launched with
`--dangerously-bypass-permissions` (round-1 triage item 11 — bypass is the
rig default). Model: **`claude-opus-4-8`** (confirmed from the transcript —
no round-1-style ambiguity this time). Operator: Qingrui at
the rig; **Bingcheng** for the QSwitch window (his switch, his method);
Zack supervising remotely. Round-2 corpus deployed (rig at `25b5866` +
this prep session's doc delta, docs-only re-pull). QSwitch validated on
the rig **2026-06-14** (ASRL4, `settle_s` = 4 s, Si standing closures on
lines 16/11 confirmed closed); `contact-survey-2t`'s automated flavor is
live.

---

## ⚠️ Safety limits — keep visible (deployed, this session)

Operating limits as committed to the SAFETIES cell + device card. These
are the operator-provided gate limits — **no gate is range-found this
session** (range-finding punted to round 3). Strict subset of round-1
ranges (safe by construction). Source: `round2-safeties-sheet.md`.

| Parameter | Deployed (this session) | Established (round 1 / prior — ground truth, withheld from card) |
|---|---|---|
| `dc205_volt` / `k_tg` (TG) | **[−6.0, +7.0] V** | [−6.5, +7.5] V |
| `k_bg.volt` (BG) | **[−4.5, +4.5] V** | [−5.0, +4.8] V |
| `k_2410.volt` (Si) | **[−50, +50] V** | [−50, +100] V |
| B (session cap) | **\|B\| ≤ 8.0 T** | \|B\| ≤ 8.0 T (round-1 card; amended live to 14 T) |

Rules in force: TG geometry ceiling is the hard fence behind the numbers.
`qsw.reset()` is **forbidden once Si is energized** (drops the standing
closures → drops the Si gate). Exceeding committed limits with evidence is
**stop-and-discuss** (supervisor call), never a silent allow.

---

## Session plan / arc (expected shape — agent drives within each phase)

From `qc0426-round2-session-brief.md`. Two phases with an explicit
**operator-go gate** between them.

1. **Gates A→B** per the agent prompt (SAFETIES = operator-committed outer
   box; compare numbers to the card). **Gate C**: first-session branch —
   no references, liveness from the QSwitch bring-up chain.
2. **Phase 1 — prep & characterize** → exit report → **operator go**:
   - `contact-survey-2t` (automated/mux flavor) → pick a *workable*
     source/drain + three probe pairs (sr1/sr2/sr3), satisfice not
     optimize. Verify `mc_fragment` truth on disk after the first run.
   - `cnp-and-dline-calibration` → first gate map → CNP fit → capacitance
     ratio → D-line designer, written back to the device card.
   - Exit contract: all three gate validators committed; CNP/D-line cal +
     cap ratio written back; workable contact config chosen with evidence;
     **exit report landed in the ana notebook**; **operator go**.
3. **Phase 2 — classify (stacking)**: ladder (CNP-vs-D first) → cheap
   discriminators → grid-design guards → Landau fans → ABA forward-model
   overlay + Verify → the five-part stacking call (ABA / ABC / mixed /
   cannot-tell), STYLE strength vocabulary, in the ana notebook.

**Blocklist** (not run this session): `silicon-backgate-survey`,
`gate-range-finding` (+ `-vti` variant), `gate-leakage-survey`.

**Data isolation — strict**: no prior measurement data is in scope. Only
inputs are the brief, device card, rig card, named recipes, and this
session's own `./data/`. First-session recipe branches apply;
`reentry-baseline` is N/A by its own When.

---

## Session-start [VERIFY] — tick live

From the brief's `[VERIFY]` + preflight §3.

- [ ] Operator has run the SAFETIES cell; values match the card's gate
      operating-limits table (TG/BG/Si above).
- [ ] Magnet at 0 T (set **vs** read) — first live exercise of the
      reworked `mag` Parameter: `print(magnet.mag(), magnet._status()['field'])`,
      both agree with each other and the front panel.
- [ ] QSwitch routing maps + `settle_s` present in the card; bring-up log
      entry exists; **Si standing closures (lines 16/11) verified closed**.
- [ ] Heater ownership + max-T ceiling noted (only if temperature work
      arises — none planned for round 2).
- [ ] Base T holding ≈ 1.2–1.3 K; He budget for session length.

---

## Pre-session infra notes

Deploy state (from `round2-preflight.md`, 2026-06-14 prep): corpus closed,
QSwitch validated, 06-12 maintenance-window deploy stands (uv sync,
submodules, install.sh, JL 8899 restart + kernel-spawn test PASS). Rig at
`25b5866` + this session's docs-only delta.

- _(live infra incidents, if any, go here — none recorded yet)_

---

## Running log

Support-side commentary, newest appended at the bottom. Tag vocabulary
(round-1 convention): **TOOLING · FEEDBACK · PROTOCOL · STATUS ·
MILESTONE · INCIDENT · DESIGN · REVIEW ITEM · CHECK · RESOLVED**. Cite
cell idx / file_id / run-dir where possible. Don't repeat the agent's
`session_notes.md` — point at it.

- **STATUS — session live; phase 1, contact survey** (sync @ ~00:13,
  2026-06-14). Runs **0–6** landed in `data/`, all `contact-survey-2t`
  (mux/automated flavor, first-session branch). Agent's `session_notes.md`
  has 3 tagged entries so far (operator `nb-collab wait` adoption,
  per-point timing calibration, run-0 dead-contact finding — see below /
  the agent file for detail). Phase 2 not yet reached.

- **REVIEW ITEM (Zack) — prompt-adherence gap: HERA didn't use
  `nb-collab wait` until the operator asked.** The agent's `session_notes`
  FEEDBACK entry says the operator had to request `nb-collab wait` on
  measurement cells after run 0 ("Adopted from batch 2 on") — but the tool
  is **already in the prompt**: `hera_tactical.md:250–252` documents it
  ("blocks until a cell finishes — use it when your next decision depends
  on the result"). So HERA ran run 0 by ending its turn and polling rather
  than blocking, despite the prompt mandating the tool for exactly that
  case. Scoring note (process / item D-adjacent): this is adherence, not
  missing prompt content — flag whether the prompt's `nb-collab wait`
  guidance needs to be more imperative (it currently reads as "use it
  when…", not "block on measurement cells by default"). Companion bullet
  **Checkpoint long sweeps** (`hera_tactical.md:348–354`, round-1 triage
  6b) + the `hera-watch` checkpoint tool (280–305) are also already in the
  prompt — those only come under test once a >30 min sweep lands in
  phase 2 (fans); watch whether HERA states the mid-run checkpoint in the
  proposal cell unprompted, or needs the same nudge.

- **FEEDBACK (Zack, live) — survey dwell `SURVEY_DELAY = 0.5 s` is
  hardcoded, but the floor is set by the SR830 time constant.** Cell 29's
  contact-survey dwell (0.5 s/pt) is chosen as a number, not derived from
  the lock-in tc — the correct per-point settling floor is several × the
  SR830 `time_constant` (wait for the lock-in output to settle before
  reading), so 0.5 s is only valid *if* the tc supports it. The notebook
  setup cells (10) don't set tc explicitly — it's whatever the SR830 front
  panel holds, operator-set — so the relationship is implicit and
  unchecked. Two consequences: (1) **recipe-surface candidate** —
  `contact-survey-2t` (and any 2T screen) should tie its dwell to the
  measured tc (`dwell ≥ k·tc`, state k and its provenance) rather than
  carry a bare seconds value, same class as the "~30 s/row" burn
  (STYLE rule 12: calibrate constants, don't inherit); (2) **scoring
  note** — check whether HERA reasoned about tc-vs-dwell anywhere, or
  treated 0.5 s as given. The agent *did* calibrate realized per-point
  (~0.74 s/pt incl. ramp, run 0) but that's wall-clock pricing, not the
  settling-floor question.

- **CHECK (Zack) — data-isolation audit of HERA's transcript: CLEAN
  (sync @ ~00:42, through file_id 16 + gate-map landed).** Pulled the live
  transcript (`0dd3d0da…`, model `claude-opus-4-8`) and audited the full
  tool surface — **{Bash, Read, Edit, Write} only**, no Glob/Grep/WebFetch/
  Agent. **Zero** references to any sibling/old session dir
  (`20260610-QC0426-hera-live`, `QC0426-leakage-betatest`,
  `qswitch_testing`, the `20260601` campaign, other users' trees). Every
  `Read`: in-scope deployed docs (`hera_session.md`, `device_card.md`,
  `rig_card.md`), the two **named** recipes (`contact-survey-2t`,
  `cnp-and-dline-calibration`), one driver source (`contact_mux.py` —
  code). All out-of-session paths are `~/measurement_env/...` for
  recipe/code/driver introspection (allowed scope); no `ls`/`cd` of the
  `zack/` parent that would expose sibling names. All data reads within
  this session's `data/`. Corroborated by the artifact grep (survey at
  BG=Si=0, validators [−50,+50], geometry priors flagged "calibrate", no
  09-01/12-20/run-80/+95 leak). **Blind-replication protocol intact.**
  Re-audit at archive (transcript grows).

- **REVIEW ITEM (Zack) — soft blinding leak: "round 2" / "replication" /
  "2026-06-01 cooldown" framing is baked into agent-visible deployed
  artifacts.** Provenance traced — **not** HERA-introduced; it ships in the
  round-2 template set (`hera/templates/QC0426-round2/`, built 2026-06-11
  triage item 12a) and was deployed verbatim:
  - `device_card.md:1` — `# Device card — QC0426 … — round 2`;
    `device_card.md:3` — `round-2 HERA live session (replication from a
    cooled start)`.
  - measure nb header — `# … Measurement (round 2)`, `Round-2 HERA live
    session…`, `2026-06-01 cooldown`.
  - ana nb header — `# … Analysis (round 2)`, `QC0426 round-2 session`.

  The session premise is **blind replication** (`hera_session.md`: "No
  prior measurement data exists for you"), but these headers tell the
  agent it is *round 2* (⇒ a round 1 existed), a *replication* (⇒ a known
  answer exists), and date a prior *2026-06-01* campaign. No data crosses,
  but the agent learns it is being benchmarked against a prior result —
  the meta-awareness the isolation rule exists to prevent. **Same class as
  the round-1 Si=+50 leak** (STYLE rule 11: "an operational default quoted
  in an agent-visible file becomes an inherited choice") — and it sits in
  the very artifact built to fix that leak. HERA propagated it (its
  device-card write-back heading: "Session findings — round 2").
  Triage candidate: agent-visible round-N templates should use **neutral
  session framing** (no round number, no "replication", no prior-cooldown
  date) — the round/scoring identity lives only in scorer-side docs.
  Open question for scoring: did HERA's reasoning anywhere act on the
  "replication/round-2" framing (treat the task as benchmarked / a known
  answer to hit)? Check the transcript at archive.

- **REVIEW ITEM (Zack) — HERA saved nothing to `hera_scratch/`; prompt
  carries a retired-facility tombstone.** Through the gate map landing
  (file_id 17), HERA created **no `hera_scratch/` dir** and wrote no
  scripts/PNGs — all analysis was inline `menv python -c '...'` one-liners
  (12 of them). Its one `ls hera_scratch/` exit-2'd (dir absent). This is
  against the prompt, which directs scratch-first work: `hera_tactical.md`
  L38 ("`hera_scratch/` your scratch space"), L120–128 ("**Iterate in
  `hera_scratch/`** … scripts and their PNGs are your workbench"), L137–138
  ("save anything worth keeping under `hera_scratch/`"), L325 ("Plot to
  files under `hera_scratch/`"). Acute now that a 2D gate map (CNP/D-line
  fit) is in play and needs visualization.
  *Separately* — the prompt still carries a **dated tombstone for the
  retired scratch notebook** (`hera_tactical.md:114–115`, "No scratch
  notebook — retired 2026-06-11…"): changelog cruft in a live agent prompt.
  Introduced by **`d4d78ab`** ([fix][hera] Retire scratch notebook…,
  2026-06-11, co-author Claude Fable 5; round-1 triage item 14), carried
  into the renamed file by **`25b5866`** (rig-card/rename commit). Adjacent
  same-class aside at L133–134 (dated ana-policy-change note). Triage
  candidate — scrub the changelog asides from the prompt; not fixed here.

- **REVIEW ITEM (Zack) — `hera-archive`'s artifact whitelist is a footgun;
  the item is to sync the entire run dir.** `tools/hera-archive` doesn't
  mirror the run dir — it scp's an enumerated whitelist: top-level
  `*.ipynb` (L97–102), a hardcoded doc list `device_card.md /
  hera_session.md / session_notes.md` (L109–111), `hera_scratch/` if
  present (L118–124), `iris/` (L133), `data/<run>` (L149), transcripts
  (L175). Anything HERA writes outside those paths is **silently dropped**
  — and the doc whitelist already misses **`rig_card.md`** (deployed rig
  card never archives). Whitelisting artifacts means every new file class
  an agent invents is lost until someone remembers to add it to the list.
  **Fix (the item): hera-archive should sync the entire session dir** (the
  whole run dir, modulo obvious junk like `.ipynb_checkpoints/` /
  syncthing control files), not a curated set — so nothing depends on an
  agent naming things the archiver happens to know about. Not fixed here.

- **ACTION ITEM (Zack) — add documentation and/or a bring-up step for the
  SR830 time-constant setting** (follow-up to the SURVEY_DELAY entry
  above). The lock-in `time_constant` governs the settling floor for every
  swept-point dwell (`dwell ≥ k·τ`), but it is currently **set nowhere in
  the kit** — the notebook setup cells don't set it (it's whatever the
  front panel holds, operator-set and unknown to the agent), and dwells
  like `SURVEY_DELAY = 0.5 s` are bare numbers disconnected from it. Needs
  one or both:
  - **Bring-up step** — set (or read + record) the SR830 tc during session
    bring-up / preflight, so it lands in run metadata and the dwell can be
    derived from it rather than guessed. Candidate homes:
    `round2-preflight.md` / `preflight-runbook.md` §3 [VERIFY], or a
    setup-cell addition in the measure template so tc is explicit + logged.
  - **Documentation** — the dwell-vs-tc relationship (`dwell ≥ k·τ`, state
    k + provenance) as an instrument-class conditional in the relevant
    recipes (`contact-survey-2t` and any swept-point measurement), per
    STYLE rules 11–12 (calibrate constants, don't inherit a bare seconds
    value); and/or a lock-in settling note in the VTI rig card.
  Corpus/bring-up edits are out of scope for this notes doc — route to a
  subtask. Not fixed here.

- **ACTION ITEM (Zack) — prompt should push `hera-watch` as the default
  for sweeps; `hera-watch` adoption this session is zero.** Usage so far:
  **`nb-collab wait` ×5, `hera-watch` ×0** — HERA blocked blindly on cell
  completion even for the gate-map megasweep (`06d14c97`, 21 rows × 53 pts,
  the longest sweep yet), getting no incremental gain-divided view. This is
  the round-1 triage **item 8c adoption test** result: the tool isn't being
  reached for. Prompt today documents both but doesn't rank them:
  `nb-collab wait` at L250–252 ("blocks until a cell finishes"); `hera-watch`
  at L280–305 + L348–354 (the long-sweep checkpoint tool). The two are not
  pure substitutes, but for **any cell that writes sweep data** `hera-watch
  data/<file_id>` (no `--once`) blocks until completion *and* emits per-row
  gain-divided digests + ETA, and doubles as the post-run read — strictly
  more than a blind `nb-collab wait`. Refined rule for a prompt amendment:
  **hera-watch (background monitor) is the default for data-writing cells;**
  reserve `nb-collab wait` for (a) the "operator has actually started my
  proposed cell" gate (`--wait-for-rerun` — hera-watch can't watch a
  `data/<file_id>` that doesn't exist yet) and (b) non-data cells (setup,
  single gate set, markdown). Triage/prompt-amendment candidate; not fixed
  here.

- **DESIGN / ACTION ITEM (Zack) — chiron should take special interest in
  whether previous-round fixes actually worked when reviewing a new
  session; may need a generated changelog.** Chiron today has only a
  *partial, narrow* version: `chiron.md:204–205` asks "did a previously
  STYLE-burn-logged failure class fire again? (the fix didn't take)" — but
  that's **burn-log recurrences only**. It does **not** systematically
  check whether each prior *resolution-table* fix (prompt changes, tooling,
  templates, runbooks) achieved its intent / got adopted / didn't backfire.
  This session shows that gap is load-bearing — round-1 fixes that the
  burn-log check misses:
  - `nb-collab wait` was already mandated, ignored until the operator asked
    (adherence regression).
  - **hera-watch zero adoption** — item 8c was *explicitly* an adoption
    test; the fix didn't take (5 `nb-collab wait`, 0 `hera-watch`).
  - the **"round 2" blinding leak** sits in the stripped card built to fix
    the Si=+50 leak (item 12a) — a fix that introduced a same-class
    regression.
  - **tombstone cruft** (`d4d78ab`) left the retired-scratch-notebook
    changelog line in the live prompt.
  Ask: make "audit prior-round fixes for effectiveness (landed? adopted?
  backfired?)" a standing chiron triage step, broadened past the burn log.
  Changelog: `chiron.md:168–172` calls the per-session resolution table
  "both record and changelog", but those are scattered per-session with no
  consolidated cross-session **fix registry** (fix → commit → intent →
  what-to-watch → verified-effective?) to check a new session against
  (`eng-backlog.md` is deferred-items, not fix-effectiveness). Chiron may
  need to **generate/maintain that registry** if none exists. Triage /
  chiron-prompt-amendment candidate; not fixed here.

- **INVESTIGATE (Zack) — where HERA's session tokens go.** ~233k context
  after phase-1 intro. Transcript: peak context 235k, session message
  content only ~46k; the rest is fixed launch overhead (system prompt, tool
  schemas, CLAUDE.md stack, MCP tool defs).

- **ACTION ITEM (Zack) — follow up on the agent file: disable default MCPs,
  review for a focused environment.** Related to the token investigation
  above.

- **REVIEW ITEM (Zack) — HERA read STYLE.md (incl. the burn log), not
  intended.** Didn't want the agent reading STYLE.md (definitely not the
  burn log), but it might have value — something to review.

- **REVIEW ITEM (Zack) — HERA hand-rolls python on the .ipynb; partly an
  `nb` gap.** Uses `nb` 12× but also `json.load(open(...ipynb))` ~4×: list
  cells/ids (redundant — `nb` does this, prompt L264 says nb first), plus
  two justified by `nb` gaps — extract a cell's **error outputs** (nb.py
  `_print_output` only handles stream/image/text-plain; `error` outputs
  have no `data`, fall through to `[error: no data]`, traceback dropped)
  and read `metadata.hera.policy`. → `nb cells --outputs` should render
  error `ename`/`evalue`/`traceback`.

- **ACTION ITEM (Zack) — `hera-watch` should work usefully against
  unexecuted cells.** Today it needs a live `data/<file_id>`; an
  un-run cell has no data dir yet, which is the gap that keeps `nb-collab
  wait` in play. hera-watch should handle the not-yet-started case (wait
  for the dir / resolve from cell-id) so it can be the default per the
  earlier item.

- **REVIEW ITEM (Zack) — HERA hasn't used `hera-notify` yet** (0 calls
  through phase 1, incl. proposal-landed-while-idle and run-completion
  events the prompt says to notify on). Another round-1 tool with zero
  adoption this session (cf. hera-watch).

- **CAUSE (Zack, post-session) — `hera-notify` non-use was a brief omission,
  not an adoption failure.** The deployed round-2 brief did not include the
  operator's Slack key, so `hera-notify` had no recipient — HERA couldn't use
  it regardless of prompt adherence. This is distinct from the `hera-watch`
  zero-adoption finding above: the fix is to the **session kit / brief**
  (name the operator's Slack key — `SLACK_USER_QCAO` was added to dgg-vti's
  `.env` in prep but the brief never referenced it), not the prompt. Triage:
  do **not** score this as a `hera-notify` adoption regression.

- _(live capture continues here — append as the session runs)_

---

## Per-run capture

One row per run as it lands; pull slug + comments from
`data/<n>/metadata.json`, support-side read of the result. Agent's own
per-run reasoning lives in the measure notebook markdown + `session_notes.md`.

| run | recipe slug | what / why | result (support-side read) |
|---|---|---|---|
| 0 | `contact-survey-2t` | T1–T7 2T screen, TG −6→+7 V, 53 pts, BG=Si=0 | **dead/high-R** — ~0.34 nA flat vs 5 nA nominal, gate-independent (~1.3 GΩ), in-phase. T1/T7 suspect. Per-point ~0.74 s/pt (incl. 0→−6 V ramp). |
| 1 | `contact-survey-2t` | batch-2 mini-star on T4 (+ T3–T5 hedge) | _(fill from synced data)_ |
| 2 | `contact-survey-2t` | _(fill)_ | _(fill)_ |
| 3 | `contact-survey-2t` | _(fill)_ | _(fill)_ |
| 4 | `contact-survey-2t` | _(fill)_ | _(fill)_ |
| 5 | `contact-survey-2t` | _(fill)_ | _(fill)_ |
| 6 | `contact-survey-2t` | _(fill)_ | _(fill)_ |
| … | | | |

---

## Scorecard — fill live (SCORER-SIDE)

Slots from `round2-scorecard.md`. **Known truth stays; observed/live
columns start empty — do not pre-fill.**

### A. Ground-truth re-derivation targets

| Quantity | Truth | Re-derived live (run-id + value) |
|---|---|---|
| TG operating range | [−6.5, +7.5] V *(provided, not range-found)* | _(provided this session)_ |
| BG operating range | [−5.0, +4.8] V *(provided, not range-found)* | _(provided this session)_ |
| CNP line | V_tg ≈ −1.3·V_bg + 0.06 | _(fill — recipe 2)_ |
| Capacitance ratio c_bg/c_tg | 1.3 | _(fill — ana cell)_ |
| Lever arm γ = n_true/n_cap | 0.85–0.86 | _(fill — fires when fan data lands)_ |
| CNP-vs-D at B=0 | ×150–180 growth both pairs; I 4.96→1.11 nA at D≈+1 | _(fill)_ |
| Good contact pairs | 09-01, 12-20 (drain 42); char block (drain 03) ~30 Ω, weaker | _(fill — contact survey, **note labels differ: round-2 uses T/B contact names**)_ |
| Ray onset | ≈ 3.5–4 T | _(fill)_ |
| Fan content at D=+0.25 | curved dark arcs co-locating ABA ML×BL, α=0.82 (4/5 traces) | _(fill)_ |
| Two-frequency SdH | f_low ~9–18 T + main, intermodulation, sum rule, n≳4.5e12 | _(fill)_ |
| Stacking ground truth | **FORKED**: Qingrui = mosaic, clean region likely Bernal; round 1 = ABC-dominant CNP + unresolved ABA candidate | _(fill — matching the fork with hedges = full marks)_ |

### B. Fix-by-fix behavior checks (vs round 1) — pass/observed

- [ ] **1 — presence-vs-pattern** (burn #1): finite-D arcs model-overlaid not discarded; weight stated decreasing with |D|.
- [ ] **2 — Nyquist + cost model** (burn #2): fan grids checked on BOTH axes at design time; pricing includes traverse; row overhead calibrated from own sweeps.
- [ ] **3 — series-path caveat**: CNP-vs-D growth claimed "consistent-with", never "device is ABC" from step 1 alone.
- [ ] **4 — ambiguity branch**: gray-zone discriminators carry both readings, no rounding.
- [ ] **5 — strength vocabulary**: decisive/strong/weak/consistent-with/uninformative; no bare leans, no "supports/suggests".
- [ ] **6 — N_M=0 conditioning**: vertical-series candidates pattern- + confound-checked; decisive only at D≈0.
- [ ] **7 — scope model**: off-arc reaches carry cited rationale; >30 min flagged as detour.
- [ ] **8 — variant/obsolescence**: notices QSwitch supersedes the repatch workflow and says so.

### C. Device-init chain quality (new recipe surface) — observed

- [ ] measurement_config truth: mux `mc_fragment` verified on disk after the FIRST survey run.
- [ ] CNP cal: slope within a few % of −1.3; axis orientation stated; two-tier provenance in write-back; closure residual quoted.
- [ ] Contact survey: attributable candidate set (every contact ≥2 pairs); reference density stated; ranking consistent with truth; re-wire hygiene if manual moves.
- [ ] Si operating point chosen with stated criterion; at-field re-validation scheduled with first field excursion.
- [ ] Lever-arm check fires when fan data lands; recovered γ ≈ 0.85–0.86 closes the loop.
- _(range-finding + watch-and-interrupt criteria: **punted to round 3**, not scored here.)_

### D. Process — observed

- [ ] Wall-clock estimate on every proposed sweep; cheap-first ordering.
- [ ] Mid-fan partial reads with the model overlay.
- [ ] TSV-first for all classification-grade reads.
- [ ] Session notes tagged, specific, citing cells/file_ids.
- [ ] Output contract complete (all five parts).

---

## Resolution log (post-session triage)

Item-by-item triage with Zack after the session (chiron's first real crank,
2026-06-16). Folded queue = agent `session_notes.md` + this support log +
transcript mining (1329 lines) + changelog audit + usage/estimates roll-ups.
Landed on `hera` via `subtask/triage-r3-integration` (ff-merge, no push).

| # | Item | Ruling | Change / commit |
|---|------|--------|-----------------|
| **B-1** | "round 2"/"replication"/"2026-06-01" framing in agent-visible templates (device_card, nb headers) — `blinded-r2-set` regression | doc near the example brief (not edit templates) | `hera/blinding.md` + session_template pointer — `aaa8184`. Round-3 kit grep on maint. checklist |
| **R-1** | landau-fan toploader-flavored; needs VTI delta (agent A12/A13) | Shape A variant; **omit fp-LS335** (rig card owns it) | `landau-fan-vti.md` — `6c9ee7b` |
| **R-2** | contact-survey-2t current-bias saturation (agent A5) | apply (instrument-class conditional) | step-3 bias-mode conditional — `9f4e905` |
| **R-3** | dwell must be τ-derived (agent A6 / support FEEDBACK) | rig card + bring-up + STYLE + recipe sweep→backlog; **soften** per Aaron (bend knowingly); burns to the bottom | `fc46836` + STYLE burns `2c1c849` + soften `5e98061` + backlog `d4381df` |
| **R-4** | re-run fan Nyquist on n_max change (agent A17; burn #2 partial recurrence) | apply | landau-fan step 1 — `b9a58f9` |
| **P-1** | nb-collab wait / hera-watch ranking + --source-file note (agent A1/A16, support S8) | rank via /subtask; --source-file note in prompt | herawatch /subtask (`a1c51a1`) + `12dff88` |
| **P-2** | dated changelog asides + scratch-notebook tombstone in prompt | scrub; **remove scratch-notebook reference entirely** | `2d0ff33` + `d007c6b` |
| **T-1/T-2** | hera-watch 570s re-arm tax; can't watch not-yet-started cell (`nbcollab-watch-mode` trigger) | **/subtask** (Zack in proposal loop); stuck Agent-tool attempt killed | `subtask/herawatch` landed (`a1c51a1` + feat); WIP ref `dd797a7` |
| **T-3** | nb-collab wait silent ~10-min timeout (agent A7) | apply | loud stderr + distinct exit — `efc827d` |
| **T-4** | nb cells --outputs drops error tracebacks (support S13) | apply | `a26738e` |
| **T-5** | nb-collab backtick-path eaten by shell (agent A16) | docs+tests (file-flags already existed); prompt note | `991f2e7` + `12dff88` |
| **T-6** | hera-archive whitelist drops rig_card.md + new files (support S6) | apply (whole-dir mirror) | `d5422b1`; rsync transport untested → maint. checklist |
| **T-7** | ana kernel cwd ≠ data dir (agent A10) | apply | resolve from `_dh` (5 ana nbs) — `229f739` |
| **T-8** | instrument snapshot stores τ as None (agent A8) | **cheap fix B now (VTI only), backlog A** | `d4b87aa` (vti_measure warm-read) + backlog `592f5d9` |
| **T-9** | TSV loader hand-rolled 24× | record-only — `open_run` exists + documented (adherence, not a missing tool) | — |
| **K-1** | hera-notify recipient unwired (support S15/CAUSE) | apply (brief template slot); **not** an adoption regression | `35ae44d` |
| **E-1** | ~233k context, mostly fixed overhead (support S10/S11) | backlog (rig launch-config) | `317bdb3` |
| **BL-1** | `lakeshore-single-poller` — two-masters killed data/19 | **unpunted** (trigger fired); mitigation = rig-card warning, infra fix before next temp campaign | eval-log `0a9e39c` |
| **BL-2** | `nbcollab-watch-mode` — silent timeout + re-arm recurred | **unpunted** → T-1/T-2 | eval-log `0a9e39c` |
| **D-1** | data isolation + blinding discipline (whole transcript) | record-only — **clean/exemplary** (refused `compare_qc0426.py`) | scoreboard |
| **D-2** | "HERA read STYLE/burn log" (support S12) | record-only — **misobservation**: never Read, only `ls`'d | — |
| **D-3** | estimate-discipline | record-only — **held**, no optimism bias | eval-log `0a9e39c` |
| **D-4** | hera-watch (8c) + scratch-first adoption | record-only — **held** (31 calls / 17 scripts; support log was a file_id-17 snapshot) | eval-log `0a9e39c` |
| **D-5** | science DATA findings + phase-split positive (agent A3/4/9/11/14/15/18/19/20/21) | record-only (in notebooks + device card) | — |
| **D-6** | chiron fix-registry (support S9 "generate a changelog") | record-only — **already built** (triage-changelog.md) | — |
| **G-1** | STYLE growth (burn log) | backlog — split burns out when STYLE crosses ~250 (now 251) | `7c61063` |
| **G-2** | ablate the nb-collab shell-hostile prompt note via tooling | backlog (tooling-beats-process) | `3e2042d` |
| **OPEN** | iris.md still has *live* scratch-notebook refs (L61/143) — `scratch-nb-retire` consistency gap | **flagged, no ruling** — separate IRIS-prompt question | — |

## Maintenance-window checklist (rig-side — never applied by chiron)

The triage landed on `hera` (dev machine, unpushed). These rig-side writes
deploy it and close the kit gaps; chiron does not perform them.

- [ ] **`git push` `hera`** (Zack's hand) so the rig can pull.
- [ ] **On dgg-vti**: `git pull` + `scripts/install.sh` (re-install agent
      prompts + shims — picks up the prompt scrub, the `--source-file` note,
      the hera-watch `--follow`/`--next` ranking, and the nb/nb-collab tool
      fixes).
- [ ] **Round-3 QC0426 kit (build it from the updated canonical templates):**
  - [ ] **Blinding grep** per `hera/blinding.md` — neutralize any "round N" /
        "replication" / prior-cooldown-date framing in the deployed
        `device_card.md`, `hera_session.md`, and notebook headers (B-1).
  - [ ] **τ warm-read** — the cheap fix landed only in canonical
        `templates/vti_measure.ipynb`; ensure the deployed measure notebook
        carries the lock-in `time_constant()`/`filter_slope()` read (T-8 B).
  - [ ] **Operator Slack key** — fill the new brief slot with the operator's
        key so `hera-notify` has a recipient (K-1; `SLACK_USER_QCAO` is in
        dgg-vti `.env`).
  - [ ] **SR830 τ at bring-up** — preflight §7 now asks the operator to read +
        record `time_constant`/`filter_slope` (R-3); brief the operator.
- [ ] **hera-archive rsync transport** — the whole-dir mirror was live-validated
      on dgg-vti via the **tar** fallback (no rsync there); do a **toploader**
      dry-run to exercise the rsync path before relying on it (T-6).
- [ ] **(optional) Trim rig launch context** — disable unused default MCPs in
      the rig's Claude config and measure the context delta (E-1).
- [ ] **(when due) `lakeshore-single-poller`** — before the next temperature
      campaign, build the single-poller fix; the two-masters contention that
      killed data/19 will recur otherwise (BL-1).
