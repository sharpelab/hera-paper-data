# {{ALIAS}} / VTI — session brief

*Session context for the agent-driven measurement session on the VTI. This file is
the `hera-tactical` agent's first message — it names the goal, activates the recipes,
and carries the session-specific facts. Protocol, gates, and boundaries live in your
agent prompt; the physics method lives in the recipes; this brief does not restate
either.*

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
  committed validators and pass their precondition reads; D-fans; field moves within
  the device-card field cap; temperature moves via `heater.set_both(T, ratio=0.95)`
  within the device-card T cap, under the temperature-dependence-vti guard set
  (hover acceptance, descend-catch, direction-aware runaway, freshness guards).
- **Consent-gated:** any deviation from `ratio = 0.95` in `set_both`.
<!-- IF-SI-GATE -->
- **Consent-gated (Si):** the Si (DC205) ramp — keep the gate-safe pacing;
  `dc205.ramp_rate` is consent-gated (never raise without operator consent).
<!-- END-IF-SI-GATE -->
- **Session-banned** (never, regardless of grant): any change to a safety surface —
  the SAFETIES validators, the gate operating limits, the field cap, or the
  T-setpoint cap; and the blocklisted recipes below.
- **Withdraw / drop:** the operator can withdraw the grant → you revert to E0. You are
  free to stop, notify, and drop to E0 on any device- or rig-safety concern. After any
  stop/E0 drop, resume autonomous execution **only on an explicit E1 re-grant**.

## Campaign goal

<!-- IF-MATERIAL-3LGr -->
**Determine the stacking order of {{ALIAS}} (trilayer graphene): ABA (Bernal) vs ABC
(rhombohedral)** — an independent, evidence-cited, region-resolved call (or a
calibrated "cannot tell"), per the governing investigation's output contract.
<!-- END-IF-MATERIAL-3LGr -->
<!-- IF-MATERIAL-4LGr -->
**Determine the stacking order of {{ALIAS}} (tetralayer graphene): ABAB (Bernal) vs
ABCA (rhombohedral) vs ABCB (mixed)** — an independent, evidence-cited,
region-resolved call (or a calibrated "cannot tell"), per the governing
investigation's output contract.
<!-- END-IF-MATERIAL-4LGr -->

## Recommended recipes

The expected arc:

<!-- IF-MATERIAL-3LGr -->
- `investigations/trilayer-stacking-fs-count.md` — the **governing investigation**
  (Fermi-surface counting at D ≈ 0): the decision procedure, the Verify suite, and the
  output contract. It orchestrates the measurement recipes below.
<!-- END-IF-MATERIAL-3LGr -->
<!-- IF-MATERIAL-4LGr -->
- `investigations/tetralayer-stacking-fs-count.md` — the **governing investigation**
  (Fermi-surface counting at D ≈ 0): the decision procedure, the Verify suite, and the
  output contract. It orchestrates the measurement recipes below.
<!-- END-IF-MATERIAL-4LGr -->
- `device-init/cnp-and-dline-calibration.md` — the CNP location and (n, D) calibration,
  **found fresh this session** (the device card carries no CNP).
- `measurements/sdh-spot-check.md` — the cheap fixed-(n, D) SdH frequency-content check
  that precedes the fan: it pins the onset, the tone frequencies, the B-step, and which
  side (hole/electron) gives cleaner SdH.
- `measurements/landau-fan.md` (the VTI variant takes precedence).
- `measurements/gatemap.md`.
- `measurements/temperature-dependence.md` (the VTI variant takes precedence — its
  guard set is mandatory for every elevated-T segment). The investigation's LK
  mass split (Verify) is in-arc, not a detour.

The rest of the corpus is available, not forbidden; off-arc composition with stated
rationale is encouraged under your scope rules (> ~30 min off-arc gets the detour
flag). The **contact configuration is provided and hardwired** (device card) — no
contact survey is in the arc, and there is no mux to reroute with: a dead provided
contact is an operator rewiring problem — flag it, don't detour.

<!-- IF-MATERIAL-3LGr -->
**Tool:** the FS-count forward model (`hera/models/trilayer_fs_count/fs_count_b0.py`)
is the primary arc-reader, per the investigation's Verify.
<!-- END-IF-MATERIAL-3LGr -->
<!-- IF-MATERIAL-4LGr -->
**Tool:** the FS-count forward model (`hera/models/tetralayer_fs_count/fs_count_b0.py`)
is the primary arc-reader, per the investigation's Verify.
<!-- END-IF-MATERIAL-4LGr -->

## Blocklist

- `device-init/gate-leakage-survey.md`
- `device-init/gate-range-finding.md` (+ `-vti` variant)
- `device-init/silicon-backgate-survey.md`

"Range-finding" here is the leakage / gate-range **survey** class — it does **not**
restrict `cnp-and-dline-calibration` or CNP / (n, D) location.

## Data isolation — strict

**No prior measurement data exists for you.** Do not read other campaign or session
directories. Your only inputs: this brief, the device card, the rig card, the
recipes/corpus they name, and the data this session produces in `./data/`. The
recipes' first-session branches apply. Provided up front (device card): the gate
operating limits and the hardwired contact configuration. **Not** provided —
established in-session: the CNP location and the (n, D) calibration.

## Session arc

1. **Bring-up.** The operator runs the setup section (instrument connect — gate A) and
   the SAFETIES cell (gate B). You author and land the VERIFY cell (below).
2. **Grant.** Operator's **"go for autonomy"** → conditional E1: kernel probe +
   VERIFY execute first; E1 engages on the green verdict.
3. **Autonomous.** Gate C (a cheap liveness check on the provided contact configuration
   — first-session branch, no designated references), then the investigation ladder per
   the governing investigation (Recommended recipes), to the call in the ana notebook.
4. **Close-out.** Ask: `return-to-initial` — per
   `recipes/utils/session-closeout.md` (+ VTI variant).

## [VERIFY] at session start

- [ ] Magnet at 0 T (read): `print(magnet.field(), magnet._status()['field'])`.
- [ ] SAFETIES committed = the device card's gate operating limits; field cap on
      the `magnet.field` validator and the T-setpoint typo-guard cap per the
      device card.
- [ ] Base (sample) T holding ≈ 1.2–1.3 K; He budget for the session.
- [ ] Heaters off (both ranges 0); `T_vaporizer` tracking base.
- [ ] Contacts hardwired (no mux this cooldown) per the device card.
<!-- IF-SI-GATE -->
- [ ] DC205 (Si gate) on its ±100 V range (RNGE 2), output on, reading 0 V.
<!-- END-IF-SI-GATE -->
- [ ] Kernel-binding: the first E1 execute is a read-only namespace probe that confirms
      it is bound to the operator's instrument-carrying kernel.

The checks above are the VERIFY cell's content — you author it, read-only by
construction, ending with the machine-readable verdict line (`VERIFY: ALL
GREEN` / `VERIFY: FAIL <item>`). The operator's **"go for autonomy"** may
arrive as soon as the cell is landed; execution of VERIFY is your first E1 act
after the kernel probe, and the grant engages on the printed green verdict
(Autonomy — Grant, above).

## Session notes

Maintain `session_notes.md` per your agent prompt (RECIPE FIX / TOOLING / PROTOCOL /
FEEDBACK).
