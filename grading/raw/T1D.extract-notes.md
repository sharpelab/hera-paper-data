# T1D extraction notes

## Files parsed
- `transcripts/<id>.jsonl` (the non-hidden `transcripts/` directory; a `.transcripts/` sibling exists but was not the path named in the task and was not used) — assistant-role messages only, `text` content blocks (29 found); `thinking` and `tool_use` blocks were not treated as claims themselves (internal deliberation / actions), only used for orientation while cross-referencing notebook cells.
- `*_measure.ipynb` — all 26 markdown cells (including the two authored mid-session by the agent under the pre-existing "Setup" skeleton).
- `*_ana.ipynb` — all 18 markdown cells (template cells 0/2/4/5/8 are boilerplate and yielded no claims).
- `data/<0..15>/metadata.json` — `type` + `comments` used to map narrative "run" references to sweep ids, and `start_time`/`end_time` (unix, converted to hours since the first assistant-message timestamp) used to anchor `t_rel_h` for claims sourced from notebook markdown (which carries local-time headers, not machine timestamps). Local-time headers in the measure notebook were cross-checked against transcript UTC timestamps and confirmed to be UTC-7.
- `session_notes.md` and `hera_session.md` were not read, per instructions.
- `hera_scratch/*` (draft cell/markdown files) was not read as a primary source; its content is superseded by what actually landed in the two notebooks, which is what was cited.

## Counts by type
- decision: 10
- inference: 25
- verdict: 1
- observation: 0 (per instructions, observations were folded into the inference cards they support rather than emitted as standalone lines)
- **total: 36**

## Boundary judgment calls
- **Excluded as calibration/card rulings**: all gate-leakage-current statements (kept only the accompanying R_xx-liveness content, per instruction); the pre-sweep SAFETIES-cell card-limit confirmation; the kernel-probe/VERIFY handshake (infrastructure, not a physics claim); the full gate-map box being "the card limits" (the box itself isn't scored, only the grid/resolution choice within it).
- **Excluded as tooling, not decision-with-consequence**: a Keithley range-argument mismatch that stopped a cell before any gate motion (zero physics/fridge-time consequence) — explicitly self-labeled "TOOLING" by the agent. By contrast, a later per-point instrument-poll bug that killed a temperature rung mid-sweep *was* kept as a decision (it cost real fridge time and produced a design change to the sweep).
- **Two supersede pairs** were identified and linked: (1) an initial zero-gate charge-neutrality-point reading from the single-gate liveness legs was later recognized as having actually read a separate top-gate-only series segment, not the true dual-gated CNP; (2) a mid-sweep, partial-record oscillation read (onset, tentative tone list, scale) was superseded by the formal full-record analysis of the same sweep once it completed. Both are flagged in the source material as explicit corrections, not just refinements.
- **Intermediate "consistent-with" calls kept as inference, not verdict**, per instructions: the single-density stacking lean, and the running verdict after the density-trajectory sweep (before the mass-splitting data existed). Only the final, post-mass-fit campaign call was scored as the verdict.
- **Decision vs. recommendation**: end-of-session forward-looking suggestions for what would strengthen the call (second contact pair, cleaner pair for a QH lever-arm pin, longer low-field record, etc.) were treated as commentary rather than decisions, since no fridge time was committed to them this session, and were not extracted as separate claims.
- **Bias-current/lock-in bring-up settings** (drive voltage, initial time constants) were folded into the first decision claim (the liveness-sweep design) rather than given a standalone card, since the settings only became a live decision once they were actually changed for a sweep.
- **Proceeding without a confirmed cryogen budget** was kept as a decision in its own right (not folded into the ladder-design decision's context only) given its explicit safety/judgment weight, but is reported jointly with the ladder design since both appear in the same authored cell and the same act of committing to the sweep.
- **De-identification**: descriptive language was used throughout in place of contact/instrument identifiers (e.g. "this contact pair," "the auxiliary gate," "the pickup channel") and in place of investigation-slug labels; run numbers are conveyed only via the `data_ids` field, never as prose identifiers, per instructions.
