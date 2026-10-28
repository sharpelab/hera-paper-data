## HERA — Step 3: SdH spot checks (`sdh-spot-check`), hole then electron, n = ∓6×10¹² at D = 0

Calibration is live (run 4; c_bg/c_tg = 1.2774, n_offset = −0.036e12). Per the investigation: two fixed-(n, D = 0) field sweeps **uniform in 1/B**, one per density sign at high |n| — they pin the onset, the tone set vs F_L, the side with cleaner SdH, and the Δ(1/B)/settling the fan inherits.

**Design.** F_L(6×10¹²) = (h/4e)·n = **62 T** (the fastest credible tone). Δ(1/B) = 1/(3·F_L) = 5.4×10⁻³ T⁻¹ (Nyquist ×1.5 margin). Window **[0.25, 8] T** (B_lo below any plausible onset at T_e ≈ 8 K; B_hi = session cap — ~120 periods of F_L in the span). N = 721 points. **Sequencing to never re-traverse**: hole side sweeps 0.25 → 8 T up; electron side runs at 8 T after a gate flip and sweeps 8 → 0.25 T down, parking the magnet low for the fan (which starts at the measured onset).

**Excitation/sensitivity** (deviation from card's zero-field metallic values, stated): I_bias = 20 nA (2 V drive, card's high-|n| setting). The card's sr1 2e-6 would ceiling at 100 Ω — guaranteed clipping under MR at 8 T. Sized instead for the worst corner: sr1/sr2 **2e-5** (1 kΩ ceiling ≈ 20× zero-field R at n = 6e12), sr3 **5e-5** (R_xy(8 T, 6e12) = B/ne ≈ 832 Ω → 16.6 µV, 3× headroom), sr0 **5e-2** (20 mV signal). Signal at B = 0: ~1 µV = 5 % of range — coarse but rising with MR exactly where the FFT reads; the spot check is itself the MR calibrator for the fan's final sizing.

**Cost each**: 7.75 T traverse ≈ 57 min (0.137 T/min floor) + 721 × ~2.3 s ≈ 28 min → **~1.5 h/side** (upper 1.7 h; per-point from runs 0–4). Checkpoints: first rows (~5 min in), then the FFT read between sides — the electron cell only runs after the hole-side verdict.

Preconditions per cell: T < 2 K; hole cell expects B ≈ 0 (magnet parked after run 4), electron cell expects B ≈ 8 T (where the hole sweep ends). Tags: `sdh-spot-check`.
