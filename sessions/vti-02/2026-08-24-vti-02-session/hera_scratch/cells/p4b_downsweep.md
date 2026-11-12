## HERA — P4b: SdH trace measured through the ramp down

Plan step **P4b**. The activation ladder (P5) must be run at zero field, so the 6 T → 0
ramp is unavoidable — 40 minutes of the magnet's fixed 0.137 T/min. Measuring through it
costs about **13 minutes extra** and turns dead time into the session's highest-resolution
SdH dataset. That is the whole justification for this cell.

**Why the fan alone is not enough for the pocket count.** Run 4's 1/B record (0.75 → 6 T,
40 rows) gives an FFT resolution of 0.86 T but a Nyquist frequency of only ~17 T, while the
Onsager frequency at the top of its density window (n = 2.09 × 10¹² cm⁻²) is 21.6 T — those
columns **alias**, and an aliased tone is worse than no tone. This sweep uses 100 field
points over a longer 1/B baseline (0.5 → 6 T): resolution **0.55 T**, Nyquist **27.3 T**,
comfortably above every Onsager frequency in play. The fan is the right instrument for the
Landau-level *sequence*; this is the right one for *counting tones*.

**Design.** Five fixed densities on the session-measured D = 0 line
(n = −0.80, +0.50, +1.00, +1.50, +2.00 × 10¹² cm⁻²), verified to sit at D/ε₀ = 0.000
exactly and inside the committed gate box. Field descends on a `field_invB` grid so
`sdh_fft` needs no resampling. One tone carrying the full Onsager value means a single
Fermi pocket (ABCA); two tones splitting it means two pockets (ABAB/ABCB). Because the
five densities span a 4× range, the tones must also **scale linearly with n** — that is a
much stronger check than any single column, and it is what would expose a spurious peak.

`magnet.field` is followed per point, which run 4 proved is not optional: the measured
field sits **+6.5 mT above the setpoint** with ~2 mT of within-row spread, ~0.9 % at
0.75 T, and that would propagate directly into the extracted frequencies.

**Sensitivity is deliberately left at 1 mV.** These are finite-density columns where Rxx
stays modest; the n = +0.50 column sits at ν ≈ 3.4 at 6 T and may clip near its
peaks, which the analysis masks. Coarsening the range to protect it would destroy the
SdH *minima* — run 4 showed those reaching 0–6 Ω, and the minima are half the signal.

**Ends at 0.5 T**, not 0: a short bare ramp then takes the magnet to zero for the ladder,
which is cheaper than measuring the last half-tesla where there is no SdH left to see.

**Checkpoints:** first rows for clipping and for the current sag (at 6 T the drain current
was already down to 6.4 nA at neutrality — these columns are away from it and should sit
near 9.9 nA); then per-row digests. Priced at 1 h.
