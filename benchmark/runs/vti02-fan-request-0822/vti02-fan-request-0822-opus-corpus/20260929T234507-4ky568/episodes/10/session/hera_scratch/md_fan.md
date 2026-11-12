## HERA — Step 4: Landau fan (`landau-fan-vti`), electron side, D = 0, n = 1.0 → 3.2×10¹², B 0.8 → 10 T

**Why this fan, and why now.** The two spot checks (runs 6, 7) are read in ana. The
electron spot (run 6, n = +3.2×10¹², F_L = 33.1 T) carries two candidate fundamentals —
**7.3 T** and **≈ 29–30 T** — each with its own harmonic comb (29.4 → 58.3 → 90.5 → 118.2 T;
7.3 → 14.8 → 22.3 T). Read as a pair they sum to 36.7 T = 1.11·F_L (inside the ±10–15 %
lever-arm prior) and partition 0.20 / 0.80, close to the model's ABAB 0.22 / 0.78 at this
density; read as a singleton the 29.4 T tone sits at 0.89·F_L, which the same scale prior
also permits — and the 7.3 T tone then has no home. **One column cannot settle it**
(`tetralayer-stacking-fs-count` Step 5): the discriminator is the *trajectory* of the tones
across density, which is scale-free. That is this fan.

**Side and window.** Electron side, per the investigation's "the fan follows the cleaner
side": run 6's oscillations are censored at the low edge of its sampling-valid leg
(onset ≤ **0.85 T**, tracker SNR 100+), while the hole spot (run 7) sits at |n| = 1.2×10¹²
— squarely in the near-CNP exception regime the investigation says to design *away* from,
with a measured onset of 0.71 T and close, balanced tones. n_max = **3.2×10¹²** is the
hard ceiling: the D = 0 line leaves the TG validator at +3.27×10¹². The window runs down to
**1.0×10¹²** because the model's ABAB heavy-tone fraction drifts **0.945 → 0.779** over
exactly that span while ABCA's stays pinned at 1.000 — a *scale-free* discriminator, and the
longest lever available under the n_max cap.

**Design numbers** (`landau-fan` step 1, computed not eyeballed; model F(n) from
`hera/models/tetralayer_fs_count`):
- **B_lo = 0.8 T** — at the measured onset bound (0.85 T, censored: a lower bound, not a
  measured die-off — hedge carried into the read). **B_hi = 10 T** = the session cap.
- **1/B record = 1.150 1/T → δF = 0.87 T.** Separates the 7.3 T partner from the 5.4 T
  model value at n = 2.6×10¹² (≥ 2·δF), and the heavy tone (22–26 T) from F_L (33 T) with
  ~10× margin.
- **Δ(1/B) = 0.00752 1/T → 154 rows**, Nyquist at **2.01·F_L(n_max) = 66.5 T**. This is
  *deliberately 2× the recipe floor*: run 6 shows real harmonic content at 58/90/118 T at
  16 % of the dominant, and at the bare 1/(2F_L) floor the 2nd harmonic aliases straight
  back onto the tone band. At this spacing the 2nd harmonic lands correctly (the harmonic
  screen can see it at exactly 2f) and the 3rd/4th aliases fall at ~44 and ~15 T, where
  their *backwards* n-dependence exposes them.
- **n-axis: 60 columns**, step 3.73×10¹⁰ cm⁻² = **2.08 points per LL ray** at B_lo (the
  recipe's ≥ 2 floor, with margin).
- **Dwell 1.8 s = 6τ** (τ = 0.3 s, 24 dB/oct — read from the instruments, not assumed);
  the recipe's per-column-SdH-FFT value. Under-settling buries the weak partner tone, which
  is the tone the whole call rests on.
- **Sensitivity 100 µV = 10 kΩ full scale** at 10 nA, fixed for the fan. Worst corner is
  low-n × high-B: n = 1.0×10¹² reads 117 Ω at B = 0 (run 5) and run 6's MR factor at
  n = 3.2 is 10×, so ≈ 1.2–2 kΩ with SdH maxima on top. **Coverage trade, stated:** this
  costs resolution at the *clean* corner — n = 3.2×10¹², B = 0.8 T sits at 0.6 % of full
  scale (run 6 ran the same corner at 1 % and returned SNR ≈ 100, so ≳ 50 expected) — but
  clipping at the low-n corner is flat-topping, unrecoverable by any windowing, and would
  destroy the exact columns the trajectory lever needs.

**Cost floor.** 154 × 60 = 9240 points. Grid 5.5 h (measured 1.17 s/pt from run 5's
gatemap at fast_delay = 1.0, i.e. ~0.25 s/pt overhead on top of the dwell) + 1.12 h bare
traverse + 6 min positioning. This is the *one* fan: n_max is validator-capped, B_lo is at
the measured onset, N_n is at its ray-Nyquist floor, and the B sampling is the harmonic-
alias floor — no lever has slack left except the claim window itself.

**Direction.** The magnet sits at 0 T after the handoff, so the fan **ascends** 0.8 → 10 T
and ends at 10 T, where the investigation's next step (the LK mass split, Verify) can ride
back down rather than re-traverse.

**Preconditions the cell asserts (assumed, not set):** thermometry worker live and the
logfile advancing; T_sample 1.0–1.5 K; V_si = 0; PS heater on and output enabled; gate
nplci = 1/1; sr1 τ = 0.3 s at 24 dB/oct (the basis of the 6τ dwell); B_vec inside the
SAFETIES field cap and both gate vectors inside their validators. A per-point 1 nA leak
guard interrupts the sweep.

**Checkpoints.** First rows — leakage, railing, a dead or flat channel, sensitivity sanity
(expect |Rxx| ≈ 60–120 Ω across the n-line at B ≈ 0.8 T, no SdH yet). Then periodically: a
partial per-column FFT on the landed rows once the record reaches B ≈ 3 T (~1/B span 0.9,
δF ≈ 1.1 T) — enough to see whether the 7 T tone tracks its own Onsager curve or sits at a
fixed multiple of the dominant. Abort criteria: any column flat-topped at 10 kΩ, the gate
current sustained over 1 nA, or no oscillation content anywhere by B ≈ 4 T.
