# Session notes — zf1 / toploader

Operational log (not a science notebook).

## 2026-06-21

**FEEDBACK — premature not-SC call; operator caught it (correct).** I issued a
"not-SC (strong)" call after clean ±D linecuts that only reached D=−0.60 V/nm,
treating the |D|=0.76 cap as if explored. Operator: "you cannot claim no SC when
you've only explored to −0.6, nowhere near the −0.76 cap." Right — the wedge
0.60→0.76 V/nm was only in the coarse, sr3-clipped survey. Root cause: I conflated
"the cap" with "what I measured," and a constant-D line caps at ~0.60 at the
candidate density so I never pushed the gate corner. **Lesson: when coverage is
gate-limited, explore the validator-edge envelope (here BG=+4.2, sweep TG) to ride
the |D| ceiling — don't extrapolate from the highest constant-D line.** Call
RETRACTED in ana; running an extremal-D corner map (run 9) to the cap before
re-issuing.

**SESSION OUTCOME (FINAL) — zf1 IS a superconductor.** Full constellation at
n≈−5.0×10¹¹, D≈−0.67 V/nm (TG=−5.64, BG=4.20): Rxx→0.57 Ω, I_c≈8–11 nA, B_c⊥≈2.5 mT
(ξ~360 nm, normal-controlled, no heating), central supercurrent lobe (phase-coherence
consistent-with), Tc~0.1–0.2 K (coarse — live thermometry stalled). Found ONLY because
the operator forced coverage past D=−0.60 to the −0.76 gate cap; the earlier "not-SC"
call (retracted) had stopped short. Full 5-part call in the ana notebook. Open
(next-round): quantitative Tc (fix thermometry), full I_c(n,D) dome (needs off-the-cap
|D| access), Tesla-scale fermiology, 2nd-contact reproduction.

