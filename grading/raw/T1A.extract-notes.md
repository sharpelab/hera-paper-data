# T1A extraction notes

## Counts
- Total claims: 33
- inference: 19
- decision: 9
- observation: 3
- verdict: 2

## Files parsed
- `transcripts/*.jsonl` (two files: one short session-init transcript, one long tactical transcript) — all `assistant`-role messages, both `text` and `tool_use` (Bash/Read/Write/Grep/AskUserQuestion) content blocks, sorted by timestamp across both files. Human/user-role messages were not used for claims (only to establish t_rel_h anchor and grant timing context).
- `<date>_measure.ipynb` and `<date>_ana.ipynb` — all markdown cells (parsed directly from the notebook JSON, not just from the transcript's heredoc source, to pick up post-landing edits such as the `ana_spot7` sed corrections).
- `data/<0-14>/metadata.json` — `type` + `comments` fields, used to map "run N" language in the transcripts/notebooks to `data/<N>` ids and to confirm run parameters (rung temperatures, sweep directions, gate targets).
- Ignored per instructions: `session_notes.md`, `hera_session.md`. Also ignored: `.transcripts/` (hidden dir, an older/incomplete duplicate of the tactical transcript — not under `transcripts/*.jsonl` and superseded by the visible copy).

## Session shape
Two-part session: a short `hera-session` (session-init) transcript that builds the session directory, fills device-card slots, and hands off; then a long `hera-tactical` transcript that runs the actual investigation (gate C -> gatemap -> CNP/(n,D) calibration -> two SdH spot checks -> Landau fan -> Lifshitz-Kosevich mass ladder -> stacking call -> close-out). `t_rel_h` is hours since the first assistant message in the session-init transcript (05:47:48Z), since it started before the tactical transcript's first message.

## Boundary judgment calls
- **Excluded entirely** (per instructions' calibration-ruling carve-out): the base-template's swapped top-/back-gate Keithley addresses and the wrong current-channel GPIB address, caught during slot-filling — these are checks against the device card only. Also excluded: the bring-up `rangei` guard trip (1.05 vs 1e-6), gate-current/leakage magnitudes and thresholds throughout (kept only the R_xx/current-liveness half of any bundled claim, e.g. gate-C "device alive" observation), and all safety-validator/card-limit numbers (blinded to "the card limits" where used only as context, e.g. LK ladder rung cap).
- **Excluded as non-physics protocol**: the blinding decision, the model-choice question, the decision to have session-init run bring-up itself vs. the brief's operator-gated bring-up, and all VERIFY/probe-cell authoring — these are workflow/authority decisions, not measurement-design or interpretive claims a domain expert would fact-check.
- **Skipped as repetitive monitoring**: the very large number of "row N at field X, on track for ETA" progress-watch messages (row/ETA polling, background-task tail greps) — these are not claims, just progress pings.
- **Observation vs. inference**: kept only 3 `observation` entries (gate-C liveness numbers, run-6 raw QH-minima pattern, run-8 raw completeness/cleanliness) as the load-bearing raw readings that the biggest inference cards rest on; did not create separate observation entries for every raw-trace description folded elsewhere into an inference's `claim`/`context` (e.g., the rho_xy-admixture drop, or the hole-side raw trace), to avoid duplicating content already captured as inference.
- **Two small self-corrections not extracted as claims**: (1) the fan's n_max was walked back twice (3.27 -> 3.26 -> 3.25) purely because of an arithmetic-margin mistake against the top-gate validator, caught before any hardware write — treated as checklist/pre-check boilerplate, not a scored decision; (2) the `hera-watch` ETA/leak-detector tooling gripes logged to `session_notes.md` were ignored as out-of-scope (session_notes.md excluded by instructions anyway).
- **Supersession chain**: T1A-005 (gatemap design) is partially superseded by T1A-006 (abort + sensitivity resize); T1A-004 (ambiguous two-CNP read from 1D legs) is superseded by T1A-007 (resolved as two parallel ridges from the 2D gatemap) once the gatemap disambiguated domain-vs-contact-artifact.
- **Verdict scope**: split the final call into two verdict entries (T1A-030 dominant-region ABAB call, T1A-031 secondary-region "uninformative") since "THE CALL" cell states both as separate, explicit final determinations for the two identified regions, rather than treating the secondary-region statement as a mere hedge.
- **Blinding of run numbers**: `data_ids` carries the integer run ids (as instructed, since "run N" in the agent's own text is how these are identified), but no session/round/date/device-name language was placed in `claim`/`context`/`evidence` text.

## Parsing notes
- No pandas used; parsed transcripts and notebooks with the standard library `json` module via inline `python3` scripts.
- Timestamps for `t_rel_h` were taken at the point a decision/inference was actually landed (notebook cell appended and, where applicable, executed against hardware), not at earlier "drafting while waiting" timestamps, since several proposals (hole-side spot check, Landau fan) were drafted well before they were actually committed/run.
