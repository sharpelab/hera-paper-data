## HERA — Step 4: Landau fan (`landau-fan-vti`), D = 0 electron side, n = +2.00 → +3.20e12, B 0.60 → 10.0 T

**Why this, now.** Runs 6/7 (Step 3, read in `_ana`) put the electron side clear of the hole
side — onset **censored at 0.30 T** (oscillations alive to the record's low edge) vs a
*measured* 0.71 T on the hole side, and the electron side reaches nominal +3.27e12 while the
hole side is capped at −1.27e12, i.e. permanently inside the investigation's near-CNP
exception regime. Run 6 resolved a coherent two-fundamental set — f_l = 7.11, f_h = 22.26,
with 2f_l = 14.22, f_h − f_l ≈ 15.4, f_h + f_l = 29.37 — whose pair **sums to 0.888 · F_L**,
one global density rescale inside the plausible band, partition 0.242, ratio 3.13. That is
ABAB-leaning on one density and **not a verdict**: the ratio sits within 4 % of exactly 3,
so a harmonic ladder on 7.11 T is not excluded by ratio alone, and the 29.37 T tone parked
on the rescaled F_L is precisely the symmetry-allowed breakdown/intermodulation confound the
investigation calls *expected*. Both are trajectory questions, so this fan is the
discriminator: across n = +2.00 → +3.20e12 the ABAB model ratio drifts **5.40 → 3.76** with
partition 0.156 → 0.210, the trilayer ML+BL overlay (binding adjacent-N check) sits at
48 → 19, and the harmonic null is pinned at exactly 3.00 / 0.250 at every column. The
per-column Luttinger sum f_l + f_h = 0.888 · F_L(n) is algebraic — no model — and a
one-density coincidence will not hold across 44 of them.

**Grid, floored (`landau-fan` step 1 — one fan, each lever at its floor).**
*B_lo = 0.60 T*: `sdh_onset` returned 0.30 T **censored**, a lower bound rather than a
measured die-off, so 0.60 T sits safely inside confirmed-oscillating field with no
low-field extension needed — and B_lo is the lever that pays twice (1/B span *and* n-axis
ray Nyquist ∝ 1/B_lo). *B_max = 10.0 T* = the session cap; under uniform-1/B sampling the
top 2 T costs ~2 % of the rows, and the high-B reach is what makes the mandatory
**F_L-tone-origin B-window split** resolvable (halves at δF = 1.28 T separate 22.26 from
29.37 T). *N_B = 157* → Δ(1/B) = 0.01004, F_Nyq = **49.8 T**: this clears not just
F_L(n_max) = 33.1 T but **2 × f_heavy = 44.5 T**, so the heavy tone's second harmonic
cannot fold back onto the heavy tone itself (N_B = 130 would fold it). *N_n = 44* →
Δn = 0.0279e12 = **2.08 points per LL ray** at B_lo, just over the ≥ 2 floor. δF = 0.638 T,
giving the ABAB partner **5.2 periods at the lowest column** rising to 11 at the top.

**Coverage trade, stated.** The fan excludes nominal n < +2.00e12. The floor is the
recipe's binding case — the partner tone at the *lowest* fan density needs ≥ 5 periods, and
at nominal 2.00 it has 5.17. Reaching down to +1.85e12 would need B_lo = 0.54 T
(N_B = 176 × N_n = 53) for **+1.5 h**, buying 0.15e12 of extra reach in the regime the
investigation tells you to design *away* from (below true |n| ≈ 1.8e12 the light pocket
empties and ABAB genuinely mimics an ABCA singleton). Also excluded: the hole side, priced
as non-decisive in run 7's cell and unchanged by anything here.

**Deviation from the spot check, called out.** `sr1` goes to **100 µV (10 kΩ FS)**, not the
spot checks' 50 µV. Both spot corners stayed ≤ 12 % of 5 kΩ, but neither visited this fan's
worst corner — **low n × high B**, where R ∝ 1/n stacks with the B-axis MR. Interpolating
run 5's R(B = 0, n = +2.0e12) = 73 Ω through run 6's 10× MR factor and the deeper ν ≈ 8
filling reached at 10 T puts that corner near 1.0–1.6 kΩ; 10 kΩ gives ~7× headroom where
5 kΩ gives ~3×. Clipping is the asymmetric failure — it flat-tops the high-B end of exactly
the low-n columns that carry the discrimination, and no window recovers it — while the cost
is ~0.3 Ω of quantisation against a 20–50 Ω oscillation. Frequencies, not amplitudes, carry
this read, so the amplitude discontinuity vs run 6 is not load-bearing.

**Direction.** The magnet sits at ~0 T, so the fan positions to 0.60 T (4.4 min) and then
**carries the field up itself** — every one of the 9.4 T of movement is recorded, no bare
traverse. Because B ascends and the record is uniform in 1/B, an interruption at any point
leaves an already-usable FFT record (stopping at 3 T still gives δF = 0.75 T), which is the
right failure mode for a 5-hour unattended run. It ends at 10 T with the gates at the run-6
spot density; the endpoint for the follow-on (LK mass split) is a decision for after the
data is read, not now.

**Preconditions this cell assumes but does not set** (asserted below, printed expected vs
actual): sample T at base and the worker logfile advancing; |B| < 20 mT at entry; V_si = 0;
gate NPLC integers at 1; PS heater on and output enabled; τ = 0.3 s at 24 dB/oct (the 1.8 s
fast dwell is 6τ — the recipe's per-column-FFT value, where 4τ would leave ~43 % of the
previous column's signal at this filter slope); Keithley `volt.step` = 5 mV, operator-owned
and only read here.

**Guards, live.** Gate-leakage trip at 1 nA (both Keithleys, per point, in the TSV not just
the plot); a **clip trip** at 95 % of full scale — 10 consecutive clipped points abort
rather than bank hours of flat-topped columns; and a temperature guard that aborts on 20
consecutive points above 1.8 K, since nothing else is watching the fridge for 5 hours.

**Checkpoints** (read off a backgrounded `hera-watch` digest, not the monitor PNG):
*first row* — signal present, no clip, leakage quiet, field readback at 0.600 T, and R across
the row tracking run 5's 73 → 56 Ω; *row ~80* (B ≈ 1.16 T, ~2.1 h) — per-column FFT on the
landed rows at δF ≈ 1.25 T, where the partner tone and the ratio trend must already be
visible, continue/adjust/abandon there; *row ~130* (B ≈ 3.0 T, ~3.7 h) — δF ≈ 0.76 T, full
tone set present and still no clipping as the worst corner approaches.
