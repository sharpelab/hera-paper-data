**Read (gate C verdict — PASS, all four legs):**

- **Alive**: sr0 drain holds the full 5.00 nA bias everywhere; sr1/sr2 four-terminal R nonzero and smoothly varying on every leg; sr3 (Rxy) ≈ 0 ± 10 Ω at B = 0 as expected. All five wired contact roles on the provided configuration respond.
- **Safe**: swept-gate current pA-scale on the charging slope to every card limit — |I_tg| ≤ 45 pA, |I_bg| ≤ 111 pA. The BG channel carries a constant ≈ −100 pA readback offset (corr with swept V between −0.10 and +0.20 across legs 0–3 → offset, **not** a cross-gate path or leak).
- **Physics for step 1**: the CNP at BG = 0 sits near V_tg ≈ 0 (sr1 peak ≈ 1.6 kΩ, width ~0.5 V) — modest peak, no strong insulating gap at D ≈ 0. A reproducible shoulder at V_tg ≈ +0.55 V (runs 0/1, sr1+sr2) to track on the 2D map. Device metallic to ~28–65 Ω at the box corners on both signs — both density signs viable for SdH.
- **Timing calibration**: 2.2 s/pt at delay = 1 s + NPLC-10 gate reads (runs 0–3, 28 row/min) — the session's measured figure for pricing.

Next: coarse-BG 0 T gatemap (BG ±2.4 V × 25 rows, TG ±3 V × 151) → `cnp-and-dline-calibration` ridge fit.
