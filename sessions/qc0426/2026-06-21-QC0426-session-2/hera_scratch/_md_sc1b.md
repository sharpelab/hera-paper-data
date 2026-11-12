## HERA — Step 3: SdH spot check HOLE, clean re-run (`sdh-spot-check`)

Run 2 clipped: sr1/sr2 railed at 546 Ω (10 µV FS) above ~4 T — the device's high-|n| MR is far stronger than estimated (Rxx ~B^1.8, →~1.6 kΩ at 8 T), and no SdH onset appeared in the clean low-field (0.2–3.8 T), so the oscillations (if any) live above 4 T where run 2 saturated. This re-run fixes the sensitivity and targets the high-field SdH region.

**Same target:** n = −3.5×10¹² cm⁻², D = 0 (V_tg=−1.560, V_bg=−1.191; gates already there). **Rides home 7.95 → 1.0 T** (magnet already at 8 T — no re-traverse), uniform-1/B, N ≈ 96 at Δ(1/B)=1/(3·F_L), F_L=36.2 T, δf≈1.1 T. Dwell 2.5 s.

**Corrected lock-in:** sr1/sr2 → **1e-4** (100 µV FS; handles ~kΩ MR with headroom), sr3 → 5e-5 (Hall ~28 µV at 8 T, was not clipped). Drive 2 V/20 nA.

**Reads:** clean Rxx(B) to 8 T → true onset, and the FFT tone content vs F_L (single ABC tone vs ABA pair). Given the warm electron-T (~8 K) onset is high, the usable 1/B window may be small — this run determines whether the SdH is resolvable here or the device is resolution-limited (→ Step 6 Streda fallback).

**Cost ~1 h** (8→1 T blocking traverse ~51 min + 96 pts). Checkpoint ~30 min: by then the expensive high-field points (8→~3 T) are in — partial FFT on the clean high-field data. Ends at 1 T.
