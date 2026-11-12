## HERA — Step 3: SdH spot check, HOLE side (`sdh-spot-check`)

First spot check of the FS-count ladder. Fixed **(n = −3.5×10¹² cm⁻², D = 0)** — the max |n| still within the Onsager model-overlay validity (≤3.5e12), metallic (~55 Ω on both Rxx pairs), hole side (prior-favored for the ABA ML/BL balance). Gate voltages V_tg = −1.560, V_bg = −1.191 (session calibration, run 1; n, D verified exact).

**Field:** 0.20 → 7.95 T sampled **uniform in 1/B** (densest at low B → captures the onset for free), N ≈ 531 at **Δ(1/B) = 1/(3·F_L)**, F_L = 36.2 T. **Dwell 2.5 s** (≈8τ, above the 24 dB/oct settling floor — non-negotiable for the weak ML-tone hunt).

**Lock-in:** sensitivities set to the high-|n| metallic scale — sr1/sr2 → **1e-5** (10 µV FS for Rxx ~1.2 µV, with MR/QH headroom to 8 T), sr3 → **5e-5** (Hall ~29 µV at 8 T). Drive already at metallic 2 V/20 nA. τ / filter_slope untouched (operator-owned). T not fp'd per-point (LS335 Grafana contention).

**Reads:** onset (warm electron-T ~8 K may push it well above the ~100 mT heuristic), tone frequencies vs F_L, and which side gives cleaner SdH. A clean two-tone partition here can be decisive on its own.

**Cost ~1.75 h** (magnet 0.2→7.95 T blocking traverse ~57 min + 531 pts × ~5.5 s/pt incl. 3 s field settle). **Checkpoint ~55 min:** confirm no lock-in overload (clipped sr X), leakage low, and whether oscillations are emerging. Magnet left at ~8 T afterward — the electron-side spot check rides home (no re-traverse).
