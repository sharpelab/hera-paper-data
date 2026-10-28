**Read.**

**The cap ratio is measured, and it vindicates geometry over the ridges.**
Seven back-gate rays give α_bg = 0.01850 V/(T·ν) → **c_bg = 2.094×10⁻³ F/m²,
dn/dV_bg = 1.307×10¹² cm⁻²/V** (implied back-gate hBN 12.7 nm vs the card's
11.0). Combined with run 5:

| | c_bg/c_tg |
|---|---|
| **measured (runs 5 + 6, quantum Hall)** | **0.832** |
| geometry prior (t_tg/t_bg = 9.5/11) | 0.864 |
| zero-field ridge slopes (run 4) | 0.58 – 0.67 |

The measured ratio lands within 4% of the geometry prior and nowhere near the
ridge slopes. That is the independent confirmation, from a completely different
observable, that **the zero-field ridges were never constant-density loci** —
the conclusion the curvature test forced but could not replace. Both lever arms
are now data-grade: the `cnp-and-dline-calibration` Step-5 quantum-Hall upgrade
is complete, and the (n, D) frame no longer rests on the geometry prior.

**Quality, honestly.** This fan is measurably worse than run 5. Slope scatter is
6% (vs 1.4%), and the ray **intercepts** barely converge — only 3 of 7 fall
within tolerance, giving V_CNP(bg) = +0.039 ± 0.034 V against run 5's ±0.008.
The reason is structural, not statistical: this cut sweeps D from +0.16 to
−0.24 V/nm, so the gap opens along it and the LL character changes with position,
whereas run 5's cut spanned only −0.05 to +0.16. **Ray slopes are robust to that;
ray intercepts are not.** So the session takes the lever arm from run 6 and the
CNP from run 5, and does not average them.

The observed filling factors here are ν = 8, 16, 20 — the ladder skips, as it did
in run 5, which is why no "fundamental spacing" estimator was used on either fan.

**The range verdict — what the campaign can and cannot reach.** With both lever
arms and the CNP at (V_tg, V_bg) = (+0.020, 0), the D = 0 line is
V_bg = V_tg/0.832 and along it n = 3.14·V_tg − 0.032 (10¹² cm⁻²). Clipped to the
committed gate windows:

> **n ∈ [−0.97, +3.11] × 10¹² cm⁻² at D = 0**

- **Electron side: reaches +3.11×10¹²** — inside the |n| ≳ 2–3×10¹² window where
  the ABAB pair (heavy tone ≈0.72–0.79·F_L plus a partner carrying 21–28%) and the
  ABCA singleton (one tone at F_L) genuinely separate. **The FS count is feasible
  on this side.**
- **Hole side: only −0.97×10¹²** — inside the investigation's named exception
  regime, where the near-CNP hole pair is close and balanced and short 1/B records
  read as beat-like. A hole-side measurement here cannot discriminate ABAB from
  ABCA and must be reported as range-limited, not as a null.

That asymmetry is a gate-window fact, not a device fact, and it is the single
most important design constraint to carry into the next session: **the top-gate
window is what limits the hole side**, since D = 0 forces V_bg = 1.20·V_tg and
V_tg bottoms out at −0.3 V.

**Next:** run 7, the investigation's Step 3 SdH spot check, at five (n, D = 0)
points on this calibration.
