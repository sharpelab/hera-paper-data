## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti` → `tetralayer-stacking-fs-count`)

**Why this fan.** Spot checks (read in `hera_scratch/ana_spots.py`, `ana_spot6_e.py`; promoted to ana next):

- **Electron side, run 6, n = +3.2:** stable tones at **7.5 / 14.9 / 22.2 / 29.7 T** (+ 59 T ≈ 2×29.7), consistent across FFT windows [1.0–2.0, 7.8] T and background degree 3/5/7.
- **Two readings.**
  - ABAB light + heavy (7.5 + 22.2 = 29.7), with the 29.7 T tone as the sum tone at global scale ≈ 0.90 (F_L = 33.1 × 0.90). Here 14.9 T would be the difference tone or 2 × light.
  - A harmonic comb of a single 7.4 T tone.
- **One density can't tell these apart.** Their n-dependence does: a comb keeps 22.2/7.4 = 3 at every n, while the ABAB partner fraction moves (model: heavy/light ≈ 3.4 at 3.2 → ≈ 5 at 2).
- **Hole side, run 7, n = −1.2:** clean, with the dominant tone 6.6 T ≈ F_L/2 and onset 0.71 T. But the D = 0 line stops at |n| ≈ 1.2 on the hole side (TG −0.3 V limit). That puts it in the recipe's low-|n| exception regime: model pair 5.9 / 6.5 T, unresolvable at δF ≈ 0.8 T.
- **So the fan goes on the electron side, where the templates separate** (Step 2: |n| ≳ 2–3×10¹²).

**Design (recipe step 1, computed):**

- **B_lo = 1.0 T.** `sdh_onset` on run 6's uniform 10 mT record gives the carrying 7.2 T tone as *censored* at 1.00 T, the record edge. So every row carries signal.
- **B_hi = 8.0 T.** This is just below run 6's QH step. The high-B record feeds the Verify B-window split (breakdown vs pocket origin of the ≈F_L tone).
- **Δ(1/B) = 0.00994 T⁻¹.** That is 3.0 points per period at F_L(3.24) = 33.5 T; Nyquist ceiling 50 T. The 59 T harmonic folds to ≈ 42 T, above the F_L band.
- **N_B = 89 rows**, uniform in 1/B.
- **δF = 1.14 T.** The partner gets ≥ 5 periods for f ≥ 5.7 T (n ≳ 2.6) and clears 2δF for f ≥ 2.3 T (n ≳ 1.8).
- **n-axis:** 1.50 → 3.24×10¹², **N_n = 37**, dn = 0.048. That is half the ray spacing 4eB/h at B_lo.
- **Dwell and sensitivity:** fast_delay 1.8 s = 6τ (τ = 0.3 s, 24 dB). sr1 at **50 µV = 5 kΩ FS**. The handoff restored 2 µV, so the cell sets it explicitly.
  - Worst corner is n = 1.5 at 8 T: R₀ ≈ 86 Ω (run 5) × MR ~10–20 (run 6 went ×10), plus a few % Hall admixture (run 6 dips to −33 Ω). That is ≲ 2 kΩ, ≥ 2.5× headroom.

**Coverage trade:**

- **Excluded: the hole side.** It is resolution-limited; run 7 is that read.
- **Excluded: n < 1.5.** The partner falls below 2δF there and ABAB's heavy tone mimics the ABCA singleton. Extending to n = 1.0 costs +31 min.
- **Not taken: pinning a lower onset.** It would lengthen the partner record at n < 2.6 but costs ~+1.5 h on both axes, and the claim doesn't need it.

**Price** (calibrated this session, not inherited):

| Item | Time | Calibration |
|---|---|---|
| Position 0 → 1 T | 7 min | — |
| Ramp 1 → 8 T | 51 min | 437.6 s/T + 3.09 s per set (runs 6/7) |
| 3293 pts × 1.9 s | 104 min | fast_delay + 0.10 s/pt (run 5) |
| 89 row turnarounds × 7.5 s | 11 min | — |
| **Total** | **≈ 2 h 55 m, ≈ 3 h 05 m with the usual overrun** | |

The magnet ends at **8 T, left there**; the LK mass-split follow-up rides it down. Gates park at 0.

**Guards:**
- Leak trip at 1 nA on either gate.
- T trip at 2.0 K.
- Rail counter, print only.

**Checkpoints (`hera-watch`, per row):**
- **First 3 rows (~T+12 min):** R(n) ≈ 60–130 Ω, no rail, gate currents at pA offsets, T at base.
- **Row ~50 (B ≈ 2 T, ~T+1 h 05 m):** a partial per-column FFT on the landed rows to check whether the light-tone trajectory is visible.
- **Row ~76 (B ≈ 4 T, ~T+2 h 05 m):** the claim-grade interim FFT. Continuing to 8 T is the default (~50 min, breakdown split). Abort only if the columns are junk.
