**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Record of record for this session's wall-clock metrics (archive pass 2026-09-09, Claude Opus subagent under Zack's direction; definitions `hera-paper/notes/trial-metrics.md`). Adopted: gross 15.3 h, standby 0.0 h, outages 0.0 h, **active 15.3 h**.

# Wall-clock itemization — vti-02 "replication" session, 2026-08-22 (Fable 5, with corpus)

Definitions of record: `hera-paper/notes/trial-metrics.md` §Wall-clock.
Format and rigor: `hera/campaigns/stacking/vti-01/comparison.md` §Run metrics.
**Timing only** — no device, fabrication, or Raman content is reported here.

**Time base.** Transcript `timestamp` fields are UTC. The rig is PDT (UTC−7).
Everything below is **PDT** unless a UTC stamp is given alongside. The offset is
confirmed inside the archive, not assumed: at transcript UTC
`2026-08-23T17:11:39Z` the agent ran `date` on the rig and the tool result reads
`Sun, Aug 23, 2026 10:11:39 AM`
(`transcripts/b0c3c413-…jsonl` L1553). `data/log.log` and the notebook cell
outputs are written in that same rig-local (PDT) clock; `data/` directory mtimes
on edhar are EDT (= PDT + 3 h) and were converted.

---

## 1. Sources

| Path | Used for |
|---|---|
| `/home/zack/sharpelab/hera-paper/notes/trial-metrics.md` | definitions (start / stop / standby / outage) |
| `/home/zack/sharpelab/measurement-env/hera/campaigns/stacking/vti-01/comparison.md` | deliverable format, precedent rulings |
| `…/2026-08-22-vti-02-session/transcripts/b0c3c413-7523-44ec-a7c1-d3680081c6cb.jsonl` | tactical session, 1934 lines, 1566 timestamped records — the authority for grant, every operator message, every agent event, the handoff |
| `…/2026-08-22-vti-02-session/transcripts/3f421a26-3bdb-47d3-afe8-84bc73f8812e.jsonl` | `hera-session` bring-up transcript, 245 lines — used only to bound the excluded bring-up |
| `…/2026-08-22-vti-02-session/data/log.log` | sweep start/stop stamps in rig-local time (360 lines) |
| `…/2026-08-22-vti-02-session/data/{0..14}/` | mtimes, cross-check on sweep completion |
| `…/2026-08-22-vti-02-session/20260822_measure.ipynb` | exec-count / cell-output timestamps (parsed as JSON, not executed) |
| `…/2026-08-22-vti-02-session/session_notes.md` | agent's own log — treated as a *claim*, not evidence (it disagrees with the transcript; see §5) |
| `/home/zack/Documents/Primer/Sharpelab/HERA T1 no-corpus control - vti-02.md` | existing record, verified against the transcript |

---

## 2. Event timeline

Excluded bring-up (protocol, per the definition): `hera-session` transcript runs
**08-22 22:47:40 → 23:34:22** (L6 first operator message "Begin session setup.";
L225 23:30:37 "i fixed the keithley celsl and ran them all, ready for hand off").
Tactical brief delivered 23:31:11.

