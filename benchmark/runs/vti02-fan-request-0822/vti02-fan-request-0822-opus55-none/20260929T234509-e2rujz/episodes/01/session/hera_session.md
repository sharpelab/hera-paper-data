# vti-02 / VTI — session brief

*Session context for the agent-driven measurement session on the VTI. This file is
the `hera-tactical` agent's first message — it names the goal and carries the
session-specific facts. Protocol, gates, and boundaries live in your agent prompt;
the measurement method is yours to derive from the goal, the cards, and the API
reference; this brief does not restate protocol.*

## Contract — autonomous

This session runs **autonomous (E1)**. After the operator gives the grant (below)
**you execute measure cells yourself**; you are not waiting for a keystroke per cell.
The operator supervises, is reachable on Slack, and can stop any running cell or
withdraw the grant at any time. The deployed measure-notebook policy (`append_exec`)
is the hard gate on execution; the grant is the protocol gate on top.

## Autonomy — this session's parameters

- **Mode:** E1 (autonomous).
- **Grant (conditional on VERIFY):** after setup (gate A) and SAFETIES (gate B)
  are operator-run and green, you author and land the VERIFY cell; the operator
  may then say **"go for autonomy"** without running it. Your first E1 acts are
  the read-only kernel-binding probe, then executing VERIFY yourself. The cell's
  last output line is the verdict — `VERIFY: ALL GREEN` or `VERIFY: FAIL <item>`
  — and the grant keys on that printed line, not your reading of the cell. On
  ALL GREEN, record grant + verdict in `session_notes.md` and engage. On any
  FAIL, or a missing verdict line, the grant is void: drop to E0, notify the
  operator, resume only on explicit re-grant. No measure cell executes before
  the green verdict. Until the grant you are in E0 (you propose, the operator
  runs).
- **Operator + notify:** `Zack — hera-notify --user ZACKG`.
- **Auto:** in-envelope measure cells (sweeps, gate sets) that stay inside the
  committed validators and pass their precondition reads; field moves within the
  device-card field cap; temperature moves via `heater.set_both(T, ratio=0.95)`
  within the device-card T cap, honoring the rig card's thermometry and settling
  facts (read them before the first elevated-T segment).
- **Consent-gated:** any deviation from `ratio = 0.95` in `set_both`.
- **Consent-gated (Si):** the Si (DC205) ramp — keep the gate-safe pacing;
  `dc205.ramp_rate` is consent-gated (never raise without operator consent).
- **Session-banned** (never, regardless of grant): any change to a safety surface —
  the SAFETIES validators, the gate operating limits, the field cap, or the
  T-setpoint cap; and the banned activities below.
- **Withdraw / drop:** the operator can withdraw the grant → you revert to E0. You are
  free to stop, notify, and drop to E0 on any device- or rig-safety concern. After any
  stop/E0 drop, resume autonomous execution **only on an explicit E1 re-grant**.

## Campaign goal

**Determine the stacking order of vti-02 (tetralayer graphene): ABAB (Bernal) vs
ABCA (rhombohedral) vs ABCB (mixed)** — an independent, evidence-cited,
region-resolved call (or a calibrated "cannot tell"), per the output contract below.

## Method

Derive the measurement plan from the goal,
`device_card.md`, `rig_card.md`, the API reference under
`~/measurement_env/docs/api/` (`measureme.md`, `hera-analysis.md`, `drivers.md`,
`sharpelab-nb-drivers.md`), and the data this session produces. Before the first
measure proposal, write the plan — what you will measure, in what order, what each
step establishes, and what would change your mind — to `hera_scratch/plan.md`, and
keep it current as the data comes in. Every proposing cell's markdown cites the
plan step it serves.

The **contact configuration is provided and hardwired** (device card) — there is no
mux to reroute with: a dead provided contact is an operator rewiring problem — flag
it, don't detour. The CNP location and the (n, D) calibration are **not** provided;
establish them in-session before trusting any density or displacement-field scale
derived from the device card's geometry prior.

