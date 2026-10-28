# Session notes — zf1 / toploader

Operational log (not a science notebook).

**SESSION CLOSE (2026-06-21).** Device safely parked: k_tg=0, k_bg=0, dc205=0,
magnet=0 T (controller; ~2 mT remanence remains), AC drive at min, base T 33.7 mK
(measure cell 67 readback). Kernel + workers left up. **Open SC thread for next
session:** reproducible low-Rxx feature at **n≈−0.48 e12, D≈−0.67 V/nm (V_tg
−5.61, V_bg 4.17 — the max accessible -D, Ising-SOC territory)**; operator
confirms (strong) it IS superconducting. My AC-Rxx-map "not-SC" call was WRONG and
retracted (a 0.5 nA AC map reads the normal state of a sub-Ic SC — see RUN 8
retraction note). **Resume with bias spectroscopy (cell 65): dV/dI vs I_dc below
Ic, low AC, ideally at the effective-zero field (cancel the ~2 mT trapped flux)
to measure Ic**, then the Ic(n)/Ic(B)/Ic(T) ladder. dV/dI on BOTH sr2 and sr3.

## 2026-06-20

**FEEDBACK — drive level as-found 40 pA, card says 1 nA.** Run 0 (Gate C)
metadata: `bias_voltage_1 = 0.004 V` (sr830_1 sine 4 mV) → I_bias = 40 pA, not
the device card's "0.1 V → 1 nA". The 4-terminal Rxx (sr3, 30-31) noise floor
at 40 pA is ~26–68 Ω, which buries the low-Rxx metal (~13 Ω) — the exact regime
SC candidates occupy. Bumping AC drive to ~0.5 nA (0.05 V) for the candidate-ID
map. Device card drive line is stale or the lock-in was left at 4 mV; confirm
with operator which is intended. (cite: run 0, ana cells 5–8.)

**RECIPE FIX — sc-characterization / gatemap drive discipline.** The recipes
specify AC excitation magnitude for SC-friendliness (0.5 nA, Step 2) but not a
pre-map SNR check: before committing a multi-hour candidate map, verify the 4T
Rxx noise floor at the chosen drive is well below the target low-Rxx scale.
Here 40 pA would have produced a map where candidates are indistinguishable from
noise. Worth a one-line "price the noise floor vs target Rxx" in Step 1/2.

**TOOLING — `Run` has no `.metadata`; it's `Run.meta` (dict).** And swept-axis
columns appear twice (planned + readback); use `col_at(col_indices(name)[-1])`
for the readback. Cost a failed analysis pass. (cite: gateC_ana.py.)

**FEEDBACK — sr4 (5-30) unusable.** Shares the current-drive contact 5; reads
±24 kΩ scatter (3-terminal, contact-R + phase). sr3 (30-31) is the clean 4T Rxx;
sr2 (5-4) is the 2T. (cite: run 0.)

**CALIBRATION — CNP slope CONFIRMS the geometry prior.** Proper polyfit on run 2
(44 complete rows): Vtg_cnp = −1.193·Vbg + 0.080, resid 0.040 V → cap ratio
c_bg/c_tg = 1.193, matching the device-card geometry prior t_tg/t_bg = 23.6/20 =
1.180 to ~1%. (My earlier 18-row eyeball "~−1.6 vs −0.85" was wrong on BOTH the
read and the prior arithmetic — prior slope is −c_bg/c_tg = −1.18, not −0.85.)
The (n, D) RATIO is data-validated; absolute scale still geometry-prior until a
QH lever-arm check. CNP at Vbg=0 is Vtg ≈ +0.08 (n_offset ≈ 0). (cite: run 2,
partial_map.py.)

**OBSERVATION — no SC candidate in BG −4→+2 (74% of map).** 4T Rxx metallic
~15–25 Ω with the CNP ridge; nothing collapses toward 0 (lowest 3×3-smoothed
8.4 Ω, at the +6 V edge). Full-(n,D) verdict pending the BG +2→+4.2 remainder
(run 3). (cite: partial_map.png.)

**RECIPE FIX — gatemap: transient SR830 SNAP crash mid-megasweep.** Run 2 died
at row 44/61 with `ValueError: could not convert string to float: '154.764-\n'`
in `AsyncStation._try_batch_read -> SR830.snap` — a malformed GPIB SNAP reply
(one-off; run 3 over the same channels was clean). The recipe should warn that a
long megasweep can be killed by a single flaky lock-in read, and recommend a
`try/finally` gate-park (which here parked gates safely) + stitch-the-remainder
recovery rather than a full re-run. A retry-on-malformed wrapper in the sweep
SNAP path would prevent it (eng-backlog). (cite: run 2, cell 31.)

**RUN 8 — not-SC verdict RETRACTED (operator, strong; 2026-06-21).** My "dip is
not SC because the trusted 4T Rxx (sr2) is high there" was WRONG. Error: a 0.5 nA
AC Rxx map cannot see a supercurrent with Ic ≲ 0.5 nA — the probe exceeds Ic so
the lock-in reads the NORMAL-state R (finite kΩ), not zero. Finite Rxx in an
above-Ic AC map does NOT exclude a fragile SC. I had flagged this exact smearing
earlier (drive-discipline note) and then contradicted it. The reproducible low-R
feature at large D / low hole dope IS the SC (operator knowledge). The (n,D) data
stands; the interpretation was wrong. CORRECT TEST: bias spectroscopy dV/dI vs
I_dc below Ic (measure cell 65), low AC. LESSON: never use an AC Rxx map at a
drive above the (suspected) Ic to rule OUT superconductivity — it shows the
normal state; go below Ic with bias spectroscopy. (cite: ana cell 27 banner.)

