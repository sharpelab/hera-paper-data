## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — the stacking discriminator

**Why now.** Runs 6/7 (`sdh-spot-check`) gave strong, clean SdH on both carrier
signs — onset ≲ 0.7 T, minima down to ≈ 0 Ω, |Rxx| ≤ 590 Ω at 10 T — but at
*fixed* n they are degenerate between the three readings that matter: the
electron-side ladder (FFT 7.8 / 14.4 / 22.2 / 30.0 T, minima spacing
Δ(1/B) ≈ 0.033 → one ~30 T periodicity with a 4-grouped amplitude modulation)
fits harmonics of a single frequency, an ABAB two-band pair, and a
degeneracy-resolved single band equally well. A fan breaks all three at once:
Landau gaps are straight rays n = νeB/h through the CNP, so their **slopes give ν
outright** — independent of the still-uncalibrated 9.5 nm geometry prior on c_tg
— and with ν in hand the degeneracy step (Δν = 1/2/4/8), the number of ray
families, whether they cross, and the zero-LL step across the CNP all read
directly off the map. It also finally pins the absolute density scale.

**Both regions in one fan.** Runs 0–3 and 5 found two CNPs in series on B_1−B_2
(region B electron-doped by 0.43×10¹² vs A). On this fast axis region A's CNP is
at n = 0 (fast index ~73) and region B's at n ≈ −0.43×10¹² (index ~49) — both
inside the window, so one fan carries an independent ray family and CNP step for
each, which is what the per-region output contract needs.

**Geometry.** Slow = `magnet.field`, 0 → 10 T, 41 rows at 0.25 T (the magnet
blocks per row; B must be the slow axis). Fast = (`k_tg.volt`, `k_bg.volt`)
co-swept along the run-5 D = 0 line, 261 points, V_tg −0.2999 → +0.9999 V at
**5.00 mV = the Keithley step** (no sub-step pacing), V_bg −0.4946 → +1.1872 V,
n = −1.280 → +3.257×10¹² at Δn = 0.0175×10¹². That resolves Δν = 1 with ≥ 2
points down to B ≈ 1.4 T and with ≥ 7 points above 5 T; the Δν = 4 spacing is
never marginal. The D = 0 line is TG-limited at **both** ends — this is the whole
accessible D = 0 window, not a chosen sub-range.

**⚠ One departure from operator-set state: `sr0`/`sr1` τ 0.3 → 0.1 s** (filter
slope untouched at 24 dB/oct). Run 5's gatemap dwelt 1.0 s at τ = 0.3 s / 24 dB —
that is 3.3τ, i.e. a 4-pole filter only ~40 % settled, tolerable for a ridge
*slope* read but not for LL minima 3–7 points wide. At τ = 0.1 s the same 1.0 s
dwell is 10τ (~1 % settled) at √3 more noise ≈ 0.5 Ω at the 10 nA bias —
negligible against 10–500 Ω features, and 2f/line rejection stays ≥ 58 dB at
13.777 Hz. **τ is left at 0.1 s after this run**; later cells must re-read it, not
assume 0.3. Zack — veto by interrupting if you want it back at 0.3 (that costs
3× the dwell, i.e. ~14 h, so the alternative is a coarser fan).

**Sensitivity and the rail.** `sr1` fixed at 100 µV = 10 kΩ FS at 10 nA (run 5's
proven setting for a gate sweep crossing both CNPs): 19× headroom over the 530 Ω
maximum seen at 10 T away from the CNP, ~4× over the largest B = 0 CNP peak.
Stated trade: if a ν = 0 insulator develops, the CNP *column* can still rail at
high B. The guard **counts and reports soft clips but does not abort** — the ray
structure away from the CNP is unaffected, and the field at which clipping starts
is itself a ν = 0 onset read. The ν = 0 state gets its own high-sensitivity 1D cut
on the ride-down (plan step 5), which costs ~35 min over the 10 → 0 T ramp the
session needs anyway.

**Coverage trade.** D = 0 only. A finite-D fan is the ABCA-vs-ABAB tiebreak if the
families come out ambiguous, but it is another ~5 h and would be flagged as a
detour; run 5 already carries R_CNP(D) at B = 0 (240 Ω → 2.4 kΩ by D ≈ +0.25 V/nm).
B rows at 0.25 T rather than 0.1 T: rays are straight, 41 rows fit slopes fine,
and 0.1 T would cost ~9 h.

**Price** (calibrated on run 5, 4158 pts in 81.1 min = 1.17 s/pt at fast_delay 1.0,
nplci 1; and on runs 6/7, 3.05 s of magnet settle per field point over the bare
0.137 T/min ramp): 10 701 points × 1.17 s = 3 h 29 m, + the 10 T traverse 1 h 13 m,
+ 41 row turnarounds (magnet settle + slow_delay + gate flyback ≈ 9.5 s) 6 m
= 4 h 48 m, quoted with the session's standing 5–10 % over-run margin.

**Preconditions the cell asserts** (it sets none of them): T_sample 1.0–1.5 K with
a live logfile, |B| < 0.05 T, V_si = 0, nplci 1/1, both Keithley `volt.step` =
5 mV, PS heater on and output enabled. Every setpoint is checked inside the
committed validators before any hardware moves; the validators remain the backstop.

**Checkpoints** (`hera-watch`, armed before the cell runs): first 2 rows — signal
level, clipping at the two CNPs, gate currents at the pA floor, both CNP dips
present; then every ~8 rows for ray continuity, with an interim ν read at B ≈ 5 T
(row 21). **Abort** if a gate leaks (>1 nA, automatic), if the map is featureless
away from the CNPs by 5 T (then the read is T_e/resolution-limited and the fan is
not the right spend), or if clipping spreads beyond the CNP columns.

**End state:** field left at 10 T (never a free re-traverse), gates parked at 0 V,
τ at 0.1 s. The ride-down is plan step 5.
