# ★ SESSION CALL — does zf1 (bottom device) superconduct?

*Per `investigations/sc-characterization.md` Step 6, five-part output contract.
Base T 33 mK, B ≈ 0 (single 4-terminal Rxx channel sr3 = 30-31; current-bias 1 nA).*

### 1. Per-candidate verdict (STYLE strength scale)
**The prior-predicted proximity-SC region (hole side, n ≈ −4 to −6×10¹¹ cm⁻²,
|D| ≳ 0.5 V/nm): not-SC — normal correlated metal / D-tuned band insulator
(strong, within coverage).** No second candidate region exists: the full-box
survey shows no low-Rxx pocket anywhere in the accessible (n, D).
**Device-level: no superconductivity found within reach — call is
coverage-limited** (see §3): |D| ≤ 0.76 V/nm (gate-limited) and no field/T/Ic
characterization was warranted (no candidate to characterize).

### 2. Evidence (with coordinates, vs the paper benchmarks)
- **Survey gatemap (run 2, B=0, 33 mK, full validator box):** Rxx(n, D) shows
  the channel CNP ridge (gap opening at high |D|) and uniform metallic ~20 Ω
  elsewhere; **no low-Rxx dome** of the kind s41586 (BLG/WSe₂) reports at
  |D|~0.5–1, n~−4 to −6×10¹¹. Cap ratio pinned 1.189.
- **Clean n-linecuts (runs 5–7), D = −0.60 / −0.45 / +0.45, n = +1→−8×10¹¹:**
  4-wire Rxx is **monotonic, never approaches 0** (global min ~17 Ω, at high
  hole density — trivial metal, not a dip); candidate band ~22–31 Ω at every D.
  Toward the CNP it rises into a **band gap** (264 Ω → >2 kΩ): *high* R, which
  rules out the **failed-SC / anomalous-metal** fork (that needs low-but-finite
  R with a partial drop — not seen).
- **±D asymmetry (the proximity-SC tell, s41586): ABSENT.** D=−0.45 and D=+0.45
  overlap to a few Ω. A WSe₂-proximity SC would appear for one D sign only.

### 3. Confidence + hedges
- **Hallmarks present: none.** No Rxx→0; no nonlinear V(I)/Ic (not measured — no
  candidate); no field response (not measured); no T-dependence (not measured).
- **Searched-and-absent (strong):** low-Rxx SC dome across the *accessible*
  (n, D) at base T, both D signs, fine n-resolution (~4×10⁹ cm⁻²/pt).
- **Not-resolvable / unexplored (the coverage hedge):**
  (a) **|D| > 0.76 V/nm** — gate-limited this cooldown; the upper half of the
  proximity-SC |D| prior is unreached.
  (b) **Normal-state fermiology** (Landau fan / SdH) — needs Tesla-scale field,
  out of this round's 100 mT cap; the parent phase is uncharacterised.
  (c) **Excitation** — 1 nA AC; a very fragile SC could in principle be
  suppressed, though the metallic (not low-but-finite) behaviour argues against.

### 4. What would firm / extend the call
- **Higher |D| access** (thinner-equiv. gating / different cooldown) to cover
  |D| ~ 0.8–1.0 V/nm where the s41586 SC is strongest — the single biggest gap.
- A **higher-field round** for the deferred fermiology (parent state) and, if any
  candidate emerges at higher |D|, the full Ic / B_c⊥ / Fraunhofer / Tc ladder.
- A **lower-excitation** linecut (≤0.5 nA) at the highest reachable |D| as cheap
  insurance against fragile-state suppression.

### 5. Outcome
**A reasoned "no superconductivity within reach this cooldown" — successful,
not a failure.** The device is healthy, well-contacted, (n, D)-calibrated
(ratio 1.189), and behaves as a clean Bernal-bilayer system (D-tuned gap at the
CNP, metallic away from it) with **no SC and no anomalous-metal fork** in the
accessible (n, D) at base T. The open question is **the gate-inaccessible high-|D|
corner of the proximity-SC prior plus the field-deferred fermiology** — a
next-round (higher-|D| / higher-field) question, not more sweeps on this
configuration.
