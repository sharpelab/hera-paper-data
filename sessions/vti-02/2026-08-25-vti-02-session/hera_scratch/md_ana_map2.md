**Read.**

*Health.* No railing anywhere (peak sr1 load 0.34 of full scale, R ceiling
≈10 kΩ). sr0 flat at 49.5 nA across all 3737 points. Gate currents: the
common-mode scatter (I_tg + I_bg) exceeds the differential (I_tg − I_bg) by
≈2×, which identifies the ±200 pA excursions as **pickup, not leakage** — a
TG↔BG leak is equal and opposite, a leak to ground shows on one gate only.
`hera-watch`'s ⚠ LEAK flag fired on every row at a steady Δ160–190 pA and never
grew, which is itself the signature of a fixed artifact rather than a
developing fault. The genuine leakage trend is the Gate C one: ~+65–100 pA above
V_tg ≈ 0.5 V, unchanged.

*The two features are real and behave oppositely.* Ridge B is strong at large
+D (2.4 kΩ at V_bg = −1.23) and **weakens monotonically toward D = 0** (234 Ω).
Ridge A is **absent below V_bg = −0.32** — a second-derivative shoulder scan
finds no trace of it in any of the 14 rows from −1.30 to −0.36 — appears near
D ≈ 0, and strengthens toward large −D (701 Ω by V_bg = +0.43, where it exits
the top-gate window). They are not peak-finder artifact: at V_bg = −0.144 the two
maxima (291 and 294 Ω) straddle a genuine dip at 240 Ω.

**This kills the two-doping-domains reading** I carried out of Gate C. Two
domains differing only in intrinsic doping would both persist across the whole
map with roughly constant relative weight and constant separation; instead each
feature lives on one side of D = 0 and dies on the other.

*And ridge B is not a constant-density contour.* n is linear in both gate
voltages, so **every constant-n locus is a straight line in gate space** — this
is arithmetic, not physics, and it makes curvature a clean falsification. Ridge
B's slope drifts monotonically from −0.767 (low-V_bg half) to −0.594 (high half),
and a quadratic term cuts the fit residual from 18.1 mV to 3.1 mV, a 5.9×
improvement over 17 points. Neither ridge's operating-window slope (−0.576 for
B, −0.673 for A) matches the geometry prior of −0.864.

*Consequence, stated plainly.* **I cannot presently identify which feature is
the charge-neutrality point**, and the cap ratio the whole (n, D) frame rests on
is not determined by this map. Every density coordinate the FS-count method
would quote inherits that. Reprojecting with the ratio fitted to flatten ridge B
near D = 0 does make both features look like constant-n loci *close to* D = 0
(ridge B at n ≈ +0.19×10¹², ridge A at ≈ −0.35×10¹², Δn ≈ 0.54×10¹²) — but no
single ratio flattens ridge B across its whole range, which is the curvature
restated, and choosing the ratio to flatten it is circular.

*Method note.* My first ridge tracker seeded on the prior slope and greedily
matched nearest peaks; it spliced ridge B's high-V_bg points onto ridge A and
reported "not parallel at 23.7σ". The 24 mV residual against the other track's
2.4 mV was the tell. Re-tracking outward from V_bg = 0 by continuity with mutual
exclusion, and then assigning by region once the second-derivative scan showed
where ridge A actually exists, is what the cell above does. **No sigma value
from a tracker should be believed before its residuals are looked at.**

**Next:** into field. At fixed B, adjacent Landau minima are separated by
Δn = eB/h exactly — degeneracy alone, no band model, no assumed capacitance — so
their gate-voltage spacing gives c_tg absolutely (the Step-5 quantum-Hall
lever-arm upgrade), the ν = 0 state identifies the CNP as the feature the fan
radiates from, and two domains would show as two superposed fans with different
origins. That is run 5.
