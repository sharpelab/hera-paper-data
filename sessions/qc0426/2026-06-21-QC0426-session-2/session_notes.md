# Session notes — QC0426 / vti

Operational log (not a science notebook).

## E1 grant — 2026-06-21
Operator (Zack) granted autonomy: "Ramp down is appropriate. go for autonomy"
once Gate A + Gate B were green and bring-up VERIFY flags addressed. E1 engaged.
First E1 execute = read-only kernel-binding probe (per VERIFY); then magnet
ramp 0.30 T -> 0 T; then Gate C contact liveness -> Step 1 (B=0 gate map / CNP).

## TOOLING — gatemap recipe is toploader-API; no gatemap-vti variant (2026-06-21)
`measurements/gatemap.md` is written in toploader API (`k_tg.volt`, `s.AsyncStation`,
fp temperature). Adapted to VTI for run 0 (Gate C) and the Step-1 map: TG axis =
`dc205_volt` (data col `DC_bias`), set-only param; no TG current monitor so gate
leakage is watched only on `k_bg.curr`/`k_si.curr`; temperature is NOT fp'd
per-point (rig card: LS335 Grafana co-master, per-point poll has killed a run) —
T captured once in `meas_config`. Station built via `async_station(meas_config)`.
A `gatemap-vti` variant capturing these deltas would help.

## PROTOCOL — settling floor vs bring-up dwell (2026-06-21)
Lock-ins read 24 dB/oct, tau=0.3 s (all channels). Rig-card settling floor at
24 dB/oct is k~7-10 tau = 2.1-3 s; the bring-up/Gate C dwell of 4 tau = 1.2 s is
BELOW it, so features can be mildly smeared (small notch at V_bg=0 in run 0).
Reasoning used for Step-1 map: a *constant* fast-axis settling lag shifts the CNP
ridge by the same amount in every row -> biases the intercept (offset) only, NOT
the slope (cap ratio). So the calibration map runs at fast_delay~1.0 s safely for
the ratio; SdH spot-checks/fan will lock proper settling per investigation Step 3.
Did not change filter_slope (operator-owned front-panel setting per rig card).

## FEEDBACK/data — Gate C result (run 0, 2026-06-21)
CNP at TG=0 is V_bg = +0.40 V, peak Rxx ~1.9 kOhm on BOTH sr1(T3-T4) & sr2(B4-B5)
(agree). Geometry-prior cap ratio c_bg/c_tg = t_tg/t_bg = 15.6/12 = 1.30 -> expected
CNP line V_tg ~= -1.30*V_bg + 0.52. Gate leakage at Keithley 1uA-range noise floor
(|I_bg|<=0.24 nA, |I_si|<=0.58 nA), not genuine. Contacts alive.

## Step 1 DONE — (n,D) calibration (run 1, 2026-06-21/22)
B=0 gate map (41x81, 74 min) -> cap ratio c_bg/c_tg = 1.309 (sr1)/1.300 (sr2),
matches geometry prior 1.300 to <1% (happy case, as prior QC0426 campaign noted).
(n=0,D=0) at Vtg=+0.087, Vbg=+0.066. D=0 line reaches >=+/-6e12 cm^-2 in-validators.
Calibration written to device_card.md + ana run-1 block. CNP peak-R grows strongly
with |D| (D-gap, interpretation held). The 24dB/oct fast-axis settling reasoning
held: map vs Gate C slopes agree, offsets differ ~0.27V (settling lag) as predicted.
Next: Step 2 feasibility (F_L) + Step 3 SdH spot checks at large |n|, D=0.

