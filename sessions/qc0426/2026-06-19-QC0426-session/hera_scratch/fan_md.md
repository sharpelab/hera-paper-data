## HERA [E1] — Landau fan (Step 4): D=0, HOLE n=−3 to −6.5e12 × B 0→8 T

The decisive FS-count measurement (`landau-fan-vti`): F(n) across density to test the
Luttinger partition — does sr1's pair (f_ML+f_BL) sum to F_L(n) across density (real ABA),
and does sr2 stay single at F_L(n) (ABC)? Resolves the mosaic call. Spans the resolvable +
model-valid (|n|≤3.5e12 at the low end) hole window. B slow (blocking magnet, ramps once
0→8), n-line fast (co-swept dc205_volt + k_2400.volt along the calibrated D=0 line).

Design: 157 B-rows (40 mT above 2 T — Nyquist for F_L≲70 T; coarse below onset), 29 usable
n-points (Δn meets the LL ray-spacing floor). **col 0 is a throwaway** absorbing the per-row
n-line retrace (BG step-ramps slowly, no snake). Lock-ins pre-set (τ=0.1, sens 2e-5 Rxx /
1e-4 Hall — no autorange mid-fan); 20 nA. fp X/Y/R + leakage, no Lakeshore poll. ~2.5 h.

**Checkpoint ~70 min (B≈4 T):** per-row SdH emerging across the n-line? leakage clean? sens
not railing at low-n/high-B? Fork: continue / adjust / abort. Then per-column 1/B FFT →
F(n) → the call. Auto: gates in validators, B≤8 T cap. Tag `landau-fan-vti`.
