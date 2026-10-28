## HERA — session close-out (`return-to-initial`)

`recipe: utils/session-closeout.md` + `utils/session-closeout-vti.md`. The
brief's close-out ask is **`return-to-initial`**: replay the bring-up capture so
the next run starts from the state this session started from.

- **Field → 0.0 T**, the session-start value (VERIFY read +0.0063 T). Explicit in
  the call, as the tool requires — the endpoint never arrives via `restore=`.
  From 1 T that is a ~7 min blocking ramp. The last two measurement runs were
  deliberately planned to *end* low (run 6 rode the magnet 6 → 1 T as a measured
  descent) precisely so this ramp would be short — the rig card's "plan the
  session's last sweep to end at the endpoint".
- **`restore=state0`** replays the bring-up capture: drive amplitude back to
  1.0 V from the 5.0 V this session committed, all four lock-ins' sensitivity /
  τ / filter slope back to their bring-up values, gates to 0. Everything this
  session changed on the rack was an acquisition setting, and all of it is in
  `state0`.
- **Heaters off** via the labelled callable — closed-loop LS335, so
  `heater.off("both")` drops both ranges (VTI variant). They were never on; this
  is belt-and-braces and the readback confirms nothing is lifting.
- **Si parks through `k_si`** (`smart_voltage`), never raw `voltage`, so the
  driver paces the set at `ramp_rate` — the VTI variant's Si-dielectric rule.
- **No `mux=`**: hardwired breakout this cooldown, so there is nothing to park.
- **Persistent switch and output are untouched** — operator-only per the rig
  card; close-out never touches them.

The readback that this prints is the handoff record and goes into
`session_notes.md` under Session close / handoff, together with the device-card
end-state block.
