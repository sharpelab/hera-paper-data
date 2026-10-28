# vti-02 stacking call — plan (HERA, E1)

*Rebuilt 2026-08-23 ~05:40 by the incoming instance. The first instance cited
"Step 1–3" in its cells but never wrote this file; steps 0–3 below are
reconstructed from its cells and session_notes and keep its numbering.*

Goal: ABAB vs ABCA vs ABCB for the one measured pair (sr1 = B_1−B_2), region-resolved,
with evidence cited by run id, or a calibrated "cannot tell".

## Discriminators (what each stacking predicts on this rig: T_e ≈ 8 K, |B| ≤ 10 T, D=0 line n ∈ [−1.28, +3.26]e12)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| SdH F(n) at D=0 | two independent bands (light + heavy bilayer-like), F₁+F₂ = F_L(n), F₂/F₁ not locked to an integer | one surface, F = F_L(n) (harmonics 2F_L, locked); F_L/3 pockets below the Lifshitz density | two+ bands, no inversion symmetry |
| Landau fan | LL crossings between two families (diamond/checkerboard pattern), crossing points move with n | one LL family, gaps at every ν = 4k beyond the zero-LL octet, no crossings at D=0 away from the CNP | crossings, plus fan structure asymmetric under D → −D |
| R_CNP(D) at B=0 | weak/moderate D response, symmetric | steep D-opened gap, symmetric | asymmetric about the true D=0, possible hysteresis in D |

Harmonic vs independent is the crux of run 6 (7.1 T + 22–30 T at n=+3.2e12): only F vs n settles it.

## Steps

0. **Gate C** — done (runs 0–3): alive, no leakage, Rxx 60–330 Ω.
1. **0 T gatemap + calibration** — done (run 5; run 4 aborted/railed): ratio c_bg/c_tg = 0.773,
   c_tg = 9.5 nm prior (absolute scale unverified), n_offset −0.089e12, D_offset −0.013 V/nm
   (R_CNP(D) vertex — note: this *defines* D=0 by symmetry, so it cannot also test ABCB asymmetry).
   Second parallel ridge B: region electron-doped by 0.43e12 vs A (series mosaic).
   R_CNP(D) rises 240 Ω → 2.4 kΩ by D ≈ 0.25 V/nm: D-tunable gap, not diagnostic alone.
2. **Feasibility model** — done (first instance, in cell 39/41 markdown): ABAB pair ≈ 7.5/25.6 T at
   n=+3.2e12, ABCA 33.1 T.
3. **SdH spot checks** — done (runs 6, 7; ana cell 15): oscillations from ≤ 0.7 T on both sides;
   electron 7.1 T + 22–30 T (harmonic-or-band ambiguous); hole 12.3 T ≈ F_L strongest + 4.7/6.6/8.5 T.
   Negative Rxx dips in run 6 → Hall admixture from the mosaic.
4. **Landau fan at D = 0** — NEXT (operator request). B slow 0.6 → 10 T ascending (uniform-1/B
   Δ0.03 to 1.25 T, Δ0.0125 to 2.83 T, then 0.1 T), fast = n along the D=0 line −1.25 → +3.20e12
   (0.05e12, co-swept Vtg/Vbg), sr1 100 µV fixed. ~6 h. Establishes: F_i(n) tracks per column
   (FFT in 1/B), LL-crossing pattern, LL-slope density calibration (fixes the c_tg scale for the
   sum rule), both regions' fans (region B's origin at n_A ≈ −0.43e12). Ends at 10 T.
5. **Finite-D fan, riding the magnet down** (10 → 0.6 T) at D ≈ +0.15 V/nm (and/or −0.15 on a later
   pass), shorter n window — how the crossings/gaps respond to D. Decide D and window from step 4.
6. **B = 0 D-symmetry / hysteresis at the CNP** — ±D sweep along n = 0, forward and back
   (ABCB polar/ferroelectric test). Cheap (~30 min) once the magnet is at 0.
7. (optional) LK T-series at one density to separate light/heavy masses — only if 4–6 leave
   ABAB vs ABCB open and the masses discriminate.
8. **Call** — final ana cell per the output contract. Then close-out (`return-to-initial`).

## What would change my mind

- Fan shows a single F track = F_L(n) with 2F_L locked, no crossings → ABCA (then 7.1 T in run 6 is
  a pocket/region-B/harmonic artifact to explain).
- Two tracks whose ratio drifts with n and that sum to the fan-calibrated F_L → two-band (ABAB/ABCB);
  step 6 asymmetry/hysteresis then separates ABCB from ABAB.
- Tracks locked at integer ratios across all n → harmonics of one surface, not bands.
- Region B's fan showing a different F(n) template than A → region-resolved verdict (a stacking domain
  boundary between the voltage probes), not a single call.
- Rails/Hall admixture swamping the columns → the fan read degrades to "cannot tell" for that n range;
  a −B fan (symmetrization) would be the fix, priced separately.

## Log
- 05:40 plan rebuilt; step 4 fan designed (hera_scratch/fan_design.py).
