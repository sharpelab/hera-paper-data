# vti-02 stacking-order campaign — plan (reconstructed at handoff, 2026-08-23 ~05:30)

Goal: ABAB vs ABCA vs ABCB for the one measured pair (sr1 = B_1–B_2), evidence-cited, with a
strength word — or a calibrated "cannot tell". No prior data; everything below is this session's.

## Done (steps 0–3)

0. **Gate C** — runs 0–3 (`gate-current-sanity-check`): alive, no leakage, Rxx 60–330 Ω; two series
   CNPs on each gate (regions A and B). PASS.
1. **0 T gatemap** — run 5 (`gatemap`, run 4 railed): ridge A slope → c_bg/c_tg = 0.773 (prior 0.864);
   c_tg anchored at the 9.5 nm prior (absolute n scale still a prior); n_offset −0.089×10¹²;
   D_offset −0.013 V/nm from the R_CNP(D) minimum. Ridge B parallel, 0.43×10¹² electron-doped vs A
   (series mosaic — a confound to carry). CNP gap is D-tunable (240 Ω → 2.4 kΩ at 0.25 V/nm): not a
   stacking read on its own.
2. **Feasibility** — F_L(3.2×10¹²) = 33.1 T; model tones ABAB ≈ 7.5/25.6 T, ABCA 33.1 T.
3. **SdH spot checks** — run 6 (e, n = +3.2, 0→10 T) and run 7 (h, n = −1.2, 10→0.3 T). Read
   (hera_scratch/spot_analysis.py): run 6 has a strong 7.1 T tone with 2×/3×/4× harmonics in 1.5–6 T
   and a lone 33.3 T tone above 4 T (= F_L: total-filling QH sequence); run 7 has 6.6 T (≈F_L/2) and
   12.3 T (= F_L). Two-band low-B regime feeding a single total-density sequence at high B.
   **Not yet landed in the ana notebook — land during the fan.**

## Now — step 4: Landau fan at D = 0 (`landau-fan`) — the stacking measurement

Field slow (magnet at 0 T now → ascend to 10 T, never re-traverse), (V_tg, V_bg) co-swept fast along the
calibrated D = 0 line, n = −1.25…+3.25×10¹² (TG-validator-limited on both ends; hole side stops at
−1.25 — stated coverage trade), step 0.03×10¹² (151 pts). Rows: 0, 0.5, 0.75 T; 68 rows uniform in
1/B from 1 to 5 T (Δ(1/B) = 0.012 T⁻¹ → per-column FFT Nyquist 42 T, covers the 33 T tone); 0.25 T
steps 5→10 T (QH regime read in 2D). 91 rows, ≈ 4.4 h nominal, 4h45m priced.

What it establishes, and the decision rule:
- **Per-band fan lines at low B (1–5 T):** extract tone frequencies vs n (per-column 1/B FFT) and the
  Rxx-minima lines in (n, B). ABCA → one tone at F_L(n) (all lines at integer ν through the CNP; ν = 8+4k
  sequence from the 16-fold zero LL). ABAB → two tones with F_1 + F_2 = F_L and a roughly *constant*
  partition F_1/F_L (both bilayer-like bands parabolic, common band bottom) → straight light-band lines
  through the CNP at non-integer apparent ν (run 6: 7.1/33.1 = 0.215 → apparent Δν ≈ 18.6).
  ABCB → two tones with an *n-dependent* partition (Dirac-like n ∝ E² vs parabolic n ∝ E) → curved
  light-band lines / F_1/F_L rising with n, and possible intercept offset from the intrinsic gap.
- **QH sequence at high B (5–10 T):** which total ν carry gaps near the CNP (±4, ±8, ±12 …) and away
  from it; interleaving of two LL ladders (ABAB/ABCB: level crossings, irregular gap strength vs ν)
  vs a single ladder (ABCA).
- **Absolute n scale:** the slopes of the integer-ν lines (dn/dB = ν e/h) calibrate c_tg — replaces the
  geometry prior; also fixes the CNP (fan apex).
- Checkpoints: row 1 (B = 0 n-trace: CNP at n ≈ 0 ± 0.1, R levels, no leak); ~1.5 T (oscillations along
  n); ~3 T (fan lines present); 5 T (QH minima). Abort on leak trip, a fully railed row, or a featureless
  map at 3 T.

What would change my mind / next after the fan:
- If the fan shows a single ladder (integer ν only, one tone = F_L at all n) → ABCA-leaning; then
  step 5a: check the ν sequence near the CNP at 10 T vs D (the rhombohedral gap opens strongly with D).
- If two ladders → ABAB vs ABCB by the partition-vs-n test above; then step 5b: LK temperature
  dependence of each tone at one or two n (masses: ABAB pair ~0.03/0.06 mₑ; ABCB Dirac band lighter and
  n-dependent) — rides the magnet down from 10 T with `heater.set_both(T, ratio=0.95)` steps, honoring
  the rig card's overshoot/settling facts.
- Region B (series mosaic, +0.43×10¹²): expect a duplicate fan offset in n at ×1.13 frequency; if
  present, report per-region where separable, else fold into the hedge.
- Close-out: `return-to-initial` (field 0, gates 0, heaters off, readback → session_notes).
