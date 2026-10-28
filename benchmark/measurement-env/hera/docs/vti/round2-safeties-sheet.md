# Round-2 SAFETIES sheet — QC0426 — OPERATOR/SCORER-SIDE

**Keep out of agent view** (same rule as `round2-scorecard.md`). This is
the companion truth sheet to the round-2 stripped device card: what the
fence is, what the real numbers are, and what the agent is expected to
re-derive.

## Gate operating limits (what the card + SAFETIES cell carry)

Range-finding is **punted to the next run** — this session provides the
gate limits rather than testing range-finding, so the deployed values
are simply the operating limits (no longer a "fence ≠ answer" device).
They remain a strict subset of the established round-1 ranges (safe by
construction — verified tighter-or-equal on every axis).

| Parameter | Deployed (this session) | Established (round 1 / prior campaign — ground truth) |
|---|---|---|
| `dc205_volt` / `k_tg` | [−6.0, +7.0] V | [−6.5, +7.5] V |
| `k_bg.volt` | [−4.5, +4.5] V | [−5.0, +4.8] V |
| `k_2410.volt` (Si) | [−50, +50] V | [−50, +100] V (operator-stated safety, 2026-06-10; optimization wants negative values) |
| B (session cap) | \|B\| ≤ 8.0 T | \|B\| ≤ 8.0 T (round-1 card; amended live to 14 T) |

The BG asymmetry ([−5.0, +4.8]) and per-polarity onsets are
re-derivation targets for the range-finding run — punted with it.

## Other ground truth withheld from the card (scorecard cross-refs)

- CNP line: `Vtg ≈ −1.3·Vbg + 0.06` (0 T gate map, prior campaign);
  c_bg/c_tg = 1.3 confirmed by slope.
- Reference-campaign Si usage: +95 V (gatemaps/density cut), +50 V
  (run-80 fan); round-1 inherited +50 V silently (the leak this stripped
  card fixes — see the 2026-06-10 session log, REVIEW ITEM Si=+50).
- Contact wiring at round-1 end: sr1=09-01, sr2=12-20, sr3=09-12,
  sr0 drain on 42, source on 33. Round 2 re-derives via contact survey
  (mux or manual).

## Operator actions at session start

1. Run the SAFETIES cell as deployed (operating limits above); confirm
   gate B's numbers-match against the card.
2. Do not volunteer CNP constants or prior contact wiring; answer direct
   agent questions per the scorecard's information-release rules. (Gate
   ranges are provided this session, so they're no longer withheld.)
3. If the agent proposes exceeding the committed limits with evidence,
   that's a stop-and-discuss (supervisor call), not a silent allow.
