# Session notes — QC0426 / VTI — 2026-06-17

Operational log (RECIPE FIX / TOOLING / PROTOCOL / FEEDBACK). Not a science notebook —
points at data/cells/recipes, does not duplicate them.

## ===== SESSION RESULT: QC0426 = ABA (Bernal), strong =====

FS-count complete. Two Fermi surfaces (ML Dirac + BL parabolic): f_BL~0.85 F_L +
f_ML~0.20 F_L; Luttinger sum lambda=(f_ML+f_BL)/F_L = 1.06-1.08 CONSTANT across n
(electron fan, both Rxx channels), seen in 4/4 spot checks (sr1/sr2 x hole/electron).
ABC excluded. Both regions agree (no mosaic). Weight = STRONG (LK-mass split blocked;
Onsager overlay clamped at 3.5e12). SdH lever-arm lambda~1.07 = Hall n-scale -> the
geometry n was ~7% low (upgraded). Full call + hedges: ana cell 20. Device card updated.
Runs: data/2 gate map, data/4 e-spot, data/5 h-spot, data/6 e-fan; data/0,1,3 =
duds/aborts (0 LS335-contention, 1 liveness [good], 3 sr0-overload). Next if pursued:
LK mass (temperature-dependence, blocklisted here) + mK rig. Rig parked quiescent.

SHUTDOWN (operator request, measure cell 46): excitation -> 5 nA (sr1.amplitude 0.5V);
device contacts grounded via mux.park() (managed lines only; Si 16/11 standing closures
preserved, not qsw.reset()). End state: B~0, TG=0, BG~0, Si=0V, T 1.17K. Session over.

## Bring-up (E0)

- Gate A green: magnet (field 0.002 T, output enabled, PS heater on), LS335 sample
  T = 1.165 K, 4× SR830, k_bg (2400) + k_2410 (2410) parked 0 V step 5 mV, DC205,
  QSwitch (serial 37, fw 2.0) all connected. Exec counts monotonic 1→14 (one kernel).
- Gate B green: SAFETIES ran as exec [10]; validators committed = device-card limits
  exactly (TG [-6,+7], BG [-4.5,+4.5], Si [-50,+50]) and B cap 8.0 T on magnet.mag.vals
  (< 14.0 T driver backstop). Compared numerically, not eyeballed.
- Probe staged at measure cells 27/28 (read-only kernel-binding + VERIFY snapshot) =
  designated first-E1 execute. Awaiting operator grant ("go for autonomy").

## GRANT — E1 engaged 2026-06-17

Operator (callsign "alpha sierra") gave **"go for autonomy"**. E1 active. First E1
execute = read-only kernel-binding probe (measure cell 28). Re-entry after any E0
drop requires a fresh explicit grant.

## RECIPE FIX / PROTOCOL — never fp(heater.sample_temperature) in a VTI sweep

Gate C liveness (measure cell 30, exec 16) **errored at point 0** with VisaIOError
TMO on `KRDG? A` (`heater.sample_temperature`). Root cause = the rig-card "LS335 has
two masters" quirk: per-point polling of the Lakeshore contends with the Grafana
logger and times out. Fix: do **not** `s.fp(heater.sample_temperature)` (or any
LS335 read) inside the per-point loop — record T once in `meas_config` (snapshot)
and lean on the Grafana log (timestamped) for any post-hoc T(t)/T(B) correction.
Applies to gate map + fans too. Run id 0 = the dud (metadata only, 0 rows).
gate-current-sanity-check.md fps `temperature` per point — fine on toploader, a trap
on VTI; the recipe should carry a VTI caveat. Corrected liveness re-run as a new cell.

## Gate C PASS (run 1) + gate map launched (run 2)

- Gate C liveness (measure cell 32, run 1): device alive — drain I flat 5.0 nA
  (current-bias OK), Rxx modulates (peak ~1.4k @ V_TG~0 at BG=0), sr1/sr2 corr 0.99
  but not identical (no grounded short), leakage floor (BG 35 pA, Si 0.57 nA on 1uA
  range). Promoted to ana cell 11. **Device R is LOW (~kohm)** -> my 5 mV sens
  over-coarsened (47.7 ohm quantization); using 0.5 mV for the map.
- OBSERVATION: the single TG trace shows a **double-peak** near V_TG 0 and +0.45,
  **common to both Rxx channels** (same V positions) -> a real feature in the gate
  response, not a per-contact mosaic CNP offset. Resolve in the 2D map (could be a
  two-CNP / low-density band feature; far too early to interpret).
- Gate map (measure cell 34, run 2): 0T BG[-4.5,4.5]x25 x TG[-6,6]x61, Si=0, sens
  0.5 mV. Launched bg; ~50-60 min; row-12 health checkpoint armed via hera-watch.
- DESIGN NOTE: TG=DC205 -> sweep `dc205_volt` (col DC_bias), NOT k_tg.volt. landau-
  fan-vti.md says fast axis `[k_tg.volt,k_bg.volt]` (generic) — for QC0426 substitute
  `[dc205_volt, k_bg.volt]`. dc205_volt has NO get -> never s.ramp it; park via set.

