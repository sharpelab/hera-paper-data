# vti-02 stacking-order campaign — plan (reconstructed at handoff, 2026-08-23 05:40)

Goal: ABAB vs ABCA vs ABCB for the one measured pair (sr1 = B_1−B_2, source T_0 → drain B_3),
evidence-cited, or a calibrated "cannot tell". Working directory `data/` is the only data input.

## Discriminants (what the stackings predict, D = 0, base T)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| bands at CNP | two bilayer-like massive bands (γ1,eff = 1.618γ1 / 0.618γ1), semimetallic overlap | one pair of E ∝ k⁴ flat bands | Dirac-like + massive, no inversion symmetry |
| SdH at fixed n | two tones, F_light + F_heavy = F_L, ratio ≈ 0.38 | one tone at F_L (4-fold degenerate) | two tones, unequal |
| low-B QH ladder | interpenetrating LL sets, many crossings; zero-energy LL 8+8-fold | ν = ±8, ±12, ±16… (no ν = ±4 gap at low B; zero LL 16-fold) | asymmetric in ±D; ν = ±4 present |
| R_CNP(D) at B = 0 | weak, roughly symmetric | strong gap: R → ≫100 kΩ by D ≈ 0.2 V/nm | asymmetric in ±D |

## Steps

1. **DONE — gatemap + cnp-and-dline-calibration** (runs 4 (aborted), 5; ana cells 12–13). Ridge A: c_bg/c_tg = 0.773, c_tg
   anchored at the 9.5 nm prior, n_offset −0.089e12, D_offset −0.013 V/nm. Parallel ridge B (0.43e12 electron-doped
   region in series) — series-mosaic confound. R_CNP(D) rises 240 Ω → 2.4 kΩ by D ≈ +0.25 V/nm and saturates:
   a D-tunable gap but weak → disfavors ABCA already (flag, not a call — absolute D scale is the geometry prior).
2. **DONE — feasibility model** (in cell 39/41 markdown): F_L(3.2e12) = 33.1 T; masses put the ABAB pair at ~7.5/25.6 T.
3. **DONE — sdh-spot-check** e-side n = +3.2e12 (run 6, 0 → 10 T) and h-side n = −1.2e12 (run 7, 10 → 0.3 T).
   Read (scratch `sdh_spot_read.py`): oscillations from the record edge (~1 T) on both sides, QH-like minima with
   Rxx → 0 in run 6 (4.25, 6.0, 7.2 T; jump to 500 Ω above 7.8 T), broad minima in run 7 (1.7, 2.04, 3.4, 4.94, 6.94, 8.34 T)
   whose 1/B spacing is not a single period → multi-band or ν-ladder that a 1D cut cannot untangle. No leakage, no rail.
   **Not yet in ana** — land raw + read while the fan runs.
4. **NOW — landau-fan at D = 0** (operator's request; this proposal). B slow 1 → 10 T (50 mT ≤ 5 T, 100 mT above,
   131 rows), n fast −1.24 → +3.23e12 in 0.03e12 steps (150 pts) co-swept along the calibrated D = 0 line.
   Establishes: (a) the ν-lines (slope dn/dB = νe/h) → the filling-factor ladder near CNP on both sides — is ν = ±4
   present at low B, or does the ladder start at ±8? (b) F(n) for each SdH tone → band count and partition;
   (c) LL-crossing pattern (ABAB hallmark); (d) the absolute density scale: the ν-line slopes calibrate c_tg
   independently of the geometry prior (closes the calibration hole left in step 1).
   Ends at 10 T with the gates at 0.
5. **Analysis of the fan** (ana): re-form with `fan_grids`/`resistance_grids`; plot raw R(n, B); extract minima per
   row, fit lines through the origin in (n, B) → ν per line; SdH FFT per n column for B 1–5 T → F(n); compare against
   the table above; verdict cell per the output contract.
6. **Contingent follow-ups (choose from the fan read, each priced then):**
   - if the ν-ladder is ambiguous near CNP → a finer fan over |n| < 1e12 riding the magnet down 10 → 4 T (~3 h);
   - if ABCB is in play → a ±D asymmetry check: two short fans / gate cuts at D = ±0.15 V/nm at fixed B (~1–2 h);
   - a T-dependence of one SdH tone (LK mass) only if the band assignment hinges on it (`set_both`, ratio 0.95, ≤ 20 K).
7. **Close-out** on the operator's `return-to-initial`.

## What would change my mind
- A rail or featureless first rows of the fan → stop, resize sensitivity / re-plan.
- Leakage trip (> 1 nA) → stop, notify, E0.
- The fan's ν-slopes disagreeing with the run-5 density scale by > 15 % → recalibrate c_tg from the fan before any
  F(n) interpretation; re-derive the D = 0 line and state whether the fan was actually at D ≈ 0.
- Region B (series mosaic) producing a second, shifted set of fan lines → attribute per-region features before any call.
