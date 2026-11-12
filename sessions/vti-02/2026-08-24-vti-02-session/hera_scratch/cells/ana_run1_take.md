**Read:** the CNP is at **V_bg = −0.250 V** at V_tg = 0, and the neutrality-point
resistance there is **Rxx = 297 Ω**. On the geometry prior that anchors the session's gate
calibration: n_offset ≈ **+3.8 × 10¹¹ cm⁻²** (slightly electron-doped as grown), the CNP
line is `V_bg = −1.158·V_tg − 0.250`, and this particular crossing sits at
D/ε₀ = **+0.034 V/nm** — effectively zero displacement field. So **297 Ω is the D ≈ 0
reference** the whole stacking argument is measured against.

Supporting reads:

- **Hysteresis is 50 mV**, one grid step, between sweeps in opposite directions. The gates
  are not charging up, so map rows taken minutes apart are comparable.
- **The point-to-point wiggle is noise, not structure.** Per-point σ is 2.2 Ω (run 0) and
  3.2 Ω (run 1); the observed run-to-run rms difference of 4.5 Ω is very close to the
  3.8 Ω that *pure independent noise* predicts, leaving only ~2 Ω (≈2 %) of reproducible
  excess. In volts that σ is ~32 nV, i.e. ~36 nV/√Hz input-referred at the 0.78 Hz ENBW —
  exactly SR830 1/f noise at 13.8 Hz. So the measurement is instrument-noise-limited and
  not drifting, and **features below ~3 % are not to be believed**. (An earlier version of
  this cell called the wiggles reproducible structure; comparing them properly against the
  noise-only prediction shows that was wrong.)
- **A double-peaked neutrality region** — peaks at V_bg = −0.25 V (297 Ω) and ≈ +0.15 V
  (272 Ω) with a 35 % dip to 194 Ω between them. That is an order of magnitude above the
  noise floor, so it is real; but it is seen in **one sweep only**, because run 0 clipped
  across exactly this region. The map's 35 independent CNP crossings are the test. If it
  persists it means either two regions of slightly different doping between the B_1–B_2
  probes, or genuine multi-band structure at neutrality — and the latter would itself be
  a stacking clue, since a Bernal tetralayer carries two bilayer-like bands with different
  masses.

**Caveat carried forward:** the device card gives no Hall-bar geometry, so these ohms are
not ohms-per-square — 297 Ω is ~1/20 of a graphene minimum-conductivity square, which
almost certainly means the B_1–B_2 probes span well under one square rather than that the
sheet is anomalously conducting. Every claim in the final call therefore rests on
*relative* changes. Probe loading pushes the same way: R₂ₜ implies ~0.4 MΩ contacts against
the SR830's 10 MΩ input, so absolute Rxx reads a few per cent low, and the quadrature
(|Y/X| ≤ 0.2) is the tell if that worsens near a gapped CNP.
