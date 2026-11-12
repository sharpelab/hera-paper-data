# T1B extraction notes

## Files parsed
- Transcript: single `transcripts/*.jsonl` (1855 lines; 536 assistant messages, 81 top-level
  assistant `text` blocks, 175 `thinking` blocks not used as claim source, 280 `tool_use` blocks).
  Assistant `text` blocks were dumped in order with elapsed-hours timestamps and read in full.
  `thinking` blocks were not treated as asserted claims (internal reasoning, not something the
  agent asserted or acted on) except where cross-referenced to disambiguate timing.
- `*_measure.ipynb`: all 35 markdown cells read in full (measurement-design rationale, cost
  pricing, checkpoint/discriminator plans).
- `*_ana.ipynb`: all 21 markdown cells read in full (raw-then-read chronological science log,
  calibration commits, per-run "Read" cards, THE CALL, CALL ADDENDUM).
- `data/<id>/metadata.json` for ids 0-20: `type` + `comments` read for every id to confirm
  run-number-to-data-id mapping and sweep identity.
- `session_notes.md` and the hera-session/root session markdown were NOT read, per instructions.
- Tool-use payloads (Bash/Write inputs) were grepped for a set of distinctive phrases to recover
  more precise elapsed-time anchors for major inference/decision/verdict landings than the
  chat-facing text blocks alone provided; this was timing-only, not a new source of claim content.

## Counts by type
- decision: 17
- inference: 17
- verdict: 2
- total: 36

## Boundary judgment calls
- **Gate-leakage exclusion applied broadly.** All claims about the top-gate leak itself (onset
  voltage, excess current, local conductance, PASS/FAIL calls on either gate, the "stop-and-report"
  branch, and the agent's own recommendation to restrict the gate's working range) were excluded
  entirely as unjudgeable instrument-offset territory, per the spec. Only the bundled R_xx/liveness
  finding (contact-limited source-drain resistance, unmodulated by either gate) was kept, per the
  explicit carve-out.
- **Card-limit language blinded.** Wherever a sweep's endpoint coincided with a device-card safety
  limit (gate ranges, field cap, temperature cap), the claim/context text was written as "the card
  limit(s)" rather than restating the specific volt/tesla/kelvin number, since the number itself
  duplicates the card and isn't the physics claim. Physically meaningful numbers (density, field,
  temperature, frequency, mass, resistance, ratios) were kept exact.
- **Observations folded, not extracted standalone.** Per the spec, raw data readings (e.g. "row N
  nominal", individual FFT peak positions) were folded into the inference cards that rest on them
  rather than written as separate `type: observation` lines; no standalone observation entries
  appear in the output.
- **Preliminary/interim reads treated as superseded, not separate open claims.** Three cases where
  a mid-run or partial-record read was later resolved or retracted by the completed record were
  written as two linked claims with `supersedes`: (1) a partial-record channel-divergence flag on
  the first spot check, resolved once the full record showed three-channel agreement; (2) a
  polynomial-degree-sensitive low-frequency hint in the quality map, resolved once the completed
  map isolated a real third branch; (3) the low-field pocket-search null, revisited and given a
  competing-hypothesis exclusion once the quality map + descent sweep directly resolved that pocket.
- **Two verdict entries, linked by supersedes.** The mid-campaign "THE CALL" and the later
  "CALL ADDENDUM" (after an operator-requested higher-quality remeasurement) are both extracted as
  `verdict` (per spec: "the campaign-goal call... with its stated strength"); the addendum is marked
  as superseding the original since it changes the stated strength/branch-count of the same
  region's stacking call, not a fresh independent verdict.
- **Decisions vs. checklist/verify boilerplate.** Pre-flight kernel-binding probe / VERIFY-checklist
  authoring, and the initial autonomy-grant bookkeeping, were treated as excluded checklist/verify
  authoring per the spec and not extracted, even though they precede the first extracted decision.
- **Si contact-doping split into four claims** (design/electron-inert/design-hole-side/inert-both-
  signs) rather than one, since each step was a distinct choice made in light of the immediately
  preceding result (a real fork point: agent chose to try the opposite gate polarity rather than
  escalate immediately), and each carries separately checkable numeric content (drain-current
  baseline, phase reading, frequency/linearity discriminators).
- **Minor mid-sweep asymmetry note kept as a small standalone inference** (electron side more
  resistive than hole side at matched field) since it is a genuine physical claim a reviewer could
  independently check against the raw traces, even though it wasn't load-bearing for the final call.
- **t_rel_h precision.** Most timestamps come directly from the chat-facing assistant `text` blocks
  (hours since the first assistant message in the transcript). For a handful of claims whose
  content was authored directly into a notebook cell without an accompanying chat message (e.g.
  the run-9 cross-side read, the fan-10 result, THE CALL itself), elapsed time was recovered by
  grepping tool-use payloads for distinctive phrases from that content and taking the timestamp of
  the matching Bash/Write call; precision is to the nearest ~0.01-0.05 h, not exact.
- No corrupted/unparseable JSONL lines encountered; no markdown cells were empty or template-only
  beyond the notebook's own header/scaffold cells (excluded as non-claims).