**ZOOM RESULT (run 4, operator-requested) — under-resolution hypothesis exhausted.**
High-res (0.07 V, 2×) map of the V_bg>0/V_tg<0 quadrant (large −D, SC-expected):
4T Rxx (sr2) 3.4–44 kΩ, ZERO pts <3 kΩ anywhere; D 0→−0.76 V/nm covered. No
narrow SC dome hides below the coarse grid. Combined with full map: no SC at the
controller's zero, either resolution, correct channel. Live remaining hypothesis:
field suppression by ~2 mT trapped flux → effective-zero-field search is decisive.
(cite: ana cells 19–21, zoom_map.png.)

**CONFIG VERIFIED (operator request, 2026-06-20) — rotator-servo lock-ins off.**
sr830_6 (θ) and sr830_7 (φ) excitations both at the SR830 minimum 4.0 mV (refs
13.777 / 17.111 Hz, internal) — effectively off, and off-frequency from the
7.777 Hz measurement so doubly rejected. Correct state (rotator blocklisted);
noise floor clean for the fragile-SC field search. (cite: measure cell 50.)

**DEVICE CARD FIX (operator, 2026-06-20) — 4T Rxx is sr830_2, not sr830_3.**
Aaron: the 4-terminal Rxx channel is `sr830_2`. The config label `sr2="5-4"`
is wrong (5-4 is the drive pair = 2T); sr2 is actually a 4T longitudinal pair
(real contacts [VERIFY]). Confirmed by the data — sr2 ~3.4 kΩ metal / ~30 kΩ at
CNP (textbook 4T graphene Rxx); sr3 (30-31) ~15–25 Ω is NOT Rxx. **All my prior
analysis used sr3 as 4T — being redone on sr2** (runs 0–3; candidate scan, CNP,
operating point). Impact: drive-bump rationale (sr3 noise floor) was moot — sr2
SNR was always fine; 0.5 nA drive harmless but re-justify. Device card updated
in-session (Measurement setup / wiring); contact pair for sr2 still needs the
operator. (cite: device_card.md correction block, run 0.)

**PROTOCOL / HARD BAN (operator, 2026-06-20) — never change `volt.step` this
session.** Aaron imposed a hard ban on modifying any `volt.step` (gate Keithleys
AND dc205) for the rest of the session. My bias-spec cell 40 had set
`dc205_1.volt.step = 0.02` (to speed the DC bias sweep past the DC205's ~1 s
fixed-ramp-per-set quirk at the default 5 mV step) — superseded by a corrected
cell that leaves volt.step at its setup default; cell 40 never executed.
**ACTION for the toploader rig card:** the canonical `hera/rig-cards/toploader.md`
should carry this as a standing rule — `volt.step` is operator-owned, not to be
changed by the agent (rig-agnostic ramp-rate safety surface). Recorded here per
the read-only-on-repo rule; Chiron/triage to propagate to the card. Consequence
for pricing: DC205 bias sweeps run slower at the default 5 mV step (≈ total
traversed/0.005 × ~1 s of DC205 ramp) — price that in, don't engineer around it
by touching volt.step.

**RECIPE FIX — bias-spectroscopy: dV/dI channel wrong for current-bias rigs.**
The recipe's `r = sr830_1_X / sr830_4_X` (sample / current-monitor) assumes a
voltage-bias rig with a dedicated current-monitor lock-in. On the current-bias
toploader (AC drive through 100 MΩ → constant I_ac) with zf1 wiring, sr830_1 IS
the current channel and sr830_4 is dead; dV/dI = (sr3_4T_V)/I_ac ∝ sr830_3
directly. Recipe should state the current-bias variant: dV/dI = 4T-voltage-chan
/ I_ac. (cite: bias-spectroscopy.md Verify, run 4.)

**CALIBRATION — full map confirms cap ratio.** Run 2+3 stitched (61 rows):
Vtg_cnp = −1.192·Vbg + 0.082, ratio 1.19 = prior 1.18. (n,D) ratio data-valid;
abs scale = geometry prior (QH lever-arm out of reach ≤100 mT). Covered n −8→+8
e12 cm⁻², D −0.76→+0.68 V/nm — full accessible window. No SC candidate; lowest
smoothed Rxx 4.4 Ω (electron side). Device-card (n,D) write-back pending operator
OK. (cite: ana cells 13–15, full_map.png.)

**TIMING — megasweep faster than the 1D per-point rate.** Run 2: ~39.8 fast-pts/
min ≈ 0.75 s/pt vs the ~1.9 s/pt I priced from the 1D legs (nplci=10). 6161-pt
map ETA ~2.6 h, not 3.5 h. Price 2D fast-axis points well below the 1D rate
next time. (cite: run 2 digest.)

