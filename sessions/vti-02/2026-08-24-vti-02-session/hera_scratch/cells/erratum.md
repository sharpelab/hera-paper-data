## ERRATUM — correcting cell idx 41 (the P4 Landau-fan proposal)

This notebook is append-only, so the erroneous claim below stays on the page. This cell is
the marker a reader needs.

**Cell idx 41 (`## HERA — P4: Landau fan at D = 0`) states:** *"a rhombohedral N-layer stack
carries an N-fold orbitally degenerate zero-energy level; for tetralayer ABCA that is 4 × 4
(spin×valley) = 16 states, so the first flanking gaps fall at ν = ±8. A Bernal tetralayer
decomposes into two bilayer-like sets whose levels arrive at different fields, giving a
visibly different sequence. Counting filling factors settles it on band structure alone."*

**That is wrong.** ABAB tetralayer decomposes into two effective bilayers, each carrying a
2-fold orbital zero level × 4 spin/valley = 8 states, and **both sit at exactly E = 0** — so
ABAB also has 16 zero-energy states, identical to ABCA. The zero-Landau-level degeneracy is
4N for N layers **regardless of stacking order**: it counts *layers*, not stacking. Counting
filling factors therefore does **not** settle ABCA vs ABAB.

**What run 4 actually contributes to the stacking call** is the **Fermi-pocket count** — one
SdH tone proportional to n, where two bilayer-like bands would give two — plus a
cross-check on the density scale. Neither depends on the retracted claim, and the run was
worth doing. See the ana notebook (`Run 4 — landau-fan`) and the final call for the corrected
reasoning.

*No measurement, setpoint or datum is affected by this erratum; it corrects reasoning only.*
