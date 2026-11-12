# HERA tactical session — postmortem (2026-06-23, zf1 / Aaron)

> **Archive note:** a bare parallel archive of this session also exists at
> `2026-06-23-zf1-session/` (notebooks + data + cards only, from a separate
> run). **This `-full` directory is the canonical record** — it adds this
> POSTMORTEM, `wiki_notes.md`, and the full `hera_scratch/` analysis trail.

zf1 bottom-device superconductivity characterization on the toploader. ~16 h
live tactical session (06-23 15:14 → 06-24 00:24), **E0 / blinded**,
`append_only`, B ≤ 100 mT. `hera-session` init run from `~/measurement_env`;
tactical launched into the session dir.

## Outcome

**zf1 (bottom device): superconductor (strong)** — gate-tuned proximity SC in
BBG/WSe₂ on the hole side at favorable D<0. n ≈ −5.2×10¹¹ cm⁻², D ≈ −0.645 V/nm,
I_c ≈ 30 nA, B_c⊥ ≈ 2.5–3 mT, ξ ~ 0.3 µm, uniform-2D (no Fraunhofer), onset
Tc ≈ 0.30 K. Cap ratio c_bg/c_tg = 1.19 (confirms card prior). Full call in
`hera_scratch/_call_md.txt` / ana cell 33. Path to decisive: R_xy pair, clean
Tc/T_BKT ladder, second-contact reproduction, push |D| past 0.68 V/nm.

## ⚠ Tactical transcript lost

The tactical chat transcript did not persist. `hera-session` (`aa4a0072`, run
from `measurement_env`) launched tactical via
`newclaude <session-dir> --agent hera-tactical`; the spawned session's
`.claude.json` cwd entry shows `history=0` and **no `.jsonl` was written**
anywhere on the rig (verified by whole-disk search). The agent ran ~16 h and
wrote all its work products to the session dir, but the conversation log is gone.

- **Recovered** (substance intact): `session_notes.md`, `hera_scratch/` (~90
  files — analysis stagers, plots, `*.npz`), the notebooks, and Aaron's wiki
  notes (`wiki_notes.md`).
- **Lost**: the agent's reasoning/dialogue.
- **Backlog item:** `newclaude` Windows tactical-spawn reliability — a 16 h
  session leaving no transcript is a data-loss bug. Add a post-launch check that
  the tactical session actually wrote a transcript before the operator commits
  to it.

## Heater settle calibration (rig-card correction)

Calibrated fridge thermal settle vs heater voltage on **Probe1** (the rig card
says to derive it from a session's own ramps). Settle = time for |dT/dt| below
threshold. **Settle is strongly asymmetric, and the card's flat "5 min/1 V" only
holds at the low-mid range.**

Cooling / DOWN ladder (adaptive, settle-verified, |dT/dt| < 1 mK/min sustained):

| Step | Settle |
|---|---|
| 6→5 V | ~14 min (840 s) |
| 5→4 V | ~13 min (780 s) |
| 4→3 V | ~13 min (780 s) |
| 3→2 V | ~13 min (780 s) |
| 2→1 V | ~15 min (880 s, glitchy) |
| 1→0 V | ~8 min (480 s) |

Heating / UP ladder: ~2–7 min/step, but a **long slow tail above ~4 V** — 6 V
kept creeping (8.4 mK/min) and only plateaued (~405 mK) ~25–30 min after the
step (the card's 423 mK is high). The first UP ladder (runs 34–39, back-to-back,
no settle between steps) was invalid — caught by Aaron; the adaptive redo
confirmed it.

**Operating rule: budget ~15 min per 1 V cooling step.** Heating is faster
(~2–7 min) but high-V (>4 V) steps still need ≥15 min for the slow tail.
Asymmetry: heating is heater-power-driven, cooling is fridge-cooling-power-
limited (~4× at the bottom rung — up 0→1 V ~2 min vs down 1→0 V ~8 min).
Raw T(t) traces: `hera_scratch/settle_down_*.npz`; writeups: `_settleup_md`,
`_settledown_md`, `_adown_md`, `_aup_md`.

## What broke / triage items

From `session_notes.md` + Aaron's wiki notes (`wiki_notes.md`):

- **Thermometry ran on a dead probe.** Probe2 was frozen 3.3 days (read 33.7 mK
  every run) and went undetected until the T-ladder; re-pointed to Probe1. The
  `assert temperature() < 0.1` precondition can't catch a frozen-but-plausible
  value. Fix: thermometry bring-up should read BOTH probe logfiles and
  auto-select the fresh/advancing one; flag "T identical to N decimals across N
  runs" as stale. Blocks only Tc; all base-T results stand.
- **gate-current-sanity-check.** Only swept ±2 V (not full range), inset the
  gatemap 0.2 V inside the validators (overridden — the validators ARE the
  known-safe envelope), and didn't propose the multiple legs itself. Consider a
  rebuild or replacement with a reentry-baseline.
- **Interruptibility.** nb-collab interrupt did not stop the Tc ladder (runs 26,
  27 ran after the interrupt). Use interruptible sleeps generally; design long
  instrument-bound loops to check an abort flag.
- **Field sweep should cross zero**, not run from a value to zero.
- **Fraunhofer current span too narrow.**
- **Bias spectroscopy** doesn't account for coherence peaks. (Otherwise a good
  new surface: the DC205 `.volt` direct-set path has no 10 s settle, so bias
  sweeps are fast — 302 pt in 6 min, vs sizing it as a ~1 h run.)
