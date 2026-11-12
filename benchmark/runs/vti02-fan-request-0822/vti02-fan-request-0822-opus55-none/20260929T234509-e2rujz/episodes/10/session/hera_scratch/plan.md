# vti-02 stacking plan (ABAB / ABCA / ABCB) — living doc

Rewritten 2026-08-23 by the incoming instance. The prior instance's plan file was not in `hera_scratch/`, so steps 0–3 are reconstructed from the notebooks.

Contact pair: one only, sr1 = B_1−B_2 (hardwired). Region-resolved = this pair, plus the two series regions A/B seen in run 5.

## Done
- **0. Gate C** (runs 0–3): alive, no leakage, Rxx 60–330 Ω. Two series CNPs.
- **1. Gatemap** (run 5; run 4 railed): ridge A (main) plus parallel ridge B, electron-doped by 0.43e12. Calibration: ratio 0.773, c_tg from the 9.5 nm prior, n_off −0.089, D_off −0.013 (taken from the R_CNP(D) minimum). **Caveat:** that D_offset method assumes R_CNP is symmetric in D. For ABCB (polar) the assumption is circular, so D = 0 is provisional until the fan's ±D symmetry test.
- **3. SdH spot checks** (run 6 e +3.2e12, 0→10 T; run 7 h −1.2e12, 10→0.3 T):
  - n scale closes to F_L within about 1 %.
  - Sub-F_L fundamentals: 7.2–7.5 T (0.22 F_L) at e+3.2; 5.0 / 6.8 T at h−1.2. Both onsets below 0.5 T.
  - Lean: more than one Fermi surface, which is against single-band ABCA.

## Next
- **4. D = 0 Landau fan** (now).
  - Grid: n fast along D = 0 over −1.25 → +3.25e12 (0.025 step, 181 pts); B slow 0 → 8 T at 0.1 T (81 rows).
  - It establishes:
    - (a) the LL degeneracy sequence and the ν-values of the strongest gaps near the CNP: 16-fold zero manifold with a clean ±8, ±12 … sequence and no crossings means ABCA; two LL families with crossings means ABAB/ABCB;
    - (b) tone count and F_i(n) from per-column 1/B FFT (3–8 T, ΔF ≈ 5 T) and per-row FFT in n;
    - (c) whether region B's second fan (apex n ≈ −0.43) is visible.
  - Ends at 8 T.
- **5. Finite-D fan riding down 8 → 0 T** (detour-free: the magnet has to come down anyway).
  - Same n-window, at a D inside the box. At n ≈ 0 the box allows D from −0.11 to +0.29 V/nm.
  - Purpose: ±D symmetry test of the LL spectrum. ABCB is polar, so its fan should differ between +D and −D. ABAB is symmetric in D, with crossings that move with |D|.
  - Pick +D or −D after reading the step-4 fan. Budget about 5–6 h; |D| ≤ 0.1 keeps both signs in reach for a later mirror.
- **6. Call** in the ana notebook per the output contract.

## What would change my mind
- A clean ABCA-like sequence in the fan (dominant ν = ±8 gap, single F = F_L tone across n): the multi-tone read at the spots was then a mosaic/region artefact, and ABCA comes back.
- ±D asymmetry of the LL spectrum at matched |D| → ABCB over ABAB.
- Two tones whose F-ratio vs n follows the two-BLG-like-band (λ = 1.618 / 0.618) model → ABAB.

## Pricing basis
- Per point ≈ 1.2 s (fast_delay 1.0 s + reads + autorange reads; run 5: 1.17 s/pt).
- Field step: 3.1 s + ΔB/0.137 T/min (runs 6/7).
- Flyback about 3.6 s. slow_delay 3 s.
