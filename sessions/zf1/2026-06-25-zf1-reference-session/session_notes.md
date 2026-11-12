# Session notes — zf1 / toploader

Operational log (not a science notebook).

## 2026-06-25 — bring-up

TOOLING — measure cell 19 (geometry/cal slot) builds `cal =
GateCalibration.from_thicknesses(t_tg, t_bg, t_bgSiO2)` WITHOUT the
`n_offset=-0.362e11*1e4` the brief/handoff §1 mandate. The deployed kernel `cal`
therefore lacks the CNP offset; n-axis would be shifted ~0.36e11 if used naively.
Worked around by constructing `cal_r4` with the explicit n_offset inside each
proposing cell (as the prior session did, prior cell 30). Template slot should
carry the in-session n_offset once calibrated.

PROTOCOL — no deployed recipe file for a plain constant-D / gate-axis 1D linecut,
though `nD-map.md` Next references `gate-axis-linecut`. Used for the gate-C
re-entry baseline (a 1D n-cut). Tagged it `add_comment('re-entry-baseline')` +
structured params rather than fake a recipe slug. Prior session tagged the same
idiom `cnp-and-dline-calibration` (also not its true purpose).

PROTOCOL — bring-up confirmed probe MC = Probe2_MixingCh_low (rotator probe,
device card), logfile fresh to ~13 s; Probe1_MixingCh_low is ~21 h stale — the
auto-pick correctly chose the live Probe2 (no >300 s warning). Cross-read vs
advancing fridge logs clears the 2026-06-23 stale-logfile trap.

## 2026-06-25 — science checkpoints

RESULT — Gate-C re-entry (run 0): dome reproduced mV-exact. Rxx=0.60 Ω at
n=−5.00e11, D=−0.64 (V_tg=−5.365, V_bg=+3.987); <2 Ω core n∈[−5.30,−4.90]e11;
leakage <75 pA; 34 mK. Device survived handover.

RESULT — Step 0 B_eff0 (runs 1,2): **B_eff0 = −0.366 mT** (midpoint −0.352 /
parabola −0.380; ±~0.15 mT). Normal Rxx ~36 Ω; B_c half-width ~2.2 mT. Flank
asymmetry −2.58/+1.88 mT = expected inter-half remanence mismatch. **Use
magnet.field(−0.366e-3) as "B=0" for all zero-field figures; Fig 4 = B_eff0 +
{1,2,4 mT}.** One-time — not re-located this session.

