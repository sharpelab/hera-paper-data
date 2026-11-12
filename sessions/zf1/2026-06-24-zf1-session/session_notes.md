# Session notes — zf1 / toploader

Operational log (not a science notebook).

## 2026-06-24

PROTOCOL — brief mode wording mismatch: the Autonomy section sets **E1 this
round** (grant phrase "go for autonomy" once VERIFY/SAFETIES green), but the
Session-arc item 2 reads "E0 throughout." Surfaced to operator at bring-up;
holding in E0 until they resolve it + give an explicit grant. No autonomous
execution before then.
**RESOLVED 2026-06-24 15:5x:** operator granted "E1 - go for autonomy". E1
engaged. Hard gate confirmed: measure policy = append_exec (execute permitted).
Abort lever = nb-collab interrupt + live hera-watch monitoring (no canonical
leakage-abort callback in sweep namespace; running gate-sanity to known-good
card limits with leg-by-leg gate-current watch).

TOOLING — `nb-collab execute-cell` default `--timeout` is 570 s (9.5 min,
"sub-CC-Bash-cap"), SHORTER than a multi-leg sweep. Gate-sanity leg 1 alone was
~9 min, so the client returned `TimeoutError: Timeout waiting for output` (exit 1)
at 570 s while the KERNEL kept running the loop fine (data/1 still writing).
Cosmetic, not a real abort. Fix for long autonomous runs: pass an explicit large
`--timeout`, OR (better) fire-and-forget the execute and gate completion on
`nb-collab wait --follow` / hera-watch instead of the execute-cell client.

RECIPE FIX — meas-config slot / gate-current-sanity-check: I_bias is STALE in
metadata. meas_config['bias_voltage_1'] = sr830_1.amplitude() is captured in the
config cell (cell 21) BEFORE the AC drive amplitude is set (the sanity-check /
measure cell sets sr830_1.amplitude(0.1) → 1 nA). Result: metadata I_bias = 40 pA
(the residual ~4 mV amplitude) while true device current = 1.008 nA. hera-watch
R = V/I_bias is therefore inflated ~25×, and any analysis trusting metadata
I_bias is wrong by 25×. Fix before the gate map: set the drive amplitude first,
then rebuild meas_config so bias_voltage_1 = 0.1 V (I_bias = 1 nA). Will append a
config-refresh cell once the kernel is free.

DATA — Gate C gate-current-sanity-check PASSED (all 4 legs clean). Swept-gate
charging currents (pA, flat — no end-of-ramp turn-up): TG +6 V → 38 pA; TG −7 V
→ 61 pA (highest, consistent w/ card "leakage onset higher on +V" asymmetry,
still < ~100 pA); BG +4.2 V → 31 pA; BG −4 V → 41 pA. Parked-gate currents all
~31-39 pA at floor (no cross-gate path). Device I steady 1.008-1.01 nA; 4T Rxx
(sr830_3, 30-31) live & gate-modulating across all legs, true R spanning ~3.6-217
Ω (low/metallic at the high-density corners, k_bg=0 / k_tg=0 baselines). Channels
vary independently — not the grounded-device failure mode. data/0-3. DEVICE ALIVE
on the 4-terminal channel; gates clean to both card limits. VERIFY contact-wiring
item now green. Cleared to proceed to Step 1 pristine-field gate map.

TOOLING — stale-YDoc hang: when execute-cell client times out (570 s) mid-run,
the KERNEL finishes the cell but the YDoc never gets the final execution_count,
so the cell shows exec `-` (running) forever AND `nb-collab wait <id> --follow`
hangs on it indefinitely. I idled ~25 min on a dead wait before the operator
prodded. Lesson: detect long-run completion via data-dir mtime / hera-watch, NOT
cell state or wait-on-cell. Launch long runs with execute-cell --timeout sized
ABOVE the run (so the client survives and finalizes the YDoc) + hera-watch
--follow as the real monitor.