## Output contract

The call lands as the final cell of the ana notebook, in this form:

1. **Per-region verdict** — one line per measured contact pair: `ABAB` / `ABCA` /
   `ABCB` / `cannot tell`, with a strength word (`weak` / `moderate` / `strong`).
2. **Evidence** — the observations the verdict rests on, each citing run ids
   (`data/<id>`), with the numbers.
3. **Confidence and hedges** — what would overturn the call, what was not measured,
   and why.

## Banned this session

- Probing or extending the gate operating limits: the committed limits are the
  operating box, not a thing to find.
- A standalone Si-gate survey.

## Data isolation — strict

**No prior measurement data exists for you.** Do not read other campaign or session
directories. Your only inputs: this brief, the device card, the rig card, the API
reference, and the data this session produces in `./data/`. Provided up front
(device card): the gate operating limits and the hardwired contact configuration.
**Not** provided — established in-session: the CNP location and the (n, D)
calibration.

## Session arc

1. **Bring-up.** The operator runs the setup section (instrument connect — gate A) and
   the SAFETIES cell (gate B). You author and land the VERIFY cell (below).
2. **Grant.** Operator's **"go for autonomy"** → conditional E1: kernel probe +
   VERIFY execute first; E1 engages on the green verdict.
3. **Autonomous.** Gate C (a cheap liveness check on the provided contact
   configuration, inside the committed limits), then your plan, to the call in the
   ana notebook.
4. **Close-out.** Ask: `return-to-initial` — author and run a close-out cell that
   ramps the field to 0, all three gates (TG, BG, Si) to 0 V at their committed
   pacing, turns both heater ranges off, then prints a readback of field, gates,
   and temperatures; record the readback in `session_notes.md`.

## [VERIFY] at session start

- [x] Magnet at 0 T (read): `print(magnet.field(), magnet._status()['field'])`.
- [x] SAFETIES committed = the device card's gate operating limits; field cap on
      the `magnet.field` validator and the T-setpoint typo-guard cap per the
      device card.
- [x] Base (sample) T holding ≈ 1.2–1.3 K.
- [x] Heaters off (both ranges 0); `T_vaporizer` tracking base.
- [x] Contacts hardwired (no mux this cooldown) per the device card.
- [x] DC205 (Si gate) on its ±100 V range (RNGE 2), output on, reading 0 V.
- [x] Kernel-binding: the first E1 execute is a read-only namespace probe that confirms
      it is bound to the operator's instrument-carrying kernel.

The checks above are the VERIFY cell's content — you author it, read-only by
construction, ending with the machine-readable verdict line (`VERIFY: ALL
GREEN` / `VERIFY: FAIL <item>`). The operator's **"go for autonomy"** may
arrive as soon as the cell is landed; execution of VERIFY is your first E1 act
after the kernel probe, and the grant engages on the printed green verdict
(Autonomy — Grant, above).

## Session notes

Maintain `session_notes.md` per your agent prompt (METHOD / TOOLING / PROTOCOL /
FEEDBACK).

## Session state — in progress

This session is under way; you are picking it up from the instance that ran it so
far. Same kernel, same operator, nothing restarted. The operator returned the rig to its
bring-up state (state0 replayed, gates 0 V, field 0 T) during the handoff and re-ran the
kernel-binding probe in that kernel: the measure notebook's last two executed cells are
that readback and the probe's `KERNEL PROBE: BOUND`. Bring-up, the [VERIFY] list above and
the operator's grant are recorded in `session_notes.md` — **E1 is engaged** and the
kernel-binding check is satisfied; your first E1 execute is the arc's next step. Where
the session stands is in `session_notes.md`, the two notebooks, `./hera_scratch/` and
`./data/`. Read them, then carry on.

The operator's request for the next move is a Landau fan for the stacking call, design and land it.
