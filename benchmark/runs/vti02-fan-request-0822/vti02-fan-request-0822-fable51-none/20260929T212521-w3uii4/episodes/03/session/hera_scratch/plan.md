# Plan — vti-02 stacking call (ABAB / ABCA / ABCB)

*Reconstructed 2026-08-23 05:xx by the incoming instance (no plan.md was on disk from the
first instance; steps 0–3 are inferred from the notebooks and re-stated here). Kept current
as data lands.*

## Physics the call rests on (D = 0, single contact pair B_1–B_2)

| stacking | low-E bands at D = 0 | LL fingerprint (fan along n at D = 0) | SdH at fixed n |
|---|---|---|---|
| **ABAB** (Bernal) | two bilayer-like parabolic bands, light m₁ ≈ 0.03 mₑ + heavy m₂ ≈ 0.06 mₑ (γ₁-split) | two interpenetrating 4-fold fans from the CNP; LL crossings fill in some Δν = 4 gaps; lowest LLs 8+8-fold | **two tones** F₁ + F₂ = F_L, the light tone visible from low B |
| **ABCA** (rhombohedral) | one flat quartic band, heavy m* ≳ 0.07 mₑ | one 4-fold fan; zeroth LL 16-fold → first gap at ν = ±8, then 12, 16, …; no crossings | **one tone** at F_L, late onset (heavy) |
| **ABCB** (mixed) | monolayer-like Dirac + trilayer-ABC-like cubic band | Dirac fan (√B, 4-fold, LL0 4-fold) crossing a 12-fold-LL0 cubic fan; ν = 2/6-type offsets | two tones, the Dirac one with F ∝ n (light) |

Complications on the table: (a) region B (second CNP ridge, run 5, electron-doped by 0.43×10¹²
relative to A) is in series with A along B_1–B_2 → every feature may appear twice, shifted
+0.43×10¹² (a ×1.13 tone copy at n = 3.2); (b) absolute density scale is a geometry prior
(c_tg from 9.5 nm) — run-6 QH minima imply n_true/n_cal ≈ 1.08; the fan's own ν-lines will
fix the scale; (c) T_e ≈ 8 K kills heavy-mass tones below ~1.5 T (LK).

## Steps

0. **Bring-up / VERIFY / grant** — done (measure cells 31–32; `session_notes.md`). E1 engaged.
1. **Gate C liveness + gross leakage** (`gate-current-sanity-check`, runs 0–3) — done; contact
   pair alive, R_CNP ≤ 330 Ω at D ≈ 0, no leakage above ~100 pA baseline.
2. **0 T gatemap → CNP + (n, D) calibration** (`gatemap`, run 5; run 4 railed) — done. ratio
   c_bg/c_tg = 0.773, n_offset −0.089×10¹², D_offset −0.013 V/nm; D = 0 window inside the box:
   n = −1.2 … +3.2×10¹². A second parallel ridge (region B) noted.
3. **SdH spot checks** (`sdh-spot-check`, run 6 e-side n = +3.2, run 7 h-side n = −1.2) — done,
   analysed in `hera_scratch/sdh_spot.py` → to be landed in ana. Run 6: QH minima at 5.93 /
   7.16 T (Δν = 4 → F ≈ 34.5 T, n ≈ 3.45), dominant light tone 7.2 T from 0.5 T with
   harmonics, plus ~30 T (≈ F_L). Run 7: 12.3 T (= F_L) + 6.8 T (F_L/2) + 3.5 T. **Read so
   far:** at least two frequencies at n = +3.2 with a light-mass low-B tone → disfavors a
   single-band ABCA at D = 0; but a 1D cut cannot separate "second band" from "region B copy"
   or harmonics. Needs the fan.
4. **Landau fan at D = 0** (`landau-fan`) — **next**. B slow 1 → 10 T (0.15 T, 61 rows), fast
   axis co-swept (V_tg, V_bg) along D = 0, n −1.2 → +3.2 (89 pts, Δn = 0.05). Establishes:
   the ν-line sequence out of the CNP (first gap at ν = 4 / 8 / 2 → degeneracy of LL0), the
   number of fans (1 vs 2), crossings, and the absolute n scale (line slopes ν e/h). Also
   separates region-B copies (they emanate from a CNP shifted by −0.43×10¹²) from genuine second
   bands (same CNP). Would change my mind: a single clean 4-fold fan with the first gap at
   ν = 8 → ABCA; two fans from one CNP with crossings → ABAB; a √B-like set → ABCB.
5. **Finite-D fan or D-cut at fixed B** (`landau-fan` at D ≈ ±0.15 V/nm, or a (n, D) map at
   fixed B = 10 T riding the magnet) — only if step 4 is ambiguous: ABCA's LL0 splits with D
   into layer-polarized levels (ν = 0 gap grows monotonically); ABAB's D-response is the
   bilayer-pair pattern.
6. **T-dependence of the light tone (LK mass)** — optional discriminator (m* 0.03 vs 0.07):
   1D B sweeps at n = +3.2 at T ∈ {base, 4, 6, 8, 12} K via `set_both(T, 0.95)`. Only if the
   fan leaves mass as the deciding fact.
7. **Call** — final ana cell per the output contract (per-region verdict, evidence with run ids,
   hedges). Then `return-to-initial` on the operator's ask.

## Timing calibration used
- gatemap run 5: 4158 pts in 81 min → 1.17 s/pt at fast_delay 1.0 s (reads ≈ 0.2 s).
- run 6: 921 B-points 0 → 10 T in 2 h 0 m → ≈ 3.8 s/pt overhead beyond the 73 min ramp.
- magnet 0.137 T/min bare; 3 s settle per set.
