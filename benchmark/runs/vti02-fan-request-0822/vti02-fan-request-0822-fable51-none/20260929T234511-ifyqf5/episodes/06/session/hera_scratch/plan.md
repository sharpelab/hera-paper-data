# vti-02 — stacking-order campaign plan (ABAB / ABCA / ABCB / cannot tell)

*Reconstructed 2026-08-23 ~05:30 by the incoming instance (no plan.md was carried over;
steps 0–3 are inferred from the landed cells' "Step N" headers and the data on disk).
Kept current from here.*

## Physics the call rests on (single contact pair sr1 = B_1−B_2, region A calibration)

| stacking | low-E bands at D = 0 | Landau-fan fingerprint |
|---|---|---|
| ABAB (Bernal) | two bilayer-like parabolic bands, masses ≈ 0.6× / 1.6× m_BLG, both gapless at E = 0 | two interpenetrating 4-fold fans from the same origin; F_light/F_total ≈ const ≈ 0.38 (n_i ∝ m_i); LL crossings form a checkerboard; ZLL 16-fold (ν = ±8 first gaps), weak D-tunability of the CNP gap |
| ABCA (rhombohedral) | one flat quartic band, strongly D-gapped | single fan, F ≈ F_L(n) = n h/4e (all density in one 4-fold pocket; harmonics if degeneracy lifts), ZLL 16-fold (ν = ±8, then ±4/±12 from symmetry breaking), R_CNP strongly D-tunable, trigonal-warping pockets only at very low n |
| ABCB (mixed) | Dirac-like cone + bilayer-like parabolic band, small intrinsic gap / band offset | two fans with *unequal* n-dependence (Dirac pocket F ∝ n^1 at fixed E_F share falls as n grows vs parabolic), ZLL 4 + 8 = 12-fold → ν = ±6 combined, offsets in the fan origins |

Evidence already in hand (runs 5–7): R_CNP grows 240 Ω → 2.4 kΩ from D ≈ 0 to +0.25 V/nm (D-tunable gap — consistent with all three, strongest expectation for ABCA); e-side spot (run 6, n = +3.2e12, F_L = 33.1 T): tones 7.2 T (+2×, 3×, 4× harmonics), 5.1 T, 3.0 T, and a dominant 29.5–31.4 T; h-side spot (run 7, n = −1.2e12, F_L = 12.4 T): 6.8 T (dominant), 12.3 T (≈ F_L), 3.5, 4.6, 8.5, 15.8 T. Single-density FFTs are ambiguous (harmonic-of-a-split-pocket vs second pocket) — the fan's F(n) slopes and the filling-factor sequence resolve that.

## Steps

0. **Gate C — liveness / leakage** (`gate-current-sanity-check`, runs 0–3). DONE: alive, Rxx 60–330 Ω, gates at pA floor to every card limit.
1. **0 T gatemap** (`gatemap`, run 4 railed → run 5). DONE: ridge A (main CNP) + parallel ridge B (second region, electron-doped by 0.43e12); c_bg/c_tg = 0.773 (data), c_tg = geometry prior; n_offset −0.089e12, D_offset −0.013 V/nm. `hera_scratch/cal_run5.json`.
2. **Feasibility model** (mass table → SdH frequencies at reachable n). DONE (in cells 39/41 markdown).
3. **SdH spot checks** e-side (run 6) and h-side (run 7). DONE: strong multi-tone SdH from ≲0.5 T on both sides; fan is feasible. Ana landing of 6/7 pending (do during step 4).
4. **Landau fan at D = 0** (`landau-fan`) — THIS STEP. n from −1.2 to +3.2e12 (Δn 0.05e12, 89 pts, co-swept TG/BG along the calibrated D = 0 line), B 1.0 → 10.0 T at 0.1 T (91 rows), base T, sr1 200 µV (20 kΩ FS). Ends at 10 T. ≈ 4 h 15 m. Establishes: filling-factor sequence out of the CNP (ZLL degeneracy), LL crossings (one vs two bands), F_i(n) for every pocket (density partition slopes).
5. **Fan analysis** (ana): raw |Rxx|(n, B) map; per-column `sdh_fft` → F(n) ridges, fit slopes dF/dn per pocket vs h/4e; Rxx-minima traces → ν assignment (n = ν eB/h through the CNP); ridge-B fan offset check (−0.43e12). Interim reads at the ~3 T and ~6 T checkpoints.
6. **Conditional — D-dependence** riding the magnet down from 10 T: either a second fan at finite D (if step 5 leaves ABAB vs ABCB open — a Dirac-like band's response to D differs from a parabolic pair's) or a B = const, (n, D) cut. Decide from step 5; ~3–4 h. Price stated when proposed.
7. **Optional — T-dependence (LK masses)** at 1–2 densities, riding the field. Only if the fan leaves a mass-ratio question that ~1 h of ladder settles; T_e ≈ 8 K on this rig limits it (rig card). Likely hedged, not measured.
8. **Verdict** in the ana notebook per the output contract; then `return-to-initial` close-out on operator ask.

## What would change my mind

- A fan with a single clean 4-fold sequence and F(n) ≈ F_L(n) → ABCA (strong if the ν = ±8 ZLL edge and the D-tunable gap are both seen).
- Two fans from one origin with a constant frequency ratio ≈ 0.4 and a checkerboard of crossings → ABAB.
- Two fans whose origins are offset / whose frequency ratio drifts with n, ν = ±6-type combined ZLL, or a small intrinsic gap at D = 0 → ABCB.
- Ridge-B region dominating the sr1 signal (its fan offset by 0.43e12) would confuse the origin count — check before assigning ν.
- If the fan shows no resolvable LL structure above ~4 T (unlikely given runs 6/7) → "cannot tell", with the T_e / disorder argument.

## Standing constraints

Validators TG [−0.3, +1.0], BG [−1.3, +2.0], Si [−25, +25] V, |B| ≤ 10 T, set_both ≤ 100 K at ratio 0.95 only. Si untouched (banned as a survey). Never re-traverse the field: each step starts where the magnet sits.
