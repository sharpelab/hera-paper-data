# vti-02 stacking-order campaign — plan (living)

Goal: ABAB vs ABCA vs ABCB, region-resolved (one measured pair: sr1 = B_1−B_2),
evidence-cited, or a calibrated "cannot tell". Envelope: TG [−0.3, +1.0], BG [−1.3, +2.0],
Si [−25, +25] V (unused), |B| ≤ 10 T, T ≤ 100 K. Base T ≈ 1.2 K, T_e ≈ 8 K.

## Discriminants (what each stacking predicts on this rig)
- **ABAB (Bernal)** — two bilayer-like parabolic bands (light + heavy), semimetallic
  overlap at CNP, small D-tunable gap. Fan: two interpenetrating 4-fold LL ladders
  (crossings), gaps at total ν = 4k near CNP; 16-fold zero mode → first strong gaps at
  ν = ±8 (±4 weaker, symmetry-broken).
- **ABCA (rhombohedral)** — one quartic band, large DOS at CNP; strongly D-gapped
  (R_CNP grows without saturating, many kΩ → MΩ at 0.25 V/nm); often correlated
  insulator at D = 0. Fan: a single ladder, no crossings; 16-fold zero mode
  (N = 0..3 orbitals), first gaps ν = ±8/±4 with orbital splittings.
- **ABCB (mixed)** — Dirac-like (monolayer-like) band + bilayer-like parabolic band,
  semimetal with small D gap. Fan: a Dirac ladder (gaps at ν_D = 4(N+½): ±2, ±6, ±10…)
  interleaved with a 4k ladder; 12-fold zero mode → ν = ±6 first gaps.

## Steps
1. **Gate C liveness** (`gate-current-sanity-check`, runs 0–3) — DONE. Alive on the
   provided pair, Rxx 60–330 Ω, gate currents at pA floor to the limits. Two peaks per
   gate leg (two CNP ridges).
2. **0 T gatemap + (n, D) calibration** (`gatemap`, run 4 aborted/railed, run 5) — DONE.
   Ridge A: slope −0.773 → c_bg/c_tg = 0.773 (prior 0.864); c_tg anchored at 9.5 nm
   prior (absolute scale UNVERIFIED); n_offset −0.089e12; D_offset −0.013 V/nm from
   R_CNP(D) vertex. R_CNP 240 Ω at D = 0 → 2.4 kΩ at D = 0.25 V/nm, saturating —
   small D gap, argues against ABCA but is not a stacking read alone. Ridge B: a
   parallel region electron-doped by 0.43e12 (series mosaic; expect shadow lines
   shifted by +0.43e12 in the fan).
3. **SdH spot checks** (`sdh-spot-check`, run 6 e-side n = +3.2e12 0→10 T; run 7
   h-side n = −1.2e12 10→0.3 T) — DONE. Oscillations from ~1 T; R→0 QH minima at
   5.92/7.16 T (run 6), 1.68/2.04 T (run 7). Minima are NOT one 1/B-periodic ladder;
   ν assignment is ambiguous at the ±8 % level of the unverified scale. FFTs are
   dominated by the non-oscillatory jump at 7.5–8 T (run 6) — combs at the window
   resolution, not tones. Read: multi-band LL structure; the fan is the decisive read.
4. **Landau fan at D = 0** (`landau-fan`, NEXT) — n fast along the D = 0 line
   (−1.28 … +3.26e12, TG-limited both ends, 100 pts), B slow 1 → 10 T in 100 mT
   (91 rows), sr1 100 µV. Establishes: (a) absolute ν per LL line from slopes
   dn/dB = νe/h → the lever-arm (absolute n scale) check the calibration lacks;
   (b) the zero-mode degeneracy from the lowest gaps emanating from the CNP
   (ν = ±4/±8 vs ±6 vs ±2); (c) one ladder vs two interpenetrating ladders
   (crossings) vs Dirac+parabolic interleaving; (d) the region-B shadow (lines
   offset +0.43e12) as a control. ≈ 4 h 40 m, ends at 10 T.
   Checkpoints: first row (rail/leak/flat channel); ~3, 5, 7 T partial `fan_grids`
   re-form; abort on rail across many columns, leak trip, T > 1.5 K, or no LL
   structure by 5 T.
5. **Conditional follow-ups** (choose from step-4 data; magnet rides 10 → low B):
   a. Fan at finite D (D ≈ +0.2 V/nm, same n line where inside the box): ABAB —
      LL crossings move, gap at CNP; ABCB — Dirac gap opens; ABCA — insulating.
   b. T-dependence of the lowest-ν gaps (set_both ≤ 100 K, ratio 0.95) only if the
      zero-mode degeneracy read is ambiguous (gap hierarchy vs T).
   c. If the ν assignment is still ambiguous, a 1/B-uniform high-resolution cut at a
      fixed n where two ladders are distinct.
6. **Verdict** in the ana notebook per the output contract (per-region line for the
   B_1−B_2 pair; evidence with run ids; hedges).

## What would change my mind
- A single clean ladder with no crossings and huge R_CNP at high B → ABCA (despite the
  small D gap at 0 T).
- ν = ±6 as the first CNP gap, or a 4(N+½) ladder coexisting with a 4k ladder → ABCB.
- Two ladders with crossings, gaps at ν = 4k, first at ±8 → ABAB.
- Fan lines extrapolating to n ≠ 0 at B = 0 → the CNP/n_offset or scale is off:
  recalibrate before any ν read.
- Region-B shadow lines confusing the ladder count → weight lines by amplitude and
  check the +0.43e12 offset before counting bands.

## Banned / out of scope
Extending gate limits; standalone Si survey; any safety-surface change.
