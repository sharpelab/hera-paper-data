## HERA — SdH spot check H: hole side, n = −3.0×10¹² cm⁻², D = 0 (`sdh-spot-check`)

Investigation steps 2–3. Design from the run-4 calibration: gates
(−1.387, −1.078) V via the committed conversion; **F_L = 31.0 T** at
|n| = 3.0e12 (kept under the FS-model's 3.5e12 overlay clamp);
**uniform-B grid** (blocking rate-limited magnet): ΔB = Δ(1/B)·B_lo² =
**5.26 mT** (⅓-Nyquist on F_L at B_lo = 0.7 T), 1389 pts, **0.7 → 8 T
ascending** (magnet sits at 0 — never re-traverse; the electron check will
descend 8 → 0.7 next, ending low for the fan). Expected onset ~0.5–1 T
(T_e ≈ 8 K rig); B_lo sits below it and the low-B edge reads the onset.
δF ≈ 1.1 T if onset ≈ 1 T — separates an ABA pair partner from F_L for ML
fractions ≳ 7%.

**Settings**: 20 nA bias (2 V/100 MΩ, card high-|n| point); sens sr1–sr3
5×10⁻⁵ (Rxx ceiling 2.5 kΩ, R_xy(8 T) ≈ 1.7 kΩ inside range; quantization
0.08 Ω — no grainy-FFT digitization), sr0 50 mV. **Dwell**: `settle_s`
1.2 s (= 4τ card floor) replaces the 3 s default as the post-step dwell,
`delay=0` — the 5 mT step ramp (~2.3 s) + 1.2 s settle + reads ≈ 3.9 s/pt.
Stated bend: settle_s is a dwell knob, not a safety surface; 3 s default
would add ~40 min for nothing at this step size.

**Cost**: 5 min ramp-in + 1389 × ~3.9 s ≈ **95–105 min**. Checkpoints:
first ~50 pts (sens railing / leakage at 20 nA / T stability), then
periodic via hera-watch; abort on railing (retune sens, restart — cheap
early), leakage off pA floor, or T runaway. E1 auto: gates and B inside
committed validators, preconditions asserted.
