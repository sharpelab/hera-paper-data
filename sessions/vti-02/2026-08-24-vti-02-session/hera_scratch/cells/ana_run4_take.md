**Read:** the fan is textbook — a symmetric ladder of Rxx minima radiating from n = 0, and
a ν = 0 insulating wedge that widens with field until, at 6 T, Rxx at neutrality reaches
109 kΩ (clipping `sr1`) with the drain current sagging to 6.4 nA, i.e. R₂ₜ ≈ 55 MΩ. Three
things come out of it, and one thing deliberately does not.

**1. One Fermi pocket — and this is the α-independent result.** The SdH spectrum carries a
**single** tone whose frequency is proportional to n through the origin (r = 0.99), sitting
at ~0.85× the full Onsager frequency on the assumed density scale. The other spectral peaks
(4.2, 9.7, 9.1, 2.6, 8.4, 4.6 T as n increases) show no trend with density and are FFT
sidelobes. This matters because **two Fermi pockets would produce two tones that BOTH scale
linearly with n at a fixed ratio** — that statement needs no calibration at all. A Bernal
tetralayer at D = 0 has two bilayer-like bands both crossing E_F and would show exactly
that; a rhombohedral one has a single quartic band and shows what we see. **This is the
fan's contribution to the stacking call, and it points to ABCA.**

**2. A uniform Landau ladder**, spacing Δν = 4.665 on the assumed density scale, with lines
resolved out to the tenth on the electron side.

**3. Following `magnet.field` per point was necessary.** The measured field sits +6.5 mT
above the setpoint with ~2 mT of within-row spread — ~0.9 % at 0.75 T, which would have
propagated straight into every extracted frequency. (An early version of this analysis read
the setpoint column by mistake: `magnet_field` appears twice, and `FanGrids.grid()` silently
resolves duplicates to the first occurrence. The giveaway was a suspiciously perfect
`|cmd − meas| = 0.0 mT`.)

**What this run does NOT establish: the absolute density scale, or the degeneracy.** Both
the SdH frequency (f = n_true·h/g·e) and the ladder spacing depend only on the **product**
α·g, where α = n_assumed/n_true is the error in the absolute gate capacitance. Both routes
agree — α·g ≈ 4.7 — and both are blind to the split. Separating them needs a density
measurement independent of degeneracy, i.e. the **Hall resistance** n = B/(e·R_xy), and
this cooldown has no Hall pair: `sr2` and `sr3` are n.c. in the provided contact
configuration, so R_xy cannot be formed. That is a wiring limitation, not an analysis one.

If one *assumes* the standard 4-fold spin–valley degeneracy — which holds for the LLs above
the zero level in every candidate stacking — then α = 1.17 and c_tg = 2.40 mF/m², an 11.1 nm
equivalent hBN thickness at κ = 3 against the card's 9.5 nm. That is a believable 17 %
geometry error, and it is the reading I adopt; but it is an assumption, and every absolute
density in this session inherits it. **Nothing in the stacking call depends on it** — the
gate map's evidence is a ratio (10.4×) and a symmetry point (D = 0), and the fan's evidence
is a tone count.
