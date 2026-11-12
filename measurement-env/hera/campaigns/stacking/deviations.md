# Deviations register — arm 1

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Departures from
`prereg-protocol.md` (§7); published with the series.

## 2026-08-19 — vti-01 intake

- The device (alias vti-01) was cooled and measured before its seal: the
  owner ran transport, and Aaron's sealed call fuses Raman with his own
  transport. Not "fresh at cooldown" per §2; the seal hashes were
  committed 2026-08-19, after cooldown start, not pre-series per §5
  step 0.
- Intake facts were drafted by the device owner and amended by the
  shield; §4 assigns intake authorship to the shield alone. The fab id
  was visible to the operator via the handoff filename (the kit carries
  the alias only).
- BIAS_R (10 MOhm) entered via the owner's handoff message, not the
  shield form — the form predates the field.
- No Hall pair is wireable this cooldown (right-side contacts dead); the
  provided configuration is Rxx-only.
- Template surfaces changed at vti-01 intake, pre-freeze-tag: device-card
  template gained LOCKIN_ADDRS / BIAS_R / DRIVE_FREQ / SR0_GAIN slots and
  dropped fixed prior-cooldown tuning text; the intake form gained the
  matching fields; hera-session now fills setup-cell instrument addresses
  from the card.
