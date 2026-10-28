## HERA — Landau fan, hole side, D = 0 (`landau-fan-vti`), investigation step 4

Spot checks read (ana nb): hole = pair template {~4 T ML, ~27–28 T BL} + a
~33 T tone at F_L; electron = bright singleton 33.2 T fixing the global
scale λ ≈ 1.07; forks: harmonic-vs-BL in the 23–28 T band, and the
F_L-tone origin (breakdown | ABC domain | mixing). **Fan side = hole**:
earliest onset (0.77 T, measured), both pair members + the F_L tone live
there — the combinatorics and the Luttinger partition F(n) need exactly
that. The electron singleton is already characterized for the overlay.

**Floored design (single fan):**
- **B**: 0.77 → 8 T (B_lo = `sdh_onset` measured, not eyeballed), uniform
  1/B (`field_invB`), **141 rows**; Δ(1/B) = 8.33×10⁻³ T⁻¹ = ⅓-Nyquist on
  40 T (covers the λ-scaled supra tone at n_max). δF = 0.85 T.
- **n**: −0.5 → −3.5×10¹² cm⁻² (n_max = overlay-validity clamp; low-|n|
  floor at 0.5 — below it F_L < 5 T merges with the ML band and the
  low-n × high-B corner blows the dynamic range), **101 columns**,
  Δn = 0.03×10¹² ≥ 2 pts/ray for B ≥ 0.86 T.
- **Sens (worst corner −0.5e12 × 8 T)**: sr1 5×10⁻⁴ (25 kΩ), sr2 2×10⁻⁴
  (10 kΩ), sr3 5×10⁻⁴ (|R_xy|max 10 kΩ). Trade: 0.76 Ω quantization on sr1
  at the metallic corner — sr2 (0.3 Ω) is the fine-grain FFT channel there.
- **Direction**: ascending from 0.77 T (magnet sits at 0.70 — no
  re-traverse); ends at 8 T for the high-field/Středa read and any LK
  descent to follow.

**Cost**: 141 × (101 × ~1.45 s + ~4 s row overhead) + 53 min traverse ≈
**6.8 h** (per-point from runs 5/6 measured 16.3 rows/min at same fp set;
headline 6.8–7.5 h). Checkpoints: first rows, then every ~10 rows
(hera-watch); abort criteria: railing at the low-|n| corner, leakage off
floor, T excursion, all-flat channel. E1 auto: axes inside validators
(asserted in-cell), B cap respected by the grid.