| # | PDT | UTC | Event | Evidence |
|---|---|---|---|---|
| — | 08-22 23:31:11 | 08-23 06:31:11 | Session brief delivered to `hera-tactical` (still E0) | tactical L6 |
| — | 08-22 23:36:44 | 06:36:44 | Agent state summary: "then I wait on the grant" | L211; `turn_duration` L214 |
| **START** | **08-22 23:45:39** | **06:45:39** | **E1 grant — operator message, verbatim: "He level is fine, system is closed loop.  He not a concern.\n\ngo for autonomy"** | tactical L215 |
| 1 | 08-22 23:45:41 | 06:45:41 | "Grant received. Executing the kernel probe first, then VERIFY." | L218 |
| 2 | 08-22 23:45:48 | 06:45:48 | Kernel probe BOUND (measure exec 16) | L228 |
| 3 | 08-22 23:45:55 | 06:45:55 | `VERIFY: ALL GREEN` — E1 engaged (measure exec 17) | L233 |
| 4 | 08-22 23:46:30 | 06:46:30 | run 0 starts (first hardware motion) | `log.log:12` |
| 5 | 08-23 00:01:05 | 07:01:05 | runs 0–3 complete | `log.log:66` |
| 6 | 08-23 00:05:13 | 07:05:13 | run 4 starts | `log.log:79` |
| 7 | 08-23 00:08:30 | 07:08:30 | **run 4 INTERRUPTED** by the agent at its own first-rows checkpoint (3 m 16 s) | `log.log:85–87` |
| 8 | 08-23 00:09:37 | 07:09:37 | run 5 starts (re-run) | `log.log:101` |
| 9 | 08-23 01:30:51 | 08:30:51 | run 5 completes (1 h 21 m 13 s) | `log.log:167` |
| 10 | 08-23 01:33:47 | 08:33:47 | run 6 starts | `log.log:181` |
| 11 | 08-23 03:34:09 | 10:34:09 | run 6 completes (2 h 00 m 21 s) | `log.log:184` |
| 12 | 08-23 03:35:17 | 10:35:17 | run 7 starts | `log.log:196` |
| 13 | 08-23 05:10:59 | 12:10:59 | run 7 completes (1 h 35 m 40 s) | `log.log:199` |
| 14 | 08-23 05:13:05 | 12:13:05 | run 8 cell stopped at its own pre-check *before hardware*; trimmed and relaunched | L1071 |
| 15 | 08-23 05:19:06 | 12:19:06 | run 8 starts | `log.log:211` |
| 16 | 08-23 08:50:47 | 15:50:47 | run 8 completes (3 h 31 m 40 s) | `log.log:315` |
| 17 | 08-23 08:51:39 | 15:51:39 | run 9 starts (ladder rung 0) | `log.log:330` |
| 18 | 08-23 10:00:15 | 17:00:15 | run 9 completes (1 h 08 m 35 s) | `log.log:333` |
| 19 | 08-23 10:02:15 → 14:07:59 | 17:02:15 → 21:07:59 | runs 10–14, five rungs at 46 m 46 s each | `log.log:335–359` |
| **20** | **08-23 14:07:59** | **21:07:59** | **run 14 completes — last measurement the locked call rests on** | `log.log:358`; `data/14` mtime 2026-08-23 17:07:59 EDT |
| 21 | 08-23 14:08:28 | 21:08:28 | "Ladder complete (runs 9–14) … Running the full LK analysis." | L1809 |
| **22** | **08-23 14:09:57** | **21:09:57** | **CALL cell lands in the ana notebook** — `appended markdown @ 23 id=7e35bfcc` | tool_use L1832 (14:09:53) → result L1833 |
| 23 | 08-23 14:10:12 | 21:10:12 | Close-out cells appended to measure nb (`md 57f767f7`, `code 1ada9337`), ETA ~15:05 | L1836 |
| 24 | 08-23 14:10:22 | 21:10:22 | Close-out cell executed in background (return-to-initial: heaters off, gates 0, field 7 → 0 T) | L1838–1839 |
| 25 | 08-23 14:10:37 | 21:10:37 | CALL pushed to operator by Slack DM (`hera-notify`, "✅ Slack DM: sent to @ZACKG") | L1846–1847 |
| 26 | 08-23 14:10:57 | 21:10:57 | Device-card write-back authored while the ramp runs | L1851 |
| 27 | 08-23 14:11:04 → 15:01:31 | 21:11:04 → 22:01:31 | Five consecutive 600-s blocking wait slices on the close-out ramp | L1854, 1857, 1860, 1863, 1866 |
| 28 | 08-23 15:01:30–15:01:38 | 22:01:30–22:01:38 | Close-out cell reports `status: done`, `execution_count: 26`; readback printed | L1873 |
| 29 | 08-23 15:01:51 | 22:01:51 | Close-out record appended to `session_notes.md`; final Slack DM sent | L1885–1886 |
| **STOP** | **08-23 15:02:05** | **22:02:05** | **Final handoff — "**Session complete.**" close-out message** | L1888; corroborated by `turn_duration` record L1891: `durationMs 54986569` = 15 h 16 m 26.6 s, which back-computes to a turn start of 08-22 23:45:39.4 |
| 30 | 08-23 15:03:12 → 15:03:41 | 22:03:12 → 22:03:41 | Five one-line replies draining stale background wait-slice notifications from the already-finished close-out; no new work | L1897, 1903, 1911, 1918, 1929 |
| 31 | 08-23 15:06:45 | 22:06:45 | `away_summary` system record — last line in the transcript | L1933 |

