## HERA — P2: coarse (n, D) gate map — the primary stacking discriminator

Plan step **P2**. This is the measurement the call rests on. ABAB, ABCA and ABCB differ
most cheaply in **what a displacement field does to the charge-neutral point**: a Bernal
tetralayer is a band-overlapped semimetal that stays conducting under D; a rhombohedral
one opens a large single-particle gap that grows with |D| and drives R_CNP up by orders
of magnitude; a mixed ABCB stack gaps too, but — lacking inversion symmetry — not
symmetrically about D = 0. One map answers all three.

**What P1 already fixed.** Run 1 puts the CNP at **V_bg = −0.250 V at V_tg = 0**, i.e.
n_offset ≈ +3.8 × 10¹¹ cm⁻² and a crossing at D/ε₀ ≈ +0.034 V/nm — effectively zero
field. So the CNP line is `V_bg = −1.158·V_tg − 0.250` on the geometry prior, and the
peak Rxx there is **297 Ω**. Hysteresis between the up- and down-sweeps is 50 mV, one
grid step, so the gates are not charging up on us.

**Why the slow axis stops at +0.400 V, not +2.000 V.** The CNP line leaves the top-gate
box at V_bg = +0.097 V. Every row above that is pure electron doping and crosses no
neutrality point, so it carries no stacking information — it would have been 25 of 45
rows and ~25 min of fridge time for nothing. Spending that budget on **resolution
instead** gives 50 mV rows over the window that matters: ~29 distinct D values along
the CNP line, from D/ε₀ = **+0.320 V/nm down to −0.067 V/nm**.

**The one-sided-D problem, stated up front.** That window is the plan's flagged risk made
concrete. Negative D at neutrality requires V_tg < 0, and the provided top-gate limit
stops at −0.3 V — which is an operating limit I am not permitted to probe or extend. So
+D has a five-fold longer lever arm than −D. This does **not** kill the ABCB test: the
inversion-symmetry question is *where the R_CNP maximum sits*, and a symmetric ±0.067 V/nm
window straddling D = 0 is available to answer it. It does mean any ABCB verdict rests on
a short lever arm and must be hedged accordingly.

**Reading it.** Rxx is `Vxx / I_measured`, and `resistance_grids` uses the measured drain
current, so the number stays honest if the current bias sags into a resistive device.
`sr1` at 1 mV covers up to 100 kΩ; if R_CNP climbs past that at high D, the clipping is
itself the ABCA/ABCB signature and I will re-range and re-cut rather than trust the rail.

**Absolute-vs-relative caveat, recorded now.** The device card gives no Hall-bar geometry,
so Rxx in ohms cannot be converted to R per square — 297 Ω is only ~1/20 of a graphene
minimum-conductivity square, which almost certainly means the B_1–B_2 probes span well
under one square, not that the sheet is anomalously conducting. Every claim in the final
call therefore rests on **relative** changes (R_CNP(D)/R_CNP(0), activation, SdH periods),
never on an absolute R per square. Probe loading pushes the same way: R₂ₜ says the probe
contacts are ~0.4 MΩ against the SR830's 10 MΩ input, so absolute Rxx reads ~7–10 % low,
and the quadrature (|Y/X| ≤ 0.2, followed and plotted) is the tell if that worsens.

**Cost** ~34 min of measurement (2310 pts at the run-1 calibrated 0.855 s/pt, plus 1.6 s
of flyback per row); priced at 42 min to leave margin.

**Checkpoints, both stated here:** first two rows read for clipping, a dead channel, or
leakage excess — the cheapest kill is in the first minute. Then per-row digests, with the
real decision at **row ~20**, by which point the CNP line has been crossed from D = +0.32
down through +0.05 V/nm. If R_CNP is climbing steeply across those rows the answer is
already rhombohedral-like and the rest of the session goes to activation; if it is flat
at a few hundred ohms, it is Bernal-like and the Landau fan becomes the confirming
measurement.
