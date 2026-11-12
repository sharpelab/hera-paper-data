# Session notes — zf1 / toploader

Operational log (not a science notebook).

## E1 autonomy grant — 2026-06-24 ~23:25
Operator (Aaron) said "go for autonomy" after VERIFY + SAFETIES confirmed green
(Gate A/B/C all passed; Gate C = runs 0–3, ana cells 10–12). Engaging E1:
I execute in-envelope measure cells (sweeps, gate sets) within the committed
validators; consent-gated items (safety-surface edits, gate ramp `step`) and the
blocklist remain off. Re-entry after any E0 drop requires a fresh grant.

## 2026-06-24 ~23:35 — survey gatemap launched (run 4), first-rows checkpoint GO
101x101 raw (V_tg[-6.9,5.9] slow x V_bg[-3.95,4.15] fast), slow_delay 3/fast_delay 1.
Measured megasweep rate ~43 pts/min -> ~4h ETA (~03:23). First-rows: leakage tens of
pA even at combined extremes (|I_tg|=84, |I_bg|=51 pA), current 1.01 nA, 2T 3-20 kOhm.

RECIPE FIX — gatemap.md: step 5 ("set sensitivity to the largest R you need to
resolve") is correct for the cap-ratio/CNP job, but at a CNP-sized sensitivity
(50 mV here) the low-R SC-candidate channel (4T 30-31) floors to ~0 across ~88% of
the metallic plane (X3 < ~0.5 uV). Worth a one-line note in the recipe that the
survey deliberately under-resolves the low-R candidate regions and the candidate
hunt belongs to the priors-aimed linecuts + candidate-sized-sensitivity zoom, not
the survey 4T map. (toploader, zf1, run 4.)

## 2026-06-25 ~03:25 — run 4 survey gatemap complete; (n,D) calibrated
Wall 3.9h (101x101, ~43 pts/min — matches the inherited ~0.31 s/pt anchor, NOT the
1.2 s/pt rig-card default; megasweep is ~4x faster per-point than a delay=1 1D sweep).
Verify clean. CNP fit (4T): c_tg/c_bg=0.844, 99.5% vs prior -> geometry cap ratio
confirmed; calibration contract written to device_card.md. 4T sensitivity-floored in
metallic regions (50 mV), so survey can't see an SC dome -> proceeding to const-D
n-linecuts at low-R sensitivity (D=-0.45/-0.55/-0.65, n past -4..-6e11 band).

TOOLING — hera-watch --channels k_tg_curr,k_bg_curr did not emit per-channel stats
for the gate-current (fp) columns (only role-tagged transport channels are digested);
had to read leakage from the live data/<id>/data.tsv directly. A --channels path that
digests any fp column (or a dedicated leakage view) would close the autonomous-leakage-
monitoring gap. Mid-run data.tsv (uncompressed) IS readable live — used it for the
leakage tripwire.

## 2026-06-25 ~04:24 — field-kill +side: NameError (mag vs magnet), no harm
RECIPE FIX — field-sweep-1d.md: the recipe writes the magnet parameter as `mag.field`
/ `mag` throughout (Recipe steps 3,7; examples), but the toploader template names the
AMI430 instance `magnet` (setup cell). A rig-variant note (or a `mag = magnet` alias
hint) would prevent the NameError. Caught pre-ramp (xp=mag.field is before the field
move) so field never moved (B=0.011 mT, gates at dome, dc205=0 — safe). Measured
magnet.ramp_rate()=1.0 mT/s (50 mT ramp ~50 s) for settle sizing.

## 2026-06-25 ~05:00 — INVESTIGATION COMPLETE: decisive superconductor
zf1 hosts a gate-tuned SC dome at n≈−5.0e11, D≈−0.64 V/nm. Full constellation:
Rxx→0 dome (run 8), Ic≈28 nA + switching peaks (run 9), B_c⊥≈1.8 mT field-kill /
ξ~0.4 µm (runs 10–12), Tc≈264–290 mK via Ic(T) collapse (runs 13–20). Verdict +
5-part contract in ana (cell 31). (n,D) cap ratio confirmed 99.5% (run 4) → device card.

State at handoff: heater OFF (probe cooling from ~486 mK), magnet at 0 (≤~10 mT
remanence from the field work), dc205=0, gates left at the dome point. Fridge will
take ~1 h to re-reach base.

TOOLING — the Flavor-B T-ladder as a single looped measure cell (ramp heater / read
heater.curr / interruptable_sleep dwell / bias sweep, ×8) ran clean start-to-finish
under append_exec; per-step files let me checkpoint Ic(T) live from disk. Good pattern.
FEEDBACK — none: operator gave the E1 grant and the full arc ran autonomously without
override or interrupt.
Open (deepen, not gate): Rxy@dome (QAH exclusion), Fraunhofer, BKT V∝I³, ±D-asymmetry
linecut, Tesla-field fermiology. Flagged in the ana verdict §4.
