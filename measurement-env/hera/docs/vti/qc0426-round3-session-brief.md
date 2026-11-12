# QC0426 / VTI — session brief

*Session context for the agent-driven measurement session on the VTI.
This file is the `hera-tactical` agent's first message — it names the
goal, activates the recipes, and carries the session-specific facts.
Protocol, gates, and boundaries live in your agent prompt; the physics
method lives in the recipes; this brief does not restate either.*

## Contract — autonomous

This session runs **autonomous (E1)**. After the operator gives the grant
(below) **you execute measure cells yourself**; you are not waiting for a
keystroke per cell. The operator (Zack) supervises, is reachable on Slack,
and can stop any running cell or withdraw the grant at any time. The
deployed measure-notebook policy (`append_exec`) is the hard gate on
execution; the grant is the protocol gate on top.

## Autonomy — this session's parameters

- **Mode:** E1 (autonomous).
- **Grant:** the operator says **"go for autonomy"** once session-start
  VERIFY and SAFETIES are green. Record it in `session_notes.md` and
  engage; until then you are in E0 (you propose, the operator runs).
- **Operator + notify:** Zack — `hera-notify --user ZACKG`.
- **Auto:** in-envelope measure cells (sweeps, gate sets, ContactMux
  routing) that stay inside the committed validators and pass their
  precondition reads; D-fans; field moves within the |B| ≤ 8 T cap.
- **Consent-gated:** none this session.
- **Session-banned** (never, regardless of grant): any change to a safety
  surface — the SAFETIES validators, the gate operating limits, or the
  field cap; and the blocklisted recipes below (temperature, gate leakage,
  range-finding).
- **Withdraw / drop:** the operator can withdraw the grant → you revert to
  E0. You are free to stop, notify, and drop to E0 on any device- or
  rig-safety concern.

## Campaign goal

**Determine the stacking order of QC0426 (trilayer graphene): ABA
(Bernal) vs ABC (rhombohedral)** — an independent, evidence-cited,
region-resolved call (or a calibrated "cannot tell"), per the governing
investigation's output contract.

## Recommended recipes

The expected arc:

- `investigations/trilayer-stacking-fs-count.md` — the **governing
  investigation** (Fermi-surface counting at D ≈ 0): the decision
  procedure, the Verify suite, and the five-part output contract. It
  orchestrates the measurement recipes below.
- `device-init/cnp-and-dline-calibration.md` — the CNP location and
  (n, D) calibration, **found fresh this session** (the device card
  carries no CNP).
- `measurements/landau-fan.md` (the VTI variant takes precedence).
- `measurements/gatemap.md`.

The rest of the corpus is available, not forbidden; off-arc composition
with stated rationale is encouraged under your scope rules (>~30 min
off-arc gets the detour flag). The **contact configuration is provided**
(device card) — no contact survey is in the arc; `contact-survey-2t`
remains available if a provided contact proves dead.

**Tool:** the FS-count forward model
(`hera/models/trilayer_fs_count/fs_count_b0.py`) is the primary
arc-reader, per the investigation's Verify.

## Blocklist

- `measurements/temperature-dependence.md`
- `device-init/gate-leakage-survey.md`
- `device-init/gate-range-finding.md` (+ `-vti` variant)
- `device-init/silicon-backgate-survey.md`

"Range-finding" here is the leakage / gate-range **survey** class — it does
**not** restrict `cnp-and-dline-calibration` or CNP / (n, D) location.

## Data isolation — strict

**No prior measurement data exists for you.** Do not read other campaign
or session directories. Your only inputs: this brief, the device card, the
rig card, the recipes/corpus they name, and the data this session produces
in `./data/`. The recipes' first-session branches apply. Provided up front
(device card): the gate operating limits, the QSwitch wiring, and a workable
contact configuration. **Not** provided — established in-session: the CNP
location and the (n, D) calibration.

## Session arc

1. **Bring-up.** The operator runs the setup section (instrument connect —
   gate A) and the SAFETIES cell (gate B). VERIFY (below) green.
2. **Grant.** Operator's **"go for autonomy"** → E1.
3. **Autonomous.** Gate C (a cheap liveness check on the provided contact
   configuration — first-session branch, no designated references), then
   the investigation ladder per `trilayer-stacking-fs-count.md`, to the
   five-part call in the ana notebook.

## Timing

Soft deadline **2026-06-16, 3 pm PT**. Actively measure until **11 am PT**
unless nothing useful is left to do.

## [VERIFY] at session start

- [ ] Magnet at 0 T (set vs read): `print(magnet.mag(), magnet._status()['field'])`.
- [ ] SAFETIES committed = the device card's gate operating limits
      (TG / BG / Si); field cap |B| ≤ 8 T on the `magnet.mag` validator.
- [ ] Base (sample) T holding ≈ 1.2–1.3 K; He budget for the session.
- [ ] QSwitch live (ASRL4, `settle_s` 4 s, Si standing closures 16/11
      closed); the provided contact configuration selects cleanly.
- [ ] Operator's **"go for autonomy"** — after the above, the grant
      engages E1.

## Session notes

Maintain `session_notes.md` per your agent prompt (RECIPE FIX / TOOLING /
PROTOCOL / FEEDBACK). This is the first autonomous session — protocol and
tooling friction are a primary deliverable, not paperwork.
