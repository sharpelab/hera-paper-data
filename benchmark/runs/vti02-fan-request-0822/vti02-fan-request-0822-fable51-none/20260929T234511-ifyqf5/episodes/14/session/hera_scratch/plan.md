# vti-02 — stacking-order plan (HERA, 2026-08-23 pickup)

Goal: ABAB vs ABCA vs ABCB on the one wired pair (sr1 = B_1–B_2, source T_0, drain B_3), evidence-cited, or a calibrated "cannot tell".

## Discriminants (what each stacking predicts, D = 0)
- **ABAB (Bernal)**: two bilayer-like bands (light + heavy) → **two SdH fundamentals** whose frequencies sum to F_L = n·h/4e; Landau fan shows two interpenetrating ladders with **LL crossings**; 16-fold zero-energy LL → first strong gap |ν| = 8 (4-fold splittings weaker); CNP gap opens with |D| symmetrically.
- **ABCA (rhombohedral)**: single flat band → **one SdH fundamental at F_L** (plus harmonics only); a single clean ladder, gaps at |ν| = 8, 12, 16, … no crossings at D = 0; strong D-tunable CNP gap; strong interaction physics near CNP.
- **ABCB (mixed)**: no inversion symmetry → intrinsic gap at D = 0 (R_CNP(D) minimum displaced or absent), Dirac-like + heavy band mix; asymmetric ladder.

## Steps
1. ✅ Gate C liveness (runs 0–3): alive, no leakage (|I| ≲ 100 pA transients only), peaks ≤ 330 Ω at D≈0.
2. ✅ 0 T gatemap (run 5; run 4 railed) → calibration: c_bg/c_tg = 0.773 (data), c_tg = 9.5 nm prior, n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex). D = 0 line inside the box: n = −1.27 … +3.27e12. Second parallel ridge B (mosaic, +0.43e12) is a confound to keep in mind.
3. ✅ SdH spot checks (run 6 electron n=+3.2e12; run 7 hole n=−1.2e12): SdH resolvable from ~1.5 T at base T. Run 6: fundamentals ≈ 7.2 T and ≈ 30 T (+ harmonics) — two-band-like; sum ≈ 37 T vs F_L 33.1 T → absolute n scale (prior) likely ~10 % low, or the 30 T tone is partly harmonic. Run 7: multi-tone (6.8, 12.3 ≈ F_L, 3.5, 15.8 T) — near-CNP, not decisive.
4. **▶ Fan 1 — coarse full-window D = 0 Landau fan** (`landau-fan`; landed 2026-08-23 ~05:23 as measure cells 47/48, id `45da862b`, execution to be verified — see session_notes STATE): B slow 0.4 → 10 T in 0.2 T (49 rows), fast = D = 0 line n −1.25 … +3.25e12 in 0.03e12 (151 pts, both carrier signs). Establishes: the ν-ladder (which |ν| gaps, crossings or not), F(n) per band from per-column FFT (slope of F vs n = absolute-n calibration = the lever-arm check), electron/hole asymmetry. Ends at 10 T with gates parked at 0. ~4 h.
5. **Fan 2 — targeted down-fan** (10 → ~1 T, direction alternated per the rig card): after Fan 1, zoom where the discriminant lives — finer B (0.1 T) over the crossing/gap window, or a D ≠ 0 fan if the D = 0 read is ambiguous (ABCA vs ABAB differ strongly in how the ladder responds to D). Priced after Fan 1.
6. Optional: T-dependence of a chosen gap (LK mass) only if Fans 1–2 leave the call weak and time allows (elevated-T rig facts read first).
7. Call in ana (output contract), then `return-to-initial` close-out on operator ask.

## What would change my mind
- Fan 1 shows a **single** clean ladder with F(n) = F_L for all n → ABCA-leaning; then Fan 2 tests D-dependence of the gap sequence.
- Fan 1 shows **two** ladders/crossings and two F(n) branches summing to F_L → ABAB-leaning; Fan 2 zooms crossings (their B positions vs n are quantitative).
- R_CNP(D) minimum not at the symmetry point / ladder asymmetric between ±n at D = 0 → ABCB in play.
- Rails at ν = 0 near n = 0 at high B are expected (accept); rails elsewhere → re-run row window at 200 µV.
- Region B (mosaic) tones at ×1.13 density would appear as faint replica lines — do not count them as bands.