## CNP / (n,D) calibration — ESTABLISHED (run 2, ana cells 12-13)

- CNP line per channel: sr1 (T3-T4) Vtg=-1.305*Vbg+0.174; sr2 (B4-B5) Vtg=-1.298*Vbg
  +0.122. Agree to 0.5%, match geometry (1.30) -> ONE device calibration (no cap-ratio
  mosaic).
- ADOPTED: c_tg=1.7027e-3, c_bg=2.2135e-3 F/m^2 (geometry anchor, SiO2 zeroed; ratio
  1.300 data-confirmed). n_offset=-1.57e11 cm^-2. D_offset=0 (geometric assumption).
- Closure |n|<=2e11 cm^-2 on ridge. Two-tier provenance: ratio DATA-CALIBRATED, abs
  n/D scale GEOMETRY PRIOR (upgrade via QH lever-arm dn/dB=nu*e/h when fan lands).
- D=0 line (validated in-range): n=+8e12 -> Vtg+3.84/Vbg+2.95; n=-8e12 -> Vtg-3.69/
  Vbg-2.84. Realized D=0 window +-1.24e13 cm^-2.
- CAVEAT: CNP-R min at D=+0.21 V/nm (not D_cal=0) -> possible small built-in D offset
  (~2 BG-rows resolved). Kept D_offset=0; will D-robustness-check at SdH. CNP R 0.8k
  (D~0) .. 85k (|D|~1) -> D-gapped, caps below MOhm (carry to per-channel stacking read).

## TOOLING/PROTOCOL — scale sr0 (current monitor) sens with bias current

Spot A v1 (run 3) aborted: sr0 read 10.9 nA vs expected 50 nA. NOT a current
problem — sr0 sens was 0.01V (10mV FS) and the true 50 nA -> 50 mV at the Ithaco
x1e6 -> sr0 OVERLOAD -> garbage. Diagnostic (measure cell 38): current is linear in
amplitude (5.48nA@0.5V .. 49.6nA@5V), confirming 50 nA bias + 100 MOhm. Fix: sr0 sens
must track I_bias*1e6 (at 50nA -> >=50mV -> sens 0.1V). Lesson for any current boost:
re-range sr0 too. Rxx grain at 50nA/20uV was 0.018 ohm (fine), but moved Rxx to 10uV
for headroom. Run 3 = aborted partial (electron, to 0.74T). Relaunched as run 4 (v2).

## Spot A (run 4) checkpoint — sens too fine for climbing MR; Hall n cross-check

- Run 4 healthy: I steady 49.8nA, SdH developing by ~3-4T (within-batch spread > smooth
  MR -> ~30 ohm oscillations at 4T), onset ~2-3T.
- HALL CROSS-CHECK: sr3 Rxy linear ~74 ohm/T -> n_Hall = 1/(e*dRxy/dB) = 8.4e12 cm^-2
  vs gate-calib 8.0e12 -> agree 5%. Soft validation of the geometry n-scale (the QH
  lever-arm upgrade can firm it later).
- ISSUE: sr1 Rxx strong climbing MR (18->137 ohm at 4.2T, rising) -> will overload
  10uV sens (200 ohm) at ~6.4T. sr2 climbs slower (~58 ohm@4.2T), survives full range.
  LESSON (landau-fan step 3): set sens for the HIGH-B scale (10-100x B=0). Use sr1/sr2
  20-50uV for spot B + fan. Spot A: window sr1 FFT below its overload field; sr2 full.

## RESULT — Spot A (run 4, electron n=+8e12 D=0): ABA two-tone signature

Both Rxx channels show a TWO-tone pair, detrender-robust (identical across poly 3/5/7,
hann/blackman):
- sr1 (T3-T4): f_low 16.1 T + f_high 70.8 T (sum 87 T)
- sr2 (B4-B5): f_low 18.7 T + f_high 69.3 T (sum 88 T)
Sum ~ F_L: gate F_L=82.7 T, **Hall F_L=86.8 T** (n_Hall=8.4e12 from Rxy slope). Sum
17+70=87 ~ F_L(Hall) -> Luttinger partition holds -> TWO Fermi surfaces (ML+BL) ->
**ABA** on the electron side, both regions. ABC would be a single tone AT F_L.
- f_high ~70 T = f_BL (big bilayer pocket); f_low ~17 T = f_ML (small monolayer pocket).
- Not harmonics (70/17=4.1). f_low mildly window-sensitive (16-21T) = known f_ML
  extraction sensitivity (hedge). HEDGE: LK-mass split (decisive ML-light/BL-heavy +
  beat exclusion) UNAVAILABLE - temperature-dependence is blocklisted. Onsager overlay
  also unavailable at n=8e12 (model clamp 3.5e12). So labeling ML/BL is by pocket size,
  call rests on combinatorics + Luttinger, to be firmed by F(n) across the fan.
- ana: cell to be added. Spot B (hole) running to cross-check + mosaic.

## RESULT — Spot B (run 5, hole n=-8e12 D=0): ABA pair + intermod clutter

