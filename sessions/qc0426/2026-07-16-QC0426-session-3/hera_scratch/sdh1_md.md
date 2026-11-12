## HERA — SdH spot check 1/2: hole side, n = −6e12, D = 0 (`sdh-spot-check`)

Investigation step 3. Fixed-(n, D) field sweep, **uniform in B** (blocking rate-limited magnet branch): ΔB = Δ(1/B)·B_lo² with Δ(1/B) = 1/(3·F_L) at F_L = (h/4e)·6e12 = **62.0 T** → ΔB = 5.38 mT at B_lo = 1.0 T → **1303 pts, 1 → 8 T**. B_lo = 1.0 T sits below the expected onset (T_e ≈ 8 K on this rig pushes onset well above the ~0.1 T heuristic; ħω_c ≳ kT already at ~0.3 T, so quantum lifetime — not thermal smearing — will set it); the onset is *measured* here, not assumed. δF = 1/(1/B_onset − 1/8): 1.14 T if onset 1 T, 1.85 T if 1.5 T — the ABA partition (f_ML expected several T at this n) resolves if onset ≲ 1.5–2 T.

**Gates**: (V_tg, V_bg) = (−2.8115, −2.1898) — run-4 calibration, D = 0. **Drive**: card high-|n| standard 2 V → 20 nA @ 13 Hz. **Sens**: sr1/sr2 5e-5 (2.5 kΩ ceiling at 20 nA = ×70 MR headroom over the 35 Ω anchor from run 5; B = 0 signal ~1.4% FS — grainy only below onset, outside the FFT window; clipping at high B is the unrecoverable failure, so headroom wins), sr3 5e-5 (Rxy ≈ 833 Ω at 8 T), sr0 unchanged. **Dwell**: `magnet.settle_s` 3 → **1.2 s** for this sweep (= 4τ; the lock-in tracks through the blocking ramp, each step 5.4 mT ≈ 2.4 s of ramp; documented tunable, restored in `finally`).

**Magnet plan**: position 0 → 1 T (~7 min), sweep up to 8 T; **ends at 8 T** — spot check 2 (electron side) rides 8 → 0 down. No re-traverse.

**Wall-clock**: 1303 × (2.35 ramp + 1.2 settle + ~0.35 reads) ≈ 85 min + 7 min positioning ≈ **1.6 h, realistic 1.7–1.8 h**.

**Checkpoints**: first rows (MR shape, no clip, drain steady), then ~mid-sweep (any visible QO above the noise; sens headroom vs MR trend). Abort: railed channel, drain sag, leakage.
