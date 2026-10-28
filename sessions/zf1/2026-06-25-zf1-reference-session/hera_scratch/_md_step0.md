## HERA — Step 0: effective-zero field B_eff0 (do ONCE)

Run 0 confirmed the dome: Rxx = 0.60 Ω at n=−5.00×10¹¹, D=−0.64 (the prior optimum, mV-exact), <75 pA leakage, 34 mK. Gates are parked there now.

**This cell** locates the cooldown's trapped-flux-compensated **B=0** at the optimum — needed because B_c⊥≈1.8 mT means nominal-0 isn't paper-grade. Rxx vs B⊥ as **two one-sided cuts** (+5→0 and −5→0, 0.1 mT step, ~4 s/pt, AC 1 nA, DC bias 0). Each half is swept **monotonically toward 0** — field-discipline-compliant; the ramps to ±5 mT are positioning, not measurement. I take B_eff0 = the fitted symmetric-dip center; ±0.1–0.2 mT is plenty (flat bottom). This is **one-time** — trapped flux is fixed at these scales, so no re-locating after Fig 4 / Fraunhofer.

**Note (field discipline):** I'm *not* using a cross-zero −5→+5 pass here — that's authorized only for Fig 2 (Fraunhofer). The two-halves route carries a small inter-half remanence mismatch (it gave the +1.4/−2.15 mT asymmetry in prior runs 11/12), but that's well inside the flat dip bottom and below the precision B_eff0 needs. If you'd rather take a single cross-zero pass for a cleaner center, say so and I'll re-cast it.

**Preconditions (printed/asserted at top):** T<60 mK, |B|<5 mT at start, gates within 10 mV of the optimum, heater=0. **~8–9 min** total (2×51 pts × ~4 s + two positioning ramps/settles). Two data files (the two halves). Ends with magnet at 0, gates at the optimum. I'll fit both halves for B_eff0 and report before Fig 1.
