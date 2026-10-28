# vti-02 — stacking-order campaign plan (HERA)

Goal: ABAB vs ABCA vs ABCB, region-resolved (one contact pair: sr1 = B_1−B_2), evidence-cited, or a calibrated "cannot tell".
Written 2026-08-23 ~06:00 by the second instance (the first left no plan file); steps 1–3 reconstruct what it did.

## Discriminants (what each stacking should show in this device's observables)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| bands at low E | two bilayer-like parabolic bands (light + heavy), semimetallic overlap | one flat ~k⁴ band (single FS) | Dirac-like (linear) + bilayer-like (parabolic); no inversion symmetry |
| SdH at fixed n | two tones, F₁+F₂ = F_L, ratio ≈ m₁/m₂ roughly n-independent | one tone = F_L = nh/4e | two tones with strongly n-dependent ratio (linear vs parabolic DOS) |
| Landau fan near CNP (D = 0) | 16-fold zero-energy multiplet split by band overlap; LL *crossings* (gaps closing/reopening along B at fixed ν) | 16-fold zero-energy LL → first gaps ν = ±8, then every 4 (±12, ±16 …), no crossings | ~12-fold zero-energy set → gaps at ν ≠ multiples of 4 (e.g. ±6, ±2), e/h asymmetric |
| R_CNP(D) | gap opens with |D|, symmetric in ±D | large D-tunable gap, symmetric | intrinsic gap at D = 0, *asymmetric* in ±D (minimum off D = 0) |

## Steps

1. **Gate C liveness** (`gate-current-sanity-check`, runs 0–3) — DONE. Alive, Rxx 60–330 Ω, no leakage. Two CNP peaks in series (regions A, B).
2. **0 T gatemap + (n, D) calibration** (`gatemap`, runs 4 (aborted) / 5; `cnp-and-dline-calibration` in ana) — DONE. c_bg/c_tg = 0.773 (data), c_tg = geometry prior (9.5 nm), n_offset −0.089e12, D_offset −0.013 V/nm (from R_CNP(D) symmetry — assumes inversion symmetry, i.e. presupposes not-ABCB; hedge). Region B parallel ridge, 0.43e12 electron-doped vs A (series mosaic confound). D = 0 window inside validators: n = −1.28 … +3.26e12 (TG-limited both ends).
3. **SdH spot checks** (`sdh-spot-check`, runs 6 e-side n = +3.2, 7 h-side n = −1.2; 0–10 T) — DONE, analysis landed in ana 2026-08-23. Both sides: clean SdH from ~1.3 T, QH-like minima to ~0 Ω, **two-tone spectra** (run 6: ~30 T + ~7 T; run 7: ~6.8 T + 12.3 T ≈ F_L). Not a single 4-fold ladder on either side → needs the fan. Filling factors of the deep minima with the calibrated n are not multiples of 4 → the absolute n scale (c_tg prior) is suspect at the ~10 % level; the fan's LL slopes are the lever-arm check.
4. **Landau fan at D = 0** (`landau-fan`, this step) — B slow 1.0 → 10 T in 0.1 T (91 rows), n fast −1.25 → +3.30e12 (92 pts, Δn = 0.05e12) co-swept (Vtg, Vbg) on the calibrated D = 0 line. Establishes: (a) the LL filling sequence near the CNP at high B (ν of the first gaps → zero-energy degeneracy), (b) LL crossings or not, (c) tone evolution with n (per-column sdh_fft over B ≥ 3 T), (d) the absolute n scale from the LL slopes dn/dB = νe/h. Price ≈ 4 h 15 m (row = 92 × 1.17 s gates + 47 s ramp/settle + ~6 s turnaround; run-5 and run-6 calibrations). Ends at 10 T, gates parked at 0.
5. **Decide from the fan** (ana). If the fan reads cleanly → write the call. If the tone/ν pattern is ambiguous: (a) a second fan or a coarser (n, D) cut at finite D riding the magnet down (ABCA's zero-energy multiplet splits under D into ν = 0, ±4 …; ABAB/ABCB differ), or (b) fine-B spot checks at 1–2 more densities (tone-ratio vs n), or (c) a hole-side/electron-side T-dependence (LK masses) — only if the ratio question is the blocker (elevated-T ladder ≤ 100 K, ratio 0.95, consent facts in rig card).
6. **Close-out** (`return-to-initial`) on the operator's ask.

## What would change my mind

- Fan shows a single 4-fold ladder with ν = ±8 first gaps and one tone tracking F_L(n) → ABCA (the two-tone spot checks would then be a series-mosaic/region-B artefact — check by whether the extra tone's frequency scales with region B's shifted density, n_B = n + 0.43e12).
- Fan shows two interpenetrating ladders with crossings and near-constant tone ratio → ABAB.
- Non-multiple-of-4 filling sequence + e/h asymmetric fan + R_CNP(D) asymmetry → ABCB; then the D_offset from symmetry is wrong and step 2's calibration needs redoing with the fan's ν = 0 line.
- Region B (series mosaic) confound: every tone/gap must be checked against the n_B = n + 0.43e12 alias before it is attributed to the main region.

## Known systematics to carry

- Lock-in τ = 0.3 s / 24 dB (operator-set) with 1 s fast dwell ≈ 3.3τ → ~40 % step response: a constant lag of ~1–2 fast points in the +n sweep direction; identical for every row (slopes unaffected, intercept shifts; read the ν = 0 line from the fan itself).
- T_e ≈ 8 K (rig card): heavy-mass LLs smear below ~2 T.
- Absolute n from the c_tg geometry prior until the fan's slopes fix it.