**SESSION STATUS [superseded] — CANDIDATE FOUND at extremal D (operator's push was decisive).**
Extremal-D corner map (run 9, to the −0.76 cap) + fine zoom (run 10) reveal a
**contiguous low-Rxx arc: Rxx→0.57 Ω at n=−5.02×10¹¹, D=−0.673 V/nm** — the
s41586 proximity-SC location, at |D| beyond the −0.60 the earlier (retracted)
call had reached. Hallmark 1 (Rxx→0) confirmed. Now running bias spectroscopy
(run 11) for a critical current (hallmark 2). The metallic/no-SC picture held
only because I'd stopped at D=−0.60; lesson logged above. Arc rides the BG=+4.2
cap (extent gate-cut). Fermiology still deferred (Tesla, next round).

**FEEDBACK / setup — AC excitation 25× below device-card nominal.** Run 0
(file_id 0, Gate C liveness) ran at `sr830_1.amplitude = 0.004 V` → I_bias =
40 pA, vs the device card's stated 0.1 V → 1 nA. Current path (5-4) pinned at
I_bias (alive); 2T (5-4) clean CNP 42.7 kΩ at BG=-0.017 V; 4T (30-31) shows a
real CNP bump at the SAME BG but only 2–8 nV signal (SNR ~2–3) because of the
low drive. Proposing to raise to the device-card 0.1 V (1 nA) for the survey
map; flag to operator in case 40 pA was deliberate. Later SC bias-spectroscopy
will want low excitation again (≤0.5 nA) — that's a separate, intentional drop.

**RIG ISSUE — temperature workers stale; logfile T frozen during heating.**
Tc ladder (run 16, heater 6.5 V): `heater.curr`=0.70 mA (working, ~4.6 mW) and
dV/dI went flat-normal (SC killed → sample hot), but `temperature` (probe MC)
stuck at 0.0337 K and `T_fridge`=0 — both logfile reads frozen/zero. Rig-card
known failure mode (dead worker → frozen logfiles → silent stale reads). Live
sample-T unreliable during the heat-up; prior base-T runs unaffected (sample
genuinely ~33 mK, frozen value matched). Flagged to operator. Working around it
by using the device-card heater-V→T table as the T proxy (coarse Tc). The brief's
[VERIFY] "workers green / temperature logfiles fresh" should be re-checked — they
were NOT fresh here, only coincidentally correct at base. Setup's `temperature()`
read at session start (0.0337 K) may also have been stale-but-correct.

**RECIPE FIX — `bias-spectroscopy.md` Verify imports a missing module.** The
recipe's Ic extraction does `from sharpelab_nb.sc import extract_critical_current`
/ `map_ic_dome`, but `sharpelab_nb.sc` is not importable in this env
(ModuleNotFoundError). Also its `r = sr830_1_X / sr830_4_X` assumes sr4 is the
current monitor; on zf1 the current channel is **sr830_1** and the 4T voltage is
**sr830_3**, so dV/dI = (sr830_3_X/sr3_gain)/(sr830_1_X/sr1_gain). Extracted Ic
by hand (threshold crossing on the smoothed dV/dI). Recipe should either ship the
helper or document the manual fallback + the channel-mapping caveat.

**RECIPE FIX / TOOLING — lock-in sensitivity must account for the voltage
preamp gain.** I set sr3 (4T) sensitivity = 5 µV reasoning from V_4T (~tens of
nV). But the voltage channels have a ×100 preamp ahead of the lock-in, so the
lock-in sees V_4T×100. Sensitivity 5 µV therefore caps the lock-in at
V_4T = 50 nV → **Rxx clips at ~50 Ω** (apparent clamp at 54.6 Ω = over-range
5.46 µV /100 /1 nA; ÷ reduced current near gaps gives the 87 Ω seen on the map).
The survey map (run 2, sr3=5e-6) and linecuts (runs 3-4, sr3=5e-6) clipped all
Rxx>~50 Ω. Low-Rxx (SC) regions are unaffected (they read below the clip), so
the no-low-Rxx-candidate conclusion stands — but resistive structure was lost.
**Rule: sensitivity_target = R_max × I_bias × preamp_gain.** For Rxx up to 1 kΩ
at 1 nA, ×100 → 100 µV (1e-4); use 2e-4 for headroom. Re-running linecuts clean.

**FINDING — 2T channel (sr2, 5-4) saturates at 1 nA drive.** Run 1 (file_id 1,
1 nA): sr830_2 X railed flat at 109 µV (std=0, over-range on the 100 µV scale)
across the whole gate sweep — including metallic regions where R predicts a few
µV — while at 40 pA (run 0) it gave a clean 3→42.7 kΩ CNP. Cause is almost
certainly drive feedthrough onto injection node 5 (2T 5-4 shares the current
contacts): at 0.1 V drive the feedthrough swamps the 100 µV range. 4T (sr3,
30-31, isolated from injection nodes) is clean at 1 nA (SNR~108). Conclusion:
**use 4T as the primary/only Rxx channel at 1 nA**; 2T is a coarse cross-check
only (coarse range). lock-in tc = 300 ms (delay 5×tc = 1.5 s in the 1D cuts).

**TOOLING — `hera-watch --next` re-arm races a run that already started.** I
proposed the survey map, armed `--next --follow`, then did ana work; the operator
ran the map meanwhile. I then stopped the `--follow` watch and re-armed `--next`,
which snapshotted runs {0,1,2} (run 2 = the already-started map) and waited for a
*run 3* that never came → 1800 s timeout, and my ~17 min checkpoint was missed.
Lesson: once a data-writing cell is proposed, DON'T stop the `--follow` watch; if
a mid-run checkpoint is wanted, watch the specific run dir (`hera-watch data/<id>
--once` / `--follow`) rather than re-arming `--next`. Checkpoint was recovered
late via `--once` on data/2; map clean (leakage ≤89 pA, on track).

**TOOLING — `fp` of the swept param duplicates its column.** In run 0 I called
`s.fp(k_bg.volt)` in addition to sweeping it, so `open_run` saw `k_bg_volt`
twice and `run.col("k_bg_volt")` raised (needs `col_at(1)`). Don't fp the
swept axis — it's auto-recorded. Minor; fix in future cells.

**Note — device card sr3="30-31" vs active-pairs list (7-31, not 30-31).**
The provided config names 30-31 for the 4T channel, but the device card's
active-contact-pairs list has 7-31, not 30-31 (contact 30 absent). 30-31 does
measure the device (CNP coincides with 2T), so it's wired and alive; flagging
the list/config mismatch. If 30-31 stays marginal at 1 nA, try 7-31.
