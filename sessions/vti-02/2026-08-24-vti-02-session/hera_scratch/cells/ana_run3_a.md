## Run 3 — `gate-map`: the (n, D) map, and the primary stacking discriminator

**Why / what we're testing:** ABAB, ABCA and ABCB differ most cheaply in what a
displacement field does to charge neutrality. A Bernal (ABAB) tetralayer is a
band-overlapped semimetal and stays conducting under D. A rhombohedral (ABCA) one is
inversion-symmetric and gapless at D = 0, so a gap opens ∝ |D| and R_CNP has a **minimum
exactly at D = 0**, symmetric either side. A mixed (ABCB) stack has no inversion symmetry,
carries a built-in gap at D = 0, and so puts its **minimum at finite D**. One map answers
all three: 35 rows × 66 points, slow V_bg −1.30 → +0.40 V, fast V_tg −0.30 → +1.00 V,
B = 0, T = 1.17 K.

The window stops at V_bg = +0.40 rather than the +2.00 limit because the CNP line leaves
the top-gate box at V_bg ≈ +0.10 — rows above that cross no neutrality point and carry no
stacking information. That budget went into resolution instead: ~30 distinct D values
along the CNP line.

*(Run 2 was this same measurement and died at point 3 of 2310 with a `BrokenPipeError`
from the live-plot subprocess — `sweep/plot.py` rebuilds the whole 2D mesh via
`ax.clear()` + `griddata` + `pcolormesh` on every point. Run 3 is identical with the 2D
live plot removed; the 3-point stub is left on disk as the record.)*
