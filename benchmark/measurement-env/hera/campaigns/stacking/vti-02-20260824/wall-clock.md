**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Record of record for this session's wall-clock metrics (archive pass 2026-09-09, Claude Opus subagent under Zack's direction; definitions `hera-paper/notes/trial-metrics.md`). Adopted reading: Stop = the 16:53:14 close-out (the 16:15:53 handoff was ruled incomplete by the operator at 16:44:42). Gross 4.7 h, standby 0.4 h, outages 0.0 h, **active 4.3 h**.

# Wall-clock itemization — vti-02 "T2" ablation session, 2026-08-24

Definitions of record: `hera-paper/notes/trial-metrics.md` §Wall-clock.
Format and rigor per the worked example,
`hera/campaigns/stacking/vti-01/comparison.md` §Run metrics.

**Times.** The transcript records UTC. The rig is PDT (UTC−7); **every time
below is PDT** unless marked. Archive **file mtimes are shown by `ls` on
edhar in America/New_York (EDT, UTC−4)** — subtract 3 h to convert an mtime
to rig time. Both conversions are applied consistently and are noted at each
use.

---

## 1. Sources

| Path | What it is |
|---|---|
| `hera/docs/notes/2026-08-24-vti-02-session/transcripts/b5a3eb9f-cdfc-4ca8-9117-05ee65c5cb30.jsonl` | **Session of record.** 1493 lines, 4.87 MB. First event 11:57:42, last 16:53:14. All line numbers below refer to this file. |
| `.../transcripts/8bd43b71-1035-42b4-9ceb-0ad93c374f16.jsonl` | **False start #1** — 58 lines, 11:51:43 → 11:52:44. Ran on the session's then-default model: it executed a real bring-up orientation pass (read rig/device cards, `nb cells` on the measure notebook, API reference) before the operator interrupted it at 11:52:44 (`[Request interrupted by user]`, line 57). No instrument writes, no grant, no data. |
| `.../transcripts/2cea1be4-2774-48d9-a71b-380edc5628a8.jsonl` | **False start #2** — 14 lines, 11:53:37 → 11:53:38. Died on the first turn: *"There's an issue with the selected model (`opus5`)"* (line 12). Zero work. |
| `.../transcripts/39761ee4-84c5-496e-972d-3dc850612166.jsonl` | **False start #3** — 18 lines, 11:54:07 → 11:54:43. Same failure with model id `opus5[1m]` (line 12); operator then ran `/model` at 11:54:43 and set **Opus 5 (1M context)** (line 17), which is the model the session of record runs on. Zero work. |
| `.../.transcripts/b5a3eb9f-….jsonl` (hidden dir) | In-session live mirror of the session of record, 1489 lines, mtime 19:53 EDT = **16:53 PDT**. Same content; the archived copy adds 4 trailing metadata lines. Used only to corroborate the session end time. |
| `.../data/0 … data/12`, `data/log.log` | 13 sweep dirs. Directory + `data.tsv.gz` mtimes used to corroborate which sweep was running during each gap. |
| `.../20260824_measure.ipynb`, `.../20260824_ana.ipynb` | Parsed as JSON. **Only the operator-run bring-up cells carry `metadata.execution` timestamps** (measure cells 2–27, all 18:44:03–18:44:12 UTC = 11:44 PDT). Every agent-executed cell went through `nb-collab`, which leaves no execution metadata — so the notebooks give no independent clock for the measurement phase. Their file mtimes do: ana `19:14 EDT = 16:14 PDT` (the call cell landing), measure `19:43 EDT = 16:43 PDT` (the mandated close-out cell). |
| `.../session_notes.md` | mtime `19:53 EDT = 16:53 PDT`; last write is the agent's final close-out correction. |
| `~/Documents/Primer/Sharpelab/HERA T1 no-corpus control - vti-02.md` | Existing record, checked against the transcript in §5. |

**Do any of the false starts count?** No. All three run 11:51:43–11:54:43,
i.e. **before** the session of record even opens (11:57:42) and 14–17 min
before the E1 grant (12:08:29). `trial-metrics.md` excludes bring-up from
wall-clock explicitly. They are worth one line in the paper only as the
reason the session-of-record transcript begins ~6 min after the first
attempt, and because false start #2/#3 are model-id misconfigurations, not
provider outages — see §4.

