# Plan — vti-02 stacking-order call (ABAB / ABCA / ABCB)

*Recreated 2026-08-23 05:30 after the instance handoff (the original plan.md did not
survive; state reconstructed from session_notes.md, the notebooks, and scratch).*

## Logic

Stacking sets the low-energy band structure at D = 0: **ABAB** (Bernal) → two
bilayer-like conduction bands (light + heavy) → **two SdH fundamentals per carrier
sign whose sum tracks full density**; **ABCA** (rhombohedral) → one flat-bottomed
band → **a single fundamental ≈ F_L = |n|h/4e** (heavy mass, weak LK amplitude at
T_e ≈ 8 K); **ABCB** (mixed) → monolayer-like + bilayer-like mix → light Dirac tone
plus massive tone, distinctive gap/degeneracy pattern. Discriminators, in order of
power: (1) **F(n) dispersion** of every fundamental across density; (2) **LL gap-line
structure** in the (n, B) fan — filling factors ν = n·h/(eB) of the strong gaps and
their degeneracy sequence (fan self-calibrates the n scale: ν must be integer);
(3) effective masses (LK) if needed to separate ABAB's light/heavy pair from ABCB.

## Steps

1. **[DONE]** Gate C liveness + 1D legs (runs 0–3): contacts alive, R sane, no leak.
2. **[DONE]** 0 T gatemap (run 4 aborted/railed; run 5 good) →
   `cnp-and-dline-calibration`: ratio c_bg/c_tg = 0.773 (data), scale = geometry
   prior, n_offset −0.089e12, D_offset −0.013 V/nm (`hera_scratch/cal_run5.json`).
3. **[DONE]** SdH spot checks at D = 0 (runs 6 e-side +3.2e12, 7 h-side −1.2e12):
   strong SdH from < 1 T both signs. e-side: tones 7.1 + ~30 T (+combinations) —
   two-band-like, sum 37.1 T vs F_L 33.1 T; h-side: multiband 5.3/8.5/12.3/14.1 T.
   Neither is single-FS at face value → not ABCA-like at face value, but a
   two-point read is not a call. Ana notebook cells 14–17.
4. **[NOW]** **Landau fan at D = 0** (operator-requested): B slow 0.2 → 10 T
   (uniform-1/B main grid, F_Nyq = 40 T), n fast −1.25 → +3.25e12 along the
   calibrated D = 0 line, 181 pts. Reads: F(n) per band (FFT vs n), gap-line ν
   assignment, n-scale self-calibration from integer ν. Ends at 10 T.
5. **[NEXT — shaped by 4]** Targeted follow-ups riding the field down:
   candidates — LK T-dependence at one or two decisive n (mass split ABAB pair vs
   ABCB), a D ≠ 0 cut if the fan is ambiguous (D-response of the band edge differs
   strongly between stackings). Choose after the fan read.
6. **Verdict** in the ana notebook per the output contract; close-out
   (`return-to-initial`).

## What would change my mind / kill criteria

- Fan step 4 first-rows: rail, leak trip, or n-axis structure smeared (fast_delay
  too short) → abort inside 15 min, redesign.
- If run-5 calibration is wrong (CNP drifts, gap lines don't converge at n = 0),
  re-derive offsets from the fan apex itself before any ν assignment.
- If the fan shows a single fundamental dispersing as F_L(n) with 4-fold gaps →
  ABCA back on the table despite step-3's face read (harmonics can mimic).
- Absolute-T / mass numbers inherit the uncharacterized mount→device gradient
  (rig card) — LK masses are ratios/bounds, not precision values.
