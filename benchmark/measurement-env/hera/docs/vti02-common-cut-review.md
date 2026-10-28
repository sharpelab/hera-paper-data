# vti-02 common cut — where the five live sessions diverge, and where to cut

Read-only survey of `hera/docs/notes/2026-08-2{1..5}-vti-02-session`, against
`hera/docs/replay-fresh-start-plan.md`. Nothing in the repo was modified; no
`hera-replay run`/`cut` was executed.

Timestamps below are transcript wall clock (UTC in the jsonl), not rig-local.
Line indices are 0-based jsonl line numbers, matching `hera-replay inspect`.

---

## 0. Headline findings (the ones that change the plan)

1. **The fan-design decision point separates the arms cleanly; the spot-check
   decision point cannot.** At the first FS-count Landau fan, all five sessions
   have a live reference. Scored with the existing `hera/graders/fan-design`
   `resolution.py` (Aaron's m = 3, `b_cut` = 2.4 T from `graders/devices.toml`):
   corpus 1.000 / 1.000, no-corpus 0.805 / 0.674. At the spot-check point the two
   no-corpus sessions **never ran a spot check at all**, so the plan's criterion
   "each live session's own choice falls inside its cell's offline distribution"
   has no value to check for the no-corpus cells there.

2. **The corpus contains the exact rule the grader scores.**
   `hera/recipes/measurements/landau-fan.md` step 1: *"a per-column SdH-FFT fan
   samples uniform in 1/B (`field_invB`, B_lo > 0) and needs Δ(1/B) ≤ 1/(2·F) (prefer
   1/3) at the highest n"* — plus the aliasing warning. The corpus sessions applied
   it (3.3–3.5 rows/period at the binding edge); the no-corpus sessions did not
   (1.1 and 1.5). 08-24 discovered its own aliasing after the fact and wrote it into
   `session_notes.md`. The causal story at this frontier is airtight.

3. **Zack's recollection is half right.** Only **08-23** measured while ramping
   (`magnet.start_field_ramp(8.0)` then rows; runs 5/6/7). **08-24 never did** — both
   its field acquisitions are stepped `multimegasweep([magnet.field], [field_invB(...)])`.
   08-24's failure is a different one: a stepped 1/B grid whose step is ~2× too
   coarse, aliasing the top-density columns. The P4b markdown title "SdH trace
   measured through the ramp down" is rhetorical ("we have to ramp down anyway") —
   the cell is stepped.

4. **08-25's good fan is the operator's design, not the agent's.** At transcript
   line 1505 (06:11:58) — after the agent had declared the session complete — the
   operator typed: *"Take an electron side fan at tau=300ms, B 1-8T in inv_b, much
   finer B. Say 4-6hr fan."* and at line 1546: *"…ramp down. take at least 100B
   steps."* Run 8 (the one scoring 1.000) implements exactly that. **08-25's
   agent-authored fans are the two deliberately-coarse calibration fans (0.503).**
   The Opus+corpus cell therefore has no clean agent-authored FS-count fan as a
   live reference.

5. **Only 08-24 has a clean fan-design cut window.** In 08-21, 08-22 and 08-23 the
   agent drafted the next cell into `hera_scratch/` *while the current run was still
   acquiring*, so every cut with a completed prior run also contains the archived
   agent's own design on disk. 08-24 drafted `p4_fan.py` only ~3 min after its
   gate-map analysis closed, leaving a usable 3-minute window (lines 704–729,
   20:03:41–20:06:56).

6. **Two harness blockers**: `open_archive` rejects 08-24 (four transcripts — three
   aborted tactical starts at 18:51/18:53/18:54, all with the session dir as cwd, so
   the `_is_init_transcript` heuristic doesn't filter them) and rejects 08-25 (the
   agent `cd`'d into `hera_scratch` for lines 690–705, so the transcript carries two
   cwds, both inside the session dir). `cut.transcript` in the case yaml is only a
   cross-check — it does not bypass `open_archive`. Both fixes are small.

---

## 1. Per-session decision timeline

Cell indices are measure-notebook indices (`nb summary`). "→ run N" is the data run
the cell produced. Times are the `nb-collab append` / draft time in the transcript.

### 2026-08-21 — Fable 5, corpus (transcript `b6d6abb9…`, 1371 lines)

| # | cell | run | t | design |
|---|---|---|---|---|
| probe/VERIFY | 31,33 | — | 03:19 (L143) | read-only |
| Gate C liveness | 35 → re-land 37 | 0–3 | 03:23 (L239, L269) | 4 single-gate legs to each card limit; re-land for a Keithley assert tolerance (agent's error) |
| **first gatemap** | 39 | 4 | 04:00 (L455) | TG −0.3…+1.0 fast ×66 (20 mV) × BG −1.3…+2.0 slow ×67 (50 mV) = 4422 pts; sr1 50 µV; dwell 0.7 s (7τ, τ 0.1 s); 1 nA leak guard; ~1 h 20 m |
| **SdH spot check (e)** | 41 | 5 | drafted 04:30 (L602), landed ~05:07 | 1 density n = +3.0e12, D = 0; B 0→10 T **uniform in B**, dB 24 mT, 417 pts; dB = Δ(1/B)·B_lo² with Δ(1/B)=1/(3·F_L)=0.0108, B_lo 1.5 T; sr1 autorange from 2 µV, τ 0.1, dwell 0.7; ends at 10 T; ~1 h 45 m |
| Si-gate detour | 43 | 6,7 | 05:52 (L758) | two TG linecuts at B = 10 T, Si 0 vs +25 V — off-arc, tests the V_bg-independent R_xx max |
| **Landau fan (e, D=0)** | 45 | 8 | 06:55 (L831) | `field_invB(10, 2.4, 36)` descending, Δ(1/B)=0.0090; fast n 3.4→1.5e12 ×41 on the D=0 line; sr1 50 µV fixed; fast 0.7 / slow 2.0 s; ~1 h 35 m |
| LK T-dependence | 47 → re-land 49 | 9–15 | 08:27 (L1097) | Flavor B ladder, 6 rungs 4–28 K, B 2.4↔9.98 T alternating; re-land because LS335 needed per-point polling |
| close-out | 51 | — | 16:15 | return-to-initial |

Operator turns: none after the brief (a fully hands-off E1 session). Call: **ABAB, strong**.

### 2026-08-22 — Fable 5, corpus (transcript `b0c3c413…`, 1934 lines)

| # | cell | run | t | design |
|---|---|---|---|---|
| VERIFY | 31,32 | — | 06:34 | — |
| Gate C | 34 | 0–3 | 06:46 (L236) | as 08-21 |
| **first gatemap** | 36 → re-run 38 | 4, 5 | 07:04 (L351), 07:09 (L393) | TG ×66 (20 mV) × BG −1.3…+1.2 ×63 (40 mV); run 4 aborted at the first-rows checkpoint, re-run at 100 µV drive |
| **SdH spot check (e)** | 40 | 6 | 08:33 (L644) | n = +3.2e12, D = 0; B 0→10 T uniform-B, 50 mT below 1 T then **10 mT above 1 T**, 921 pts; `delay = 0` (the 3 s magnet settle = 10τ); sr1 50 µV; ~2 h 15 m |
| **SdH spot check (h)** | 42 | 7 | 10:34 (L837) | n = −1.2e12; B 10→0.3 T ride-down @ 20 mV — rides the traverse back |
| **Landau fan (e, D=0)** | 44 → re-land 46, 48 | 8 | 12:11 (L1048); drafted 09:08 (L742) | `field_invB(1, 10, 101)`, Δ(1/B)=0.009; fast n 3.27→1.60e12 ×61; sr1 100 µV; fast_delay 1.2 s; ~3 h 55 m. Two re-lands only to trim n_max 3.27→3.26→3.25 against the TG limit |
| LK ladder | 50 | 9–14 | 15:51 (L1374) | 6 rungs base–30 K, B window 2–7 T @ 25 mV alternating |
| close-out | 52 | — | 21:10 | — |

Operator turns: 1 (`"…go for autonomy"`, 06:45). Call: **ABAB**.

### 2026-08-23 — Fable 5, NO corpus (transcript `fc1603b4…`, 1162 lines)

| # | cell | run | t | design |
|---|---|---|---|---|
| probe/VERIFY | 31,32 | — | 03:21 | — |
| gate-c-liveness | 34 | 0 | ~03:27 | 1D TG 0→−0.3→+1.0→0 @ 5 mV, τ 30 ms |
| bg-sweep-1d (CNP hunt) | 36 | 1 | ~03:32 | BG 0→+2.0→−1.3→0 @ 10 mV, 661 pts |
| **gatemap-coarse** | 38 → relaunch 40 | 2, 3 | 03:42 (L513) | BG slow @ **100 mV** ×34 × TG fast ×66 (20 mV). Run 2 died — 7 × 2D live mesh plots crashed the sweep plotter subprocess |
| cnp-band-map | 42 | 4 | 04:09 (L613) | 39 rows V_bg −1.3…+0.6 × TG ±0.15 V @ 5 mV about the run-3 ridge, 2199 pts |
| **Landau fan up (D≈0)** | 44 → relaunch 46 | 5(aborted), 6 | 04:33 (L727), 04:38 (L777); drafted 04:12 (L644) | **measure-while-ramping**: `magnet.start_field_ramp(8.0)` then 38 rows × 122 gate points along the D≈0 line, B read per point, rows slanted ~0.2 T; fast_delay 0.5 s, τ 100 ms; ~65 min. Run 5 aborted: int64 row setpoints broke the metadata JSON |
| Landau fan down | 48 | 7 | 07:37 (L894) | 8→0 T continuous ramp at D−D0 ≈ +0.20 V/nm, 40 rows × 125 pts |
| cnp-t-ladder | 50 | 8–18 | 08:36 (L1012) | 11 rungs base–50 K, 5 D-windows at B = 0 |
| close-out + erratum | 52, 53 | — | 18:15 | operator asked `return-to-initial` |

Operator turns: `"go for autonomy"` (03:27), six bare `.` nudges 05:46–07:32 (during
the fans), `"return-to-initial"` (18:14). Call: **ABAB** (the plan doc: weakest claims
of the series).

### 2026-08-24 — Opus 5, NO corpus (transcript `b5a3eb9f…`, 1493 lines)

| # | cell | run | t | design |
|---|---|---|---|---|
| kernel probe / VERIFY | 31, 33 | — | 19:07 (L151) | — |
| `plan.md` written | — | — | 19:04 (L113) | full P1…P6 plan into `hera_scratch/plan.md` (brief-mandated) |
| gatec-liveness | 35 | 0 | 19:11 (L234) | 1D BG −1.3→+2.0 ×133 (25 mV), τ 0.3 s, dwell 2.1 s. sr1 **railed** at 2 µV |
| bg-cut (re-range) | 37 | 1 | 19:20 (L380) | same cut reversed, sr1 → 1 mV, τ → 0.1 s |
| **gate map** | 39 → re-run 41 | 2, 3 | 19:25 (L433), 19:28 (L500) | BG slow −1.3…+0.4 ×35 (50 mV) × TG fast ×66 (20 mV) = 2310 pts. Run 2 killed by the 2D live plot; re-run without it. Completed 20:01 |
| map analysis | — | — | 20:01–20:04 (L678–707) | `a3_gatemap.py`, `a4_symmetry.py`: CNP line fit → **measured c_tg/c_bg = 1.2737 ± 0.0470** (prior 1.1579); R_CNP 296 Ω → 3074 Ω (10.4×) with D; minimum at D/ε₀ = 0.000 ± 0.008, branches symmetric to 7 % |
| **Landau fan (D=0)** | 43 | 4 | drafted 20:07 (L730), landed 20:08 (L745) | `field_invB(0.75, 6.0, 40)` ascending; fast co-swept (V_tg,V_bg) on the measured D=0 line, V_tg −0.30→+0.60 ×46 (20 mV), n = −1.04…+2.10e12; fast 0.7 / slow 1.0 s; sr1 1 mV; stated ~1 h 30 m. **Δ(1/B) = 0.0299 → 1.54 rows/period at n_max; Nyquist 17 T vs F_L 21.6 T → top columns alias** |
| sdh-downsweep | 45 | 5 | 21:22 (L998) | `field_invB(6.0, 0.5, 100)` descending at 5 fixed densities; Δ(1/B)=0.0185 → 2.61 rows/period. Written *because* run 4 aliased |
| tladder-cnp | 47 | 6–12 | 22:23 (L1135) | 7 rungs, CNP-line multisweep at 5 perpendicular offsets |
| close-out ×2 + erratum | 49, 50, 52 | — | 23:11, 23:42 | operator: *"Please use the mandated `close_out(restore=state0)`"*, then *"It's not a close out if the device isn't cooled to the level you received it"* |

Operator turns: `"go for autonomy"` (19:08), two close-out corrections (23:41, 23:44).
**No operator involvement in any measurement design.** Call: **ABCA** (wrong).

### 2026-08-25 — Opus 5, corpus (transcript `0f342f88…`, ~1900 lines)

| # | cell | run | t | design |
|---|---|---|---|---|
| probe / VERIFY | 31, 33 | — | 00:15 (L144) | — |
| bring-up read, settling/noise ×2, drive | 35,37,39,41 | — | 00:19–00:27 | no-sweep instrument characterisation: settling floor, SNR vs drive; commits I_bias 49.2 nA |
| Gate C | 43, 45 | 0–3 | 00:32 (L323) | 4 legs; nplci reset cell |
| **first gatemap** | 47 | 4 | 00:53 (L613) | TG fast −0.3…+1.0 ×**101** × BG slow −1.3…+1.3 ×37; fast_delay 0.70 s |
| **calibration fan #1** | 49 | 5 | 01:54 (L857) | *first field of the session.* B slow 0→6 T ×**13 (0.5 T rows)**, V_tg fast ×201 at V_bg = 0. Explicitly labelled *"B rows 0.5 T are deliberately coarse: this fan is read as LL structure vs gate at each field, NOT by 1/B FFT"*. Run because the zero-field calibration did not close |
| **calibration fan #2** | 51 | 6 | 03:17 (L1055) | B 6→1 T ×6 descending, V_bg fast ×301 at the measured CNP V_tg — back-gate lever arm |
| **SdH spot check** | 53 | 7 | 04:20 (L1216) | 5 fixed (n, D=0) points [−0.9, 1.8, 2.2, 2.6, 3.0]e12, B slow 1.5→6.0 T uniform-B at dB = Δ(1/B)·B_lo² with Nyquist ×3 on F_L = 32 T; sr1 → 100 µV; ~1 h 10 m |
| close-out (interrupted) | 55, 57 | — | 05:49 (L1435) | agent declares the session complete |
| **FS-count fan** | 59 | 8 | 06:15 (L1526) | **operator-specified** (L1505, L1546): `field_invB(8, 1, 101)` descending, n fast 1.2→3.05e12 ×57 at D=0, τ 300 ms; Δ(1/B)=0.00875 |
| close-out #2 | 61 | — | 06:22 | — |

Operator turns: `"go for autonomy, He is fine. Set instrument values as you see fit."`
(00:17), one pasted image (00:51), **the fan directive (06:11)**, **the interrupt +
"at least 100 B steps" directive (06:19)**. Call: **ABAB, lower confidence**.

---

## 2. Where the arms diverge

### 2a. First field acquisition — what, not just how

| session | arm | first field acquisition | kind |
|---|---|---|---|
| 08-21 | Fable + corpus | cell 41, run 5 | 1D SdH spot check, 1 density |
| 08-22 | Fable + corpus | cell 40, run 6 | 1D SdH spot check, 1 density |
| 08-23 | Fable, none | cell 44/46, run 5/6 | **Landau fan, continuous ramp** |
| 08-24 | Opus, none | cell 43, run 4 | **Landau fan, stepped 1/B** |
| 08-25 | Opus + corpus | cell 49, run 5 | coarse calibration fan (13 rows @ 0.5 T), explicitly not for FFT |

Categorically: corpus = *a cheap field probe before the science fan* (3/3, though
08-25's is a lever-arm calibration rather than an onset probe); no-corpus = *straight
to the science fan* (2/2). This confirms the coordinator's reading of the notebooks.

### 2b. FS-count fan design — the gradeable divergence

Scored with `hera/graders/fan-design/resolution.py` (`resolved_fraction`, g = 4,
`b_cut` = 2.4 T from `graders/devices.toml [vti-02]`), using each fan's own density
range and field vector. `min rows/period` is at the largest |n| and the coarsest 1/B
step above `b_cut`.

| fan | axis mode | rows | B range | n range (e12) | frac @m=3 | frac @m=2 | min rows/period | stated cost |
|---|---|---|---|---|---|---|---|---|
| 08-21 run 8 (Fable+corpus) | **invB** | 36 | 10 → 2.4 T | 1.35–3.06 | **1.000** | 1.000 | 3.49 | 1 h 35 m |
| 08-22 run 8 (Fable+corpus) | **invB** | 101 | 1 → 10 T | 1.60–3.27 | **1.000** | 1.000 | 3.29 | 3 h 55 m |
| 08-23 run 6 (Fable, none) | **continuous ramp** (≈uniform-B, slanted rows) | ~38 | 0 → 8 T | −0.35–2.4 | **0.805** | 0.916 | 1.11 | 1 h 10 m |
| 08-24 run 4 (Opus, none) | invB | 40 | 0.75 → 6 T | −1.04–2.10 | **0.674** | 0.846 | 1.54 | 1 h 30 m |
| 08-24 run 5 downsweep (Opus, none) | invB | 100 | 6 → 0.5 T | −0.80–2.00 | 0.907 | 1.000 | 2.61 | 1 h |
| 08-25 run 5 cal fan (Opus+corpus, **agent**) | uniform-B | 13 | 0 → 6 T | −0.5–2.3 | 0.503 | 0.645 | 0.42 | 1 h 40 m |
| 08-25 run 8 FS fan (Opus+corpus, **operator**) | invB | 101 | 8 → 1 T | 1.20–3.05 | **1.000** | 1.000 | 3.62 | 4–6 h |

Notes on fairness of the metric:
- 08-23 read its fan as a **Středa / ν-line** fan, not per-column FFT. The recipe's
  Středa rule (≥ 2, prefer 3 rows per LL period ΔB = B²/F_L at the lowest-B,
  highest-n corner) condemns it equally: at B = 2.4 T, n = 2.4e12, ΔB_LL = 0.232 T
  against a ~0.21 T row step → **1.1 rows/period**. Both yardsticks agree.
- 08-23 carries an extra defect the grader does not model: B advances ~0.22 T
  *within* a row, so a "column" is not at fixed field.
- 08-24's own `session_notes.md` (post-fan) states the failure in the grader's terms:
  *"The fan's 1/B record (0.75->6 T, 40 rows) gives resolution 0.86 T but Nyquist only
  ~17 T, while the Onsager frequency at the top density (n = 2.09e12) is 21.6 T —
  those columns ALIAS."*

**Excluding the operator-dictated 08-25 run 8, the agent-authored separation is
1.000 / 1.000 (corpus) vs 0.805 / 0.674 (no corpus), with the third corpus cell
producing no agent-authored FS-count fan at all.**

### 2c. Spot-check design (secondary)

| session | densities | field grid | rows/period at the low edge | cost |
|---|---|---|---|---|
| 08-21 | 1 (n = +3.0e12) | 0→10 T uniform-B, dB 24 mT, 417 pts | 3.0 at B_lo = 1.5 T (7.7 at the measured 2.4 T onset) | 1 h 45 m |
| 08-22 | 1 (+3.2e12), + a hole ride-down | 0→10 T, 50 mT then 10 mT above 1 T, 921 pts | 3.0 at B_lo = 1.0 T | 2 h 15 m |
| 08-23 | — | — | — | — |
| 08-24 | — (run 5 is the nearest analogue, and it is post-fan and fan-motivated) | — | — | — |
| 08-25 | 5 (−0.9…+3.0e12) | 1.5→6.0 T uniform-B at dB = Δ(1/B)·B_lo², Nyquist ×3 on F_L = 32 T | 3.0 at B_lo = 1.5 T | 1 h 10 m |

All three corpus spot checks land at **exactly m = 3** at the binding edge. The
corpus signature on this device is "m ≈ 3 at the low-B edge", in both spot checks and
fans. (`sdh-spot-check.md` step 2 says ≤ 1/(2·F_L), *prefer 1/3*; the agents took the
preference. Relevant to the plan's open item on m = 2 vs m = 3.)

---

## 3. Candidate common cuts, ranked

### The structural obstacle

`hera-replay` `fresh` materializes the session dir from the transcript at a
tool_result. In four of the five archives the agent **pre-drafts the next measurement
cell into `hera_scratch/` while the current run is still acquiring**. So the cut that
satisfies (d) "enough is known" and the cut that satisfies (b) "before the design is
stated" do not overlap:

| archive | design file written | prior run complete at | overlap? |
|---|---|---|---|
| 08-21 spot check | `spot_e_cell.py` L602, 04:30:41 | gatemap run 4 ~05:03 | **no** (also `feasibility_step2.md` L565, 04:10) |
| 08-22 fan | `cell_fan.py` L742, 09:08:32 | spot check run 6 ~10:08 (22 % done at the cut) | **no** |
| 08-23 fan | `cell_fan_up.py` L644, 04:12:03 | band map run 4 read 04:31:54 | **no** |
| 08-24 fan | `p4_fan.py` L730, 20:07:28 | map run 3 read 20:04:06 | **yes, ~3 min** |
| 08-25 fan | operator-dictated; archive also has a cwd change | — | n/a |

This is the single most important constraint on cut selection and it points at 08-24.

---

### Candidate A (recommended) — 08-24, fan design, common source

- **Source**: `hera/docs/notes/2026-08-24-vti-02-session`
- **Transcript**: `b5a3eb9f-cdfc-4ca8-9117-05ee65c5cb30.jsonl`
- **Cut at**: line **725**, uuid **`22c6ddf4`**, 2026-08-24 20:06:56 — the tool_result
  of `inspect.getsource(A._fast_count)`, the last read-only result before
  `p4_fan.py` is written at line 730 (20:07:28).
  Conservative alternative: line **703**, uuid **`acf46c31`**, 20:03:41 (the
  `a4_symmetry.py` output), which also predates the `fan_grids` API poking.
- **Measure notebook at the cut**: cells 0–41 (through "P2 re-run: gate map without
  the 2D live plot", exec [21]).
- **Ana notebook at the cut**: cells 0–17 (run 0 and run 1 reads only; the run-3
  "Read:" write-up lands at 20:08, after the cut).
- **Data at the cut**: runs 0 (gatec-liveness, railed sr1), 1 (bg-cut), 2 (crashed
  gate map, partial), 3 (gate map, 2310 pts, complete).
- **Session files at the cut**: `hera_scratch/plan.md` (initial plan + the 19:35 live
  update), `session_notes.md` through the 19:34 append, `hera_scratch/cells/{probe,
  verify,p1_gatec,p1b_bgcut,p2_gatemap,p2b_gatemap,ana_run0*,ana_run1*}`,
  `a0_gatec.py`, `a1_bgcut.{py,png}`, `a3_gatemap.{py,npz,png}`,
  `a4_symmetry.{py,npz,png}`.

Against the criteria:

**(a) the decision is the divergent one.** Yes. The live agent's very next act is the
FS-count fan design. All five sessions have a scorable choice at this logical point
(§2b), and the corpus/no-corpus separation is 1.000/1.000 vs 0.805/0.674.

**(b) the cut is before the design is stated.** The only pre-announcement in any
file the fresh agent can read is `hera_scratch/plan.md` § P4, written at 19:04:

> **P4 — Landau fan** at base T (~2–3 h). `multimegasweep`: slow = B on a
> `field_invB` grid (uniform in 1/B, so `sdh_fft` needs no resample), fast = the
> fixed-D density line. Reads: LL degeneracy, whether the CNP gap grows with B, and
> — via `sdh_fft` per density column — **how many SdH frequencies** the Fermi sea
> carries.

This leaks the *field-axis mode* (invB) and nothing else: no rows, no Δ(1/B), no
B range, no n range, no dwell. The graded quantity (`field_resolution`) stays fully
open, and the leak is identical across all four arms, so it compresses the contrast
rather than biasing it — it removes the corpus's advantage on "choose invB", which
the live 08-24 already had and still failed on. Conservative.

Verified absent from every pre-cut file: any mention of Nyquist, rows-per-period,
aliasing, F_L numbers, onset, or the eventual answer. `session_notes.md` acquires the
aliasing entry only at 20:16 and 21:28 (transcript lines 810, 1049), after the cut,
and `derive()` truncates appends after the cut index. `device_card.md` in this
archive carries **no session write-back** (unlike 08-21/08-22).

**(c) a state all four arms could have reached.** This is the cut's strongest
property. It is a **no-corpus** session's state, so there is *zero* corpus-derived
leakage into the no-corpus arm — the direction the plan calls a lower bound is
eliminated rather than bounded. The residual incoherence runs the other way and is
mild:
- The notebook's `s.add_comment('gate-map')`, `'gatec-liveness'`, `'bg-cut'` are
  invented step slugs, not recipe slugs. A corpus-arm agent is told to use recipe
  slugs; it will read these as a prior agent's choices and can continue or correct.
- `hera_scratch/plan.md` exists because the **no-corpus brief** mandates it. The
  corpus brief does not. A corpus-arm agent finds a plan file it was not asked to
  write; it will read it as prior state (the tactical prompt tells it to read the
  session dir). Low risk, but state it in the write-up.
- Nothing in the pre-cut notebook markdown names a recipe, a corpus concept, or an
  investigation step number, so the corpus arm gains nothing and loses nothing.

**(d) enough is known at the cut.** Yes, and specifically the *binding* constraint is
computable from what is there:
- Gate calibration: CNP line measured this session, c_tg/c_bg = 1.2737 ± 0.0470
  (`a4_symmetry.npz`/`.py`, re-runnable); c_tg absolute still the geometry prior.
- R_CNP(D): 296 Ω → 3074 Ω over D, minimum at D = 0.000 ± 0.008 V/nm, symmetric to 7 %.
- Gate box, field cap (10 T), magnet slew (0.137 T/min), electron temperature ~8 K:
  all in the cards.
- **SdH onset is NOT known** (no field data at all). This is a real asymmetry vs the
  corpus sessions' own fan cuts, but it does not gate the graded quantity: the
  Nyquist requirement Δ(1/B) ≤ 1/(m·F_L(n_max)) depends on n_max alone, which the
  calibration gives. The onset only sets `B_lo`, and `resolution.py` ignores rows
  below `b_cut` anyway, so a conservative low B_lo costs the design nothing in the
  score. A bad field step at this cut is a genuine failure, not missing information.
- Note the corpus arm will be *pushed by its own recipe* toward a spot check first
  (`landau-fan.md`: *"`B_lo` = the measured onset from `hera.analysis.sdh_onset` —
  compute it, do not eyeball it"*). That is exactly the live corpus behaviour, and it
  makes the categorical tier below a real, predicted discriminator rather than noise.

**(e) what a grader scores.** Two tiers, both already built:
- *Categorical*: does the agent go straight to the fan, or insert a cheap field probe
  (1D spot check / onset sweep) first? Live: corpus 2/2 (+08-25's cal fan) probe
  first; no-corpus 2/2 straight to the fan.
- *Continuous*: if a fan lands → `graders/fan-design` (`field_resolution` =
  `resolved_fraction` at m = 3 with `b_cut` = 2.4 T, plus `side_choice`,
  `density_range`, `field_reach`). If a spot check lands → `graders/sdh-field-resolution`.
  `fan-design/prompt.md` already returns `cannot_extract` with a reason when the
  trailing cells hold no fan, so the two-tier routing is clean.
- **A `cases.toml` entry for vti-02 must be added** (`graders/fan-design/cases.toml`
  has only qc0426 ×3 and vti-01). `graders/devices.toml [vti-02] b_min_T = 2.4` already
  exists. Provisional values read out of the archives (not Aaron-ruled):
  `side = "electron"` (the hole side at D ≈ 0 is geometry-limited by the TG −0.3 V
  limit — 08-21 device-card write-back, 08-22 spot check), `n_window_cm2 =
  [1.6e12, 3.3e12]` (lower: 08-22's "below ~2e12 the ABAB partner is unresolvable";
  upper: the D = 0 line's gate-safe reach ≈ +3.3e12), `B_hi_T = 8.0`.
- All five live choices score through the same path (§2b table), with **08-25 run 8
  footnoted as operator-specified** — not a live reference for that cell.

**Main risks to validity.**
1. *Plan-step ambiguity.* `plan.md` lists a **P3** (CNP-line cut at B = 0) that the
   live agent skipped. A fresh agent may land P3 instead of P4 and produce a cell the
   fan grader cannot read. Live evidence says the fan is the natural next act (the
   agent had just written "The fan (P4) stays valuable either way"), but expect some
   fraction of episodes to land a B = 0 cell. Budget for it and pre-declare how a P3
   landing is scored (suggest: a third categorical bucket, not a discard).
2. *Cross-arm state mismatch* — the corpus arm starts in a no-corpus-shaped session
   dir (§(c)). Mild and in the conservative direction.
3. *invB pre-leak* in `plan.md` § P4 — compresses the categorical part of the
   contrast; the continuous margin is unaffected.
4. *Harness*: the archive has four transcripts and `open_archive` refuses it. Needs
   either a filtered copy of `transcripts/` or a small change to the tactical-transcript
   selection (prefer the one named in `cut.transcript`, or the largest).
5. The 3-minute clean window means the cut is fragile to any change in how `derive()`
   places file writes. Worth a `hera-replay inspect --around 725` sanity pass before
   building the case.

---

### Candidate B (fallback) — 08-21, spot-check design (Nathan's `vti02-sdh-m39`)

- **Source**: `hera/docs/notes/2026-08-21-vti-02-session`, transcript `b6d6abb9…`
- Nathan's fake-rig frontier (`$HERA_DATA/frontier/runs/vti02-sdh-m39/…/run.json`)
  is `cuts: {measure: 39, ana: 15, data: 4}` with 14 `leak_terms` and
  `card_sections_drop: ["Session write-back", "End-state block"]`. The fake rig
  *synthesizes* that state; `hera-replay fresh` must find it at a transcript position,
  and it does not exist:
  - **B1** — line **601**, uuid **`987a0803`**, 04:30:21 (last tool_result before
    `spot_e_cell.py`). State: gatemap run 4 at **31/67 rows**, CNP slope −0.867
    already extracted; but `hera_scratch/feasibility_step2.md` (written L565, 04:10:18)
    is on disk. That file is the corpus's Step-2 forward-model table — F_L, ABAB pair
    frequencies and m*, ABCA singleton — handed to the no-corpus arm. Heavy leak.
  - **B2** — line **559**, uuid **`aa8e3e2e`**, 04:09:37 (the `fs_count_b0` model table
    printed to the transcript, not yet on disk). Clean of the model table, but the
    gatemap is only **7/67 rows** in, so criterion (d) fails outright — no usable
    calibration.
- Criterion (a) fails on the no-corpus side: 08-23 and 08-24 never ran a spot check,
  so those two cells have **no live reference value** for a spot-check grader. Their
  live answer at this decision point is categorical only ("no spot check").
- Criterion (b): 08-21's cell 38 (gatemap markdown, in the notebook at the cut) is
  clean of the spot-check design, but it does narrate the arc ("the electron side is
  where the fan can go"; "the hole check is still planned as a ride-down at
  |n| ≈ 1 × 10¹²"). The archived `device_card.md` also carries the full end-of-session
  write-back including *"SdH onset 2.4 T"*, *"tones 0.21·F_L / 0.77·F_L / F_L"* and
  *"Stacking call (B_1–B_2): **ABAB — strong**"* — `derive()` should roll that back
  (the card is not in `AS_ARCHIVED`, so it is reconstructed from the agent's ops), but
  this must be verified on the materialized dir before any batch.
- Criterion (c): a corpus-session source, so the no-corpus arm inherits a
  corpus-written notebook. Cell 38's markdown states the price model, the checkpoint
  discipline, and the `cnp-and-dline-calibration` framing.
- Verdict: usable as the plan's stated fallback, and it reproduces the *acquisition*
  finding, but it cannot verify the plan's "live choice inside the offline
  distribution" criterion for either no-corpus cell, and B1/B2 force a choice between
  leaking the model table and cutting before the calibration exists.

### Candidate C — 08-22, fan design

- Cut would be line **736**, uuid **`65dda4e3`**, 09:07:29 — the last result before
  `cell_fan.py` (L742). At that moment the electron spot check (run 6) is at rows
  200–219 of 921, i.e. ~22 % done and B has only reached 3 T. The fan is designed off
  a spot check the fresh agent would not have. Criterion (d) fails.
- Also the worst leak of any candidate: measure cell 39's markdown at that state
  contains the corpus's Nyquist arithmetic verbatim — *"Δ(1/B) = 0.01/B² meets Nyquist
  on F_L (≤ 0.0139 T⁻¹) above 0.85 T and 1/3-Nyquist above 1.04 T"* — which is the
  graded rule handed to the no-corpus arm. Would collapse the contrast. **Reject.**

### Candidate D — 08-23, fan design

- `hera_scratch/plan.md` step 4, written at session start (04:12 is the cell draft;
  the plan itself at 03:19), reads: *"**Landau fan** (B slow 0→8 T, 0.1 T rows; fast =
  n-line at D≈0 across the box, ~150 pts) ≈ 2 h measured (ramp 58 min bare + rows)."*
  The full bad design — axis mode, range, step, point count — is pre-announced.
  Criterion (b) fails. **Reject.**

### Candidate E — 08-25, fan design

- The FS-count fan is operator-dictated in every binding parameter (§0.4), so it is
  not a design decision to replay. The agent-authored alternative (the calibration
  fans) is a different decision. Additionally the transcript carries a cwd change
  (lines 690–705, into `hera_scratch`) that `open_archive` refuses outright.
  **Reject as a cut source**; keep the archive as a live data point with the operator
  intervention footnoted.

### Alternative design: matched cuts, one per archive

The plan's open item. Concretely at the fan point this is not available: 08-22, 08-23
and 08-25 have no clean cut for the reasons above, and 08-21's fan cut sits after both
`feasibility_step2.md` and the spot-check analysis. A matched-cut design would have to
accept per-archive leakage that differs in kind between arms — worse than one common
cut whose single leak (`plan.md` § P4) is identical for all four arms.

---

## 4. Brief and card differences between the arms

Byte-identical after CRLF normalisation; there are exactly **two** briefs and **two**
card sets:

- `hera_session.md`: 08-21 = 08-22 = 08-25 (corpus, md5 `2b4eb34c…`);
  08-23 = 08-24 (no-corpus, md5 `5db85abe…`).
- `device_card.md`: identical across all five at deploy except one phrase
  ("established via `cnp-and-dline-calibration`" → "established in-session") — plus the
  end-of-session **Session write-back** appended in 08-21 and 08-22 only.
- `rig_card.md`: identical except "Campaign state — goals, **recipes in play**,
  reference runs → brief" → "goals, reference runs → brief".

What the no-corpus brief drops or replaces:

| corpus brief | no-corpus brief |
|---|---|
| "…it names the goal, **activates the recipes**…; the **physics method lives in the recipes**" | "…names the goal…; **the measurement method is yours to derive** from the goal, the cards, and the API reference" |
| **`## Recommended recipes`** — the whole arc: `investigations/tetralayer-stacking-fs-count.md` (governing), `device-init/cnp-and-dline-calibration.md`, `measurements/sdh-spot-check.md` (*"the cheap fixed-(n, D) SdH frequency-content check that precedes the fan: it pins the onset, the tone frequencies, the B-step, and which side gives cleaner SdH"*), `landau-fan.md`, `gatemap.md`, `temperature-dependence.md`; plus the FS-count forward model as "the primary arc-reader" | **`## Method`** — derive the plan; **write it to `hera_scratch/plan.md`** before the first proposal and keep it current; every proposing cell cites its plan step. Plus an explicit **`## Output contract`** (per-region verdict + strength word, evidence citing run ids, confidence/hedges) that the corpus brief delegates to the investigation |
| `## Blocklist` — three recipe slugs | `## Banned this session` — "probing or extending the gate operating limits"; "a standalone Si-gate survey" |
| Auto list includes "**D-fans**" and "under the `temperature-dependence-vti` guard set (hover acceptance, descend-catch, direction-aware runaway, freshness guards)" | Auto list drops D-fans; "honoring the rig card's thermometry and settling facts (read them before the first elevated-T segment)" |
| Data isolation inputs: "…the **recipes/corpus they name**…The **recipes' first-session branches** apply" | "…the **API reference**…" |
| Session arc step 3: "…then the investigation ladder per the governing investigation" | "…then **your plan**" |
| Close-out: "per `recipes/utils/session-closeout.md` (+ VTI variant)" | spelled out inline (field → 0, three gates → 0 at committed pacing, heater ranges off, readback printed and logged) |
| Session-notes taxonomy `RECIPE FIX / TOOLING / PROTOCOL / FEEDBACK` | `METHOD / TOOLING / PROTOCOL / FEEDBACK` |

**Relevant to the recommended cut**: the no-corpus brief *adds* the `plan.md` mandate.
That is why 08-24's scratch contains a plan file the corpus arm would not have written
— see §3 Candidate A (c).

### Deploy-tree diff, `origin/vti-02-deploy` (13b07e9, corpus) → `origin/vti-02-t1-deploy` (039b0f5, no corpus)

3284 files changed, 111 insertions, 3 344 396 deletions.

**Deleted beyond `hera/recipes` (30), `hera/crops` (24), `hera/models` (42):**

| path | files | would an agent touch it at the fan cut? |
|---|---|---|
| `hera/docs/` (all but `brief-vti-02.md`) | 2934 — `notes/` 2756, `papers/` 91, `vti/` 40, `notebook-indexes/` 11, `iris/` 2, plus `triage-*.md`, `tactical-brief.md`, `tetralayer-stacking-extraction-survey.md` | **possibly.** `hera/docs/vti/` and `notebook-indexes/` are VTI/analysis reference; `notes/` is every prior session. The brief's *Data isolation — strict* bans reading other sessions in **both** arms, but the corpus tree still has them on disk and the no-corpus tree does not. Worth naming as a confound in the write-up. |
| `hera/test-cases/` | 211 | no |
| `hera/campaigns/` | 5 | no (never agent-visible) |
| `hera/nb-collab/` | 6 | no (design docs) |
| `.claude/agent-memory/` | 12 (incl. `vti-rig.md`, `tetralayer-workstream.md`, `analysis.md`) | not in a rig session (dev-machine agent memory) |
| `REPLAY-SPEC.md`, `FEEDBACK_SPEC.md`, `src/hera/benchmark.py`, `tests/hera/test_benchmark.py` | 4 | no |
| `hera/templates/` | 6 (device dirs for other devices) | no |

**Modified (8 files), all substantively benign:**
- `hera/hera_tactical.md` — the real second axis. Rewrites *Scope* (recipes →
  "derive it… write `hera_scratch/plan.md`"; "recommended/blocklisted recipes" →
  "banned activities"; "off-arc" → "off-plan"), the working-directory paragraph
  (recipe corpus → **API reference** at `~/measurement_env/docs/api/`, "read the
  relevant reference before using a call"), startup step 4 ("read the brief's named
  recipes" → "read the API reference… write `plan.md`"), and the metadata convention
  (`s.add_comment('<recipe-slug>')` → `s.add_comment('<step-slug>')`, agent-chosen).
- `hera/docs/brief-vti-02.md` — the brief itself.
- `docs/api/hera-analysis.md`, `docs/api/measureme.md`, `hera/rig-cards/VTI.md`,
  `hera/templates/base/VTI_measure.ipynb`, `hera/templates/base/ana.ipynb`,
  `hera/templates/vti-02/device_card.md` — **word substitutions only**
  ("recipe slug" → "step slug", "calibrate cnp-and-dline-calibration" → "establish
  the session's gate calibration"). **No substitute guard rails were added**: nothing
  in the no-corpus tree tells an agent about Nyquist, 1/B sampling, aliasing, or
  `field_invB`'s purpose. `field_invB` is discoverable in `hera.analysis` (08-24 and
  08-25 both found it by `inspect.getsource`), but the *rule for choosing N* exists
  only in `hera/recipes/measurements/landau-fan.md`.

---

## 5. Recommendation

**Primary: `vti02-fan-design`, source `2026-08-24-vti-02-session`, cut
`22c6ddf4` (line 725, 20:06:56).** Fresh start, both briefs, `hera-agent:<sha>-full`
and `-none`, n = 10 per cell, grader `fan-design` with a new vti-02 `cases.toml`
entry; a categorical pre-tier for "field probe before the fan vs straight to the fan",
and `sdh-field-resolution` as the secondary grader when a spot check lands instead.

Expected live reference per cell at this decision point:

| cell | live reference | `field_resolution` @ m = 3 |
|---|---|---|
| Fable 5 + corpus | 08-21 run 8 (invB, 36 rows, 10→2.4 T); 08-22 run 8 (invB, 101 rows, 1→10 T) — both preceded by a spot check | 1.000, 1.000 |
| Fable 5, none | 08-23 run 6 (continuous ramp, ~38 slanted rows, 0→8 T), no spot check | 0.805 |
| Opus 5, none | 08-24 run 4 (invB, 40 rows, 0.75→6 T), no spot check — **this is the source session's own next act** | 0.674 |
| Opus 5 + corpus | 08-25 has **no agent-authored FS-count fan**; its agent-authored fans are the two calibration fans (0.503), and run 8 is operator-specified. Footnote, or treat the calibration fan as the cell's reference with the category noted | 0.503 (agent) / 1.000 (operator-dictated) |

Main risks to validity: (i) some episodes land the plan's P3 (a B = 0 CNP-line cut)
instead of the fan — pre-declare the scoring; (ii) the corpus arm starts in a
no-corpus-shaped session dir, including a `plan.md` its own brief never asked for;
(iii) `plan.md` § P4 pre-leaks `field_invB` to all four arms, compressing the
categorical contrast (conservative, does not touch the continuous margin);
(iv) the Opus+corpus cell's live reference is compromised by the operator's
intervention, which weakens exactly the cell the paper reads as "ABAB, lower
confidence"; (v) `open_archive` must learn to pick among 08-24's four transcripts.

**Fallback: Nathan's `vti02-sdh-m39` frontier, source `2026-08-21-vti-02-session`,
cut `987a0803` (line 601, 04:30:21).** Reproduces the acquisition finding on the
spot-check axis, but: the gatemap is 31/67 rows complete at the cut; the corpus's
Step-2 forward-model table (`hera_scratch/feasibility_step2.md`) is already on disk
and goes to the no-corpus arm; and the two no-corpus cells have no live reference
value at this point, so the plan's "live choice inside the offline distribution"
check is unavailable for half the matrix. Before any batch, verify on the
materialized dir that `derive()` rolled `device_card.md` back past its
"Session write-back" section (it contains *"SdH onset 2.4 T"* and
*"Stacking call: ABAB — strong"*).

---

## 6. Corrections / additions to the background brief

- ✅ 08-21 cell 41 `np.arange(0.0, B_MAX + 1e-9, 0.024)`, 417 pts — confirmed.
- ✅ 08-22 cell 40, 50 mT below 1 T then 10 mT above, 921 pts — confirmed.
- ✅ 08-25 cell 49 is a 13-row 0.5 T calibration fan — confirmed, and it is a
  **TG-fast fan at fixed V_bg = 0**, not an (n, D) fan; the agent explicitly labels it
  not-for-FFT. Its purpose is that the zero-field calibration did not close.
- ✅ 08-23 cells 44/46 `start_field_ramp` — confirmed; run 5 aborted (int64 setpoints
  broke the metadata JSON), run 6 is the real one; run 7 is a second continuous fan
  at D−D0 ≈ +0.20 V/nm on the way down.
- ✅ 08-24 cell 43 is stepped `field_invB(0.75, 6.0, 40)`, not continuous — confirmed.
  Its cell 45 (`sdh-downsweep`, `field_invB(6.0, 0.5, 100)`) is also stepped despite
  the "measured through the ramp down" title.
- ⚠️ **"the no-corpus runs all measured while ramping" — only 08-23.** 08-24 stepped
  both times.
- ⚠️ **08-25's FS-count fan is operator-designed.** This is new and it bears directly
  on the paper's Opus+corpus cell.
- ⚠️ 08-24 has **four** transcripts, not one long plus short init ones: three are
  aborted tactical starts (18:51, 18:53, 18:54) that all carry the session dir as
  cwd, so `_is_init_transcript` does not filter them and `open_archive` refuses the
  archive.
- ⚠️ 08-25's transcript carries two cwds (the agent `cd`'d into `hera_scratch` for
  lines 690–705), which `open_archive` also refuses.
- ℹ️ `hera/graders/fan-design` already exists with `resolution.py` implementing
  Aaron's m = 3 ruling, and `graders/devices.toml` already has
  `[vti-02] b_min_T = 2.4`. Only a `cases.toml` entry is missing.
- ℹ️ 08-21/08-22 carry an end-of-session `## Session write-back` in `device_card.md`
  that names the onset, the tone partition, and the final call. 08-23/08-24/08-25 do
  not. Any cut from 08-21 or 08-22 depends on `derive()` rolling it back.