---

## 2. Event timeline

Operator messages are quoted verbatim. "queue enqueue/remove" is how the
harness logs a message typed while the agent is mid-turn: `enqueue` is when
the operator sent it, `remove` is when it reached the agent.

| PDT | UTC | Line | Event |
|---|---|---|---|
| 11:51:43 | 18:51:43 | — | False start #1 begins (other transcript) |
| 11:54:43 | 18:54:43 | — | Operator sets model to Opus 5 (1M context) (other transcript) |
| 11:57:42 | 18:57:42.659Z | 6 | Session of record opens; brief delivered (bring-up, excluded) |
| 12:07:53 | 19:07:53 | 163 | Agent Slack-DMs the operator: gates A+B green, VERIFY cell landed, *"Say 'go for autonomy'"* |
| 12:08:24 | 19:08:24 | 169–172 | Agent's bring-up state report; turn ends |
| **12:08:29** | **19:08:29.333Z** | **173** | **START — E1 grant.** Operator: *"go for autonomy"* |
| 12:08:32 | 19:08:32 | 178 | Kernel-binding probe executed |
| 12:08:45 | 19:08:45 | 188 | VERIFY executed; `VERIFY: ALL GREEN`, E1 engaged (12:09:49, line 193) |
| 12:11:11 | 19:11:11 | 216 | Agent escalation #1 (Slack): two front-panel asks, sr1 sensitivity + time constant, *"time-critical"* — **agent keeps working**, does not drop to E0 |
| 12:14:38 | 19:14:38 | 310 | Agent escalation #2 (Slack): *"Escalating the sr1 sensitivity ask — it is now BLOCKING, not a nicety"* — still keeps working (run 0 in flight) |
| 12:16:51 | 19:16:51 | 327 | run 0 (`gatec-liveness`) near-completion notification |
| **12:17:06** | **19:17:06.513Z** | **334 (enqueue)** | **Operator message 1** (chat, queued mid-turn): *"You can change the sr1 sensitivity/time constant via the qcodes api in a cell.  you are authorized to use the values you think are best."* |
| 12:17:21 | 19:17:21.261Z | 338 (remove) | …delivered to the agent |
| 12:18:20 | 19:18:20 | 354 | Agent acknowledges the authorization and acts on it |
| 12:35:55 → 12:43:22 | | 626→631 | idle 7.5 min — gate map (run 3) mid-run checkpoint |
| 12:45:43 → 13:00:52 | | 656→666 | **Gap A, 15.1 min** — run 3 running (§3) |
| 13:00:51 | | | run 3 lands (`data/3` mtime 16:00:51 EDT) |
| 13:28:01 → 13:37:06 | | 943→947 | idle 9.1 min — Landau fan (run 4) row-22 checkpoint |
| 13:37:49 → 14:22:00 | | 968→973 | **Gap B, 44.2 min** — run 4 running (§3) |
| 14:21:55 | | | run 4 lands (`data/4` mtime 17:21:55 EDT) |
| 14:31:59 → 15:23:02 | | 1111→1116 | **Gap C, 51.0 min** — SdH down-sweep (run 5) running (§3) |
| 15:23:01 | | | run 5 lands (`data/5` mtime 18:23:01 EDT) |
| 15:29:32 | 22:29:32 | 1242 | Close-out cell (`p6_closeout.py`) written while the ladder runs |
| 15:30:21 → 16:08:13 | | 1261→1266 | **Gap D, 37.9 min** — temperature ladder (runs 6–12) running (§3) |
| 16:08:03 | | | **Last measurement the call rests on** — run 12 lands (`data/12` mtime 19:08:03 EDT); notification at 16:08:13 (line 1268) |
| 16:09:57–16:10:21 | 23:09:57 | 1298–1302 | Agent's own close-out (P6) executed: heaters off, gates to 0, field readback, close-out readback logged |
| **16:14:24 / 16:14:28** | **23:14:24.192Z / 23:14:28.070Z** | **1373 / 1374** | **The call cell lands** — `nb-collab append` of `ana_run6_take.md` + `ana_call.md` to the ana notebook issued / confirmed. (Ana notebook mtime 19:14 EDT = 16:14 PDT.) |
| 16:14:42–16:15:36 | | 1376–1388 | Session notes, erratum cell appended to the measure notebook, run inventory (13 runs, `interrupted=False` on all) |
| **16:15:53** | **23:15:53.577Z** | **1390** | **Handoff A** — *"Session complete. The rig is safe and the call is on the page."* Turn ends. |
| 16:18:58 | 23:18:58.718Z | 1399 | Harness `away_summary` fires (idle marker; no agent activity) |
| **16:41:30** | **23:41:30.856Z** | **1400** | **Operator message 2** (chat): *"Please use the mandated close_out(restore=state0) to restore the initial state"* |
| 16:42:46 / 16:42:53 | 23:42:46/53 | 1418/1419 | Mandated `close_out()` cell appended and executed (measure notebook mtime 19:43 EDT) |
| **16:43:32** | **23:43:32.258Z** | **1426** | **Handoff B** — *"the rig is in its restored initial state."* Turn ends. |
| **16:44:42** | **23:44:42.596Z** | **1430** | **Operator message 3** (chat): *"It's not a close out if the device isn't cooled to the level you received it.  what is the ETA?"* |
| 16:45:47 | 23:45:47.439Z | 1453 | Agent launches a background waiter on the sample thermometry log |
| 16:45:54 | 23:45:54.928Z | 1461 | Agent: *"ETA: 3–8 minutes, and I'm holding the session open until it's confirmed"* — turn ends, hardware wait begins |
| 16:51:43 / 16:51:51 | 23:51:51.338Z | 1467 | Target temperature reached (6 min 2 s); notification wakes the agent |
| **16:53:14** | **23:53:14.526Z** | **1489** | **Handoff C (final)** — *"Close-out is now genuinely complete — 6 min 2 s"*. Last event in the transcript (turn_duration 23:53:14.789Z, line 1492). |

