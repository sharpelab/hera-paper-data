# QC0426 ladder — metrics progression (v2, 2026-07-06)

Nine HERA sessions on QC0426 (VTI), 2026-06-10 → 06-22, from the full-extraction
pass (`analysis/runs.csv`; per-run detail in `analysis/reports/`). r6 (38-min
false start) excluded per ruling. Interventions are still the raw human-message
proxy — the label review pass has only run on r3.

## The ladder

| run | date | mode | session h | measuring h | util raw→HIL | human msgs | longest unattended | cost* |
|---|---|---|---|---|---|---|---|---|
| r1 | 06-10 | E0 | 41.8 † | 26.2 | 72 % (no stamps) | 25 | 9.7 h | $98 (Fable 5) |
| r2 | 06-14 | E0 | 24.4 | 8.0 | 43 → 70 % | 17 | 15.5 h | $70 |
| r3 | 06-16 | **E1** | 20.2 | 15.4 | 79 → 90 % | 46 ‡ | 7.8 h | $130 |
| r4 | 06-17 | E1 | 22.0 | 12.5 | **95 → 96 %** | **4** | **21.8 h** | $52 |
| r5 | 06-19 | E1 | 18.0 | 9.3 | 54 → 59 % | 7 | 13.4 h | $68 |
| r7 | 06-19 | E1 | 13.4 | 10.8 | 95 → 96 % | 3 | 12.9 h | $60 |
| r8 | 06-20 | E1·V | 6.7 | 5.4 | 90 → 90 % | 9 | 1.2 h | $39 |
| r9 | 06-21 | E1·V | 17.4 | 15.8 | 94 → 95 % | **1** | 17.3 h | $52 |
| r10 | 06-22 | E1·V | 10.0 § | 9.0 | 93 → 94 % | 3 | 9.9 h | $61 |

\* API list-price equivalent (ran on subscription). † includes day-2 +
post-session retrospective tail — needs a session_h override. ‡ r3 includes the
K2400 over-range incident + protocol violation + heavy live physics
collaboration with Aaron. V = variability set (same brief ×3). r6 (excluded)
was a 38-min false start on 06-19; r7 is its rerun. § r10's session ends at
its deliverable-complete standby (15:47 UTC, ruling 2026-07-06); the
operator-initiated step-6 extension is post-session and counts as a strong
intervention.

## What the progression shows

**1. The intervention decline is real and steep.** E0 rounds: 25 and 17
messages. First E1 (r3): 46 — but that run absorbed a hardware incident and a
deliberate evening of operator-in-the-loop physics. From r4 on: **4, 7, 3, 9,
1, 3**. r9 ran 17.4 h on a single human message. Longest-unattended grows in
step: 9.7 h → 21.8 h peak. This is fig 2's declining-interventions curve,
with the r3 spike needing its one-line explanation (or the labeled subset —
draft labels put r3's true corrections at ~12 of 46).

**2. E0→E1 is directly visible in the court split.** r2's idle was 39 % human
court (operator reaction latency) vs ≤ 1 % on the good E1 runs — the HIL
metric behaves exactly as designed, and the E0/E1 category change is
annotated rather than hidden.

**3. The one real utilization failure is a premature standby — r5.** Good E1
runs hit 90–96 % raw, and after the r10 boundary ruling only one weak run
remains. Both apparent stalls were "deliverable-complete standby" in the
transcript, but they resolve differently:

- **r5** (6.1 h idle, 12:56→19:07 UTC): HERA finished the FS-count analysis
  at 13:03, reported the result *plus a scope question*, parked the rig, and
  stood by. The operator returned at 18:58 with a correction — *"You didn't
  complete the arc of the investigation and dropped out"*. A **premature**
  self-declared pause: the session rightly continued, and the 6 h stays
  charged to HERA court. This is the ladder's genuine failure datapoint.
- **r10**: *"Standing by at the campaign's natural pause point — deliverable
  complete, recorded, reported"* (15:47). Ruled a **true session end**; the
  operator's later step-6 extension is post-session and a strong
  intervention. Re-scored to the boundary, r10 is 93 → 94 % — indistinguishable
  from the other good E1 runs.

Consequence: the protocol fix targets exactly r5's failure mode — the corpus
needs a rule for the self-declared pause (the brief defines the arc so
"complete" isn't reachable early, and an idle fridge means run the next-value
measurement, not park). This is the eng-backlog "idle-time prompt norm", now
with one clean supporting datapoint and one counter-example showing when
standby is *correct*.

**4. The model switched mid-ladder — quietly useful for the "loop, not
model" claim.** r1 ran on **claude-fable-5**; r2–r10 on claude-opus-4-8. The
ladder's improvement therefore can't be attributed to a model upgrade (it ran
on the *same* model from r2 on, and the most capable model was actually the
*first*, weakest-metrics run). Worth one sentence in the paper; also means r1
cost is priced at Fable rates.

**5. Variability set (r8/r9/r10, same brief).** Session length 6.7 / 17.4 /
10.0 h; measuring 5.4 / 15.8 / 9.0 h; utilization **90 / 94 / 93 %**; messages
9 / 1 / 3. With the r10 boundary fixed, utilization is uniform — the variance
lives in *duration and measurement strategy* (2.6× spread in fridge-hours to
answer the same brief), which is itself a quantitative result (fig 2 error
bars).

**6. Cost is flat and modest.** Steady-state E1 runs: **$40–70 per session**
(API-list equivalent) regardless of length — cache reads dominate (~2/3 of
cost). Context audit (r3): 242 k at noon, **495 k at 18:54 UTC** (matching
the 400–500 k seen live in CC that evening), growing unattended overnight to
908 k at the 05:43 closeout — single-iteration, non-sidechain API-reported
numbers, so the totals are sound. r3's $130 outlier tracks its 388 requests /
46-message interactivity. "A full autonomous measurement shift costs ~$50 of
inference at list price" is a strong systems datapoint.

**7. decision_h works but needs its hand pass.** The heuristic found the
call-labeled cells cleanly (r2: first ABC call at +5.7 h into a 24 h session
— it then kept verifying; r3: "cannot tell" at +7.5 h superseded by the
updated call at +20 h). r1 predates cell stamps → no decision_h; recoverable
by hand from the transcript if wanted.

## Data-quality flags (carried in the manifest)

- r1: session_h needs an override (retro tail); no appended_at stamps → HIL = raw.
- r5/r7 archives contained each other's / init transcripts — now attributed by
  cwd (r7: 37.8 h → 13.4 h, 24 → 3 msgs). Worth a spot-check of the other
  archives' `n_extraneous_transcripts` (all currently 0).
- r6 false start: excluded from the ladder (manifest `exclude: true`); its
  archive remains as a tooling-failure record.
- Label review pass (interventions) pending for all runs except r3.

## Suggested next steps

1. Land the self-declared-pause norm in the corpus (highest leverage, backed
   by §3's autopsy: don't park a cold idle fridge at a "natural pause" —
   continue the arc or run the best optional measurement) — via Chiron, as a
   recipe/prompt amendment.
2. Label pass over the remaining 15 message CSVs (fast — median 7 msgs/run),
   then fill `n_interventions` and freeze the fig 2 numbers.
3. Hand-check: r1 session_h override + r1 decision time; r2's "was +5.7 h the
   decision" question; veto proxy on the never-executed cells.
4. Then the expert-eval dossiers (content discussion pending).
