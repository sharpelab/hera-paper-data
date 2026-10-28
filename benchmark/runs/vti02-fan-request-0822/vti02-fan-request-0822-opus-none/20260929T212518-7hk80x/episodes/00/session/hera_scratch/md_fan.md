## HERA — Step 4: Landau fan (`landau-fan`) — B × n at D = 0, the measurement that decides the stacking call

**Why now, and why this is the decisive step.** Runs 6/7 (analysed at the handoff) show
strong SdH from ≲ 1 T to 10 T — 80–600 % peak-to-peak of the local background, SNR 20–120 —
but they are **multi-tone and harmonic-rich**, and a single-density FFT cannot tell a real
Fermi surface from a harmonic, from the run-5 A/B mosaic, or from a window artefact. (My
first pass on runs 6/7 reproduced that trap: `sdh_fft` windows whose 1/B span sets a coarse
bin grid put "peaks" at identical frequencies in two runs at *different* densities — 5.0 /
22.5 / 45.0 T in both. Lomb–Scargle on the native samples gives run 6: 30.0, 8.0, 22.2 T
with F_L = 33.1 T; run 7: 9.0 T with F_L = 12.4 T plus content above F_L that can only be
harmonic.) The fan resolves all three ambiguities at once, because it measures **F vs n**:

- real subbands → lines **through the origin**, slopes summing to 1 (ABAB/ABCB = two, ABCA = one);
- the run-5 A/B mosaic (two domains, same lever arms, Δn = 0.43×10¹²) → lines of the **same
  slope, offset** by ≈ 4.4 T — the one confound a fixed-density FFT cannot see through;
- harmonics → exact integer multiples that scale with the parent.

It also self-calibrates: LL gap slopes dn/dB = νe/h give integer ν, fixing the **absolute n
scale**, which is currently only the 9.5 nm geometry prior (run 5 calibrated the *ratio*
c_bg/c_tg = 0.773, not the scale). Every F/F_L fraction quoted in the call depends on that.

**Geometry.** Slow = B, 150 rows: 5 low-field context rows (0, 0.2, 0.4, 0.6, 0.8 T) then
**145 rows uniform in 1/B from 1 → 10 T**. Uniform-in-1/B is what `sdh_fft` consumes without
resampling: over [1, 10] T, dF = 1.11 T and Nyquist = 80 T — deliberately above 2·F_L(3.2×10¹²)
= 66 T, so the second harmonic cannot alias onto the fundamental (the failure mode that
poisoned my first read of run 6). Fast = **n = −1.20 … +3.20×10¹² at D = 0**, 111 points at
0.040×10¹², co-swept (V_tg, V_bg) = (−0.2770, −0.4650) → (+0.9836, +1.1661) V. The full
realized D = 0 window inside the validators is −1.27 … +3.27; the ends are pulled in to land
**exactly on the run 6 and run 7 spot densities**, so the fan's first and last columns
reproduce those runs as a built-in consistency check. That n lever arm (a factor ~3.7 in |n|)
is what separates "different slope" from "same slope, offset" — it is the reason the fan is
wide rather than cheap.

**Dwell, and the one trade I am making.** fast_delay = 0.5 s against τ = 0.3 s / 24 dB/oct,
i.e. ~1.7τ vs run 5's 1.0 s (3.3τ). A 4-pole filter's group delay (~4τ = 1.2 s) is then ~2.4
points of **uniform lag** — a constant shift of ~0.10×10¹² in n, identical on every row
because every row sweeps the same direction at the same rate. A constant n-shift is
degenerate with n_offset, which this fan re-derives anyway from the LL slopes, so it does not
touch a single slope, frequency or fraction. It buys ~50 min. **The B = 0 row measures it:**
that row is a direct repeat of run 5's D = 0 cut, so the CNP position difference *is* the lag.

**Sensitivity.** Fixed 100 µV = 10 kΩ FS at 10 nA, no autorange mid-row. Observed maxima:
530 Ω (run 6 at 10 T), 587 Ω (run 7 at 10 T), 240 Ω (run 5 CNP at B = 0) → ~17× headroom.
Per the run-4 lesson in `session_notes` I am sizing to the *worst corner*, not the 1D peak;
here the unknown corner is R_CNP at high B. The CNP column sits 28 % into every row, so
R_CNP(B) is watchable from row 1 — see the 2 T checkpoint. A soft rail watch warns once per
row above 90 % FS but does **not** abort: a railed CNP column costs the CNP read, not the
F-vs-n read that carries the call. The leak guard (>1 nA either gate → interrupt) stays on.

**Price** (from run 5: 1.10 s/pt at fast_delay 1.0 → ~0.12 s of stepping + reads per point;
run 6: 3.09 s/pt of magnet overhead on top of the bare 0.137 T/min): 16 650 points × 0.62 s
= 2.9 h + 150 row turnarounds (~3.5 s flyback + 2 s slow_delay + 3 s magnet settle) ≈ 0.35 h
+ 73 min of ramp = **4.4 h nominal**; quoted at 5h10m because this session's actuals have run
5–10 % over even the upper bracket. Ends at **10 T with the gates at n = +3.2×10¹²** — no
re-traverse; the field stays up for whatever step 5 turns out to be, and close-out brings it
down once at the end.

**Checkpoints.** (1) *First rows, ~4 min* — B = 0 row vs run 5's D = 0 cut: CNP position
(= the lag measurement) and R_CNP ≈ 240 Ω; no rail, no leak, R scale sane. (2) *~2 T,
≈ 1.2 h* — are LL gaps resolving; extrapolate R_CNP(B) toward 10 T and abort/re-size if it
is heading past ~8 kΩ; first partial F-vs-n on the landed rows. (3) *~5 T, ≈ 2.8 h* — tone
count and slopes from the partial fan: if one tone tracks F_L across all n the call is
already ABCA and the remaining rows only sharpen it; if two lines through the origin appear,
likewise for ABAB. Continue / adjust / abandon, with the price of each call.

*Note (rig card): interrupting this cell stops the sweep but **not** the magnet — the supply
keeps ramping to its last setpoint. Aborting a ramp is hands-on-the-instrument, and any abort
is followed by re-reading the actual field before the next move.*
