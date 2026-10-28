# vti-02 stacking-order plan — status as of 2026-08-23 (post-handoff)

Goal: ABAB vs ABCA vs ABCB call on vti-02 (tetralayer graphene), evidence-cited,
per the brief's output contract. One measured region (hardwired pair sr1 = B_1−B_2,
source T_0 → drain B_3).

## Steps

1. **[DONE] Gate C — liveness + gross gate safety** (`gate-current-sanity-check`,
   runs 0–3). All wired contacts alive; gate currents < ~120 pA transient, no
   sustained leak inside the operating box.
2. **[DONE] 0 T gatemap → CNP + (n, D) calibration** (`gatemap`, run 4 aborted
   at 20 µV / railed, run 5 good at 100 µV; `cnp-and-dline-calibration` in ana).
   cal: c_bg/c_tg = 0.773, c_tg = 2.796 mF/m² (geometry prior), n_offset
   −0.089×10¹², D_offset −0.013 V/nm → hera_scratch/cal_run5.json. CNP ridge R
   grows with |D| (330 Ω at D≈0 → >2.9 kΩ at |D|max) — a D-tunable gap exists
   (leans away from pure ABAB, but B=0 T_e-limited; not decisive).
3. **[DONE] SdH spot checks at D = 0** (runs 6 electron +3.2×10¹², 7 hole
   −1.2×10¹²; ana cells landed 2026-08-23). Multi-band, light-mass SdH both
   sides; hole side two fundamentals 5.3 + 7.0 ≈ F_L = 12.4 T (ABAB model pair
   5.3/7.1). **ABCA disfavored; ABAB vs ABCB open.**
4. **[NOW] Landau fan at D = 0** (`landau-fan`, this cell): fast co-swept
   (V_tg, V_bg) along D = 0, n = −1.25 → +3.24×10¹² (205 pts, Δn ≈ 0.022);
   slow B = 0.2 → 10 T, 0.1 T steps (99 rows), ascending from the parked 0 T.
   Establishes: ν-line sequence and slopes (independent n-scale check),
   LL-crossing pattern (two-band ABAB lattice vs ABCB hybrid), CNP gap vs B,
   separates real second-band tones from harmonics.
   What would change my mind: a single-band fan with one dominant ν ladder and
   a strong-D-gapped CNP → revisit ABCA; crossing pattern inconsistent with
   two bilayer-like bands → ABCB.
5. **[NEXT] Contingent on fan read**: (a) if crossings ambiguous, a D ≠ 0 fan
   or fixed-B gate-gate map riding B down from 10 T (never re-traverse); (b)
   optional T-dependence (LK masses) at 1–2 (n, B) spots via set_both ≤ 100 K
   if masses are needed to close ABAB vs ABCB.
6. **Verdict cell in ana** per the output contract, then close-out
   (`return-to-initial`).

## Standing facts
- Fan end state: B = 10 T, gates at n = +3.24×10¹² — step 5 starts there.
- Known benign signature: sustained ≈ −100 pA TG current at negative V_tg
  (run 7); hera-watch LEAK warnings on hole-side half-rows are expected.
- Timing cal: fast axis 0.945 s/pt at fast_delay = 1.0 (run 5); ramp 0.137
  T/min bare; actuals run 5–10 % over (session evidence).
