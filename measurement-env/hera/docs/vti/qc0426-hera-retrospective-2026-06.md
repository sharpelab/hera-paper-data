# HERA self-retrospective — QC0426 live sessions, 2026-06 (verbatim)

*At session close, Zack interviewed the HERA instance that drove the
QC0426 campaign ("what went well vs what didn't — physics, tooling,
humans; then requests/advice for future runs"). The response below is
verbatim from the session transcript (2026-06-12), promoted here because
it is the densest single artifact of the campaign: the agent's own
defect list and feature requests, several of which were corpus-amended
within days (disposition table at bottom).*

*Context: the session ran the stacking investigation through the
two-frequency fork and its deciding measurements (LK mass split,
beat-damping exclusion, D-pinning), including the rig's first
agent-driven heated runs. Session dir:
`vti/zack/20260610-QC0426-hera-live/`; analysis narrative in
`20260610_ana.ipynb`; operational log in `session_notes.md`.*

---

## What went well

**Physics**
- The recipe ladder's cheap-first ordering paid off exactly as designed. The 4-minute CNP-vs-D line (run 2) carried more discriminating weight than the 2.6 h fan, and having it first meant every later result had a frame to be read against.
- The frequency-domain pivot was the session's decisive move. Three campaigns of arc-hunting in (n,B) gave nothing classification-grade; one FFT per column on the fine-B fan exposed the two-pocket structure immediately. The fine-B overnight fan was specced for chain-hunting — its real value turned out to be Nyquist coverage in 1/B. Lucky in design, but the lesson generalizes.
- The fork-closing logic held under pressure. When the two-pocket vs. two-region question arose, we found three independent discriminators (LK mass split, beat-damping exclusion, D-pinning) rather than re-arguing one ambiguous extraction. The beat-damping argument (intermod components damp as m_A+m_B) was discovered mid-session and is recipe-grade.
- Honest anomaly bookkeeping worked. E3 was logged as an anomaly rather than claimed as ABA evidence — when run 16 retired it, nothing in the call had to be retracted.

**Humans**
- The approval-by-execution contract was friction-free. You ran, edited, skipped, and overrode cells exactly as the protocol intends — the settle-loop rewrite, ratio=0.99, the 13.5 T cap, get_field() — every override was an improvement, and none required negotiation.
- The expert escalation chain functioned: Bingcheng's rules arrived mid-design, Aaron's override arrived an hour later, and the design absorbed both flips without losing the night.
- The interruption of run 7 was handled correctly by you — and the partial data was salvageable because metadata writes per row.

**Tooling**
- nb-collab append/wait was reliable throughout — ~20 cell-blocks landed, zero RTC conflicts despite simultaneous human editing.
- The scratch → ana promotion discipline kept the ana notebook readable as a narrative while ~15 scratch scripts churned underneath.

## What didn't go well

**My mistakes (the important ones)**
1. The classical-Hall identity trap. I initially read Rxy = h/(ν_app e²) at minima as plateau confirmation. It's a tautology (B/ne with ν_app from the same n). Caught within the same analysis pass, but a less careful read would have shipped fake quantization evidence.
2. The FFT-forensics spiral. Three successive f_low-slope extractions gave +3, −0.5, and +0.1 T per 10¹² — I kept refining instead of recognizing extraction-instability and stepping back to "report the fork + name the deciding measurement." Cost ~40 minutes and two confusing status updates. The protocol now has a note about this, but the instinct needs to fire earlier.
3. Wall-clock estimation was repeatedly wrong in the same direction. Brief said 30 s/row; reality was 278 s (magnet-ramp-limited). My "measured ramp = free" claim ignored per-point overhead (~40% over bare). Run 5 came in at 13.6 h vs 12.3 estimated. Every fan estimate this session was corrected upward mid-flight. The arithmetic should have been calibrated from run 3's first two rows and then trusted over the brief's figure for everything after.
4. E3 should never have become a "vertical candidate." Four B-rows can't establish dispersion. I hedged it correctly in the record, but I let it shape one status update and a queued measurement. (Run 16 was still worth it — but as low-ν structure mapping, not anomaly-chasing.)
5. Small cell bugs that you caught: magnet.mag() as getter, the "ends at 6 T" print. In an unattended queue these matter; the preconditions exercise exists because cells I land must survive nobody-watching execution.

**Tooling**
6. The Lakeshore VISA contention killed run 7. Two masters (Grafana + kernel) on one instrument is an architecture problem; the session worked around it by pausing the logger, which means the lab lost telemetry for the whole heated period. Needs a real fix (single poller, two consumers).
7. nb crashes on cp1252 — worked around with an env var every call, should be fixed in nb.py.
8. nb summary doesn't show execution counts — Gate A/B verification needed raw JSON spelunking.
9. Background-watch ergonomics: my sentinel shell-loops had a logic bug (false-fired once), and nb-collab wait's default timeout silently expired during the long fan. The monitoring layer was duct tape all session.

**Humans/process**
10. The rules arrived after the design, twice. Bingcheng's no-T-at-field constraint and the 0 T heat-up rule each invalidated landed cells. Not anyone's fault — first heated run on this rig with an agent — but rig-owner constraints should be in the device card before the session, not discovered at 18:02.
11. The brief's reference timing data was wrong (30 s/row), and the operator-gap window (2–4 pm) never matched reality. Briefs should mark which logistics facts are measured vs. assumed.

## Requests / suggestions for future runs

1. Add a "rig rules" section to the device card — owner-approved constraints (T-vs-field coupling, heat-up procedure, logger ownership, persistent-switch state, who can approve exceptions). Half of day 2's churn was discovering these live.
2. Promote two methods into trilayer-stacking-id: per-column SdH FFT (with the ≥80-rows-in-1/B sampling requirement) and the LK mass-split + beat-exclusion verify. They outperformed arc-hunting on a moderate-mobility device and should be the default for stacking ID above ~1 K.
3. Encode the dispersion rule: no verticality/dispersion claims from <8 B-rows spanning <1.5 T. Cheap to write, prevents the E3 class of false candidate.
4. Give HERA a calibrate-then-override discipline for timing: first sweep of a session measures s/row and T/min; all subsequent estimates use measured values, brief figures demoted to priors.
5. Fix the instrument-sharing architecture before the next T-campaign: one Lakeshore poller process, Grafana and the kernel both read from it. Same pattern will bite on any logged instrument.
6. A queue-preflight recipe/template: the assert-precondition pattern we converged on (state chaining, halt-on-failure, no-asserts-on-the-park-cell) worked well and should be the standard for unattended chains rather than reinvented per session.
7. Session-brief honesty markers: tag logistics numbers as [measured: run N, date] vs [assumed].
8. For this device specifically: before the toploader cooldown, one contact-mapping session (which pairs bound the ABA vs ABC segments — the unused contacts are uncharacterized), and a plateau-resolving measurement to pin γ and the absolute ν assignments. Both are half-day VTI jobs.
9. A small wish: a nb-collab watch mode that streams new cell outputs/files as events would replace the entire shell-sentinel apparatus and remove my most error-prone moving part.

> The one-sentence version: the physics workflow (gates → cheap discriminator → expensive measurement → adversarial verify → independent cross-checks) is sound and produced a stronger-than-asked result; the soft spots are timing calibration, rig-rule discovery, and the monitoring duct tape — all fixable in the card, the recipes, and the tooling before the next live run.

---

## Disposition (2026-06-12 triage)

| # | Suggestion | Status |
|---|---|---|
| 1 | Rig-rules card section | → round-2 preflight §2 (card design); collect from Bingcheng/Aaron/Qingrui |
| 2 | SdH-FFT into recipe | ✅ landed (step 3.5 + `hera.analysis.sdh_fft` + STYLE rule 14) |
| 2b | LK mass-split + beat-exclusion verify | ✅ landed with this triage (recipe Verify) |
| 3 | Dispersion rule (<8 rows / <1.5 T) | ✅ landed with this triage (recipe step 3) |
| 4 | Calibrate-then-override timing | ✅ landed pre-retro (STYLE 12, landau-fan cost model) |
| 5 | Lakeshore single-poller | → eng-backlog (architecture; pre-T-campaign) |
| 6 | Queue-preflight recipe | → eng-backlog (run-2 desirable) |
| 7 | Brief honesty markers | ✅ landed with this triage (STYLE 12 extension) |
| 8 | Contact mapping + γ-pinning | contact mapping = round-2 arc; γ/plateaus → toploader plan |
| 9 | nb-collab watch mode | → eng-backlog (tooling) |
| 7/8 (tooling) | nb cp1252 + exec counts | ✅ landed pre-retro (`ef26959`) |
