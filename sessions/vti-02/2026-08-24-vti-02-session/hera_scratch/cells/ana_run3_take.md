**Read:** this is the measurement the stacking call rests on, and it says three things.

**1. A displacement field opens a gap — 10.4×.** R at neutrality goes from **296 Ω** at
D ≈ 0 to **3074 Ω** at D/ε₀ = +0.31 V/nm, rising steeply through 0.1–0.2 V/nm and then
saturating above ~0.23 V/nm. **This excludes ABAB.** A Bernal tetralayer is a
band-overlapped semimetal: displacement field gaps each bilayer-like subband but shifts
them relative to one another, so the overlap survives and the CNP stays conducting. A 10×
insulating rise is not that.

**2. The gap minimum sits at D = 0 — the stack is inversion-symmetric.** The R_CNP minimum
is at **D/ε₀ = 0.000 ± 0.008 V/nm** (argmin −0.008, parabolic fit on log R +0.008), and it
is robust: pushing the measured c_tg/c_bg by ±1σ moves it by under 0.001 V/nm. Folded about
that minimum the two branches lie on top of each other — R(+D)/R(−D) = 1.07, 1.01, 1.03,
0.96 at |ΔD| = 0.02, 0.04, 0.06, 0.08 V/nm, against a ~3 % per-point noise floor.
**This disfavours ABCB**, which lacks inversion symmetry: its built-in D = 0 gap is closed
by a field of one particular sign, so its R_CNP minimum must sit at finite D. Nothing here
is displaced by more than 0.008 V/nm out of a 0.39 V/nm range.

Together: **ABCA (rhombohedral)**.

**3. The session's own gate calibration.** The CNP-line slope over 26 unambiguous rows gives
**c_tg/c_bg = 1.2737 ± 0.0470**, ~10 % above the geometry prior's 1.1579 — within about 2σ,
but the measured value is what every subsequent cell uses to define the D = 0 line. The
*absolute* scale still rests on the prior; the Landau fan is what will fix that.

**Three honest limits on this evidence.**

- **The −D lever arm is only 0.26 of +D.** Negative D at neutrality needs V_tg < 0, and the
  provided top-gate limit stops at −0.3 V — an operating limit the session brief bans me
  from probing. So symmetry is demonstrated over |D| ≤ 0.08 V/nm, not over the full range.
  An ABCB asymmetry that only develops beyond that would not be visible here.
- **Seven rows have a double-peaked neutrality region**, all at low |D| — the same structure
  run 1 showed. Those rows sit squarely in the window used for the symmetry test. It is
  most likely two areas of slightly different doping between the B_1–B_2 probes; that the
  branches still fold cleanly argues it is not corrupting the result, but it is the reason
  the peak extraction is parabolic and the line fit uses only single-peaked rows.
- **The saturation above 0.23 V/nm is not what a clean growing gap does.** A single-particle
  gap should keep driving R up exponentially. A plateau at ~3 kΩ points to a parallel
  conduction path or disorder-induced in-gap states setting a floor — and it means the
  activation measurement, not R itself, is the honest route to a gap in meV.