**Operator messages after the grant: none.** The tactical transcript has 320
`user`-role records; every one after L215 is either a `tool_result` or a
`<task-notification>` from the harness's own background-task machinery. All 195
`queue-operation` records and all 95 `queued_command` attachments are
`<task-notification>` blocks — no human text. **0 interventions**, chat channel.
Notebook channel: measure-notebook exec counts run 16 → 26 unbroken, all agent-authored
(`20260822_measure.ipynb`, cells 31–52), so **0 interventions** there as well.

**Agent-initiated stops (E1 → E0): 0.** No `E0`, stop-and-report, or "awaiting
your ruling" text appears anywhere in the tactical transcript after the grant.

---

## 3. Every gap > 10 min, classified

70 inter-record gaps of ≥ 10 min exist. **The largest gap in the entire
post-grant session is 10.03 min** (08-23 05:24:10 → 05:34:12, L1151 → L1152).
Every one of them is the 600-second Bash tool timeout on a blocking
`until grep -q "status:" "$f"; do sleep 120; done` wait against a running
sweep's output file — i.e. the agent polling hardware, which the definition
calls **ACTIVE**. Each is bounded on the left by an assistant `tool_use` whose
`description` names the thing being waited on.

Because 10.03 min is the ceiling, **no gap in this session can be standby or an
outage**: standby requires the agent to be idle awaiting a human, and there was
no human contact after the grant at all; a provider outage of consequence would
show as a gap longer than the harness's own 10-min tool ceiling, and none exists.

Grouped by what the hardware was doing (all 70 gaps; total 700.6 min = 11.7 h):

| Window (PDT) | Slices | Minutes | Waiting on | Classification | Evidence |
|---|---|---|---|---|---|
| 00:14:30 – 01:20:54 | 5 | 50.0 | run 5 rows / completion | **active-on-hardware** | L426, 491, 494, 529, 559 ("Foreground wait slice for gatemap completion"); run 5 spans 00:09:37–01:30:51 (`log.log:101,167`) |
| 01:33:37 – 01:56:05 | 2 | 20.0 | run 6 first-rows + 3 T checkpoint | **active-on-hardware** | L654, 696; run 6 starts 01:33:47 (`log.log:181`) |
| 02:08:40 – 03:29:05 | 6 | 60.0 | run 6 to 6 T then completion | **active-on-hardware** | L751, 754, 799, 802, 817, 820 ("Block until run 6 completes"); run 6 ends 03:34:09 |
| 03:40:50 – 05:08:51 | 8 | 80.1 | run 7 interim read + completion | **active-on-hardware** | L932, 954, 957, 964, 999, 1002, 1008, 1013; run 7 spans 03:35:17–05:10:59 |
| 05:24:10 – 08:50:11 | 19 | 190.2 | run 8 row-25 / row-80 checkpoints + completion | **active-on-hardware** | L1151, 1156, 1159, 1210, 1218, 1225, 1230, 1233, 1236, 1242, 1250, 1255, 1314, 1319, 1327, 1334, 1337, 1340, 1345; run 8 spans 05:19:06–08:50:47 |
| 08:56:34 – 09:58:46 | 6 | 60.1 | run 9 ("Wait for rung 0") | **active-on-hardware** | L1448, 1451, 1467, 1472, 1475, 1478; run 9 spans 08:51:39–10:00:15 |
| 10:01:32 – 10:42:14 | 4 | 40.0 | run 10 ("Wait for rung 1") | **active-on-hardware** | L1550*, 1557, 1565, 1570; run 10 spans 10:02:15–10:49:02 |
| 11:00:02 – 11:30:13 | 3 | 30.0 | run 11 ("rung 2") | **active-on-hardware** | L1612, 1615, 1618 |
| 11:40:43 – 12:21:02 | 4 | 40.0 | run 12 ("rung 3") | **active-on-hardware** | L1658, 1661, 1664, 1669 |
| 12:30:20 – 13:10:57 | 4 | 40.0 | run 13 ("rung 4") | **active-on-hardware** | L1718, 1726, 1729, 1732 |
| 13:18:51 – 13:59:13 | 4 | 40.0 | run 14 ("rung 5") | **active-on-hardware** | L1777, 1782, 1787, 1790; run 14 ends 14:07:59 |
| 14:11:04 – 15:01:31 | 5 | 50.0 | close-out magnet ramp 7 → 0 T | **active-on-hardware** | L1854, 1857, 1860, 1863, 1866 ("Wait for close-out completion"); cell launched 14:10:22, `status: done` at 15:01:38 |
| | **70** | **700.6** | | | |

