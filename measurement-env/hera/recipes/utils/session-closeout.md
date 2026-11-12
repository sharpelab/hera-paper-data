# Session close-out

**Tool**: `sharpelab_nb.close_out()` owns the mechanics — stage ordering,
`mux.park()` (managed lines only), the explicit-field guard, the final
readback. This recipe carries only the decisions that build the call.

## When

At session end, per the brief's **Close-out** line. Ask vocabulary:

- **`return-to-initial`** — replay the bring-up capture: pass the
  State-capture cell's `state0` as `restore=`. For when another run is
  queued behind this one and should start from the state this session
  started from.
- **`return-to-card`** — build the stage lists from the device card's
  values (acquisition table, gate park values), not from `state0` — the
  bring-up state is not authoritative when panels have drifted from the
  card (Examples: 2026-07-14). The default for longer / multi-session
  campaigns.
- **`update-card`** — park nothing beyond what safety requires; the
  session's end state *is* the intended standing state. End-state block
  (below) still mandatory.
- **`none`** — no close-out; legal only when the brief says so explicitly.

Every ask except `none` ends with the device-card end-state block.

## Decisions

1. **Field endpoint — explicit in the call, resolved by the ask.**
   The endpoint enters only through `field=`; `close_out` raises if the
   field parameter appears in `restore=` or a stage, so a snapshot replay
   can never start a long blocking ramp as a side effect. The ask
   resolves the target: `return-to-initial` → the session-start field
   (bring-up record / VERIFY); `return-to-card` → the card's standing
   field; `update-card` → `"hold"` (readback prints the FIELD HELD
   flag). Departing from the ask — e.g. holding at B for a planned
   follow-up — is a brief deviation, handled by normal protocol, not a
   close-out rule. Where the ramp is the expensive axis, plan the
   session's last sweep to *end* at the endpoint rather than parking
   afterward (rig card, Magnet).
2. **Standing state survives by omission.** Anything not passed is
   untouched; contact grounding is `mux.park()`, never a switch reset —
   and pass `mux=` only when the device card blesses a mux this cooldown
   (hardwired cooldowns omit it). What must stay biased or closed is a
   device-card fact — read the card's wiring/standing-state notes before
   building the call.
3. **Excitation parks at the standing value, not zero** — a device-card
   fact.
4. **Heaters off — the method is rig-shaped** → rig variant.

## Output contract (binding)

- The `close_out` readback (values + validators) is the handoff record —
  it goes in `session_notes.md` under Session close / handoff.
- **Device-card end-state block**: field, gate voltages, acquisition
  state, anything deliberately held and why. The deployed card is
  canonical (`hera/CLAUDE.md`, Cards); the next bring-up reads it.

## Examples

TBD — no session has run `close_out()` yet; the first close-outs under
this recipe populate this section. Pre-tool precedents:

- `docs/notes/2026-06-17-QC0426-session/hera_scratch/shutdown.py` —
  park-quiescent: standing excitation + `mux.park()` preserving Si
  standing closures.
- `docs/notes/2026-07-14-QC0426-session/` measure cell 37 —
  return-to-card by hand: acquisition restored to card values (bring-up
  panels had drifted), full readback incl. validators.
- `docs/notes/2026-07-17-QC0426-capstone-2/` — hold endpoint: B left at
  the follow-up's start field, flagged by hand.
