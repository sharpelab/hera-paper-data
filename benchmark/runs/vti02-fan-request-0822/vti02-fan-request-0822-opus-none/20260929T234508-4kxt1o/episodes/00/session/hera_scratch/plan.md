# vti-02 — stacking-order plan (ABAB / ABCA / ABCB)

*Reconstructed and carried forward at the instance handoff (2026-08-23). The
previous instance ran steps 0–3b without landing this file — see
`session_notes.md` (PROTOCOL).*

## Goal

Region-resolved stacking call for tetralayer vti-02 on the one hardwired pair
(`sr1` = B_1 − B_2, source T_0 → drain B_3). One measured region only, so the
"per-region" contract is one verdict line + the region-mosaic caveat (below).

## What separates the three parents (what I am actually measuring)

| | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| bands at D = 0 | **two** bilayer-like subbands, band overlap → semimetal | **one** quartic-touching band, 4-fold | hybrid, inversion **broken** |
| Fermi surfaces at moderate n | 2, density split in a fixed ratio (ΣF = F_L) | 1, F = F_L | 2, different ratio |
| fan lines | **two families**, slopes in the density ratio; the minority family does *not* extrapolate to n = 0 (overlap density) | **one family**, all lines converge on n = 0 | two families + intrinsic CNP gap |
| D → −D | symmetric | symmetric | **asymmetric** |

Decisive observable = the Landau fan: fan-line **slopes** are `dn/dB = ν·e/h`,
so counting families and indexing ν gives (i) the Fermi-surface count, (ii) the
density fractions, (iii) an absolute lever-arm calibration independent of the
9.5 nm hBN prior.

**The mosaic confound and why the fan settles it.** Run 5 found two parallel CNP
ridges (regions A and B in series, B electron-doped by 0.43×10¹²). Two series
regions also produce two superposed oscillation families — indistinguishable
from two Fermi surfaces in a single 1D trace. In a fan they are *not*: two
regions give families with the **same** ν-slopes offset by a constant Δn; two
Fermi surfaces give families with **different** slopes (proportional to their
density fractions) sharing one origin. This is the single strongest reason the
fan, not more 1D spot checks, is the next move.

## Steps

- **0. Gate C — liveness** (runs 0–3, done). Alive, no leakage, R 60–330 Ω.
- **1. 0 T gatemap** (run 4 railed → run 5, done). Two parallel CNP ridges;
  ridge A R_CNP 240 Ω at D ≈ 0 rising to ~2.4 kΩ at D ≈ +0.25 V/nm (D-tunable
  gap — consistent with all three parents, not a stacking read).
- **2. (n, D) calibration** (run 5 ana, done). c_bg/c_tg = 0.773 (data);
  c_tg = 2.796 mF/m² (geometry prior — **absolute scale still uncalibrated**);
  n_offset −0.089×10¹²; D_offset −0.013 V/nm. D = 0 line inside the validators:
  n = −1.27 … +3.27×10¹².
- **3/3b. SdH spot checks** (runs 6, 7, done — analysed at handoff). Both sides
  oscillate strongly: e-side (n = +3.2) tones 7.1/14.1/22.2/29.5 T, onset ≤ 0.3 T,
  R_xx → 0 minima at 4.3 and 7.2 T; h-side (n = −1.2) tones 4.7/6.6/9.4/12.3 T,
  onset 0.71 T, minima → 0 at 1.8 T. **Establishes**: quantum-Hall-quality
  quantization at base T, so LL indexing in a fan will work. **Does not settle**
  the tone count — the FFTs are harmonic-rich (the QHE lineshape is strongly
  non-sinusoidal) and cannot separate a harmonic from a second pocket, nor a
  second pocket from region B.
- **4. Landau fan at D = 0 — THIS STEP.** n = −1.22 … +3.22×10¹² (111 pts,
  fast) × B = 0.25 → 10 T (79 rows, 125 mT). Establishes: family count,
  ν-indexing, absolute calibration, CNP convergence structure.
  *Changes my mind:* one family converging on n = 0 → ABCA; two families with
  different slopes → ABAB/ABCB; two families with equal slopes at constant Δn →
  the mosaic, and the tone count from runs 6/7 is an artefact.
- **5. (contingent) D-asymmetry cut.** If step 4 leaves ABCB live: a fan or a
  gate cut at fixed high B swept through D of both signs — ABCB is asymmetric
  under D → −D, ABAB and ABCA are not. Note the run-5 D_offset was set *by
  assuming* that symmetry, so this test must re-derive D = 0 from a
  symmetry-free feature.
- **6. (contingent) mass via LK.** Only if the family split is ambiguous and
  time allows; the rig's T_e ≈ 8 K and untuned sample-loop PID make this
  expensive (rig card: descents are passive, τ ≈ 27 min).
- **7. Close-out** (`return-to-initial`) + the call as the final ana cell.

## Standing hedges

- Absolute n scale rests on the 9.5 nm hBN prior until step 4's ν-slopes
  calibrate it; every F_L quoted before then carries that ~10 % uncertainty.
- One contact pair only → no region resolution beyond A-vs-B-in-series.
- T_e ≈ 8 K (rig card) sets the lightest resolvable mass; a null on a light
  band is a resolution limit, not evidence.
