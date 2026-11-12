## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — the stacking read

**Plan step 4.** Runs 6/7 (`sdh-spot-check`) gave strong SdH — onset 0.3–0.7 T,
many tones — but a 1D trace at one density **cannot** tell the three candidate
readings of run 6's comb (7.1 / 14.1 / 22.1 / 29.5 T) apart: a harmonic ladder
on a 7.4 T fundamental, the ABAB two-pocket pair (7.5 / 25.6 T predicted at
this n), or a single F_L = 33.1 T surface with spurious low-F residue. The fan
separates them because **frequency must be tracked against density**:

1. **F vs n.** Harmonics hold an exact integer ratio at *every* n; two real
   Fermi surfaces do not, and each extrapolates to F = 0 at its own band edge.
2. **Sum rule.** ΣF_i(n) = F_L(n) = |n|h/4e — a line through the origin of
   slope h/4e. This also audits the absolute n scale, which is still the 9.5 nm
   geometry prior (only the c_bg/c_tg *ratio* was calibrated on run 5).
3. **Fan origins.** Run 5 found a two-ridge mosaic under this contact pair
   (region B electron-doped by 0.43×10¹² vs A). Two convergence points in the
   fan confirm the mosaic and explain surplus tones; one says the surplus is
   real band structure. Expect a satellite family offset by ≈0.43×10¹² in n.
4. **ν-resolved gaps** at high B, and the electron–hole symmetry of the whole
   map (ABCB's band overlap breaks it hardest).

**Geometry.** Fast axis is the gate pair co-swept along the calibrated D = 0
line (`multimegasweep`), 89 columns at Δn = 0.05×10¹²; slow axis is the
magnet, ascending from where it sits — no dead traverse. The two edge columns
are placed **exactly** on the run-6 (+3.20) and run-7 (−1.20) spot densities,
so the fan's frequency extraction can be checked against those 10/20 mT 1D
records at the same (V_tg, V_bg). Gate excursion: V_tg −0.2770…+0.9836 V
(16 mV under the limit), V_bg −0.4650…+1.1661 V — inside the committed
validators, and the cell asserts it before any hardware moves.

**B grid.** Six cheap rows at 0.30–1.10 T catch the low-field convergence of
the fan lines, then 71 rows **uniform in 1/B** from 1.2 → 10.0 T: Nyquist
F = 47.7 T (covers F_L = 33 T and a 4th harmonic at 29.5 T with margin) and FFT
resolution ΔF = 1.36 T (the 22.1-vs-29.5 T question is a 7 T split — resolved
5×over). Uniform-in-1/B also front-loads the run: 62 of 77 rows land by 4 T.

**Settings.** `sr1` at 100 µV (10 kΩ full scale at 10 nA) — the ν = 0 state at
the CNP at 10 T is the one unknown resistance in the map and run 5's lesson was
to size for the ridge, not the flanks; SNR cost is nil because the noise is
device-limited (run 6: δR rms 64 Ω = 0.64 µV, vs an SR830 floor ~5 nV).
`fast_delay = 1.0 s` = 3.3τ at τ = 0.3 s / 24 dB — the same under-settled
choice run 5 made, and harmless here: the residual is a fixed ≲8 % admixture of
the *adjacent n column* at the same field, so it mildly smooths the n axis and
does not touch the B-direction FFT. Measured field is followed per point
(duplicate `magnet_field` column: index 1 is the setpoint, the follow is the
readback) so the 1/B axis is read-truth, not setpoints. Leak guard trips the
sweep at |I_gate| > 1 nA; the ±200 pA row-start flyback transient sits 5× under
it.

**Preconditions the cell asserts** (state it assumes but does not set):
T_sample 1.0–1.5 K, |B| < 0.05 T at the start, V_si = 0, gate NPLC = 1, PS
heater + output on, thermometry logfile live.

**Checkpoints** (all read off the armed `hera-watch` digest): **first 2 rows**
(~4 min) — signal across n, CNP visible near n ≈ 0, nothing railed, gate
currents at the pA floor; **B ≈ 2 T** (row 38, ~1 h 20 m) — partial re-form,
do the fan lines converge on one origin or two; **B ≈ 4 T** (row 62,
~2 h 20 m) — partial FFT vs n at ΔF = 1.71 T, which is already enough to call
one-surface vs two. Abort at any checkpoint that shows a dead or railed channel
or a featureless map; a truncated fan is still a complete fan up to that field.

**Ends at** B = 10 T with the gates parked at 0 V — the magnet is left high on
purpose (step 5 will use it; re-traversing costs 73 min).
