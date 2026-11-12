# HERA session — <device> / <user> / <YYYY-MM-DD>

*Fill out and paste as the first message to HERA after loading
`hera_tactical.md`. The agent reads any path-pointers below.*

## Cards
See `./device_card.md` (in this measurement directory) — per-device facts
(gate stack, hBN thicknesses, contact map, prior operating points) — and
`./rig_card.md` — rig-level machine facts (magnet, thermometry, envelope,
silent preconditions). Read both before proposing.

## Recipes
- **Recommended**: <the expected arc — e.g. for device-init:
  `gate-current-sanity-check` → `gate-leakage-survey` →
  `silicon-backgate-survey`>
- **Blocklisted**: <hard no for this session, with reasons; "none" is fine>

> **Blinded campaign?** If this session is a replication / scored round /
> A/B against a known result, the campaign frame must stay out of every
> agent-visible file — see [`blinding.md`](blinding.md). The `Cooldown` /
> `Session #` fields below are scorer-side metadata in that case: fill them
> in the support log, leave them neutral here.

## Session context
- **Operator + notify** *(the human supervising the session and the
  `hera-notify` target for proposal-landed-while-idle / run-completion
  pings)*: `<name> — hera-notify --user <KEY>`, e.g.
  `Zack — hera-notify --user ZACKG`. `<KEY>` is the bare measurebot user
  key, not `SLACK_USER_<KEY>`. Omit the notify clause to disable pings —
  say so; no target is a silent no-op.
- **Notebook**: `./<YYYY MM DD>_measure.ipynb` *(or absolute path; in this
  measurement dir is fine since CC is rooted here)*
- **Cooldown**: <number, with rough start date>
- **Days into cooldown**: <integer>
- **Session # in this cooldown**: <integer>
- **Recent interventions** *(since last session — e.g. reseated contacts,
  thermal cycle, swapped a bias source, none)*: <free text>

## Close-out
<ask: `return-to-initial` | `return-to-card` | `update-card` | `none` —
per `recipes/utils/session-closeout.md` (+ rig variant); the ask also
resolves the field endpoint.>

## Campaign goal — this session
<one or two sentences — what you're trying to accomplish, what you'd like
HERA's attention on. For a fresh-insertion / device-init session: "Just
inserted, taking the device through device-init recipes; no measurement
campaign yet.">

## Notes / scratch
<anything else HERA should know that didn't fit above — e.g. "the magnet
hasn't been ramped this cooldown", "we deliberately skipped the small-poke
ramp because the contact-resistance check from cell N already confirmed
liveness", whatever's relevant.>
