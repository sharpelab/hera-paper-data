# vti-02 stacking call — plan (HERA, written at handoff 2026-08-23 ~05:40)

*The previous instance left no plan.md; this reconstructs the arc from the notebooks and
data, and carries it forward. Keep current as data lands.*

## Discriminators (what separates ABAB / ABCA / ABCB in 4L graphene)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| SdH tones at D = 0 vs n | **two** tones ∝ n (light + heavy bilayer-like bands), ratio ≈ 0.28 : 0.72 (γ1·0.618 vs γ1·1.618), sum = F_L | **one** tone = F_L above the Lifshitz density (F_L/3 pockets only at low n) | two bands but not with the ABAB fixed ratio / sum structure; no inversion symmetry |
| Landau fan at D = 0 | two interleaved LL families → **LL crossings** (degeneracy 4↔8 alternation) at finite n | fan from CNP with no D = 0 crossings; 4N = 16-fold zero LL → first gaps ν = ±8 | crossings, but at positions not matching the ABAB two-band model |
| CNP vs D (0 T) | semimetal; modest R_CNP growth with |D| | large D-opened gap (insulating at |D| ~ 0.2 V/nm) | intrinsic gap / R_CNP(D) **asymmetric** in ±D (spontaneous polarization) |

## Arc

- [x] **Gate C** — runs 0–3: alive, no leakage, Rxx 60–330 Ω.
- [x] **Step 1 — gatemap** — run 5 (run 4 aborted rail): ridge A (dominant) + parallel ridge B (region B electron-doped by 0.43e12 vs A — series-mosaic confound).
- [x] **Step 1b — calibration** — ratio c_bg/c_tg 0.773 (data), c_tg = 2.796 mF/m² (prior — **absolute scale unverified**), n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex). R_CNP rises 300 Ω → 2.4 kΩ at D = +0.25 V/nm, saturating: modest for ABCA 4L (expect insulating) — weak lean away from ABCA, confounded by the mosaic.
- [x] **Step 3 — SdH spot checks** — run 6 (n = +3.2e12, 0→10 T), run 7 (n = −1.2e12, 10→0.3 T). Run 6: tones 7.2 T and 22.2 T (ratio 0.245 : 0.755, sum 29.4 T vs prior F_L 33.1 T → prior c_tg ~11 % high if these are the two bands), plus 29.5–31.3 T content (4×7.2 harmonic, or a singleton F_L — ambiguous). QH minima near zero Rxx from ~2 T. Run 7: 3.5 / 6.8 / 12.3 T, messy near the CNP. Onset ≈ 0.5–1.3 T. **Not landed in ana at handoff — land it.**
- [ ] **Step 4 — Landau fan at D = 0** (run 8, now): Rxx(n, B), n fast −1.25 … +3.25e12 along D = 0 (151 pts, δn = 0.03e12), B slow 1 → 10 T, 1/B-uniform (δ = 0.009 T⁻¹) capped at ΔB = 0.2 T (115 rows). ~8 h. Establishes: (a) per-column FFT → F_i(n): count of tones, their ratio, sum-rule vs F_L; (b) QH minima lines in (n, B) → ν sequence and degeneracy, **absolute density calibration** (dn/dB = νe/h) independent of the geometry prior; (c) LL crossings at D = 0 (ABAB signature); (d) region-B fan from n_A ≈ −0.43e12 (mosaic, identify and discount).
- [ ] **Step 5 — fixed-B (n, D) map at high field** (starts at 10 T where the fan ends): D-driven LL crossings and **±D asymmetry** (ABCB test; ABAB/ABCA symmetric). Size after the fan.
- [ ] **Step 6 (optional)** — 0 T R_CNP(D) over the full ±D reach for asymmetry, if step 5 is ambiguous (cheap-ish, gate-only).
- [ ] **Call** — final ana cell per the output contract; then close-out (`return-to-initial`).

## What would change my mind

- Fan FFT shows a single tone tracking F_L (after QH calibration) across n → ABCA, overriding the run-6 two-tone lean.
- Two tones whose ratio drifts strongly with n or whose sum ≠ F_L → not simple ABAB; consider ABCB (check ±D asymmetry in step 5).
- The 7.2 T tone tracks region B's density (offset fan origin at n_A ≈ −0.43e12) → it's mosaic, not a second band.
- No crossings at D = 0 and a clean 4-fold sequence from ν = ±8 → ABCA.
