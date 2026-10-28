# Extraction prompt template (v2, post-calibration 2026-08-26)
# Fill: {KEY} run key (e.g. T1A), {ARCHIVE} archive dir. Model: Sonnet 5 subagent.

You are extracting every physics/experimental CLAIM an autonomous measurement agent ("HERA") made during one archived measurement session, for a blinded expert fact-check. Be exhaustive on inferences, verdicts, and consequential decisions; missing claims is the failure mode we care about.

ARCHIVE: {ARCHIVE}
Read: all transcripts under transcripts/*.jsonl (assistant-role messages only — ignore human messages), markdown cells of *_measure.ipynb and *_ana.ipynb, and the sweep index (data/<id>/metadata.json: type + comments — "run N" in the agent's text/plots = data id N). IGNORE session_notes.md and hera_session.md.

A CLAIM is any statement the agent asserted, or choice it made, that a careful experimentalist could disagree with. Types:
- observation: a reading of the data. Extract these, but they are NOT scored — they get folded into the inference cards that rest on them. Skip repetitive "row N nominal" pings.
- inference: an interpretation of data (band structure, stacking-consistency, calibration scale, gap, pocket assignment, tension between datasets, proposed explanations/forks).
- decision: an experimental choice WITH physics or fridge-time consequence — drive current/voltage, gate/field/temperature ranges, resolution/step/points, time constant, sweep rate, sweep ORDER, what to measure next, when to stop a sweep, declaring the deliverable complete. Do NOT extract: checklist/verify-cell authoring, time re-pricing, cost/checkpoint boilerplate.
- verdict: the campaign-goal call (final stacking/region determination or SC determination) with its stated strength; intermediate "consistent with X" statements are inference.

EXCLUDE entirely (calibration rulings): gate-leakage claims (instrument offsets make them unjudgeable — if bundled with an R_xx liveness statement, keep only the R_xx part); claims whose only check is against the device card or rig card (safety-envelope matches, card-limit verification).

Fields (one JSON per line, {KEY}-NNN sequential):
- id, type
- claim: one or two self-contained sentences (quantity, value, region/column, conditions). Blind device-identifying numbers: safety limits and card gate ranges → "the card limits" unless the value IS the claim.
- context: 1–3 sentences: what the agent had just seen/done, and HOW the fact was established (which readback, plot, or computation). Enough to judge WITHOUT the rest of the session.
- evidence: what the agent pointed to — ana/measure notebook cell numbers, figure/output description, numerical values cited.
- data_ids: [ints] — the sweep id(s) under data/ the claim rests on ([] if none / pre-flight).
- source: {file, locator} (stripped before scoring)
- t_rel_h: hours since first assistant message, or null
- supersedes: id of an earlier claim this retracts/corrects, else null
NEVER put dates, device names, session names, run numbers-as-session-identifiers, corpus hashes, or people's names in claim/context/evidence.

Write /home/aaron/work/projects/hera/quality/raw/{KEY}.claims.jsonl and /home/aaron/work/projects/hera/quality/raw/{KEY}.extract-notes.md (counts by type, files parsed, boundary judgment calls; no archive path/date). Return only: total, counts by type, parsing problems.
