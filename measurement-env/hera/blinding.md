# Blinding conventions — keep the campaign frame out of agent-visible files

*Companion to `session_template.md` and the card schemas
(`rig-cards/EXAMPLE.md`, `device-cards/EXAMPLE.md`). When a session is part
of a **blinded or benchmarked campaign** — a replication, a scored round, an
A/B against a known prior result — the agent must not learn that it is being
benchmarked. This doc is the rule for keeping that frame out of the files the
rig agent reads. Not every session is blinded; when one is, the brief says so
(scorer-side) and these conventions bind the deployed kit.*

## The failure mode

The isolation premise is "no prior measurement data exists for you." It is
defeated not only by leaking *data* but by leaking the **meta-frame**: that a
round 1 happened, that a known answer exists to hit, that this is a
"replication". An agent that knows it is being scored against a prior result
reasons differently — toward the expected answer — even with zero data
crossing. The frame is information.

Two burns, same class (STYLE rule 11, *an operational default quoted in an
agent-visible file becomes an inherited choice*):

- **Si = +50 V** (2026-06-10): an operating setpoint quoted in an
  agent-visible file became the agent's inherited choice.
- **"round 2" / "replication" / "2026-06-01 cooldown"** (2026-06-14): shipped
  in the deployed `device_card.md` header and the measure/ana notebook
  headers — built into the very round-2 template set created to fix the Si
  leak. The agent propagated it (device-card write-back "Session findings —
  round 2"). Its *reasoning* stayed blind (it refused a round-1 overlay
  script on isolation grounds), but the frame was in front of it the whole
  session.

## The rule

**Agent-visible artifacts carry the science, never the campaign frame.**
Agent-visible = anything the rig agent reads: the brief (`hera_session.md`),
`device_card.md`, `rig_card.md`, the measure/ana notebook headers and
markdown, recipe Examples, `hera_scratch/`, committed agent-memory.

In those files, **forbidden** when the campaign is blinded:

- **Round / session identity**: "round 2", "round N", "session 3 of this
  cooldown", "replication", "repeat run", "re-do". Use neutral framing — the
  device, the date, the goal. No ordinal that implies a prior.
- **Prior-result framing**: "benchmark", "known answer", "expected", "match
  the prior", "ground truth", "score", "as before", any reference to a
  specific prior campaign or cooldown date that the agent is meant to
  reproduce.
- **Operating setpoints as defaults** (the standing STYLE-11 rule, restated
  here because it is the same leak): gate operating points, screening
  voltages, sensitivities quoted as a value the agent should adopt. Examples
  cite *where* a value is recorded (`measurement_config`, device card,
  notebook index), never quote it as the choice to inherit.

The neutral form of the round-2 header that burned:
`# Device card — QC0426 — <date>` (not `… — round 2`); brief goal "classify
the stacking of this device" (not "replicate the round-1 ABC call").

## Where the frame is allowed to live

The round / scoring / replication identity lives **only in scorer-side
docs** — the support-session log, the scorecard, the safeties sheet — which
already carry the standing quarantine header (*SCORER / SUPPORT-SIDE — not
for agent view*). The fence is the agent prompt's data-isolation rules plus
this convention; the two together keep the frame on the scorer side of the
wall.

## Per-session checklist (run before deploying a blinded kit)

Before a blinded session goes live, grep the deployed agent-visible files for
the frame and neutralize any hit:

```bash
grep -rniE 'round[ -]?[0-9]|replicat|benchmark|ground[ -]?truth|known answer|as before|cooldown [0-9]' \
  device_card.md rig_card.md hera_session.md *_measure.ipynb *_ana.ipynb
```

`session_template.md`'s own `Cooldown #` / `Session # in this cooldown`
fields are **scorer-side metadata** — fill them only in the support log, not
in the deployed brief, when the session is blinded. (For a non-blinded
session they are fine in the brief.)

Triage (Chiron) re-audits these surfaces every run under Scope hygiene; a
frame leak is a high-priority queue item and a `blinded-r2-set`-class
recurrence.