DATA — Step 1 gate map (data/4) launched: gatemap 81×69 over full validator box,
pristine field (B=−53 µT, untouched), I_bias fixed to 1 nA, 4T sens 5 mV.
First-rows checkpoint CLEAN: |I_tg| 83 pA / |I_bg| 49 pA max (no leak, mostly
mutual-C displacement), no clipping (4T |X| 3 µV vs 5 mV rail), current flat
1.01 nA, 4T R ~10-30 Ω at V_tg=−7 (metallic edge). Rate ~60 fast-row/min, ETA
~18:35 (~1.5 h). Mid-run alarm armed.

DATA — Step 1 map mid-run checkpoint (row 44/81, V_tg=+0.15): HEALTHY. 4T median
R 12-22 Ω metallic background with sharp CNP-ridge spikes to 3-5 kΩ (not clipping,
5 mV sens good); 2T 3.6-4.2 kΩ bg, CNP spikes 100-700 kΩ (<1 MΩ rail); current
1.01 nA w/ ~12% dips only at CNP crossings (contact-R freeze-out near gapped CNP,
physics). Leakage clean through CNP: 0/3170 pts >100 pA, |I_tg|max 83 pA at the
V_tg=−7 corner (mutual-C displacement, not the CNP). On track ~18:32. Analysis
pre-staged (hera_scratch/ana_gatemap_step1.py): TSV reform, CNP-ridge fit vs prior
ratio 1.18, candidate hunt in D<0 / n<0 prior region. Caps confirmed: c_bg/c_tg
prior 1.18, expected CNP slope dVtg/dVbg=-1.18.

TOOLING — bring-up clean. Gate A/B green: setup exec [1]-[11] linear; SAFETIES
validators match device card exactly (TG (-7,+6), BG (-4,+4.2), |B|<=0.1 T,
heater 6.5 V, dc205 +/-15 V). VERIFY: B=5.5 uT, probe MC 33.9 mK w/ Probe2
logfile mtime advancing (cross-checked vs fridge -- NOT the 2026-06-23
frozen-bridge case). Proposed Gate C gate-current-sanity-check (measure idx
24/26).

DATA — Step 1 map (data/4) COMPLETE & CLEAN (5589/5589, wall 1.5h, 0 leak pts
>100pA). Cap ratio c_bg/c_tg = 1.1833 (CNP fit, 0.3% from prior); CNP -> n=0 in
reprojection. Device uniformly metallic off the ridge (~10-30 ohm). Ana blocks
landed (gatemap raw+CNP fit+nD; linecuts) in 20260624_ana.ipynb.

DATA — Step 1 locate linecuts (data/5-8): CANDIDATE. Sharp localized 4T Rxx dip
to 6.27 ohm at n=-0.55e12 cm^-2, D=-0.60 V/nm (Vtg=-5.03 Vbg=3.73); absent at
D=-0.5/-0.7; opposite sign D=+0.5 shows a PEAK at same n. dip-vs-peak +/-D
asymmetry = graphene-WSe2 proximity-SC signature. Verdict: candidate
(consistent-with), 6 ohm low-but-finite. sens 2e-5 rails ~200 ohm near CNP.

TOOLING — nb-collab inline --markdown/--code with BACKTICKS gets shell
command-substituted (bash) -> backtick fragments VANISH. Hit it on an ana
citation. Use --markdown-file/--code-file/--source-file for backticks or $().

RECIPE FIX — bias-spectroscopy / calc_gate_voltages: returns (1,)-shaped arrays;
float() on them errors in this numpy; also needs np.array (not list) args. Works:
Vt,Vb=calc_gate_voltages(np.array([n]),np.array([D]),...); float(Vt[0]). Two
measure-cell failures before I dry-ran offline (both errored at the calc, BEFORE
any hardware move). Lesson: dry-run gate-vector calcs offline first.

