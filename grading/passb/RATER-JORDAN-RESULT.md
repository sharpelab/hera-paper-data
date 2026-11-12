# Pass B second rater (Jordan) — result, post hoc

*Zack + Claude, 2026-09-04. Analysis written after the exports were read; no
agreement metric or reporting rule was pre-declared for this rater (only scope,
seeded order, and knowledge state — `ANALYSIS-PLAN.md` decision (a),
`RATER-JORDAN.md`). Labeled post hoc accordingly. Exports: branch
`rater/jordan`, `passb/<key>.jordan.passb.json`, committed 2026-09-03; five
non-vti-01 runs plus CAL2 practice. `dossiers/hera_synth.py` discovers them by
filename and carries him as a Pass B rater.*

**Rule applied (from PREREG "Second rater, Pass A subset", rule 4, applied
here retroactively):** the expert's rulings remain the rulings of record; the
second rater's are reported beside them, never averaged.

## Numbers

Unit rulings on the same unit ids (context units excluded): 58 units, 50 with
both raters ruling sound/shaky/wrong. Exact agreement 29/50 = 0.58; Jordan
kinder on 15, harsher on 6. Quadratic-weighted κ on sound/shaky/wrong = 0.22.
Jordan never ruled `wrong` (expert: 8). Knowledge state: "no" on all five —
did not know the device by name, assumed Bernal for every device.

Final dispositions / supervision, expert vs Jordan: orig a/a vs d/c; T3 a/b vs
c/b; repl b/b vs a/a; T1 (no corpus) c/c vs b/b; T2 (no corpus, wrong call) d/d
vs a/b. Jordan's rulings do not reproduce the corpus / no-corpus partition.
Effort ≈ 3.8 h active across the five.

## Reading

The two raters graded different things. The expert's notes are physics
validity (is the discriminant real, is the mass plausible, does the fit
support the number). Jordan's notes are legibility and data quality ("hard to
follow", "real lack of plots", "too noisy to make claims", "unusual tests, or
at least unusual to me"). He rated the wrong-call session "answers the brief
as-is" while writing that he disagreed with its conclusion. Reported as an
instrument finding: Pass B requires a rater able to adjudicate the
discriminants.

## Data that survive the divergence

- The agent never flagged top-gate leakage in four of five runs (Jordan's
  liveness-unit notes; the expert did not mention it). Recipe amendment
  candidate for the gate-check step.
- Original run, in-arc LK verify unit: "It was waiting for confirmation to
  proceed but didn't receive and went ahead anyway?" — checked against the
  transcript 2026-09-16: HERA asked three times for a He-level reading
  (operator-attested, AMI 1700 not bound in the kernel; transcript lines 152,
  896, 983) and proceeded under the E1 grant (`hera_session.md:33-39`), which
  did not gate on it; the only user turn in the transcript is the brief
  (line 6). Not an intervention.
