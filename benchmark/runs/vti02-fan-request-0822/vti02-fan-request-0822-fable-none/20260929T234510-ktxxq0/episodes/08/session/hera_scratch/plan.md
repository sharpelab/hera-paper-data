# vti-02 stacking-order plan — living copy

*(Re-created at handoff pickup 2026-08-23 — the prior instance's plan.md never
landed on disk; steps 1–3 below are reconstructed from the notebooks and
`session_notes.md`.)*

Goal: ABAB vs ABCA vs ABCB call on the one wired region (T_0→B_3, Rxx = B_1−B_2),
per the output contract. Discriminant: the low-energy band structure at D≈0 —
number of Fermi surfaces vs n, their frequency partition F_i(n), and the LL
wedge structure. ABAB (Bernal): two bilayer-like bands (light + heavy), two
incommensurate F(n) branches with F_light+F_heavy = nh/4e over both signs.
ABCA (rhombohedral): one flat heavy band, single branch F = nh/4e (LK-suppressed
at T_e≈8 K), strong e–h asymmetry. ABCB: three-ish bands / monolayer-like light
cone + heavy, distinct partition.

## Done

1. **Gate C liveness** — runs 0–3: alive, Rxx 60–330 Ω, gates at pA floor over
   full limits. Two resistance maxima per gate leg → two series regions.
2. **0 T gatemap + calibration** — runs 4 (aborted, railed) / 5: two parallel CNP
   ridges (regions A dominant, B fainter), ratio c_bg/c_tg = 0.773,
   n_offset = −0.089e12, D_offset = −0.013 V/nm (`hera_scratch/cal_run5.json`);
   ana cells land the read. D=0 line inside validators spans n = −1.27…+3.27e12.
3. **SdH spot checks** — run 6 (e-side, n=+3.2e12, 0→10 T): oscillations from
   ≲0.3 T; tones 7.1 T (+2×,3×,4× harmonics) and ~30 T ladder. Sum 37.1 T vs
   F_L=33.1 T. Run 7 (h-side, n=−1.2e12, 10→0.3 T): tones ~4.7/5.3, 6.6, 8.5,
   12.3–12.9 T. **Two-band structure on both signs → leans ABAB; not yet a call**
   (single-point n; harmonics vs fundamentals unresolved; 12% Luttinger excess).

## Now

4. **Landau fan at D = 0** (operator-requested, this cell): B slow 0.5→10 T
   (two-segment uniform-1/B grid, 132 rows: Δ(1/B)=0.02 below 1.3 T / 0.0095
   above; Nyquist 25/52 T), n fast −1.25→+3.20e12, 131 pts (Δn=0.034), through
   the CNP. Establishes: per-column F(n) branches and their slopes (degeneracy
   partition — the ABAB/ABCA/ABCB discriminant), fan apex vs CNP, ν-gap wedges,
   e–h asymmetry, whether run 6's 30 T tone is a fundamental (F(n) linear,
   slope ≠ 4×7.1-slope) or magnetic-breakdown/harmonic content.
   ~5¾ h. Ends at 10 T, gates at n=+3.2e12 end of the line.

## Next (contingent on 4)

5. **Read**: per-column sdh_fft F(n) + wedge map → if two branches with
   F_l + F_h = nh/4e on both signs → ABAB; single full-degeneracy branch with
   heavy-mass LK death → ABCA-leaning (then a T-ladder at one n for masses);
   three branches / anomalous partition → ABCB candidate.
6. **Targeted follow-up riding 10 T down**: finite-D fan or fixed-n D-cut
   (layer-polarization response separates Bernal vs rhombohedral gap behavior),
   or T-ladder for m*(n) if the frequency partition alone can't separate
   ABAB from ABCB. Decide from step 5.
7. **Verdict cell** in ana (output contract), then close-out `return-to-initial`.

## What would change my mind

- F(n) single branch matching nh/4e with no light partner → drop ABAB.
- The two 0 T ridges (region B) intruding into the fan (parallel-region
  artifacts): watch for a second, offset fan apex; if present, hedge the
  verdict to region A and say so.
- Luttinger sum ≠ nh/4e beyond cal error after the fan's own slope-based
  recalibration → revisit degeneracy assumption (symmetry breaking).
- Leakage / rail / T excursion → stop, notify.
