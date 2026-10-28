## Run 4 — `landau-fan`: band structure at D = 0, and a correction

**Why / what we're testing:** the gate map settled the call on gap physics. This is an
independent look at the *band structure* — 40 field rows (0.75 → 6 T, uniform in 1/B) ×
46 densities co-swept along the session-measured D = 0 line, n = −1.05 → +2.09 × 10¹² cm⁻²
with the CNP at V_tg = −0.003.

**Correction to the proposing cell.** When I launched this run I claimed the Landau-level
degeneracy would separate ABCA from ABAB — that a rhombohedral tetralayer's 4-fold orbital
zero level (16 states, first gaps at ν = ±8) would look different from a Bernal one.
**That is wrong, and I retract it.** ABAB tetralayer decomposes into two effective bilayers,
each carrying a 2-fold orbital zero level × 4 spin/valley = 8 states, and both sit at
exactly E = 0 — so ABAB also has 16 zero-energy states. The zero-LL degeneracy is 4N for
N layers *regardless of stacking*: it counts **layers, not stacking order**. The measure
notebook is append-only so the original claim stands there; this is the corrected record.

What this run can still do is count **Fermi pockets**, which does discriminate: a
rhombohedral stack has one quartic band at D = 0, a Bernal tetralayer has two bilayer-like
bands both crossing E_F and therefore two SdH tones.