\* The 10:01:32 → 10:11:32 entry is a **sorting artifact, not an idle gap**: line
1550 is a `queued_command` attachment that carries the *original* timestamp of a
task notification queued at 10:01:32 and delivered at 10:11:32 (see L1548/L1549,
both stamped 10:11:32). The agent was inside the L1546 wait slice throughout. It
is counted above as an ordinary hardware wait because that is what it was.

**Outage search — negative.** No `isApiErrorMessage`, `API Error`,
`overloaded_error`, `rate_limit`, `Internal server error`, `Retrying`,
`service_unavailable`, or `Connection error` string appears anywhere in the
1934-line tactical transcript. The 30 hits on the literal `529` are all token
counts, base64 payload fragments, or resistance values — none is an HTTP status.
The 15 `system` records are 7 `stop_hook_summary` (all `hookErrors: []`), 7
`turn_duration`, and 1 `away_summary`. Model throughout: `claude-fable-5`.

### Hardware-occupancy cross-check

Independent of the transcript, `data/log.log` gives instrument-busy time
directly: 828.97 min of sweeps (runs 0–14, including the 3.27 min of run 4
before it was aborted) plus 51.2 min of close-out ramp = **880.2 min = 14.7 h**,
which is **96.0 % of the 916.4 min gross**. The residual 36.0 min is the sum of
the sixteen inter-run dead bands (largest 8.1 min, run 7 → run 8, 05:10:59 →
05:19:06), during which the agent was analysing and authoring the next cell.
There is no unaccounted time.

---

## 4. Metrics

Times PDT (rig). Numbers to one decimal in hours.

| Metric | Value |
|---|---|
| Bring-up (excluded) | `hera-session` 08-22 22:47:40 → 23:34:22; tactical brief 23:31:11 → E1 grant 23:45:39 |
| Wall-clock, gross | grant 08-22 23:45:39 → final handoff 08-23 15:02:05 = **15.3 h** (916.4 min = 15.274 h) |
| Standby (idle on a human) | **0.0 h** — itemization: *none*. No operator message after the grant, no agent-initiated stop, no close-out awaiting direction (the handoff *is* the stop). Largest inter-record gap in the whole post-grant session = 10.03 min, and it is a hardware wait slice. |
| Outages (platform/provider) | **0.0 h** — itemization: *none*. Zero API-error records, zero retries, zero unexplained gaps; every ≥ 10 min gap is a 600-s harness tool timeout on a deliberate wait loop. |
| Wall-clock, active | **15.3 h** (= gross; monitor polls on running sweeps and the close-out ramp are active by definition) |
| — of which instrument-busy | 14.7 h (96.0 %); agent-only work with no sweep or ramp running: 0.6 h |
| Interventions (operator messages after bring-up, both channels, liberal) | **0** — chat: none after the grant; notebook: none (measure exec 16 → 26 unbroken and agent-authored) |
| Agent-initiated stops | **0** |
| Interrupted runs | **1** of 15 sweeps (runs 0–14): run 4 aborted by the agent at its own first-rows checkpoint after 3 m 16 s (`log.log:85`), re-run as run 5. One further cell (run 8) failed its own validator pre-check twice at 05:13 before hardware moved — not an interruption, no run existed. |