## FEEDBACK/RECIPE FIX — SdH sensitivity vs strong MR (run 2, 2026-06-22)
SC1 (hole, n=-3.5e12, run 2) sr1/sr2 sensitivities (1e-5 = 10uV FS) chosen with
"headroom for MR" CLIPPED above ~4T: Rxx grows ~B^1.8 (49 ohm@0.2T -> 552 ohm@4.4T,
extrap ~1.6 kohm@8T -> 32uV). My MR estimate (~200 ohm@8T) was an order low. The
device has STRONG positive MR at high-|n| metallic. Lesson: for SdH field sweeps on
this device, size Rxx sens off the 8T MR-extrapolated Rxx (~kohm), not the B=0 value
-> use 1e-4 (100uV FS) for sr1/sr2 at n~3.5e12. sdh-spot-check recipe step 3
("full scale ~ I_bias x R_target") should say R_target = the high-B MR value, not B=0.
Also: SdH onset not found below 4.4T (warm electron-T ~8K pushes it high) -> oscillations
live >4T; small 1/B window risks resolution-limited read (investigation anticipates this;
Step 6 Streda fallback). Re-run SC1' rides home 8->1T at sens 1e-4 (no re-traverse).
Also TIMING: uniform-1/B high-B points are EXPENSIVE on the blocking magnet (large dB
per step); SC1 ETA underestimated the high-field tail by ~30min. Price the high-B
traverse explicitly for fans.

## Step 3 HOLE result — resolution-limited (runs 2 clipped + 3 clean, 2026-06-22)
Clean hole-side SdH (run 3, n=-3.5e12, D=0, B 8->1T, sens 1e-4): NO FS count
extractable. Onset high (~3T, warm electron-T ~8K thermally suppresses low-B SdH)
-> short 1/B record -> FFT peak WANDERS across extraction (4/36/19/24T vs cutoff;
10->19T vs bg-degree). Broad ~10-20T blob, no sharp line, ~no power at F_L=36T.
Fork per STYLE rule 14, not a number. Does NOT distinguish ABA vs ABC (both
unresolved). Recorded ana cells 14-17. Electron-side mirror running (run 4). If
both sides limited -> Step-6 high-field Streda/Chern, or resolution-limited
cannot-tell. Step-4 fan NOT yet justified (would inherit the same limitation).
OPERATOR DECISION likely needed on strategic pivot (Step-6 vs report) after run 4.

## Step 3 ELECTRON result — CLEAN, ABC-leaning (run 4, 2026-06-22)
Electron side (n=+3.5e12, D=0, mirror of run 3) is RESOLVABLE: clean periodic SdH,
robust dominant tone ~34T (sr1)/33.5T (sr2), STABLE across cutoff(1.5-4T) & bg-deg(3-7)
[hole wandered 4-36T]. F_L/dom=1.06-1.08 -> tone AT F_L within scale uncertainty =>
single Fermi surface = ABC single-pocket signature (provisional, single density).
Satellites (~6/14/21/30/40/50T) = sidelobe ringing of one tone, not a 2nd pocket.
ABA (f_BL~34T + tiny unresolved f_ML~2T) NOT excluded at this resolution. Recorded
ana cells 18-21. Electron is the clean side.

## Step 4 FAN LAUNCHED — electron D=0 (run 5, 2026-06-22 ~05:00)
landau-fan-vti: n[0.5-3.5]e12 (40 fast) x B[7.95-1.0]T (96 slow, uniform-1/B Nyquist/3
F_L=36T), B descending (rides home from run4 @8T), dwell f2.5/s2, sens 1e-4. ~4.5h.
Per-column SdH FFT -> F(n) vs F_L resolves ABC (single tone tracking F_L) vs ABA
(partition Sigma f = n). The decisive measurement. Checkpoint ~50%.

## FAN clipping at low-n/high-B corner (run 5, ~05:15) — NOT re-running
At ~31min/7 rows, sr1 max|V|=109uV > 100uV FS (sens 1e-4): clips at low-n(<~1e12)
+ high-B(>~6T), i.e. the DEEP-QH corner (n=0.5e12,8T -> nu~2.6, Rxx peak 5528 ohm).
Sized sens off the run-4 spot check (n=3.5e12, Rxx~671 ohm, shallow QH) -> missed the
low-n QH peaks. LESSON: a fan spanning low->high n needs sens for the low-n QH Rxx
(kohm+), not the high-n metallic value; 2e-4 or restrict n>=1e12 would avoid it.
DECISION: continue, NOT re-run. The n>=1.5e12 columns (nu>=8, Rxx<=~1-2kohm) are
CLIP-FREE and carry the decisive F(n)/ABC-vs-ABA read; low-n/high-B is QH (SdH-FFT
invalid there anyway). Analysis: per-column FFT on n>=1.5e12, mask |V|>=99uV points.

