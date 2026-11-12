# vti-02 — stacking-order plan (ABAB / ABCA / ABCB)

*Written 2026-08-23 on pickup (the first instance ran steps 0–3 without landing this
file). Kept current as data lands. One measured contact pair this cooldown: `sr1` =
B_1−B_2 (Rxx), drain on B_3, source T_0 — one per-region verdict line.*

## Logic of the call

All three tetralayers share a 16-fold zero-energy LL (Σ chirality = 4), so ν = ±8 is
generic. The stackings differ in the **higher LL sequence and its B-dependence at D = 0**:

| stacking | low-E bands | LL energies | fan signature at D = 0 | other handles |
|---|---|---|---|---|
| ABAB (Bernal) | two bilayer-like blocks, m_l ≈ 0.62 m_BLG, m_h ≈ 1.62 m_BLG (ratio ≈ 0.38) | two ladders ∝ B·√(N(N−1)), ω_h/ω_l ≈ 2.6 | **two interleaved ladders**: 4-spaced minima with *missing/weak* ones where the ladders cross (parabolic model: ν = 20, 36 weak; real bands make crossings B-dependent → minima that vanish over a B range) | SdH: **two tones** F_l + F_h = F_L, F_l/F_h ≈ 0.4 (+ MIS sum/difference tones); semimetal at D = 0 (weak CNP peak); D-gap saturates small |
| ABCA (rhombohedral) | one quartic flat band | single ladder ∝ B²·√(N(N−1)(N−2)(N−3)) | **monotonic regular 4-fold sequence**, gaps ν = 8, 12, 16, … all present and growing; LLs unresolved at low B (heavy) | SdH: **single tone at F_L** (full density, 4-fold); large D-induced gap (R_CNP ≫ 10 kΩ at 0.25 V/nm) |
| ABCB (mixed) | Dirac-like + cubic bands | √B ladder (sparse) + B^{3/2} ladder | two ladders with very different B-scaling; Dirac N = 1 far up → cubic ladder fills in | inversion-asymmetric: **D-asymmetric** R_CNP, intrinsic gap at D = 0 |

## Steps

0. **Gate C liveness** — runs 0–3. DONE. Alive, no leakage, Rxx 60–330 Ω; two CNPs in
   series (regions A, B).
1. **0 T gatemap → (n, D) calibration** — run 5 (run 4 railed). DONE. Ridge A slope
   c_bg/c_tg = 0.773; c_tg = geometry prior (absolute scale unverified); n_offset
   −0.089e12; D_offset −0.013 V/nm (R_CNP(D) vertex). Region B parallel, +0.43e12
   electron-doped. R_CNP(D) 240 Ω → 2.4 kΩ at 0.25 V/nm, saturating — a *small*,
   saturating D-gap (already a soft lean away from ABCA).
2. **SdH spot checks at D = 0** — runs 6 (n = +3.2e12, 0→10 T) and 7 (n = −1.2e12,
   10→0.3 T). DONE, analysis pending in ana (this instance). Run 6: Rxx → 0 minima from
   1.8 T; tones 7.3 / 14.8 / 22.3 / 29.4 T — harmonic series *or* two bands (7.3 + 22.3
   = 29.6 ≈ 0.9 F_L). Run 7: tones 7.1 and 12.6 (≈ F_L). A ~7 T tone at both
   densities is suspicious (a fixed-density region gives an n-independent tone) —
   the fan's line slopes settle it.
3. **Landau fan at D = 0** — `landau-fan`, this step. Rxx(n, B): B slow 1.0→10.0 T in
   0.1 T (91 rows), fast (V_tg, V_bg) co-swept along the calibrated D = 0 line, n =
   −1.26…+3.24e12 (130 pts, TG-limited both ends). Establishes: (a) the ν assignment
   of every minimum (line slopes through the origin — also fixes the absolute n scale,
   the geometry prior is ±10 %); (b) whether the 7 T tone is a gated feature (sloped
   line) or a parasitic (horizontal); (c) one ladder vs two — missing/crossing minima
   vs a monotonic sequence; (d) the ν = 0 CNP behaviour vs B. ≈ 5.3 h + overrun.
   Checkpoints: rows 1–2 (rail? TG current), then every ~10 rows (re-form, trace lines).
   Ends at 10 T.
4. **Decide from the fan** — if the fan is unambiguous (clean single ladder, or clear
   two-ladder crossings), go to the call. If ambiguous: (a) a fan at finite D (e.g.
   D = ±0.15 V/nm riding the magnet down) — ABAB's two blocks split differently with D
   than ABCA's single band; the D-asymmetry tests ABCB; (b) a T-ladder at one (n, B) for
   LK masses of the tones (rig card: settles 2–5 min, hover acceptance).
5. **Call** — final ana cell per the output contract (one verdict line for sr1 =
   B_1−B_2; evidence with run ids and numbers; hedges).
6. **Close-out** — on the operator's `return-to-initial`.

## What would change my mind

- A single strong tone exactly at F_L with a monotonic 4-fold fan → ABCA despite the small
  D-gap (then the gap saturation needs another explanation — series region B?).
- D-asymmetric CNP resistance or a clear intrinsic D = 0 gap → ABCB into play; would need
  a ±D map (run 5 covers only D = −0.08…+0.30 along the ridge).
- A horizontal fan line at F ≈ 7 T → parasitic region; strip it before counting tones.
- Region B (series, +0.43e12) duplicates every line shifted in n by +0.43e12 (weaker) —
  expect doublets, don't count them as extra ladders.
