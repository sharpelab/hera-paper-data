# Step 2 feasibility (investigation tetralayer-stacking-fs-count), computed 2026-08-21 ~21:20

Model table (fs_count_b0, u_D = 0; F in T, m* in m_e):

| n [e12] | F_L | ABAB (light, heavy) | ABCA |
|---|---|---|---|
| +0.7 | 7.2 | 0.4/0.029, 7.6/0.057 | 7.2/0.176 |
| −0.7 | 7.2 | 2.3/0.076, 5.0/0.034 | 7.2/0.665 |
| +1.5 | 15.5 | 2.0/0.023, 13.5/0.057 | 15.5/0.104 |
| +2.0 | 20.7 | 3.6/0.024, 17.1/0.058 | 20.7/0.089 |
| +2.5 | 25.8 | 5.1/0.026, 20.7/0.059 | 25.8/0.081 |
| +3.0 | 31.0 | 6.7/0.027, 24.4/0.060 | 31.0/0.076 |
| +3.5 | 36.2 | 8.3/0.028, 27.9/0.061 | 36.2/0.073 |
| −1.5 | 15.5 | 7.5/0.033, 8.0/0.074 | 15.5/0.966 |
| −2.0 | 20.7 | 9.1/0.033, 11.6/0.075 | 20.7/0.208 |

Design at the electron design point n ≈ +3.0e12 (D = 0 line reaches ≈ +3.5e12 on the partial-map calibration):
- Nyquist on F_L = 31 T: Δ(1/B) ≤ 1/62 = 0.016 T⁻¹; design 1/(3·F_L) = 0.0108 T⁻¹.
- Partner tone 6.7 T, ≥ 5 periods: 1/B span ≥ 0.75 T⁻¹ → with B_max = 10 T, B_lo ≤ 1.18 T.
- Heavy ABAB (24.4) vs ABCA singleton (31): separation 6.6 T; δF ≤ 3.3 T (2·δF rule) → 1/B record ≥ 0.30 T⁻¹ → B_onset ≤ 2.5 T at B_max = 10 T.
- Uniform-B (blocking magnet): ΔB = Δ(1/B)·B_lo² — at B_lo = 1.5 T: 24 mT; 1.5 → 10 T = 355 pts; from 0 T: 417 pts.
- Thermal damping (T_e ≈ 8 K rig-card figure): X = 14.69·m*·T/B; m* = 0.06 at 5 T → X = 1.4 (amp 0.74); at 2 T → X = 3.5 (amp 0.21). Light tone m* 0.027: X = 0.6 at 5 T. Heavy/ABCA tones need B ≳ 3 T to be strong.

Hole side at D = 0 is confined to |n| ≲ 1.0e12 by the TG limit (−0.3 V): F_L ≈ 10 T; ABAB predicts a close light pair (2.3 / 5.0 T, m* 0.03–0.08 → visible), ABCA a singleton with m* ≈ 0.5–0.7 m_e → X ≈ 12 at 5 T / 8 K: invisible. A hole spot check is therefore one-sided evidence: tones present → ABAB-consistent; absent → uninformative (resolvability cited).

Timing: spot check at ΔB = 24 mT, 0 → 10 T: ramp floor 73 min + 417 × (3 s settle + 0.7 s dwell + 0.25 s read) ≈ 27 min → ~1h40m. Hole spot check rides the magnet 10 → 0 T at the hole gate point: same cost.
