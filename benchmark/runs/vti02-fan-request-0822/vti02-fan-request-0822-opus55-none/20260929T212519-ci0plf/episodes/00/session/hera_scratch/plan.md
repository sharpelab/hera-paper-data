# vti-02 stacking call — plan (HERA, rewritten at handoff 2026-08-23 05:30)

Goal: ABAB vs ABCA vs ABCB, per measured contact pair. Only one pair is wired
(sr1 = B_1–B_2, T_0 → B_3), so there is one region to call, with a series-mosaic
confound (ridges A and B in run 5).

## Discriminators (model: chiral decomposition, γ0 + γ1, γ1 = 0.38 eV, v = 1e6 m/s)

| | bands at D = 0 | SdH tones at fixed n | light-tone fraction vs n | D response |
|---|---|---|---|---|
| ABAB | two BLG-like (λ = 1.618, 0.618) | F_l + F_h = F_L, both ∝ n | ≈ 0.25–0.30, ~flat (rises slowly with n) | CNP gap weak/moderate; R(D) = R(−D) (inversion) |
| ABCA | one J = 4 band (trigonal-warping pockets at low n only) | single F_L at n ≳ 1e12 | — (no light tone) | large D-gap at CNP; symmetric in ±D |
| ABCB | J = 3 + J = 1 (cubic + Dirac-like) | two tones, F_D small | small at low n, **grows with n** (∝ E^{4/3}) | polar: R(n, D) ≠ R(n, −D); CNP min off D = 0 |

LL-level signatures: ABAB shows periodic missing 4k minima (light/heavy LL
coincidences) and LL crossings in the fan. ABCA shows a regular 4k ladder at high n.
ABCB's Dirac band carries a π Berry phase (half-integer Landau-plot intercept).

## Steps

1. [done] Gate C liveness (runs 0–3). Pass.
2. [done] 0 T gatemap + calibration (run 5). Ratio 0.773, n_off −0.089, D_off −0.013 (R_CNP symmetry vertex); two parallel ridges (series region B, +0.43e12).
3. [done] SdH spot checks (runs 6 e / 7 h). Fan feasible. Electron side has a two-band signature (7.1 / 22.2 / 29.5 T, ladder scale s = 0.894, missing ν = 40, 52, 56, 68–76). ABAB lean.
4. **[next] Landau fan at D = 0**: B slow 1 → 10 T uniform in 1/B (82 rows, Nyquist 45 T, ΔF 1.1 T); n fast along D = 0, −1.25 … +3.25e12 prior (151 pts, 0.03e12). Establishes:
   (a) the absolute n scale from the ν-line slopes (replaces the prior c_tg);
   (b) the tone count and F_i(n) per column, the sum rule F_l + F_h = F_L, and the light fraction vs n (ABAB flat vs ABCB rising vs ABCA none);
   (c) the missing-minima / LL-crossing pattern across n;
   (d) the hole side and near-CNP structure.
   ≈ 5 h 45 m. Ends at 10 T.
5. Finite-D fan or ±D cut, riding the field down from 10 T. Tests the D-symmetry (ABCB polarity) and the D-gap size (ABCA) at the densities where step 4 is clean. Shape decided from step 4. Candidates: an (n, D) map at fixed B ≈ 8–10 T on the ride down, or a fan at D = ±0.1 V/nm (the ±D reach is TG-limited; compute the window).
6. T-dependence of SdH amplitude (LK masses) at one electron density, if step 4 leaves ABAB vs ABCB open. Mass ratio m_l/m_h ≈ 0.38 for ABAB; the Dirac m* in ABCB is ∝ √n_D and small.
7. Call → final ana cell (per-region verdict, evidence with run ids, hedges).
8. Close-out: return-to-initial.

## What would change my mind

- The fan shows a single tone = F_L at n ≳ 1.5e12 with a complete 4k ladder, and the 7 T tone was region-B or harmonic content → ABCA.
- The light fraction climbs strongly with n (e.g. ≲ 0.1 at 1e12 → ≳ 0.25 at 3e12), or the Landau-plot intercept of the light tone is at 1/2 → ABCB.
- Strong ±D asymmetry in step 5 → ABCB. A large D-gap (≫ kΩ at |D| ≈ 0.2) → ABCA-leaning (run 5 already shows R_CNP rising to 2.4 kΩ at D ≈ +0.25; this alone does not discriminate).
- Series region B dominating the tone content → hedge the per-region call.