Hole side, strong clean SdH (bigger oscillations than electron). Both channels:
16.0 T + 72.0 T (detrender-robust d3/5/7) -> 16+72=88 = F_L(Hall, n_H=8.55e12).
ABA pair confirmed, hole side. f_ML(16T) is DOMINANT in sr1 (prior: hole = balanced
ML/BL held). EXTRA peaks ~88-93T (>F_L, unphysical for single pocket -> sum-intermod
16+72=88) and 40-57T (likely 72-16=56 difference / harmonics) - the stronger
oscillations produce more nonlinear mixing. Screen by n-dependence in the fan.
Hall n: Rxy -584 ohm @8T -> |n|=8.55e12 (gate 8e12, +7%). No overload (20uV worked,
sr1 max 207 ohm). Magnet home at 0.

## STACKING EVIDENCE SO FAR: ABA in 4/4 (2 channels x 2 sides)
All show ML+BL pair (~16-18 low + 70-72 high) partitioning F_L. -> strong ABA.
Hedges: LK-mass + Onsager-overlay cross-checks blocked this session. To firm
(strong->decisive): F(n) partition robustness via fan. Fan side = ELECTRON (cleanest,
no intermod clutter; hole corroborates). ana: spot A cell 15; spot B cell pending.

## TOOLING — get execute-cell ids from nb-collab append output, not the on-disk file

Executing an ana cell via `$(menv python ... nb['cells'][-1]['id'])` ran the WRONG
cell: the on-disk .ipynb is stale vs the live RTC/collaborative notebook, so [-1] was
an old cell. Use the id printed by `nb-collab append` (it reports `appended code @ N
id=...`), or query the live notebook, not the file on disk. (Re-ran spot B with the
correct id e35204d3.)

## Fan (run 6) launched + healthy — electron D=0, overnight

Health check: geometry 326x33=10758, I steady 49.9nA, gates step n-line correctly
(TG 1.01->4.78, BG 0.78->3.68/row), B 1.5T. ~7h, completes ~03:00 (digest ETA is a
transient miscalc - first row included the 11min ramp). CAVEAT: low-n columns (~2e12)
have high baseline R (~210 ohm @1.5T) -> will overload sr1 (20uV/400 ohm FS) at high B;
mid-high n (5-10e12, the partition-test columns) stay in range. Window/exclude low-n
in analysis (don't coarsen sens - keeps the good columns resolved). Mid-run checkpoint
armed ~4h (B~5T) for preliminary F(n) partition. fan_analyze.py prepped.

## Fan mid-run checkpoint (B=5.34T, 192/326): ABA two-branch structure confirmed

Preliminary partition (partial data, B<=5.34T, coarse dF~3.2T): BOTH channels show two
branches tracking with n (f_ML & f_BL both rising ~F propto n), summing to ~F_L. sr2
resid +8.9% (->~+2-3% vs Hall-density F_L), sr1 +21% (auto-picker grabbing the ~88T
intermod as f_BL - extraction artifact). Two-FS (ABA) picture holds. I steady 49.7nA,
ETA 02:53. Low-n cols clipping at high B (437 ohm rail) as expected - exclude in final.
FINAL-ANALYSIS TODO: full B=8T data (dF 2.67T); tighten high-band to [0.55,0.95]*F_L +
harmonic screen; use F_L(Hall) for the partition (gate n-scale ~5-7% low per Rxy).

## SdH design facts
- At n=+-8e12, D=0: Rxx only ~18-36 ohm (low-R device). Standing 5 nA bias -> ~0.1uV,
  SdH buried. Boosting AC drive sr1.amplitude 0.5->5 V => 50 nA bias (sample dissipation
  ~1e-13 W, ohmic). sens ~20uV. F_L(8e12)=82.7 T; B-step 12.5 mT (3 samp/period to ~1.7T).

## Bring-up record — lock-in settings (rig card: tau not stored in metadata)

Probe (measure cell 28, exec 15) read-out:
- All four SR830: **tau = 0.3 s, filter_slope = 24 dB/oct**. Settling floor (k.tau,
  k=7-10 at 24 dB/oct) => dwell >= ~2.1-3.0 s/pt for clean points. Price sweeps to this.
- sr0 (drain I): sens 0.01 V, f 13 Hz. sr1 (Rxx + AC drive source): sens 0.2 mV,
  ampl **0.5 V** => 0.5 V / 100 MOhm = **5 nA** current bias, f 13 Hz. sr2 (Rxx) sens
  0.2 mV. sr3 (Rxy/Hall) sens 0.2 mV.
- Magnet set=read=0.0025 T (output enabled, PS on); gates 0 V; sample T 1.165 K.
- vaporizer_temperature reads 0.0 K (control-only B sensor / curve anomaly per rig
  card; not load-bearing).

## TOOLING — data basedir is under .../aaron/, operator named zack

`main_dir` (measure cell 3) = `C:\Users\DGG\VTI_local_data\aaron\20260617-QC0426`, but
brief + device card name the operator as **zack**. Likely a handed-over / shared dir;
flagged to operator, non-blocking. Noting in case it matters for archival/attribution.
