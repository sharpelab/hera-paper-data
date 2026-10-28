## Runs 6–7 — SdH spot checks at D = 0 (`sdh-spot-check`): two-band structure on both carrier signs

Run 6 (`data/6`): electron side, n = +3.2×10¹² cm⁻², B 0→10 T. Run 7 (`data/7`): hole side, n = −1.2×10¹², riding 10→0.3 T. Calibration: run 5 (`hera_scratch/cal_run5.json`). Raw R_xx(B) first, then `sdh_onset` tone tables and FFTs in 1/B with the full-degeneracy Luttinger marks F_L = nh/4e.

**Read (lands the handoff gap — runs 6/7 were measured but never analyzed on the page):**
- **Electron (run 6):** oscillations persist to the 0.3 T record edge (light carriers). Two tone families: **F ≈ 7.1 T** with its 2×/3×/4× harmonic ladder, and **F ≈ 30 T** (dominant above 3 T, own harmonic ladder at 60/90/120 T). Sum 7.1 + 30 ≈ 37 T vs F_L = 33.1 T — Luttinger-consistent two-band partition to within ~12% (inside the geometry-prior calibration uncertainty).
- **Hole (run 7):** multi-tone: ~4.7–5.3 T dominant below ~2 T, 6.6 / 8.5 / 12.3 T tracked, FFT above 3 T peaking at ~12.9 T ≈ F_L = 12.4 T. Near-CNP: tones close, harmonic/fundamental assignment ambiguous at a single density.
- **Take:** two incommensurate frequency families on the electron side and multi-tone holes ⇒ **multiple Fermi surfaces at D = 0 on both signs — leans ABAB (Bernal), disfavors single-band ABCA**; not yet a call. A single-n FFT can't separate fundamentals from harmonics/breakdown or give the degeneracy partition — that is the Landau fan's job (plan step 4).
