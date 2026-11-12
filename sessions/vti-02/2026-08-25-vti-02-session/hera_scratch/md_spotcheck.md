## HERA — SdH spot check on the measured D = 0 line (investigation Step 3)

`recipe: measurements/sdh-spot-check.md`. First measurement of the session that
is *science* rather than calibration — everything before it existed to make this
one interpretable.

**The calibration is closed.** Run 6's back-gate rays give α_bg = 0.01850 V/(T·ν)
→ **dn/dV_bg = 1.307×10¹² cm⁻²/V** (6% slope scatter over 7 rays; implied
back-gate hBN 12.7 nm vs the card's 11.0). With run 5's top gate that gives

> **c_bg/c_tg = 0.832 (measured)** — against the geometry prior 0.864, and
> against the **0.58–0.67** the zero-field ridge slopes implied.

That agreement with geometry, and disagreement with the ridges, is the
independent confirmation that the zero-field ridges were never CNP lines. The
(n, D) frame is now data-grade in *both* lever arms — the
`cnp-and-dline-calibration` Step-5 upgrade, completed.

Run 6's ray **intercepts** are much weaker than run 5's (3/7 within tolerance,
V_CNP(bg) = +0.039 ± 0.034 V vs run 5's ±0.008), which is expected: this cut
sweeps D from +0.16 to −0.24 V/nm, so the gap opens along it and LL character
changes. **Slopes are robust to that, intercepts are not** — so the lever arm is
taken from run 6 and the CNP from run 5.

**Design densities, and the range verdict.** D = 0 is V_bg = V_tg/0.832, and
along it n = 3.14·V_tg − 0.032 (10¹² cm⁻²), giving a reachable window of
**n ∈ [−0.97, +3.11]×10¹² cm⁻²**. So the **electron side reaches the
|n| ≳ 2–3×10¹² window where the ABAB and ABCA templates separate; the hole side
does not** — it tops out at −0.97×10¹², inside the exception regime where the
ABAB pair collapses toward a single tone near 0.95·F_L and genuinely mimics an
ABCA singleton. Five points are taken: **n = +1.8, +2.2, +2.6, +3.0** on the
electron side (spanning into the design window so the n-dependence of any tone
is visible), plus **n = −0.9** so the hole side gets its spot check as the
investigation requires — reported for what it is, a range-limited look, not a
comparable measurement.

**All five ride one traverse.** B is the slow axis and the five (V_tg, V_bg)
pairs are the fast axis, so the magnet ramps once per field row and every
density is sampled at every field — five spot checks for one magnet traverse
instead of five.

**Sampling, computed not guessed** (recipe Step 2). F_L = (h/4e)·n at the
largest |n| is ≈32 T. The magnet is blocking and rate-limited, so the recipe's
blocking branch applies: sample **uniformly in B** with ΔB = Δ(1/B)·B_lo², taking
Δ(1/B) at Nyquist×3 on F_L. B runs 1.5 → 6.0 T. B_lo = 1.5 rather than lower
because ΔB scales as B_lo² and a deeper floor multiplies the row count — the
onset region below 1.5 T is already characterised by runs 5/6, which show
oscillations developing by 1 T and minima reaching 6.6 Ω at 1.5 T.

**`sr1` re-ranged to 100 µV.** The 500 µV range used for the fans put the
metallic signal at ~2% of full scale, which is exactly the recipe's grainy-FFT
failure mode ("a signal at a few % of range is coarse-ADC digitized"). Away from
the CNP R_xx runs 50–300 Ω, so 100 µV puts full scale near 2 kΩ and the signal
at ~10% — quantisation drops to ~0.03 Ω, well under any oscillation amplitude
worth resolving.

**Stated assumption:** D_offset = 0. No feature has yet been found that
physically locates D = 0 on this device, so "D = 0" here means "the
capacitance-symmetric line through the measured CNP". The recipe requires this
be said out loud rather than assumed silently.

**Carried caveat:** R_xx includes a ~1% R_xy admixture (negative R at deep
minima, scaling with h/νe² as expected), and every run this session is
single-polarity, so no ±B symmetrisation is possible. For frequency *content*
this is benign; for any amplitude-based claim it is not.

**Cost:** traverse 4.5 T / 0.137 ≈ 33 min, plus one 3 s magnet settle per row,
plus the grid. **ETA 1h10m**, ending at 6 T.