DATA — Step 2 bias-spec (data/9) at candidate: CRITICAL-CURRENT signature. dV/dI
~7.5 ohm at zero bias, sharp switching peaks at +/-Ic ~= 15 nA (symmetric, no
fwd/bwd hysteresis), rising to ~45-51 ohm normal. Ic comparable to ~20 nA proximity
reference. Verdict: compelling candidate, consistent-with->leaning strong. Hedge:
zero-bias finite (failed-SC fork open); dV/dI peak confound-prone. Ana landed.

DATA — Step 3 field-kill pass A (data/10, +50 mT -> 0, zero DC bias): Rxx declines
gently 43->36 ohm, NO dip at controller-0 (T base throughout, leak 72 pA). The
50 mT excursion left ~10 mT remanence -> true B=0 (SC field max) shifted to NEGATIVE
controller field. This is the investigation's effective-zero subtlety in action.
Pass B (data/11, -50->0) launched to cross true-zero and reveal the dip + field-kill
mirror. NOTE: first magnet move of session; pristine-field era now ended.

DATA — Step 3 field-kill COMPLETE (data/10 +50->0, data/11 -50->0). Combined Rxx(B)
is a symmetric V centered at controller ~0 mT: rises with |B| both sides (~36 ohm
near 0 -> ~43 ohm at +/-50 mT), normal state field-insensitive = FIELD-KILL,
consistent-with SC, B_c-perp ~tens of mT. T held base both passes. CAVEAT: 50 mT
excursion left ~10 mT remanence; controller-0 != true zero; pristine 7-ohm dip not
cleanly recovered (clean B_c needs degauss/thermal re-zero). Ana landed.

DECISION — session verdict delivered (ana cell ed9b8622): candidate C1 (n=-0.55e12
cm^-2, D=-0.60 V/nm) = CONSISTENT-WITH superconductivity, compelling proximity-SC
candidate (leaning strong). 4 hallmarks: Rxx dip + critical current (Ic~15nA
switching peaks) + +/-D asymmetry + field-kill. Hedges: zero-bias R finite
(failed-SC fork open), Ic(T)->0 at Tc NOT measured, B_c not clean (remanence), QAH
not excluded (no Hall channel). Read temperature-dependence.md: Step 4 is a ~3h
heat-up that ENDS base-T work + remanence puts SC slightly off-optimum. Discretion
call given marathon session + strong constellation: deliver the calibrated call now,
tee up T-dependence (after a magnet re-zero) + Hall-channel routing + lower-AC dip
refinement as scoped next steps. Device left safe: gates 0, dc205 0, magnet 0, AC 1nA.

RECIPE FIX — sc-characterization Step 3 vs brief field discipline CONFLICT
(surfaced live): investigation says "sweep continuously across zero" to find
effective zero; brief (toploader) says NEVER cross B=0 in a measurement (eddy heat +
remanence). Resolved by two one-sided passes (+Bmax->0, -Bmax->0) bracketing 0. Also:
a finite-field excursion to locate B_c then leaves remanence that offsets true-zero,
so the SC optimum is lost for subsequent base-field work until a re-zero -- the
investigation's effective-zero step needs an explicit degauss/re-zero procedure on
this rig. Worth a recipe note: budget a magnet re-zero between field-char and any
return to zero-field characterization.

ABORT — operator called the session during the base-reference bias-spec re-run
(was prepping Step-4 T-dependence). nb-collab interrupt sent; cell caught early
(during setup, before gates moved). Safe-parked + verified: gates 0/0 V, dc205 0 V,
magnet ~-2.5e-5 T (~0), T 34 mK base. Kernel idle, no runaway sweeps. data/12 may
be an empty/partial stub (ignore). Session deliverable (verdict, ana cell ed9b8622)
stands. RESUMPTION: T-dependence (after a magnet re-zero), Hall-pair routing,
lower-AC dip refine — all scoped in the ana verdict (part 4).
