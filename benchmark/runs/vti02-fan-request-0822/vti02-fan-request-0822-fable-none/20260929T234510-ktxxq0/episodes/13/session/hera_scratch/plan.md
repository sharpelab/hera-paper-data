# vti-02 stacking-order campaign — plan (v2, recreated 2026-08-23 after handoff; v1 file lost in handoff)

**Goal:** ABAB vs ABCA vs ABCB call, region-resolved (one wired pair: sr1 = B_1–B_2), per the output contract.

## Done

1. **Gate C liveness** — runs 0–3 (`gate-current-sanity-check`): contacts alive, leakage < ~120 pA transients, R(D≈0) peaks ≤ 330 Ω. ✔
2. **Gatemap + calibration** — run 4 (aborted, sr1 railed), run 5 (100 µV): CNP line slope −0.773 = c_bg/c_tg, n_offset −0.089×10¹², D_offset −0.013 V/nm (`cal_run5.json`; ana cell 13). ✔
3. **SdH spot checks** — run 6 (electron n = +3.2×10¹², 0→10 T), run 7 (hole n = −1.2×10¹², 10→0.3 T ride-down). Read (ana cell 15): two-band SdH at both signs, sums ≈ F_full. **ABCA strongly disfavored; ABAB consistent (7.1 + ~22–26 vs model 7.5/25.6 T electron; 4.7/6.6 vs 5.3/7.1 T hole); ABCB not excluded.** ✔

## Now

4. **Landau fan at D = 0** (`landau-fan`) — the decisive measurement: frequency-vs-n partition + LL gap/crossing pattern vs n separates ABAB (two bilayer-like bands, smooth F₁(n)/F₂(n) both ∝ n-ish, characteristic 8-fold-ish low-ν structure with crossings) from ABCB (monolayer-like + trilayer-like decomposition: different F(n) partition and LL sequence) and confirms the ABCA exclusion.
   - Fast: (V_tg, V_bg) co-swept along D = 0 (run-5 cal), n = −1.25 → +3.25×10¹² cm⁻², 131 pts (Δn = 3.46×10¹⁰; ≥ 7 pts per Δν=1 at 10 T, 1 pt per Δν=1 at ~1.4 T — ν lines resolved above ~2–3 T).
   - Slow: B = 0.4 → 10 T ascending (magnet sits at 0), 60 mT, 161 rows. 1/B Nyquist supports per-column FFT of all tones (≤ 35 T) above ~2 T.
   - sr1 200 µV (20 kΩ FS): CNP stripe may rail at high B (ν = 0 insulator) — accepted; sr0 (drain current) covers the railed stripe.
   - Price: 131 × 1.10 s/pt (run-5 actual) + 26 s ramp + ~9 s turnaround ≈ 180 s/row → 8.0 h + start-up ≈ **8 h 45 m realistic**. Ends at 10 T, gates → 0.
   - Checkpoints: first rows (~12 min); ~2 T (~1.5 h); ~5 T (~4 h); ~8 T (~6.5 h). Wash-out: rail across the line, leak trip, dead channel, or no n-dependent structure by 3 T.

## Then

5. **Fan analysis** — re-form (n, B) maps of R_xx and I_d; per-column FFT → F(n) branches; LL index map at high B (ν = n·h/eB lines, gap sequence, crossings); compare against ABAB/ABCA/ABCB band-model expectations.
6. **Contingency** (only if fan ambiguous): targeted follow-ups — e.g. D ≠ 0 cut (gap-vs-D at CNP distinguishes stackings' D response) or a T-dependence (LK masses) at chosen spots. Priced when proposed.
7. **Verdict cell** in ana (output contract: per-region call + evidence + hedges).
8. **Close-out** — `return-to-initial` (field 0, gates 0, heaters off, readback → session_notes).

## What would change my mind

- Fan shows a single F(n) branch ∝ n with no light band → re-open ABCA (against runs 6/7).
- F(n) branches with monolayer-like √-behavior / a branch that persists to n = 0 → ABCB weighting.
- Calibration drift (CNP position at B = 0 rows vs run 5 off by > 1 Δn step) → re-derive cal from the fan's own low-B rows before frequency analysis.
