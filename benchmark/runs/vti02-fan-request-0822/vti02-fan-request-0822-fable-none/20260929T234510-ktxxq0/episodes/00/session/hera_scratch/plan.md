# vti-02 stacking-order campaign — plan (recreated at handoff, 2026-08-23)

*(plan.md was absent in scratch at pickup; reconstructed from the notebooks,
session_notes, and scratch. State below is current.)*

Goal: region-resolved stacking call — ABAB vs ABCA vs ABCB — per the output
contract. One measured pair only (sr1 = B_1–B_2; sr2/sr3 n.c.), so "region"
= the B_1–B_2 channel region.

## Steps

1. **[done] Gate C** — liveness + gate-current sanity (runs 0–3, B=0). Alive,
   leakage at pA floor.
2. **[done] 0 T gatemap** (run 5; run 4 aborted, sensitivity rail) →
   `cnp-and-dline-calibration`: ratio c_bg/c_tg = 0.773, n_offset −0.089e12,
   D_offset −0.013 V/nm (scale = 9.5/11 nm geometry prior). `cal_run5.json`.
3. **[done] SdH spot checks at D = 0** — run 6 (e, n=+3.2e12, 0→10 T): light
   fundamental 7.1 T + harmonics; missing ~26 T of F_full → hidden heavy band.
   Run 7 (h, n=−1.2e12, 10→0.3 T): pair 4.7 + 6.6 ≈ F_full 12.4 T. Both lean
   ABAB; not yet a call (harmonic/heavy-band degeneracy at ~29 T; ABCB not
   excluded). Ana cells 14–17.
4. **[NOW] Landau fan at D = 0** (`landau-fan`) — n ∈ [−1.2, +3.2]e12 fast
   (111 pts) along D = 0, B slow 0.5→3 T @ 25 mT + 3→10 T @ 50 mT (241 rows),
   ascending from B = 0 (magnet parked there). Establishes: per-band fans
   (slopes → band density fractions vs n), light/heavy crossings (ABAB
   fingerprint), single-fan-with-gaps (ABCA), Dirac+bilayer hybrid (ABCB);
   CNP gap growth with B on the D = 0 column. ~10.5 h. Ends at 10 T.
5. **[next] Read the fan** — re-form, per-column FFT vs n (F(n) branches),
   LL index fits. Decision point: if the stacking call is already strong,
   go to 6; if the heavy band is still ambiguous, consider a D ≠ 0 leg
   (gap-vs-D at fixed B, riding down from 10 T: ABAB gapless→gapped vs
   ABCA gapped at D=0) — that D-response is the cleanest ABAB/ABCA/ABCB
   discriminator and likely worth doing regardless.
6. **[then] Optional elevated-T LK masses** at fixed (n, B window) if masses
   are needed to seal the call (heater.set_both, ratio 0.95, ≤ 100 K cap;
   watch untuned-PID overshoot ~+1.4 K).
7. **Call** — final ana cell per the output contract; then `return-to-initial`
   close-out.

## What would change my mind

- Fan shows a *single* fan with all-4-fold gaps and no second-band crossings
  → ABCA-like single band; re-examine run 6's 7.1 T tone (moiré/subband?).
- F(n) branches not summing to F_full(n) → density calibration off; re-derive
  n_offset from the fan's own CNP column before any verdict.
- Strong e–h asymmetry beyond two-band expectations, or a zero-mode fan
  (Dirac) coexisting with a bilayer fan → ABCB candidate; then the D-response
  leg is mandatory.