- **CNP extraction.** 2T argmax fails here (contact features + V_bg~0 stripe pull
  the peak off the CNP); 4T + iterative 2σ outlier rejection works. Prefer 4T
  robust fit; never 2T argmax.
- **Slot-fill placeholders recurred:** B-cap 5.0 T vs the brief's 0.1 T; ana
  geometry t_tg/t_bg wrong vs card (23.6 / 20 nm). Both caught at init.
- **Toploader heating tooling** missing — wants a simple "temp A→B with progress
  print" helper.
- **Live plots** should plot all live values (gatemap didn't plot gate current);
  the hera-watch digest omits the gate-current fp columns.

## Artifacts

This directory: notebooks, `data/`, `device_card.md`, `rig_card.md`,
`hera_session.md`, `session_notes.md`, `hera_scratch/`, `wiki_notes.md`.
`transcripts/`: `aa4a0072` (hera-session init + the 06-24 transcript-recovery
query), `d1fe1407` (13-line false start). **Tactical transcript absent — see
above.**

## Triage resolution (chiron, 2026-06-24)

Merged queue: `session_notes.md` + wiki support log (`wiki_notes.md`) +
this POSTMORTEM + the changelog recurrence audit. Landed on
`subtask/triage-20260623-zf1`. Recipe-science (A/B/C/K) drafted minimal +
routed to `aaron-handoff.md` for the science pass (Aaron's ruling).

| # | Item | Ruling | Change / commit |
|---|---|---|---|
| A | Bias spec ignores coherence peaks (W6) ⚠recur T2 | apply (recipe-sci) | `sc-characterization` Step 2 + `bias-spectroscopy` Verify · `400f4aa` |
| B | Field sweep one-sided, not across zero (W7) ⚠recur T3 | apply (recipe-sci) | `sc-characterization` Step 3 · `400f4aa` |
| C | Fraunhofer current span too narrow (W8) ⚠recur T3 | apply (recipe-sci) | `sc-characterization` Step 3 · `400f4aa` |
| K | CNP: never 2T argmax; 4T + 2σ robust fit | apply (recipe-sci) | `cnp-and-dline-calibration` Step 1 · `8d52458` |
| I | Heater "5 min/1 V" wrong | apply — **modified** (asymmetry claim cut: up ladder invalid) | `rig-cards/toploader.md` · `d353cdf` |
| J | DC205 `.volt` has no 10 s settle (fast bias) | apply | `rig-cards/toploader.md` · `d353cdf` |
| E | Dead probe undetected 3.3 d (W10) | apply cheap (card + template mtime guard); deeper → backlog | `toploader.md` + `toploader_measure.ipynb` · `d353cdf`/`94a2a2e` |
| G | Plot all live values; gatemap plots gate current (W5) | apply (prompt); hera-watch tooling → backlog | `hera_tactical.md` · `70b060f` |
| D | Slot-fill placeholders recurred (W1): B-cap 5 T vs 0.1 T, geometry | backlog (safety-flagged) | `eng-backlog.md` · `8d39456` |
| F | Heater ramp helper missing (W9) | backlog | `eng-backlog.md` |
| H | Interrupt didn't stop the Tc ladder (W12) | backlog (safety) | `eng-backlog.md` |
| L | Inset committed validators 0.2 V (FEEDBACK) | backlog/watch (one incident) | `eng-backlog.md` |
| N | `newclaude` 16 h session left no transcript | backlog | `eng-backlog.md` |
| M | Gate-range ±2 V / mangled limits / no multi-leg (W2/W3/W4) ⚠recur T4 | already fixed (rewrite `5a37a6f`, prior) | eval-log entry |
| O | Science: zf1 bottom device SC (strong) | record-only | POSTMORTEM / Aaron's pass |
| P | Caught Tc higher than expected (W11); coarse gatemap finer than prior | record-only (+) | scoreboard / changelog |

## Maintenance-window checklist (rig-side — chiron does not apply these)

After this branch ff-merges to `hera`:

1. **Rig `~/measurement_env`: `git pull --ff-only`** — pulls this crank + the
   gate-current rewrite (`5a37a6f`), updated `toploader.md` rig card, measure
   template, and recipes. (Rig was at `84857f8` during the session.)
2. **Re-run `scripts/install.sh`** on the rig (Git Bash copies drift; refreshes
   agent prompts + shims).
3. **Re-deploy `rig_card.md`** next to the device cards from the updated
   canonical `toploader.md` (heater settle, DC205 `.volt`, thermometry staleness).
4. **Investigate the dead probe**: confirm which probe is the live sample
   thermometer (live = Probe1 this session, not the device-card's "rotator
   probe"); fix the dead probe-bridge worker; correct the device card if the
   live thermometer is the fridge MC, not the loaded rotator probe.
5. **Investigate `newclaude` transcript-loss**: why the tactical spawn wrote no
   `.jsonl` (a 16 h session with no transcript is a data-loss bug).
