# Round-2 scorecard — SCORER-SIDE ONLY

*⚠️ Not for agent view. Contains ground truth the round-2 session is
designed to re-derive blind. Lives in the repo under the soft-quarantine
posture (agent prompt's data-isolation rules are the fence); do not cite
it in any agent-visible doc.*

Round 2 = replication from a cooled start under the amended corpus. Two
comparison baselines: **Qingrui's manual campaign** (2026-06-01 dir,
~1 week load-to-conclusion) and **HERA round 1** (2026-06-10 dir, fan
stage only, pre-amendment corpus). Score = (a) ground-truth accuracy of
re-derived quantities, (b) fix-by-fix behavior deltas vs round 1,
(c) process quality.

## A. Ground truth (re-derivation targets)

| Quantity | Truth | Source |
|---|---|---|
| TG operating range | [−6.5, +7.5] V | Qingrui range-finding — **punted to next run** (provided this session, not range-found) |
| BG operating range | [−5.0, +4.8] V | Qingrui — **punted to next run** (provided this session, not range-found) |
| CNP line | V_tg ≈ −1.3·V_bg + 0.06 | Qingrui 0 T map fit |
| Capacitance ratio c_bg/c_tg | 1.3 (geometry exact match) | analysis cell 24 |
| Lever arm γ = n_true/n_cap | 0.85–0.86 | round-1 run-5 FFT |
| CNP-vs-D at B = 0 | ×150–180 growth both pairs; I 4.96→1.11 nA at D≈+1 | round-1 run 2 + our pre-read |
| Good contact pairs | 09-01, 12-20 (drain 42); characterization block (drain 03) much weaker (~30 Ω signal) | both campaigns |
| Ray onset | ≈ 3.5–4 T (quantum mobility ~10× below paper ref) | round 1 |
| Fan content at D = +0.25 | curved dark arcs co-locating with ABA ML×BL model at α = 0.82 (4/5 of Qingrui's traces) | model subtask |
| Two-frequency SdH | f_low ~9–18 T + main branch, intermodulation, sum rule, n ≳ 4.5×10¹² | round-1 run 5 |
| Stacking ground truth | FORKED: Qingrui = mosaic, clean region likely Bernal (by-eye); round 1 = ABC-dominant CNP + unresolved ABA candidate | — |

Scoring note: matching the *fork*, with hedges, is full marks. A
confident unforked call must bring feature-level evidence neither prior
campaign had — extraordinary, not forbidden.

## B. Fix-by-fix behavior checks (vs round 1)

| # | Fix under test | Pass looks like |
|---|---|---|
| 1 | Presence-vs-pattern (burn #1) | Arcs at finite D get model-overlaid, not discarded as "not ABA evidence"; weight stated as decreasing with \|D\| |
| 2 | Nyquist + cost model (burn #2) | Fan grids checked on BOTH axes at design time; pricing includes traverse; row overhead calibrated from own sweeps, not inherited |
| 3 | Series-path caveat | CNP-vs-D growth claimed as "gappable content in path" / consistent-with, never "device is ABC" from step 1 alone |
| 4 | Ambiguity branch | If any discriminator lands in the gray zone, both readings carried, no rounding |
| 5 | Strength vocabulary | Verdicts carry decisive/strong/weak/consistent-with/uninformative; no bare leans, no "supports/suggests" |
| 6 | N_M=0 conditioning | Any vertical-series candidate pattern-checked + confound-checked, decisive only at D ≈ 0 |
| 7 | Scope model | Off-arc reaches carry cited rationale; >30 min flagged as detour |
| 8 | Variant/obsolescence reasoning | Notices the QSwitch supersedes the repatch workflow and says so (the -vti variant's obsolescence clause activating live) |

## C. Device-init chain quality (new recipe surface)

- Range-finding: **punted to next run** (gate limits provided this
  session, not range-found). Criteria retained for that run:
  evidence-based narrowing inside the outer box; per-polarity onsets or
  geometry-ceiling reasoning stated; ranges within ~10% of truth *or*
  differences justified by data; validator commit handshake honored.
- Watch-and-interrupt: **punted to next run** with range-finding (agent
  reads a partial interrupted leg and brackets — step-7 fast-path).
- measurement_config truth: mux `mc_fragment` verified on disk after
  the FIRST survey run, before the loop continues.
- CNP calibration: slope within a few % of −1.3; axis orientation
  stated; two-tier provenance (ratio data-calibrated, absolute scale
  geometry-prior) in the write-back; closure residual quoted.
- Contact survey: attributable candidate set (every contact ≥2 pairs);
  reference density stated; ranking consistent with truth; re-wire
  hygiene if any manual moves happen.
- Si survey: operating point chosen with stated criterion; at-field
  re-validation scheduled with the first field excursion.
- Lever-arm check fires when fan data lands; recovered γ ≈ 0.85–0.86
  closes the loop (and validates the calibration recipe's upgrade path).

## D. Process

- Wall-clock estimate on every proposed sweep; cheap-first ordering.
- Mid-fan partial reads with the model overlay.
- TSV-first for all classification-grade reads.
- Session notes: tagged, specific, citing cells/file_ids.
- Output contract complete (all five parts).

## E. Cross-campaign comparison (writeup material)

- Time: Qingrui ~1 week; round 1 ~1 day (fan stage only, given
  optimized configs); round 2 target: full chain in one session.
- Decision-point diffs vs round 1 at the same junctures (fan grid
  design, finite-D reasoning, CNP-vs-D claim shape, call vocabulary).
- Recipe-surface report: which recipes ran as written, which needed
  live deviation (RECIPE FIX entries = the corpus's next iteration).
