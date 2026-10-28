## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — the stacking discriminator

**Why this, now (plan step 4).** Runs 6 and 7 gave huge, clean SdH — 241 Ω pk-pk
(73 % of R) above 7 T on the electron side, onset ≲ 0.3 T — but they cannot
settle the stacking. Run 6's FFT over 1.5–10 T (δF = 1.76 T) has peaks at
**7.06 / 15.88 / 22.94 / 30.0 T**, and two incompatible readings fit inside that
resolution:

- **(a) one Fermi surface** at F = 7.06 T plus its 2nd/3rd/4th harmonics
  (14.1 / 21.2 / 28.2 T) — the ABCA-like "single band" picture; but 7.06 T is
  only 21 % of the Luttinger frequency for the nominal density, so it would
  also mean the calibration or the degeneracy is badly wrong;
- **(b) two Fermi surfaces**, F₁ = 7.06 and F₂ = 22.94 T, with the
  magneto-intersubband combinations F₂−F₁ = 15.88 and F₂+F₁ = 30.0 T — the
  **ABAB** signature (two decoupled bilayer-like bands), with ΣF = 30.0 T
  giving n = 2.90×10¹² cm⁻² against the 3.20×10¹² geometry prior (a 10 %
  over-estimate, which is exactly the uncalibrated-scale residual from run 5).

Every peak in (b) sits ~1.8 T — **one resolution element** — above its harmonic
counterpart in (a). No single-density measurement can separate them. A fan can,
and this is the whole reason for the run.

**The decisive test this fan runs.** Sweeping n while tracking every tone
separates the three possibilities by the *slope* of F vs n, which is model-free:

| the tone is… | F(n) track |
|---|---|
| a real Fermi surface | linear through the origin, fixed fraction of ΣF |
| a genuine harmonic | exactly k × the fundamental's track (slope k×) |
| an **aliased** harmonic (F > F_Nyq) | folds — **negative** slope vs \|n\| |

Alongside it, two free results: the **Luttinger sum rule** ΣFᵢ = \|n\|·h/4e read
as a line over 89 densities replaces run 5's geometry-prior density scale with
an in-session absolute calibration; and the **LL gap-line filling sequence** at
B ≳ 2 T gives the degeneracy directly, plus whether the D = 0 CNP gaps at high
field (it does not at B = 0 — run 5 put the D = 0 CNP peak below 330 Ω).

**Design.** Slow axis is B, because the magnet blocks at 0.137 T/min and must
never be re-traversed; fast axis is (V_tg, V_bg) co-swept along the D = 0 line
via `multimegasweep`. The **110 field rows are uniform in 1/B** (`field_invB`),
not in B: SdH is periodic in 1/B, so this hands `sdh_fft` an already-even record
with no resampling, puts the sampling where the LL lines are dense, and makes
the gap lines vertical in the (ν, 1/B) view. Over 0.7 → 10 T that gives
**δF = 0.75 T** — enough to split 7.06 from 21.2 *and* from 22.94 — and
**F_Nyquist = 41 T**, above every expected fundamental (ΣF ≤ ~34 T). The fast
axis runs n = −1.20 → +3.20×10¹² at Δn = 0.05×10¹², whose **endpoints are
exactly the run 7 and run 6 spot settings** — the fan's first and last columns
reproduce those runs, which is the drift check for a 5 h sweep.

**Coverage trade, stated.** (i) D = 0 only — no displacement-field axis. That
is deliberate: D = 0 is where the two-band partition is cleanest, and the
D-dependence (ABCA gaps symmetrically, ABCB asymmetrically) is plan step 5,
which rides the magnet back down from 10 T and costs ~1 h instead of the ~40 h
a (n, D, B) volume would. (ii) Nothing below 0.7 T: going to 0.4 T would add
~55 rows (~1.7 h) to buy δF = 0.42 T we do not need, and would drop F_Nyquist
to 29 T, *below* the fundamentals — worse, not better. (iii) Δn = 0.05×10¹²
resolves ν = 4 gap lines only for B ≳ 1 T; below that the fan is read through
the per-column FFT, not by eye. (iv) Second harmonics (2ΣF ≈ 60 T) do alias —
but they fold to a *negative* slope vs n, so the table above catches them.

**Preconditions checked before anything moves** (the cell asserts and prints
expected vs actual): T_sample 1.0–1.5 K, B ≈ 0 T, V_si = 0, Keithley NPLC = 1,
persistent-switch heater on and output enabled. Sensitivity is fixed at
**sr1 200 µV = 20 kΩ full scale** for the whole fan — ~34× the largest R in
runs 6/7 and ~60× the B = 0 CNP peak, so the CNP column has room to grow at
10 T (run 4's lesson: size for the map's worst corner, not the 1D peak).
A 1 nA leak guard interrupts the sweep; a soft-rail counter logs without
aborting. On any exit the `finally` parks both gates at 0 V; the field is
**left at 10 T** for step 5.

**Price** (calibrated on run 5: 0.10 s/pt read + fast_delay, 4.6 s/row
turnaround): 110 rows × 105 s = 3.2 h of points, + 68 min of magnet ramp +
5 min of settles = **≈ 4 h 30 m**, and the rig card's "actuals run 5–10 % over"
rule puts the headline at **≈ 4 h 50 m**. Ends at B = 10 T, gates at 0 V.

**Checkpoints** (armed on `hera-watch data --next --follow`):
1. **First rows** (~2 min, B = 0.70 T) — R across the line should run ~150 Ω at
   n = −1.20, a few hundred Ω at the CNP, ~55 Ω at n = +3.20 (runs 6/7 numbers
   at low field); no rails, no leakage, field readback tracking the setpoint.
2. **~1 h** (B ≈ 1.1 T) — are LL gap lines forming in the landed rows?
3. **~2 h 30 m** (B ≈ 2.2 T) — re-form the partial fan and run the per-column
   FFT on the landed 1/B range; check the sum rule and the F(n) slopes early.
   **Abort** if rails cover >10 % of the map, if leakage trips, or if the
   endpoint columns disagree with runs 6/7 (device drift).
