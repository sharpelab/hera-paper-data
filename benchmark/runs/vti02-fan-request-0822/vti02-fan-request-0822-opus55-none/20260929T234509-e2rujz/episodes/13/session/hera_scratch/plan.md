# vti-02 stacking call — plan (kept current as data lands)

Goal: ABAB vs ABCA vs ABCB for the one measured pair (sr1 = B_1–B_2), evidence-cited,
or a calibrated "cannot tell". Contacts hardwired; one Rxx pair; no Hall channel.

Calibration in use (run 5, ana cell 13): c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m²
(9.5 nm prior — absolute n scale NOT yet data-calibrated), n_offset −0.089e12,
D_offset −0.013 V/nm (R_CNP(D) vertex). D = 0 window inside validators: n = −1.28 … +3.26e12.

## Done
- Step 0 — gate C (runs 0–3): alive, no leakage, Rxx 60–330 Ω, two series CNPs.
- Step 1 — 0 T gatemap (run 5; run 4 aborted/railed): ridge A (main) + parallel ridge B
  (region B, CNP offset −0.43e12 in region-A n). R_CNP 300 Ω at D≈0 → 2.4 kΩ at
  0.25 V/nm, saturating — D-tunable but weak "gap" (not a stacking read alone).
- Step 2 — feasibility model (in cell 39/41 md): F_L(n) = n h/4e; ABAB → two tones summing
  to F_L (light ≈ 0.23–0.28 F_L, heavy ≈ 0.72–0.77 F_L at high n); ABCA → single tone ≈ F_L
  above the trigonal-warping Lifshitz regime, heavy (LK-weak at T_e ≈ 8 K near CNP).
- Step 3 — SdH spot checks at D = 0 (runs 6 e-side n=+3.2, 7 h-side n=−1.2), B 0↔10 T.
  Run 6: oscillations from ≤ 0.5 T, QH (Rxx → 0) from ~1.5 T; tones 7.2 / 22.2 / 30 T.
  7.2 + 22.2 = 29.4 ≈ 30 T (sum rule → ABAB-like) BUT 22.2 ≈ 3×7.2 and 30 ≈ 4×7.2
  (harmonic series of one tone) — single-n record cannot separate. Also 30 T ≈ 0.9 F_L(prior),
  i.e. prior scale may be ~10 % high. Run 7: many tones (3.5–22 T) near CNP, mosaic-confused.

## Next
- **Step 4 — Landau fan at D = 0 (`landau-fan`)**: slow B ascending 0.6 → 9 T
  (1/B-uniform 0.6–3 T, Δ(1/B)=0.0125 T⁻¹ → Nyquist 40 T > F_L max 33.6 T; then 0.1 T to 9 T),
  fast = D = 0 line n −1.20 … +3.25e12, 91 pts (Δn 0.05). Establishes:
  (a) every tone's F(n): an independent band has its own slope and F1+F2 = F_L(n) at every n;
      a harmonic tracks exactly k× its parent across n. ABCA → one tone on F_L(n) (+ harmonics).
  (b) absolute density scale from QH minima lines n = ν eB/h (calibrates c_tg; fixes the
      sum-rule test's denominator).
  (c) LL structure: ABAB → light/heavy LL crossings (gaps closing/reopening vs B along fixed ν),
      ABCA → 16-fold zero LL, no crossings in the low-LL fan at D = 0, ν = ±8 strongest.
  (d) region B: a second fan origin at n ≈ −0.43e12 — same or different template.
  Checkpoints: first rows @0.6 T; ~1 T (row ~53, partial FFT for light tone vs n);
  3 T (row 108 — full SdH record: decide continue to 9 T vs stop and go to D).
- Step 5 — at the fan's end field (9 T, no re-traverse): D-dependence at fixed B
  (n–D map or fixed-ν D cuts inside the window). ABCA: D drives zero-LL/layer-polarization
  transitions and a strong ν=0 insulator; ABAB: D shifts LL crossings; ABCB: asymmetry in ±D
  (no inversion) — also the check on the D_offset convention (which assumed ±D symmetry).
- Step 6 — descend 9 → 0.6 T as a second fan at finite D (only if step 5 says D matters).
- Step 7 — the call (ana final cell) + close-out (return-to-initial).

## What would change my mind
- Fan shows 22 T tone exactly at 3×F_light for all n and nothing else independent → single-band
  (ABCA-like) reading of run 6; then F_dominant ≈ F_L would carry the call.
- Tones whose sum ≠ F_L(n) after QH-calibrated scale → neither simple template; mosaic/ABCB.
- Region B fan different from region A → region-resolved "mixed"/hedge.
- R_CNP(±D) asymmetric once D is scanned at field → ABCB weight up; D_offset convention revisited.
