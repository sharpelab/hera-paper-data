# Rig cards — layer model, deployment, interactions

Rig cards carry per-fridge machine facts: magnet semantics, thermometry
topology, silent preconditions, standard equipment, quirks. One card per fridge (`VTI.md`, `toploader.md`, …);
`EXAMPLE.md` is the authoring template.

## The layer model

| Layer | Artifact | Carries | Changes when |
|---|---|---|---|
| Protocol | agent prompt (`hera_tactical.md`) | how to behave: gates, handshakes, tools, working style | the methodology changes |
| **Machine** | **rig card** | what the fridge is: magnet, thermometry, equipment defaults | the hardware changes |
| Sample | device card | what's bonded: wiring, gates, validators, calibrated values | the device / cooldown changes |
| Campaign | session brief | what we're after: goal, recipes in play, references, blocklist | the session changes |
| Method | recipes | how to measure a thing, rig- and device-agnostic | the technique improves |

Tie-break for a contested fact: **does it survive a device swap?** →
rig card. Does it survive a rig swap? → protocol or recipe. Is it
chosen per session? → brief or device card. Worked cases:

| Fact | Home | Why |
|---|---|---|
| Driver field limit (`max_field_T`) | rig card | machine property |
| Session field cap | device card + SAFETIES | per-session choice inside machine limits |
| Never-re-traverse discipline | rig card | derived from this magnet's fixed slow ramp |
| QSwitch identity, port-wander, `settle_s` default | rig card | rack hardware behavior |
| `lines`/`breakouts` maps, calibrated settle | device card | bonding/wiring, changes per load |
| Default GPIB/COM addresses | rig card (as defaults) | device card overrides/fills holes; addresses move |
| Timing rules of thumb | rig card (as defaults) | calibrate per session against real runs — never inherit blindly |

The equipment model is **defaults with holes**: the rig card lists what
is racked and its usual addresses/roles; the device card fills the
per-device holes (wiring, gains, roles) and wins any conflict.

## Deployment and the improvement loop

- **Repo-canonical.** The card's truth lives at
  `hera/rig-cards/<rig>.md`. This is the opposite of device cards,
  whose deployed copy is canonical and mutates per cooldown.
- **Deployed as a copy** named `rig_card.md`, next to `device_card.md`
  in the measurement directory. The fixed, rig-anonymous name lets
  prompts and gates reference it generically and keeps deployed dirs
  uniform.
- **Agents are READ ONLY on the repo.** A rig-card error or gap found
  in-session goes into `session_notes.md` (TOOLING/PROTOCOL entry);
  post-session triage applies it to the repo card; the next deploy
  picks it up. Copy → use → note → triage → commit — same loop as
  recipes.
- A finished card has no `[VERIFY]` markers (see EXAMPLE.md header):
  the rig layer is static; open questions get resolved with the rig
  owner before the card ships, or live on the device card if they are
  actually session-scoped.

## Gate B — the rig-card leg

Gate B today: SAFETIES cell ran in this kernel, and its committed
values match the device card's validators. The rig card adds a third
leg, validated the same way (read both, compare numbers, don't
eyeball):

1. **Caps inside machine limits.** The SAFETIES field cap (and any T
   cap) sits inside the rig card's stated machine limits.
2. **Silent preconditions read.** The card's Silent preconditions
   table names each hazard's one-line read; the gate (and any proposed
   cell's preflight asserts, per the prompt's working-style bullet)
   uses exactly those reads. This is where temperature gets checked.

## What migrated out of the tactical prompt

Applied 2026-06-12: `hera_vti.md` was stripped of all VTI content and
renamed **`hera_tactical.md`** — the sole, rig-agnostic tactical prompt
(installed as the `hera-tactical` agent). The old toploader v0 prompt
was deleted once `rig-cards/toploader.md` absorbed its rig content
(git history has it as `hera_tactical_old.md`). If a fact resists
card-ification, that's signal the schema needs adjusting, not grounds
to put it back in the prompt.

Moved to `rig-cards/VTI.md`:

- **"VTI rig conventions"** — the entire section: *Sweep stack*, *Data
  on disk*, *Magnet discipline (FastBi1K5)*, *Wall-clock arithmetic*'s
  rig numbers (the "price everything / estimate in the markdown" rule
  itself is protocol and stayed).
- Machine clauses embedded in protocol sections: the magnet facts
  restated in **"What you do not do" → "No magnet shortcuts"** and in
  **"When things break" → "Sweep interrupted"** (the protocol clauses
  stayed).
- Working directory / environment VTI-isms (paths, PC name) — now
  Identity facts on the card; the prompt describes the layout
  generically.

Stayed in the prompt (protocol, fridge-agnostic): gates A/B/C, notebook
policies, analysis workflow, working style (incl. "preflight the
silent preconditions", which *points at* the card), session notes,
tools, blast-radius rules.

The prompt gained: read `./rig_card.md` in the first-turn protocol
(alongside `./device_card.md`), and Gate B's rig-card leg.