### Reconciliation with the existing record

`Primer/Sharpelab/HERA T1 no-corpus control - vti-02.md` states grant 23:45 →
call 14:10 → close-out 15:04 = 15.3 h gross, 0 interventions. Verified against
the transcript: grant **23:45:39** ✔; call cell **14:09:57** (rounds to 14:10) ✔;
0 interventions ✔; 15.3 h ✔. The one correction is the handoff stamp — the
close-out message is at **15:02:05**, not 15:04; 15:04 appears to round the
15:03:41 last-line stamp. The correction does not move the reported figure:
15:02:05 → 15.274 h and 15:03:41 → 15.301 h both give **15.3 h**.

---

## 5. Ambiguities and where the definitions do not decide

1. **Which of the three end-stamps is "the final handoff."** Candidates:
   15:02:05 (the "Session complete." close-out message, and the end of the
   single autonomous turn per `turn_duration`), 15:03:41 (last assistant line,
   five one-sentence acknowledgements that stale background notifications needed
   no action), 15:06:45 (`away_summary`, a harness artifact). I used **15:02:05**
   as the substantive close-out. All three round to 15.3 h, so nothing rests on
   the choice. *Recommend the paper adopt "end of the agent's close-out turn"
   as the operational rule* — it is machine-readable from `turn_duration` and
   immune to notification drain.

2. **Whether the 51-min close-out ramp belongs inside wall-clock at all.** The
   definition's stop is "the agent's close-out after the last measurement,"
   which plainly includes it, and vti-01 counted its close-out the same way — so
   I counted it. But it is worth naming that the *scientific* session ended at
   14:09:57 with the CALL cell, 14.4 h after the grant, and the last 0.9 h is
   return-to-initial rig housekeeping. If the figure ever wants "time to the
   locked call," that number is **14.4 h** (grant → CALL cell; grant → run 14
   complete is also 14.4 h). This does not affect standby or outage, which are
   0.0 h either way.

3. **The archive's own prose disagrees with the transcript, twice.**
   `session_notes.md` records "E1 granted 23:35" and "Close-out readback
   (measure cell 52, exec 26, 15:12)", and the agent's final message says the
   arc was "23:35 → 15:12". Both are the agent's estimates written from memory,
   and both are wrong: the grant is timestamped 23:45:39 at tactical L215, and
   the close-out cell reported `status: done` between 15:01:30 and 15:01:38
   (L1873) against an ETA the agent had itself quoted as "~15:12" at 15:01:34
   (L1871) — it wrote the estimate into the log instead of the readback. Using
   23:35 → 15:12 would give 15.6 h, an over-count of 0.3 h. **The transcript is
   used throughout; `session_notes.md` timings are not.** Chiron may want the
   note that the session log's self-reported "≈ 15.5 h hands-off" is derived
   from these two bad stamps.

4. **The 10-min ceiling is a harness artifact, not a physical one.** Every wait
   in this session was chopped into 600-s slices by the Bash tool timeout, so
   the gap distribution is censored at 10 min by construction. That is why the
   ">10 min gap" screen is uninformative here and the classification instead
   rests on (a) the wait command's own target, (b) `log.log` sweep boundaries,
   and (c) the 96 % instrument-occupancy cross-check. A session on a harness
   with a longer tool timeout would not be comparable on gap statistics alone.

5. **Standby is structurally zero, not measured as zero.** The definition scopes
   standby to "idle waiting on a human." This session had exactly one human
   contact — the grant — and it opens the clock. There is therefore no window in
   which standby *could* have accrued, and 0.0 h is a consequence of the session
   shape rather than an empirical finding about pacing. Worth stating that way
   in the figure, so 0.0 h here is not read as an improvement over vti-01's
   16.6 h; the two sessions differ in how many rulings the agent needed, not in
   how promptly the operator answered.
