# vti-02 — plan (stacking order: ABAB / ABCA / ABCB) — kept current

*Reconstructed at handoff 2026-08-23 (no plan.md existed; the prior instance carried
its plan in the proposing-cell markdown, measure cells 33–42). Steps 1–3 are done.*

## Discriminants — what the data can say (hedged expectations, D = 0 unless noted)

| observable | ABCA (rhombohedral) | ABAB (Bernal) | ABCB (mixed) |
|---|---|---|---|
| Fermi surfaces at finite n | one (flat band) → one SdH tone F = nh/4e | two bilayer-like bands (light/heavy, m_h/m_l ≈ 2.6) → two tones, F_h + F_l = nh/4e, F_h/F_l ≈ m_h/m_l at fixed E_F | Dirac-like pair + cubic pair → two tones, Dirac one growing ∝ √-like LL spectrum |
| zero-energy LL manifold | 16-fold (4 orbital × 4) → first gaps ν = ±8, then 4-fold steps | 16-fold total (8 + 8) → ν = ±8 strong, higher gaps from two interpenetrating ladders with different ħω_c | 4 (Dirac) + 12 → 16-fold; distinct crossing pattern |
| gap vs D at the CNP | large, ~linear in D (tens of meV at 0.25 V/nm → CNP insulating at 1.3 K) | small / semimetallic overlap at finite D (modest R rise, saturating) | intrinsic gap at D = 0 (no inversion) → R_CNP(D) minimum offset from D = 0 / asymmetric |
| run 5 evidence so far | disfavoured: R_CNP only 2.4 kΩ at 0.25 V/nm, saturating | consistent | weakly disfavoured: R_CNP(D) symmetric with a 297 Ω minimum at D ≈ 0 |
| runs 6/7 evidence so far | run 7 ≈ F_L single tone fits; run 6's 30 T + ~8 T does not (unless 8 T is a bunching sub-tone) | run 6 two-tone content fits; partition 30:8 vs expected ~2.6:1 unclear until the n scale is pinned | not excluded |

The stacking call rests on the **fan** (family count, degeneracy sequence, tone partition
F_i(n)) with run 5's D-response and a T-dependence (mass ratio) as corroboration.

## Steps

1. **DONE — gatemap (run 5) → cnp-and-dline-calibration**: ratio c_bg/c_tg = 0.773 (data),
   c_tg = 9.5 nm prior (absolute scale UNVERIFIED), n_offset −0.089e12, D_offset −0.013 V/nm.
   Region B (parallel ridge, +0.43e12 electron-doped) = series-mosaic confound.
2. **DONE — feasibility model** (in cell 39/41 markdown): F_L(3.2e12) = 33.1 T, F_L(1.2e12) = 12.4 T.
3. **DONE — SdH spot checks** runs 6 (e, +3.2e12) / 7 (h, −1.2e12) at D = 0: resolvable SdH from
   ~1–1.5 T; run 6 = 30 T + ~8 T (+ mixing), run 7 = 12.5 T ≈ F_L + F_L/2 sub-tone. Ambiguous
   at one density: scale error vs band partition. → the fan.
4. **NOW — Landau fan at D = 0 (`landau-fan`)**: B slow 0, 0.5, 1 → 10 T (0.15 T, 63 rows) ×
   (V_tg, V_bg) fast along D = 0, n −1.26 … +3.22e12 (0.04e12, 113 pts), fast_delay 1 s,
   sr1 100 µV. ≈ 3 h 40 m, ends at 10 T with gates at 0. Establishes: absolute n scale from LL
   slopes (ν e/h) and their CNP intercept; the gap sequence from the CNP (ν = ±8? ±4?); the
   number of line families; per-column 1/B spectra F_i(n).
5. **Fan analysis** (ana, per checkpoint and at completion): re-form (fan_grids/resistance_grids),
   log-R map in (n, B) and (n, 1/B); trace Rxx minima → fit n = ν e B/h + n_0 per line → ν
   assignment, n-scale factor, lag/offset; per-column sdh_fft → F_i(n) and whether ΣF_i = nh/4e;
   compare to the table above. Update the calibration (c_tg scale) if the slopes demand it.
6. **Discriminating follow-ups, riding the magnet down from 10 T** (choose by the fan read;
   each priced when proposed):
   a. **T-dependence at a fixed n where two tones coexist** (LK masses: ABAB predicts
      m_h/m_l ≈ 2.6 with both ≪ 0.1 mₑ; ABCB's Dirac branch has a B-dependent "mass"). Uses
      `heater.set_both(T, ratio=0.95)`, hover acceptance, ≤ 100 K cap; field fixed, B-sweep
      windows 3–10 T per T. ~45 min per T point.
   b. **D ≠ 0 fan or fixed-B (n, D) map**: how the LL gaps at the CNP evolve with D
      (rhombohedral: gap grows fast and symmetric; Bernal: layer-polarized crossings).
   c. Hole-side densities beyond −1.26e12 are out of the operating box — not measured; state
      in the hedges.
7. **Call** — final ana cell per the output contract (one region: B_1–B_2 on sr1; region B
   mosaic noted as a confound, not a separate contact pair).
8. **Close-out** on the operator's `return-to-initial`: field → 0, gates → 0, heaters off, readback
   to session_notes.

## What would change my mind
- Fan shows a **single** line family with gaps at ν = ±8, ±12, ±16 … and one tone F = nh/4e
  everywhere → ABCA despite run 5's weak D-gap (then the D-gap read must be revisited: maybe D
  calibration/thermal broadening; step 6b becomes mandatory).
- Two families whose partition F_h/F_l is ~2.6 and constant in n → ABAB (strong with 6a).
- Two families with one whose LL spacing scales as √B (Dirac) → ABCB; also a CNP gap at D = 0
  in the fan (ν = 0 insulating already at low B).
- Slopes implying an n scale off by > 20 % → recalibrate before any frequency argument.
- Rail/lag/smearing making lines untraceable → repeat a narrower fan at fast_delay 2 s.