## FAN PREVIEW (run 5, 29/96 rows, B>2.6T, df~3.9T) — ABC-consistent (2026-06-22 ~06:20)
Per-column SdH FFT on clean n>=1.5e12: dominant F(n) TRACKS F_L across density,
F_peak/F_L ~ 1.0 +/- 0.1 (1.16 @1.5e12 -> 0.88 @3.5e12, crossing ~1), BOTH channels
(sr1,sr2) agree closely. Sits ON F_L, NOT F_L/2. => single Fermi surface carrying
full Luttinger density => ABC (rhombohedral) leaning/consistent. No partition, no 2nd
branch. Slight ratio slope => small global lever-arm rescale due (pin-the-scale).
PRELIMINARY (partial, coarse df; a small ML partner unresolvable here). Full-res
verdict + Onsager overlay (fs_count_b0) + Luttinger sum at completion (~08:20).
Channels agree => coherent single-domain region (not mosaic).

## CAMPAIGN CALL — fan complete (run 5, 2026-06-22 ~08:30)
Electron-region FS-count: SINGLE Fermi surface tracking F_L across n=1.5-3.5e12,
both channels agree (coherent single domain), Onsager overlay rescale lambda=1.03
(scale prior validated), Luttinger F~=F_L (one 4-fold pocket). => CONSISTENT-WITH
ABC (weak lean). BUT ABA NOT EXCLUDED: model says ABA's ML discriminator pocket is
~0.1-2.2T over this range (fs_count_b0), below this run's resolution (df~1.9T) and in
the MR-background band, and ABA-BL coincides with ABC's tone (~F_L). So the ML partner
is NOT-RESOLVABLE (not searched-and-absent) -> cannot positively distinguish ABA/ABC by
low-field FS-count at this T(~8K electron)/field. Recorded ana cells 22-25 (full output
contract). To FIRM: Step-6 high-field Streda/Chern (dedicated low-n QH run; note ABC LL
model not built -> qualitative ABC side) OR lower T (mK rig) OR n>3.5e12 (extend solver).
Hole side resolution-limited (run3). DELIVERABLE REACHED; Step-6 vs accept = operator call.
Magnet left at 1.0T, device idle, gates on D=0 n-line @ n=0.5e12 (run5 end).

## TODO/RECIPE-FIX surfaced this session (for triage)
- gatemap-vti variant (toploader-API gap) [logged above]
- sdh-spot-check step-3 R_target = high-B MR value (not B=0) for sens sizing [above]
- fan low-n QH needs QH-appropriate sens (or restrict n>=1e12) [above]
- fs_count_b0 Onsager clamp >3.5e12 blocks operating-density overlay (README TODO)
- LK-mass cross-check (temperature-dependence Flavor B) is BLOCKLISTED this session.
- TOOLING: hera-watch `--next` default --wait-start=1800s TIMED OUT (exit 2) on the
  step-6 scout (run 6) because a ~51min magnet ramp precedes the sweep. For runs gated
  behind a long field ramp, pass --wait-start > ramp time (used 2400s on re-arm). The
  execute itself was unaffected (the watch is just the monitor).

## Step 6 SCOUT result — QH NOT viable; CAMPAIGN CONCLUDED (run 6, 2026-06-22 ~14:05)
n-sweep at fixed B=7.95T (nu 1-7.8), QH sens (no clip). Rxx(nu) MONOTONIC, no minima
at integer nu (~12% washed modulation only); Rxy classical slope BELOW h/nu e2, NO
plateaus. => Landau gaps unresolved at 7.95T/8K = modest quantum mobility. Full Step-6
fan would NOT discriminate (LL sequence doesn't form). Scout (~1h) correctly gated out
the ~4-5h fan. FINAL CALL: consistent-with ABC / weak lean, ABA-not-excluded; both
discriminators (low-field small pocket; high-field QH/Streda) are mobility/T-limited on
VTI. Decisive needs mK rig. Recorded ana cells 26-28 (campaign conclusion).
CLEANUP: ramping magnet 7.95->0T (run after-the-fact, ~58min). Gates on low-n D=0 point.
