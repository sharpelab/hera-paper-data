## HERA — P4: Landau fan at D = 0 — independent test of the band structure

Plan step **P4**. The gate map has taken the call a long way: R at neutrality rises
**10.4×** with displacement field (296 Ω → 3074 Ω), and its minimum sits at
**D/ε₀ = 0.000 ± 0.008 V/nm** with the two branches symmetric to within 7 % out to
|D| = 0.08 V/nm. That excludes ABAB (a band-overlapped semimetal would not gap like that)
and disfavours ABCB (which, lacking inversion symmetry, must put its minimum at finite D).
The remaining hypothesis is **ABCA**.

Everything above, though, is one measurement of one quantity. This fan is an
**independent** test, of the band structure rather than the gap:

- **Landau-level degeneracy.** A rhombohedral N-layer stack carries an N-fold
  orbitally-degenerate zero-energy level; for tetralayer ABCA that is 4 × 4 (spin×valley)
  = 16 states, so the first flanking gaps fall at ν = ±8. A Bernal tetralayer decomposes
  into two bilayer-like sets whose levels arrive at different fields, giving a visibly
  different sequence. Counting filling factors settles it on band structure alone.
- **Fermi-pocket count.** One SdH tone carrying the full Onsager frequency ⇒ a single
  quartic band (ABCA); two tones splitting it ⇒ two pockets (ABAB/ABCB).
- **The first absolute density calibration.** Every number so far rests on the
  *geometry prior* for c_tg. LL slopes give dn/dB = νe/h directly, which either confirms
  that prior or corrects it. Note the map already moved the *ratio*: measured
  c_tg/c_bg = **1.2737 ± 0.0470** against the prior's 1.1579, and this cell uses the
  measured value to define the D = 0 line, not the prior.

**Design.** Fast axis is density along the measured D = 0 line (V_bg = 1.2737·V_tg),
n = −1.04 → +2.10 × 10¹² cm⁻² with the CNP at V_tg = −0.003, so the fan is centred on
neutrality and covers both carrier signs. Slow axis is field on a **1/B-uniform grid**
(`field_invB`), which is what `sdh_fft` wants — no resampling, and it naturally puts more
rows at low field where the levels converge. D = 0 is chosen deliberately: it is the
symmetric point, so the band structure is seen unperturbed.

`magnet.field` is **followed per point** because the rig card is explicit that this
supply's setpoint is not readable as field — only the measured current is truth.

**Cost** ~1 h 15 m: 5 min to reach 0.75 T, ~38 min of ramping spread across the 40 rows
(the magnet's fixed 0.137 T/min is the floor and dominates), ~28 min of measurement,
~2 min of flyback. Priced at 1 h 30 m. Field is the expensive, one-way axis, so this runs
**upward once** and does not re-traverse — the session's remaining field need after this
is the ramp back to zero.

**Checkpoints:** first row read for clipping and leakage (the gates sit at new values
here); then per-row digests, with the decision at row ~10 (B ≈ 1.2 T) — if no oscillatory
structure is developing by ~2 T I will reconsider whether the mobility supports a fan at
all rather than spend the full hour. Ceiling is 6 T, not the 10 T session cap, precisely
because the ramp is the cost: 6 T already puts ν = ±8 comfortably inside the density
window, and every extra tesla is ~7 min each way.
