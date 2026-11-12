## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n = −1.27 … +3.25×10¹², B 0 → 10 T

**Why this, and why it is the decisive step (plan step 4).** The spot checks
(runs 6, 7) did their job — SdH is strong here, onset **0.3–0.7 T**, minima
reaching R ≈ 0 — but they cannot settle the stacking question, because at a
*single* density a second Fermi surface and a harmonic of the first are the
same thing to an FFT. Run 6 (n = +3.20×10¹², F_L = 33.1 T) is exactly that
trap: `sdh_onset` finds 7.1 T plus 14.1 / 22.2 / 29.5 T and flags the latter
three as 2×/3×/4× of 7.1 T, while 7.1 + 26 ≈ F_L would instead read as a
two-band (ABAB-like) pair. Both stories fit one density. **Sweeping density
breaks the degeneracy:** a real Fermi surface carries a fixed share of n, so
its frequency runs **F = α·n·h/4e — a straight line through the CNP with its
own slope**; a harmonic is pinned to an exact integer multiple of its parent at
*every* density. One run therefore answers (a) one branch or two, (b) the split
α₁:α₂ if two, and, straight off the image, (c) the Δν step of the fan lines and
the ν-width of the gapless region flanking the CNP — the Landau-level
degeneracy. That is the discriminator set the campaign needs.

**Grid.** Fast axis is the **D = 0 line** from the run-5 calibration (c_bg/c_tg
= 0.773, c_tg = 2.796 mF/m² from the 9.5 nm prior, n_offset −0.089×10¹²,
D_offset −0.013 V/nm), co-swept (V_tg, V_bg) via `multimegasweep` — 164 points
uniform in n over the **full range the validators allow**, n = −1.27 …
+3.25×10¹² (V_tg −0.297 → +0.998, V_bg −0.491 → +1.185; both ends land 2 mV
inside the committed limits, and |D| ≤ 5×10⁻¹⁷ V/nm by construction). Slow axis
is **B = 0 → 10 T uniform in 0.25 T, 41 rows**. Uniform in B, not in 1/B: the
fan image wants even field rows, and the periodicity read here is taken
**along n at fixed B** (Δn = 4eB/h per band), which the 0.0277×10¹² density
step samples at 6.9 points per Δν = 4 at 2 T and 35 at 10 T. Runs 6/7 already
own the dense-1/B axis at two densities, so this run does not need to.

**Coverage trade, stated.** Fan-line resolution on the density axis needs
B ≳ 1.5 T — at 0.5 T a Δν = 4 spacing is 1.7 fast points and the row is
aliased. The six rows below 1.25 T are therefore the B = 0 reference and the
low-field magnetoresistance background, not fan structure; the decisive image
is the 35 rows from 1.5 to 10 T. Buying the low-B rows properly would mean
halving the density step and doubling the run. Not bought.

**Sensitivity — 200 µV (20 kΩ full scale).** Measured, not guessed: the
point-to-point noise on `sr1_X` is **≈ 47 nV in runs 5, 6 and 7 alike**
(100 µV, 50 µV, 50 µV ranges) — it is an *absolute* floor, not a fraction of
range, so buying headroom is free. 47 nV at the 9.9 nA measured bias is
**4.7 Ω**, against oscillation amplitudes of ~100 Ω. The headroom is for the
CNP column at high field: R_CNP(B = 0, D = 0) ≈ 330 Ω (run 5), and run 7
reached 587 Ω and climbing at 10 T a mere 1.2×10¹² from the CNP, so a few kΩ at
ν = 0 and 10 T is plausible. This was the failure that killed run 4 — the
session-notes lesson was *size to the corner of the window, not to the 1D
peak*, and ν = 0 at 10 T is this window's corner.

**Dwell — `fast_delay = 1.0 s`, knowingly under the step-settling floor.**
τ = 0.3 s at 24 dB/oct, so 7–10 τ ≈ 2–3 s is the floor for a *step*. This axis
does not step: consecutive points move V_tg by 8 mV, so the filter acts as a
lag of ≈ 4 τ = 1.2 s ≈ 1.2 fast points ≈ 0.03×10¹² in n — a uniform shift along
the fast axis, identical every row, not a contrast loss, because the features
of interest are ≥ 10 τ wide in sweep time (a ν = 4 gap at 2 T is 6.9 points
≈ 8 s). Paying the full step floor instead would add ~1 h 50 m for a
correction smaller than one pixel. The lag is noted here so it is not
mistaken later for a calibration offset.

**Price** (calibrated on *this* session, run 5 — 4158 points at the same fp set
and `fast_delay = 1.0`, measured **1.17 s/pt** all-in including flyback):
6724 points × 1.17 s = 131 min, plus the 10 T traverse at the driver's fixed
0.137 T/min = 73 min, plus 41 × 3 s magnet settle ≈ 2 min → 3 h 26 m computed,
quoted with the session's observed 5–10 % overrun. Ends at **B = 10 T with the
gates at the electron end** — deliberate: the D-dependence step (plan step 5)
or any follow-up spot check should ride the field down rather than re-traverse.

**Preconditions** (assumed, not set): thermometry worker live, T_sample
1.0–1.5 K, **B ≈ 0** (the grid starts there), V_si = 0, persistent-switch
heater on and output enabled. The cell stops before the magnet moves if any
fail.

**Checkpoints** — all three read off the backgrounded `hera-watch` digest:
1. **Rows 0–2** (B = 0, 0.25, 0.5 T; ~12 min in). R(n) must reproduce the run-5
   D = 0 cut — CNP peak ≈ 330 Ω at n ≈ 0 — with no rail, sustained |I_gate|
   well under 1 nA, T_sample flat, and the noise floor ≈ 5 Ω. A rail or a
   missing CNP peak here kills the run in the first minutes.
2. **B ≈ 2.5 T** (row 10, ~1 h). Fan lines resolved? They must index to integer
   ν. If there is no resolvable structure the density step is too coarse —
   that is a re-grid, **not** a stacking conclusion.
3. **B ≈ 6 T** (row 24, ~2 h 15 m). CNP-column rail check, and the first real
   test: FFT along n at fixed B, one branch or two.
**Leak guard**: trips on **3 consecutive** points over 1 nA on either Keithley,
not one — the session notes recorded the row-start flyback transient
(−200/+120 pA around a −92 pA median) as a false-positive source, and a
single-point trip would throw away a 3½ hour run.
