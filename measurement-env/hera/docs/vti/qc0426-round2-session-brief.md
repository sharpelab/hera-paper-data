# QC0426 / VTI / 3LGr — session brief: bring-up then classify

*A live HERA session on a cooled, wired, unknown-stacking device,
structured as **two phases with an explicit gate between them**. Phase 1
(prep & characterize) takes the device from cooled-and-wired to a
blessed measurement configuration — recipe-encoded, mux-automated device
bring-up; driving it is half the session's purpose. Phase 2 (classify)
runs the stacking investigation on phase 1's groundwork.*

## Contract

HERA drives via `hera-tactical`; the operator executes every cell —
execution is approval, declining is veto (including **interrupting a
running sweep cell**, which is always the operator's prerogative;
partial runs land readable); Zack supervises remotely. The phase gate
(below) adds one session-level handshake of the same kind.

## Starting state

A trilayer-graphene device (`QC0426`) is **cold (≈ 1.2–1.3 K), wired,
and unknown-stacking**. The device card describes what is physically
true: gate stack, contact map, instrument rack, the QSwitch routing
maps + calibrated `settle_s` (bring-up record complete), and the **gate
operating limits**, provided by the operator and committed as validators
at session start (not range-found this session).

**Provided to you up front (operator sets these — do not re-derive):**
**all three gate operating limits** — top gate (`dc205_volt` / `k_tg`),
back gate (`k_bg.volt`), and Si (`k_2410`). No gate is range-found this
session; commit each as its validator. The geometry ceiling is the hard
fence behind the TG numbers.

What the card deliberately does NOT carry, and what **phase 1
establishes**: the **CNP-line constants + capacitance calibration** and
a **workable contact configuration**.

## Blocklist

- `device-init/silicon-backgate-survey.md` — not run this session.
- `device-init/gate-range-finding.md` — not run this session.
- `device-init/gate-range-finding-vti.md` — not run this session.
- `device-init/gate-leakage-survey.md` — not run this session.

## Data isolation — strict this session

**No prior measurement data exists for you.** Do not read other
campaign or session directories — not the 2026-06 campaign dirs, not
any other session directory. Your only inputs: this brief, the device
card, the rig card, the recipes/corpus docs they name, and the data
this session produces in `./data/`. If a comparison seems to need prior
data, the recipes' first-session branches apply (there are no
designated references; `reentry-baseline` is N/A by its own When). Ask
the operator by name if you believe something is missing. In phase 2,
phase 1's data and write-backs are your priors — and your only ones.

---

## Phase 1 — prep & characterize

**Goal**: a blessed measurement configuration, evidenced and written
back to the device card. Recipes, in dependency order:

1. `measurements/contact-survey-2t.md` — automated flavor (QSwitch
   bring-up record complete; routing maps and `settle_s` in the card).
   **Pick a *workable* configuration, not the optimum**: a source/drain
   and three voltage-probe pairs (sr1/sr2/sr3) that are **acceptable,
   not best**. Satisfice and move on — contact optimization is not this
   session's purpose.
2. `device-init/cnp-and-dline-calibration.md` — first gate map on the
   chosen configuration → CNP fit → capacitance ratio → D-line designer.

**Phase-1 exit contract.** Phase 1 ends when all of:

- [ ] **All three gate validators** (TG, BG, Si) committed to the
      **provided** operating limits.
- [ ] CNP/D-line calibration + capacitance ratio established and
      written back to the device card.
- [ ] **Workable contact configuration** chosen: a source/drain + three
      acceptable probe pairs, with brief evidence each is adequate.
- [ ] **Exit report landed in the ana notebook**: one section — what
      was established, run-id citations for each item, the blessed
      configuration, anomalies still open. Write it for the operator —
      it's the gate on phase 2.
- [ ] **Operator go.** Phase 2 does not start without it. The exit
      report is the ask; the operator's go is the approval. If the go
      comes with corrections, fold them in before proceeding.

Phase-1 work is tens-of-minutes-scale per step (the contact survey is
minutes-per-pair with the mux). No magnet hours belong in phase 1
beyond what its recipes themselves require.

## Phase 2 — classify (stacking investigation)

**Goal**: an evidence-cited, region-resolved stacking call (ABA vs ABC
vs mixed vs cannot-tell), per
`recipes/investigations/trilayer-stacking-id.md`'s output contract, on
the configuration phase 1 blessed.

4. `investigations/trilayer-stacking-id.md` — the governing procedure;
   its ladder (CNP-vs-D first), Verify suite, and five-part output
   contract.
5. `measurements/landau-fan.md` — grid design per its Nyquist check and
   full cost model (calibrate row overhead from this session's own
   sweeps; the magnet is ramp-limited and blocking — fine B is nearly
   free).
6. `measurements/gatemap.md`, `gatemap-in-field.md`, and the rest
   of the corpus: available under your scope rules — off-arc
   composition with stated rationale encouraged; >~30 min off-arc gets
   the detour flag.

**Tool**: the ABA forward model (`hera/models/aba_trilayer/`) is the
primary arc-reader for fan features, per the investigation's Verify.

Phase-2 arc: cheap discriminators before magnet hours; grid design
guards before any fan; model overlay + Verify before any feature
claim; iterate per the recipe's step 4. The call lands as the five-part
output contract, STYLE strength vocabulary, in the ana notebook.

---

## Session arc (expected shape — you drive, within each phase)

1. Gates A→B per the agent prompt (SAFETIES = the operator-committed
   outer box; compare numbers to the card). Gate C: first-session
   branch — no references; liveness comes from the bring-up chain.
2. Phase 1, recipes 1–2 → exit report → **operator go**.
3. Phase 2, ladder → fans → Verify → the call.

Wall-clock realism: phase 1 is minutes-to-tens-of-minutes per step;
phase 2's field work is hours-scale. Price everything; cheap-first
throughout. The phase gate is also the natural break if the session
splits across operator windows or days — phase 2 re-enters through
Gate A/B and the silent-precondition reads, not through re-doing
phase 1.

## Timing + logistics

- Magnet facts per the rig card; traverse is the dominant fan cost.
  Calibrate per-point and per-row from this session's first sweeps.
- Operator windows: confirm at start. Cryocooling is closed-loop on
  this rig — session length is operator time, not cryogen budget.
- The QSwitch is live but newly commissioned: any mux anomaly
  (state/`mc_fragment` mismatch, settle violations in Verify) is
  stop-and-report, not push-through.

## [VERIFY] at session start

- [ ] Operator has run the SAFETIES cell; values match the card's
      gate operating-limits table.
- [ ] Magnet at 0 T (set vs read).
- [ ] QSwitch routing maps + `settle_s` present in the card; bring-up
      log entry exists; **Si standing closures (lines 16/11) verified
      closed**.
- [ ] Heater ownership + max-T ceiling (if temperature work arises).
- [ ] Base T holding.

## Session notes

Same discipline as ever (`session_notes.md`, tagged entries). New
recipe surface this session (agent-driven, mux-automated contact
bring-up) — RECIPE FIX entries are a primary deliverable. The phase
split is new — note any thoughts on it.
