# T1C extraction notes

## Files parsed
- `transcripts/*.jsonl` (single transcript file, 1162 lines): filtered to `type == "assistant"`
  messages, and within those only `content` blocks of `type == "text"` (thinking blocks and
  tool_use blocks excluded from direct quoting, though tool_use `name` counts were scanned to
  confirm no additional narrative channel was missed — the agent's tool use was almost entirely
  `Bash` calls to a notebook-collaboration CLI and `Write` calls to scratch markdown files that
  mirror the notebook cells verbatim).
- `<date>_measure.ipynb`: all markdown cells (27 of 54 cells).
- `<date>_ana.ipynb`: all markdown cells (20 of 38 cells) — this notebook is the session's
  chronological science log (raw → analysis → take per run) and carries essentially the full
  evidence chain and the final call.
- `data/<0-18>/metadata.json`: `type` and `comments` fields only, used to map each sweep name/
  description the agent used in prose ("run N") to its numeric `data/<id>`, and to confirm which
  ids are the two discarded tooling-failure stubs (a crashed live-plotter run and an int64-
  metadata-serialization failure).
- `hera_scratch/*.md` and `plan.md`: read for cross-check; these are drafts that duplicate the
  landed notebook cells and the final-call cell almost verbatim. No claims were sourced from them
  that weren't already in the notebooks — used only to confirm timing/sequence and to resolve one
  ambiguity (which data id corresponds to the discarded fan-ramp stub vs. the successful relaunch).
- `session_notes.md` and `hera_session.md`: excluded per instructions, not opened for content.

## Counts by type
- decision: 9
- inference: 16
- verdict: 1
- Total: 26

## Boundary judgment calls
- **Gate-leakage exclusion**: several run reads included gate-current/leakage figures
  (offsets, drift, single-point glitches). Per the exclusion rule these were dropped everywhere;
  only the paired Rxx/liveness content was kept (e.g. the first-sweep "pair alive" claim).
- **Card-limit-only exclusion**: the VERIFY cell's checklist (magnet zero, validators vs. device
  card, heaters off, wiring map, gate zeroing) was excluded entirely as a card-consistency check
  with no independent physics content.
- **Numeric box edges blinded**: sweep-span decisions that exactly reused the committed gate box's
  edges (the full top-gate/back-gate range) were paraphrased as "the full accessible gate box" /
  "most of the back-gate range" rather than quoting the literal volt values, since those values
  are the device-card gate limits, not a session finding. Resolution/step values (mV steps, point
  counts, field caps chosen mid-range) were kept as-is since those are the actual decisions.
- **Tooling-failure relaunches**: two sweeps failed for non-physics reasons (a live 2D-mesh
  plotter crash; a metadata int64 JSON-serialization bug). The bare fact of crashing and re-running
  identical sweep parameters was treated as boilerplate/tooling and not extracted as its own claim.
  However, one relaunch *did* carry a physics/fridge-time decision layered on top — riding an
  in-progress field ramp rather than paying the time cost to return to zero field, accepting loss
  of the lowest-field coverage — and that was kept as a decision (T1C-013).
- **"Continue, no adjustment" checkpoints**: mid-sweep health checkpoints that simply confirmed a
  sweep was healthy and continued unchanged (e.g. a row-13 checkpoint on the second field-dependent
  sweep) were not extracted as decisions, since no consequential choice was made — this is
  distinguished from the temperature-ladder's genuine mid-course inference (flat-below-7K read),
  which was kept because it's a substantive interim data interpretation, not a bookkeeping ping.
  Similarly, checkpoint/cost/time-repricing narration threaded through the transcript's non-text
  (tool-call) turns was not treated as claim content per the instructions.
  Ordinary "row N nominal" liveness pings during 2D map runs were likewise skipped.
- **Intermediate leans vs. final verdict**: every "stacking read so far" / "lean" statement after
  each successive measurement (coarse map, fine map, first field sweep, second field sweep) was
  extracted as `inference`, each chained via `supersedes` to the prior lean, per the instruction
  that only the campaign-goal call with stated strength counts as `verdict`. Only the single final
  cell ("FINAL CALL") was scored as the verdict.
- **Secondary/parallel resistance feature**: a weak, field-flat resistance ridge seen twice during
  the zero-field gate sweeps was interpreted twice — first as an open two-way fork (T1C-005), later
  resolved at the final call into a specific attribution (contact-doped strip, not a second stacking
  domain) that was kept as a distinct, `supersedes`-linked inference (T1C-025) because it is a
  materially different, checkable claim from the earlier open fork.
- **Lock-in setting changes**: the two deliberate lock-in sensitivity/time-constant changes (at
  bring-up, and again after the first sweep to kill an observed ripple) were kept as `decision`
  since they trade noise floor against point rate and were explicitly flagged/justified by the
  agent, distinguishing them from routine per-run instrument snapshot bookkeeping (not extracted).
- **Bias current**: 10 nA drive current appears throughout but was not extracted as a decision —
  it derives from a pre-existing amplitude/bias-resistor setting captured in the state snapshot at
  bring-up, not a choice made by the agent during the session.
- **`t_rel_h` estimation**: the notebook markdown cells carry local wall-clock time headers (not
  matched 1:1 to transcript timestamps); local time was mapped to the transcript's UTC timestamps
  using a fixed 7-hour offset cross-checked against the close-out cell's local header against the
  session-end assistant message's timestamp (agreement to within ~1 minute). Where an assistant
  text block gave a directly computable `t_rel_h` for the same event, that value was preferred over
  the header-derived estimate.

## Parsing notes
- No pandas used; jsonl parsed line-by-line with `json.loads`, notebooks parsed as raw JSON via
  `json.load` and cell `source` fields joined without a notebook-specific library.
- The single transcript file's `type` distribution was tallied first to confirm `assistant` was the
  correct role filter and to see the shape of non-text content before deciding to rely on the
  notebooks (not the transcript's terse text blocks) as the primary source for the physics
  narrative — the transcript's own text blocks were still fully read and cross-checked against the
  notebook content; they added timing/sequence confirmation and one interim reading (the mid-ladder
  flat-below-7K claim) that has no standalone notebook markdown cell of its own.