Operator messages after the grant: **three**, all chat. No operator notebook
input after bring-up (the bring-up cells at 11:44 are the operator's only
notebook executions).

---

## 3. Every gap > 10 min, classified

Threshold per the brief. Sub-threshold gaps (7.5 min at 12:35:55, 9.1 min at
13:28:01, 5.9 min at 16:45:54) are all hardware waits on a running sweep or
on the sample cooling — active, listed in §2 for completeness.

| # | Interval (PDT) | Length | Classification | Evidence |
|---|---|---|---|---|
| **A** | 12:45:43 → 13:00:52 | 15.1 min | **ACTIVE — on hardware** | Line 652: *"~16 min to completion; the completion waiter will wake me."* Line 656: *"I'll wait for the completion notification rather than continue polling… The gate map (run 3) is at row 17/35."* Gap ends with the run-3 completion notification (line 666–668). `data/3` mtime 16:00:51 EDT = **13:00:51 PDT**. |
| **B** | 13:37:49 → 14:22:00 | 44.2 min | **ACTIVE — on hardware** | Line 964: *"Waiting for completion."* Line 965 arms a background waiter on `data/4/data.tsv.gz`. Line 968: *"Waiting on the fan (~13:58). Everything for the next two steps is written, validated, and queued."* Gap ends with that waiter firing (line 973–975), whose payload shows row 39/40. `data/4` mtime 17:21:55 EDT = **14:21:55 PDT**. |
| **C** | 14:31:59 → 15:23:02 | 51.0 min | **ACTIVE — on hardware** | Line 1107: *"Waiting for the down-sweep (~15:18)."* Line 1108 arms a waiter on `data/5/data.tsv.gz`. Gap ends with it firing; payload shows row 98/100 (line 1121). `data/5` mtime 18:23:01 EDT = **15:23:01 PDT**. |
| **D** | 15:30:21 → 16:08:13 | 37.9 min | **ACTIVE — on hardware** | Line 1255 (15:29:51): measure notebook `busy`, `run 6: 140 pts`. Line 1261: *"The ladder is running (run 6 at 140/245…). Waiting for it to complete at ~16:17."* Gap ends with the T-ladder completion notification. `data/6`…`data/12` mtimes 18:31:20 → 19:08:03 EDT = **15:31:20 → 16:08:03 PDT**, i.e. seven runs land *inside* this gap — the rig was working continuously. |
| **E** | 16:15:53 → 16:41:30 | **25.6 min** | **STANDBY — on human** | The agent had handed off (line 1390, *"Session complete"*) and produced no further event. The harness `away_summary` at 16:18:58 (line 1399) confirms an idle session, not a background wait: no background task was in flight (the last waiter, the T-ladder's, fired at 16:08:13 and none was re-armed). The gap ends only when the operator types (line 1400). This is the definition's *"close-out awaiting direction"* exactly. |

One sub-threshold standby also exists and is itemized in §4 for
completeness: **16:43:32 → 16:44:42, 1.2 min** (Handoff B, line 1426, idle
until operator message 3, line 1430).

**On the 12:17 capability answer — there is no standby there.** The agent
escalated twice (12:11:11, line 216; 12:14:38, line 310, calling the ask
"BLOCKING") but never dropped to E0 and never idled: it kept run 0 in
flight, polled at 12:14:44 and 12:14:50, and the longest quiet stretch
between the first escalation and the operator's answer is **1 min 48 s**
(12:15:03, line 321 → 12:16:51, line 327 — and that stretch ends with a
*sweep* notification, not the operator's). The operator's message was
**queued mid-turn** (enqueue 12:17:06, delivered 12:17:21) and picked up
in-band at 12:18:20. **Standby on this intervention: 0.0 h.**

---

## 4. Metrics

Two readings of the Stop are defensible (§5). Both are given; **Reading B is
recommended** and is the one that matches the 4.7 h the figure currently
carries.

### Reading B (recommended) — Stop = the final handoff at 16:53:14

| Metric | Value |
|---|---|
| Bring-up (excluded) | 3 false starts 11:51:43–11:54:43; session of record opens 11:57:42; E1 grant 12:08:29 |
| Wall-clock, gross | grant 12:08:29 → final handoff 16:53:14 = **4.7 h** (4.7458 h; 284 min 45 s) |
| Standby (idle on a human) | **0.4 h** (26 min 47 s) — Handoff A 16:15:53 → operator "use the mandated close_out" 16:41:30 (25 min 37 s); Handoff B 16:43:32 → operator "it's not a close out…" 16:44:42 (1 min 10 s) |
| Platform/provider outages | **0.0 h — none.** Zero `isApiErrorMessage` records in the session of record; zero API-error, overload, 529, rate-limit or retry strings anywhere in the transcript. (The two model-id errors at 11:53:38 and 11:54:07 are in false-start transcripts, are a client-side model-selection misconfiguration rather than a provider outage, and fall 14 min before the Start in any case.) |
| **Wall-clock, active** | **4.3 h** (4.2994 h) — all four >10 min mid-session gaps (2.5 h combined) are waits on running sweeps and are active per the definition |
| Interventions after bring-up (both channels, liberal) | **3**, all chat: 12:17:06 sr1 acquisition-settings authorization (answering an agent-initiated escalation); 16:41:30 use the mandated `close_out()` (operator-initiated correction); 16:44:42 close-out is not complete until the device is back at its received temperature (operator-initiated correction) |
| Agent-initiated stops (E1 → E0) | **0** — the agent escalated twice on the sr1 ask but never dropped autonomy |
| Interrupted runs | **0** of 13 (runs 0–12); line 1388 reports `interrupted=False` for every run |

### Reading A — Stop = Handoff A at 16:15:53

| Metric | Value |
|---|---|
| Wall-clock, gross | grant 12:08:29 → handoff 16:15:53 = **4.1 h** (4.1233 h) |
| Standby | **0.0 h** |
| Outages | **0.0 h** |
| **Wall-clock, active** | **4.1 h** |

Under Reading A the three post-16:15 minutes of agent work (16:41:50–16:43:32
and 16:44:54–16:53:14, ≈ 10 min of activity) fall outside the session
entirely, and operator messages 2 and 3 are post-stop.

### Consequence for the figure

The figure currently reports **4.7 h gross** for this session. That is
grant → 16:53:14, i.e. it is already using Reading B. Under Reading B the
ACTIVE number is **4.3 h**, a 0.4 h reduction. If the figure is instead
re-based on Reading A, gross and active are both 4.1 h and the bar does not
change between the two metrics at all — which is itself an argument for
Reading B, since a session whose gross and active are identical hides the
one real standby stretch it had.

---

## 5. Ambiguities, and where the definitions do not decide

**(a) The Stop — this is the live one.** `trial-metrics.md` says *"Stop: the
final handoff — the agent's close-out after the last measurement the locked
call rests on."* The last measurement the call rests on is run 12, landed
16:08:03. There are then **three** handoffs after it (16:15:53, 16:43:32,
16:53:14), and the definition does not say which is "the" close-out when the
first one is declared and then rejected.

- *For Reading A (16:15:53):* the agent performed a close-out (P6, executed
  16:09:57–16:10:21 — heaters off, gates zeroed, field readback logged) and
  handed off. On its face that satisfies "the agent's close-out."
  The Extensions clause also cuts this way: *"an operator-requested
  extension counts… when the locked call includes its data (an addendum);
  otherwise the stop is the handoff before it."* Nothing after 16:41
  produced data, and the locked call is unchanged.
- *For Reading B (16:53:14):* the operator's ruling at 16:44:42 is precisely
  that the close-out **had not happened** — the rig was not returned to the
  state it was received in (line 1439: *"You're right — I called it closed
  out with the sample at 1.761 K when I received it at 1.170 K. That's not
  restored."*). Under that ruling 16:15:53 was a *claimed* close-out, and
  the close-out event is the one confirmed at 16:51:43 / reported 16:53:14.
  The Extensions clause is also the wrong lens: this was not an extension
  for extra data, it was the completion of the close-out step itself, which
  the Stop definition already includes.
- *vti-01 precedent:* there, the stop was taken **after** a post-handoff
  operator round-trip (close-out handoff 08-20 03:40 → extension 08:57 →
  final handoff 17:22), with the intervening idle counted as standby. The
  shape here is the same, minus the new data.

**Recommendation: Reading B.** The definition's Stop is the close-out, and
the operator — who owns that judgement — ruled at 16:44:42 that the close-out
was not done. Taking 16:15:53 as the stop would silently adopt the agent's
own rejected claim as the metric, and would delete from the record the only
genuine standby the session had. Reading B also costs nothing in fairness:
the 0.4 h is *removed* from active time, not added.

**(b) The Start is unambiguous** — "go for autonomy", 12:08:29 PDT
(19:08:29.333Z), line 173. Matches the existing record exactly.

**(c) The call timestamp in the existing record (16:14:27) is ~1 s off and,
more importantly, is not a Stop.** The transcript has the append issued at
16:14:24.192Z-UTC-equivalent and confirmed at 16:14:28.070Z; 16:14:27 is
within the append. The existing record's **"4.10 h" is a grant→call
interval** (4.0997 h to 16:14:28 — the arithmetic checks out), not
grant→stop. Under either reading of the Stop, 4.10 h is not the wall-clock
figure the definitions ask for. This should be corrected in
`~/Documents/Primer/Sharpelab/HERA T1 no-corpus control - vti-02.md`.

**(d) The existing record's "no platform outages" is confirmed** by direct
check (zero `isApiErrorMessage` records, zero retry/overload strings).

**(e) Its "session end 16:53" is confirmed** — last assistant message
23:53:14.526Z = 16:53:14 PDT, corroborated by `session_notes.md` mtime
19:53 EDT and the live-mirror transcript mtime 19:53 EDT.

**(f) Its intervention list is right but its 12:17:06 timestamp is the
*send* time, not the delivery time** (delivered 12:17:21, acted on 12:18:20).
No consequence for wall-clock; worth one word if the paper quotes
response latency.

**(g) A definitional edge the paper may want to close:** the 1.2 min
16:43:32 → 16:44:42 is standby by the letter of the definition (agent idle,
handed off, waiting on a human) but is small enough that including or
excluding it does not move the one-decimal figure (4.2994 h vs 4.3188 h,
both → 4.3 h). Included above for consistency with the vti-01 practice of
itemizing every stretch.

**(h) Not decided by the definitions, and not needed here:** whether a
harness `away_summary` counts as agent activity. It is machine-generated on
idle, so I treated it as evidence *of* idleness, never as an event ending a
gap. This only matters inside gap E, where the 16:18:58 summary sits; had it
been treated as activity it would have split gap E into 3.1 + 22.5 min
without changing the standby total.