FEEDBACK/decision — took Step 0 as two one-sided cuts (discipline-compliant),
NOT cross-zero (that's authorized for Fig 2 only). Flagged the cross-zero
alternative to operator on the page; awaiting any preference.

FEEDBACK — Figure 1: operator rejected the 1806-pt / ~1h map (cell 31) as not
publication quality. Wants ~10 h figure-grade, WIDE range (n −7→−1, D out to the
BG-cap extremal up to −0.4) and FINER than 0.02/0.005 on both axes. His exact
0.005/0.001 spec = ~314k pts ≈ 5–8 days; I priced it and he set a ~10 h budget.
Committed (cell 33, supersedes 31): n[−7,−1]@0.015 × D[−0.69,−0.40]@0.004,
26.5k pts, delay 1.3, ~10.6 h, D ordered extremal→−0.4 for early-dome checkpoint.
Lesson for pricing: "figure-grade" here means many-hour maps, not 1 h.

PROTOCOL — measure is append-only, so the revised Fig 1 was landed as a NEW cell
(33) superseding cell 31 with a "don't run 31" note, not an edit.

FEEDBACK — Figure 1 v3 (cell 35, supersedes 31 & 33): operator wanted (a) more
symmetric sampling — drop the n/density resolution (cell 33 was 3.75:1 n:D step
ratio vs dome aspect ~11:1, so n ~3x oversampled); (b) lower lock-in sensitivity
(1 mV too sensitive for a wide map approaching the CNP gap). Committed: n 0.03
(201) x D 0.0025 (117), dome resolved ~27x28 pts, pixel aspect 1.7:1, ~8.5 h;
4T sens 1 mV -> 5 mV (ceiling 10k -> 50k, near-CNP gap won't rail). Good general
lesson: for WIDE (n,D) maps that approach the CNP gap, size sensitivity to the
landscape's dynamic range, not the SC floor; and match step-ratio to feature
aspect for isotropic sampling.

FEEDBACK/correction — Fig 1 sensitivity: I had the SR830 direction backwards.
Bigger full-scale value = LESS sensitive. Operator wanted it DROPPED to resolve
1 kOhm at 1 nA: V = R*I*G = 1k * 1n * 100 = 0.1 mV full scale. I wrongly went
1 mV -> 5 mV (bigger). Corrected cell 37: sr830_3 sens = 1e-4 (0.1 mV), rails
above ~1 kOhm (near-CNP gap, don't care). 2T kept at 5 mV (contact monitor).
ALSO: I misread the operator's "1K" as 1 Kelvin (temperature) — it meant 1 kOhm
(the resistance scale for sizing sensitivity). No T-ceiling implication; Figs 3-5
still run base -> ~490 mK per brief. Principle for downstream: size lock-in
full-scale to the ~1 kOhm SC R-scale (0.1 mV at 1 nA), let high-R gap rail.

RESULT — Figure 1 (run 3, 21239 pts, 8.6h, verified clean): wide SC dome map at
B_eff0. Dome tilts (n-center more negative as |D| grows), sits below-left of the
CNP/gap ridge. Core <2ohm width flat ~0.45-0.55e11 across accessible D[-0.64,-0.66];
true peak ~0.60 at D~-0.665/-0.67 but BG-cap-limited for the T-map (high-|D| flank,
V_bg->4.2). SELECTED widest-D line = D=-0.64 (flat-max width + best cap margin
153mV + matches all prior Ic/Tc/Bc characterization); OPTIMAL n=-5.0e11
(V_tg=-5.365, V_bg=+3.987). Fig 1 confirms the prior optimum with hi-res
justification. 0.1 mV sens behaved as designed (rails ~1.09 kOhm near CNP).
Pcolormesh reconstructs boustrophedon/variable-len rows by binning to grid
(hera_scratch/dome_pcolor.py). Promoted to ana cells 13-16.

RESULT — Heater warm-up (cell 40): heater->T re-confirmed vs prior cooldown
(1/2/3/4/4.5/5/5.5/6/6.5 V -> 49/100/158/229/262/317/364/428/480 mK). Free Tc
PREVIEW from 4T R(T) at the optimum: R->0 below ~150 mK, normal ~43 ohm by
~360 mK, 50%-normal at T~280 mK = Tc, matches prior 0.26-0.29 K. Settle times
152-782 s for 0.5-1 V steps -> tau~2 min; dense 4.4 mK steps settle ~100 s ->
Fig-3 slow_delay = 90 s. Heater left at 6.5 V for the descending Fig-3 ladder.

PLAN — heater block ordering to minimise cycles: warm up ONCE (done), then 4
field-maps alternating ladder direction (Fig3 descends 480->34 @B_eff0; Fig4a
ascends @+1mT; Fig4b descends @+2mT; Fig4c ascends @+4mT), field changes at the
ladder endpoints. Fig3 = cell 43 (~7 h, ends heater-off at base).

RECIPE FIX — temperature-dependence (Flavor A) / heater discipline: the brief's
"~100 T-pts, small steps -> short dwell, measure-while-cooling" FAILED here. Fig 3
(run 4, 90 s dwell, descending) shows a ~50 mK SAMPLE-PROBE LAG through the SC
transition: dynamic R(T) at optimum is 3-5x the equilibrium warm-up R at the same
recorded probe-T (229 mK: 26.6 vs 5.8 ohm), biasing Tc to 223 mK vs equilibrium/
prior ~280 mK. Root cause: probe MC thermometer cools faster than the sample;
90 s dwell << sample-probe equilibration time through the transition. The dome
SHAPE is correct; the absolute T-axis is not. Lesson: for THIS sample's thermal
link, R(T,n) maps need full per-step settling (R-plateau gated), not a fast
dynamic ladder. The warm-up (heating, dT/dt-gated) was closer to truth but may
carry the opposite-direction lag -> settle test (cell 49) measures the true dwell.

FEEDBACK — operator chose FULL SETTLED RE-DO (most rigorous) over the
remap-salvage. Discard run 4 for the quantitative figure; re-measure Figs 3/4/5
with per-step equilibration. Block grows to ~40-50 h (accepted). Run 4 kept as
the diagnostic (ana cells 17-19).

RECIPE FIX (refined, operator) — T-dependence dwell: the right rule is **~1 tau
dwell per step + SMALL steps**, NOT zero-dwell and NOT full-settle, and NEVER
up/down averaging (ambiguous). At 1 tau each step is ~63% thermalized; small steps
make the ~0.37x(step) remainder negligible -> sample tracks T. My settle-test
(big base->4.5V jump) was a poor tau probe; tau ~3.5 min from the warm-up 1 V
settles (probe dT/dt<1 mK/min in ~510-780 s). Fig 3 re-do (cell 52): ascending,
120 uniform-T steps (~3.7 mK), slow_delay 210 s (~1 tau), single direction,
~12.5 h, residual per-step lag ~1.4 mK. Run 4's ~80 mK lag = 90 s dwell (<1 tau,
under-thermalized) + only 100 pts (bigger steps). Verify lag post-hoc vs prior
Tc~280 + run 4; no processing tricks.

RESULT — Figure 3 (run 5, settled, 11.9 h, verified clean): quantitative R(T,n)
at D=-0.64, B_eff0. Clean dome in (n,T); per-row T-drift ~1 mK. **Tc(optimum) =
235 mK** (50%-normal). Run 5 (up,235) & run 4 (down,223) BRACKET true Tc ~228-235
mK (11 mK apart -> residual lag few mK). This is BELOW the handoff/prior 264-290 mK
-> the prior + the warm-up were under-settled (biased Tc high). **Device card Tc
should drop to ~0.23 K (pending operator confirm).** Promoted to ana cells 20-22.
Method (1 tau dwell, small steps, single ascending) carries to Figs 4 & 5.

PLAN — Fig 4 = R(T,n) at B_eff0+{1,2,4 mT}, each ascending-from-base settled,
all ASCENDING (consistent lag). Position each field one-sided, read B back.
FEEDBACK (operator) — finite-field maps need only go to ~350 mK: field suppresses
Tc below the zero-field 235 mK, so 480 mK wastes time on flat normal. Capped Fig 4
ladders at 350 mK (86 pts, ~3.7 mK, ~8.9 h each). Fig 4a = cell 57 (supersedes 55).
+2/+4 mT members also trimmed to fewer T-pts (dome near-gone). Full Fig 4 -> ~24-28 h.

PROTOCOL — caught my own Fig-3 bug: n-line missing *1e11 -> validator assert
fired before any hardware moved (cell 43 -> corrected cell 46). Validators did
their job. Unit convention: cell nD_to_V takes cm^-2, callers pass n*1e11.

RESULT — Fig 4 field members (R(T,n), settled, capped): dome collapse with B.
  B_eff0 (run5): Tc=235 mK, floor ~0
  +1 mT (run6):  Tc=166 mK, floor 4.4 ohm
  +2 mT (run7):  Tc=113 mK, floor 11.6 ohm  (R-settle fix worked, clean start)
Trend monotonic; +4mT (4c) expected fully normal (no dome). Will build Fig-4
composite (Tc-vs-B / dome collapse) ana entry after 4c. Field stable each run.

FEEDBACK — operator: +2 mT already non-SC (Tc 113, floor 12 ohm), so +4 mT (4c,
cell 63) is worthless -> DROPPED (don't run 63). Replace with intermediate fields
to resolve the collapse: +1.25 mT (cell 65, steep region 1->2 mT) then +0.5 mT
(0->1 mT gap) -> 5-pt dome-collapse (0,0.5,1,1.25,2 mT). Intermediates positioned
by decreasing |B| from current +1.634 mT (one-sided, no zero-cross).
TOOLING — nb-collab execute-cell: re-deriving "last code cell" via menv python
reads the on-disk .ipynb which LAGS RTC -> grabs a stale id. Use the cell id from
the append output directly.

RESULT — Figure 5 (run 12, dV/dI(I_dc,T), settled, 8.9h): clean supercurrent dome
in the (I,T) plane. Ic(base 34mK)=36 nA (matches verify/run9/handoff). Ic(T)->0
at ~216 mK -> independent Tc, consistent with Fig 3 R-50% Tc=235 mK; both well
below the prior under-settled 264-290 mK. Verify (run 11) was textbook: switching
+/-36 nA, non-hysteretic, field at B_eff0. Promoted to ana.
RESULT — xi_GL(0)=0.30 um from Fig-4 B_c2(T) dome collapse (5 pts, dB_c2/dT=-16
mT/K). Brackets 0.3-0.4 um with the direct base field-kill. Promoted to ana.
PLAN — only Fig 2 (Fraunhofer) left: re-run cell 75 (recovery verify) at base,
then the Fraunhofer (cell landed): cross-zero B_eff0+/-5mT x bias, ~4.6h.

RESULT — Figure 2 Fraunhofer (run 13, 5.3h, base T held 33-34 mK): single central
lobe, Ic max 37 nA at B_true=0.000 mT (= B_eff0) -> supercurrent recovered post-
cycle AND B_eff0 validated to <0.05 mT. Ic(B)->0 by +/-1.5 mT (~B_c). NO side
lobes resolved -> claim phase-coherence + Phi0/area (~1 um^2, single-lobe est),
NOT a microscopic junction (per guardrails). ALL 6 FIGURES COMPLETE.
