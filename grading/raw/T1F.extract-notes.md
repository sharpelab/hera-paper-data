# T1F extraction notes

## Counts
- Total claims: 52
- decision: 17
- inference: 21
- observation: 13
- verdict: 1

## Files parsed
- `transcripts/*.jsonl` (4 files present): two tiny model-error stubs contained no real content (skipped, nothing to extract). One ~193KB file was the session-init/preflight transcript (bring-up narration only, no scored claims — folded into context, not separately claimed). The ~4.9MB file was the main tactical transcript; all 110 assistant `text` blocks were read in full (assistant `thinking` and `tool_use` content blocks were not used as claim sources, per the instruction to read assistant-role messages — text blocks are what the agent "asserted"; markdown notebook cells were used as the second, more polished source for the same content).
- Both notebooks (`*_measure.ipynb`, `*_ana.ipynb`): all markdown cells read in full (27 + 18 cells).
- `data/0` through `data/12` `metadata.json`: type + comments read for all 13 run directories; confirmed "run N" in agent text/notebook prose maps 1:1 to `data/<N>`.
- Ignored `session_notes.md` and `hera_session.md` per instructions.
- Also ignored a duplicate hidden `.transcripts/` directory containing an older, truncated copy of the largest transcript file (missing the final human message and stop-hook records present in the instructed `transcripts/` copy) — out of scope since instructions named `transcripts/*.jsonl` specifically.

## Boundary judgment calls
- **Gate-leakage exclusion applied strictly**: all Keithley leakage-current readings and the "common-mode pickup, not real leakage" reasoning were dropped entirely; where bundled with a contacts/Rxx liveness statement (e.g. the first back-gate cut), only the Rxx/current-liveness content was kept as a claim.
- **Card-limit / safety-envelope exclusion applied**: VERIFY-cell content (validator-vs-card-limit numeric matches, magnet-at-zero / thermometry-worker-live checks) was excluded wholesale as pure card-limit verification. Where a decision's sweep window happened to start exactly at a committed gate-range boundary, the boundary value itself was blinded to generic phrasing ("full negative range", "the card limit", "the session's field cap") and only the *chosen* (non-boundary) endpoint was reported as the decision's numeric content, per the "blind card-limit values unless the value IS the claim" instruction.
- **Observations vs. inferences**: kept observation entries to the numeric readings that are explicitly cited as load-bearing evidence in the final call (CNP location, 10.4x rise, D-minimum location, capacitance ratio, SdH tone ratios, activation gaps/crossing field, field-vs-setpoint offset) rather than every intermediate row-by-row checkpoint number; routine "row N nominal" pings and per-row progress checkpoints were skipped as instructed.
- **Retractions/corrections kept as pairs** (wrong claim + corrected claim, linked via `supersedes`) rather than silently reporting only the final version, since the taxonomy explicitly wants tension/error history preserved: the "reproducible structure" -> "instrument noise" correction; the Landau-level-degeneracy discriminator claim -> corrected 4N-regardless-of-stacking claim (also entered as a notebook erratum); the "every density gives one tone" -> "four of five, one gives none" correction; the linear-intercept-extrapolation gap-symmetry test -> corrected parabolic-minimum test; and the premature "close-out complete at 1.761 K" declaration -> corrected declaration after the sample was confirmed back near its received temperature.
- **Excluded as non-physics/tooling housekeeping** (not extracted as claims): the coding bug where `V_bg` was accidentally used as both a slow and fast sweep axis in an early ladder draft; the `nb summary`-lags-live-document false alarm; the reshape/completeness guard added for a still-writing run; and various session-notes tooling suggestions (e.g. that a duplicate-column helper should raise instead of silently preferring the setpoint) — these are debugging/authoring housekeeping, not assertions about the physical system or fridge-time-consequential experimental choices.
- **Kept as decisions despite being framed as "obviously correct" by the agent**: the choice to run the operator-mandated `close_out(restore=state0)` instead of the hand-written version (it reverts working lock-in settings to a known-bad configuration, a real consequence for the next session), and the sequence of two close-out declarations (premature, then corrected) — both fit the taxonomy's explicit "declaring the deliverable complete" decision type.
- **Not extracted as a standalone claim**: the fact that only one four-terminal contact pair is wired and the other four contacts are dead — this is a hardwired device/rig configuration fact rather than a judgment call, so it was folded into the verdict's context (scope of the call) rather than given its own entry.
- One transcript (`8bd43b71...`) is a separate agent instance (session-init/bring-up) preceding the main tactical transcript; its four assistant text blocks are pure orientation narration duplicating the main transcript's own bring-up summary, so nothing additional was extracted from it.

## Parsing problems
- None blocking. `metadata.json` comment strings for `data/5` embedded raw `np.float64(...)` reprs (cosmetic; values still parsed as decimals for use in claims). No corrupted JSONL lines encountered in any of the four transcript files.
