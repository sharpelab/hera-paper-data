# zf1 / toploader — session brief

*This file defines the session — it names the goal, activates the recipes, and
carries the session-specific facts. Protocol, gates, and boundaries live in your
agent prompt; the physics method lives in the recipes; this brief does not
restate either.*

## Contract

- **HERA** — drives the session arc: decides what to measure next, reads every
  sweep from disk, commits to a direction, and proposes paired markdown+code
  cells. Protocol, gates, and boundaries: your agent prompt — this brief does
  not repeat them.
- **Aaron — operator.** At the keyboard. Executes every cell; running a cell IS
  the approval handshake; declining is the veto; interrupting a running cell is
  always his prerogative (partial runs land readable). Owns every instrument
  write and all physical rig actions. Agent cells land *un-executed* — review,
  edit if needed, run or skip.

## Autonomy — E1 this round

- **Mode:** E1 (autonomous).
- **Grant:** the operator says **"go for autonomy"** once session-start VERIFY and
  SAFETIES are green. Record it in `session_notes.md` and engage; until then you are
  in E0 (you propose, the operator runs).
- **Operator + notify:** Aaron — `hera-notify --user ASHARPE` (run-completion /
  proposal-landed-while-idle pings).
- **Auto:** in-envelope measure cells (sweeps, gate sets, ContactMux routing) that
  stay inside the committed validators and pass their precondition reads; D-fans;
  field moves within the device-card field cap.
- **Session-banned** (never, regardless of grant): any change to a safety surface —
  the SAFETIES validators, the gate operating limits, or the field cap; and the
  blocklisted recipes below.
- **Withdraw / drop:** the operator can withdraw the grant → you revert to E0. You are
  free to stop, notify, and drop to E0 on any device- or rig-safety concern. After any
  stop/E0 drop, resume autonomous execution **only on an explicit E1 re-grant**.

## Campaign goal

**Does this device superconduct? If so characterize the superconducting state.**
Deliver an evidence-cited, per-candidate call per the governing investigation's
output contract: a calibrated SC determination (superconductor / failed-SC ·
anomalous-metal / not-SC / cannot-tell) on the STYLE strength scale, with the
properties you can extract.

## Recommended recipes

The governing investigation and the measurements it orchestrates:

- `investigations/sc-characterization.md` — the **governing investigation**:
  locate candidate low-Rxx regions → confirm SC against its confounds (the
  constellation call; the failed-SC / anomalous-metal fork) → characterize →
  the five-part output contract. Read its two reference papers before claiming a
  feature.
- `measurements/nD-map.md` / `gatemap.md` — the (n, D) map that locates
  candidates (pristine-field map first, per the investigation's Step 1).
- `measurements/bias-spectroscopy.md` — dV/dI vs I_dc and the Ic read: the
  engine behind Ic(n), Ic(T), Ic(B).
- `measurements/field-sweep-1d.md`, `fraunhofer.md` — field response (B_c⊥,
  phase-coherent oscillations); these reads are mT-scale, within the session
  field cap.
- `measurements/temperature-dependence.md` — Tc / T_BKT (heat up LAST).

Normal-state fermiology (`landau-fan.md` / `sdh-spot-check.md`, the
investigation's Step 4) needs Tesla-scale field — **out of reach under this
round's 100 mT cap; defer to a higher-field round.**
- `device-init/cnp-and-dline-calibration.md` — confirm the (n, D) calibration
  (the device card's geometry is a flagged prior, not blessed).

The rest of the corpus is available, not forbidden; off-arc composition with
stated rationale is encouraged (> ~30 min off-arc gets the detour flag).

## Blocklist

- **The rotator (ANC350 θ/φ) and all in-plane-field / TRS / Hc2-anisotropy
  work** — out of scope this campaign. Do not move the rotator; do not attempt
  in-plane field work.
- Device-init **surveys** (`gate-range-finding`, `gate-leakage-survey`,
  `silicon-backgate-survey`) — not in the arc; the gate operating limits are
  provided (device card), and there is no Si gate. This does **not** restrict
  `cnp-and-dline-calibration` (CNP / (n, D) location).

## Data isolation — strict

**No prior measurement data exists for you.** Do not read other campaign or
session directories, and specifically not: any campaign synopsis, notebook
index, prior session / measurement directory, or any "hard-limits" / "state"
handoff document — they carry prior results. Your only inputs: this
brief, the device card, the rig card, the recipes/corpus they name (and the
recipes' reference papers), and the data this session produces in `./data/`. The
recipes' first-session branches apply. Provided up front (device card): the gate
operating limits (commit as validators) and the contact wiring. **Not** provided
— established in-session: the (n, D) calibration (confirm the card's prior),
where (if anywhere) the device superconducts, and the SC parameters.

## Field discipline — this session

**Session field cap: |B| ≤ 100 mT** (out-of-plane). All field work this round
stays within it; the SC field reads (B_c⊥, Fraunhofer) are mT-scale and fit.

Per the rig card's machine field behavior (crossing B = 0 injects eddy-current
heat; direction reversal leaves mT-scale remanence): take every quantitative
B-sweep one-sided and monotonically toward 0 — ramp to the extreme |B|, settle,
sweep down. **Never increase |B| through B = 0 during a measurement.** Settle
after each ramp before sweeping, scaled to the ramp magnitude; derive the settle
from this session's own ramps (rig card Timing rules) and price it into 2D field
runs. The investigation's effective-zero-field step (the SC's own field maximum
≠ the controller's nominal zero) is downstream of this.

## Live plots — verbatim, every sweep

Every sweep stands up exactly these plots, in this order — leakage vs `'time'`,
transport channels vs the sweep's fast axis `xp`:

    s.plot('time', k_tg.curr)  # TG leakage
    s.plot('time', k_bg.curr)  # BG leakage
    s.plot(xp, sr830_1.X)      # current monitor (~1 nA flat)
    s.plot(xp, sr830_2.X)      # 2T (5-4)
    s.plot(xp, sr830_3.X)      # 4T Rxx (30-31)

## Session arc

1. **Bring-up.** Operator runs setup (gate A) + the SAFETIES cell (gate B).
   VERIFY (below) green.
2. **Gate C.** A cheap liveness check on the provided contact wiring
   (first-session branch — no references).
3. **The investigation ladder** per `sc-characterization.md`: pristine-field map
   → candidate nonlinear characterization → field response → (heat up last)
   T-dependence → the call in the ana notebook.

## [VERIFY] at session start

- [ ] Magnet at 0 T (set vs read): `magnet.field()`.
- [ ] SAFETIES committed = device card gate operating limits (TG / BG); field
      cap |B| ≤ 100 mT committed on the magnet validator.
- [ ] Base (sample) T holding (mK range); workers green / temperature logfiles
      fresh.
- [ ] Provided contact wiring reads cleanly (no mux — wired direct); a
      four-terminal Rxx channel is live.
- [ ] Heater ownership + ceiling (device card) if temperature work arises.

## Session notes

Maintain `session_notes.md` (RECIPE FIX / TOOLING / PROTOCOL / FEEDBACK). The SC
measurement recipes (`bias-spectroscopy`, `fraunhofer`) are new surface — RECIPE
FIX entries are a primary deliverable.
