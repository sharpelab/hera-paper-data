**Read — three results, in order of importance.**

**1. One CNP, not two.** Seven LL rays were tracked across field; six of their
seven B = 0 intercepts agree to ±9 mV. A Landau fan radiates from charge
neutrality, so a *single* convergence point means a **single** charge-neutrality
point. This retires the two-doping-domain hypothesis carried since Gate C — and
with it the confound that mattered: two domains at different densities would each
contribute their own SdH frequency, and **two tones from two domains would
masquerade as the two Fermi surfaces that are precisely the ABAB signature this
campaign exists to detect**. That risk is now excluded for this contact pair.

**2. The CNP is at neither zero-field ridge — it is between them, at the R_xx
minimum.** Ridge A (−0.203 V) and ridge B (+0.113 V) flank **V_CNP = +0.021 ±
0.007 V**, which is the shallow resistance *minimum* sitting between them —
visible in the very first Gate C leg (201 Ω at V_tg ≈ +0.02) and walked past at
the time. So R_xx is locally **minimal** at charge neutrality with maxima on
either side.

This retrospectively explains every zero-field failure: the ridge slopes never
matched the geometry prior, and ridge B was measurably curved (slope drifting
−0.767 → −0.594, quadratic term cutting the residual 18.1 → 3.1 mV), **because
neither ridge was ever a constant-density locus**. A curved locus cannot be
constant-n — n is linear in both gate voltages — and that was the correct
falsification; what was missing was the alternative, which field supplied.

A semimetal with overlapping electron and hole bands produces exactly this shape:
minimum resistance where both carrier types coexist, maxima where each pocket
empties. ABAB tetralayer is predicted to be such a semimetal (the FS-count model's
own note: "ABAB is semimetallic near the CNP; for small |n| tiny electron and hole
pockets coexist"). **This is an observation to test, not evidence to bank** — the
investigation is explicit that CNP character is not a stacking read (survey §5:
three candidate parents), and it enters the record as consistent-with at most.

**3. The lever arm is now data-grade — and it says the campaign needs the back
gate.** The ray slopes fall in near-exact ratio **4 : 8 : 12 : 16 : 20 : 24** with
slope/ν consistent to **1.4%** across all seven rays — a clean 4-fold-degenerate
ladder, and independent support for the g = 4 assumption the Luttinger reference
frequency F_L = (h/4e)·n rests on (the investigation's degeneracy audit). Hence
α = 0.01540 V/(T·ν) and **c_tg = 2.515×10⁻³ F/m², dn/dV_tg = 1.570×10¹² cm⁻²/V**
— 0.90× the geometry prior, implying top-gate hBN ≈ 10.6 nm against the card's
9.5 nm. This is the `cnp-and-dline-calibration` Step-5 quantum-Hall upgrade: the
top-gate scale is **data-grade, no longer prior-grade**.

The consequence is a constraint, not a win: the V_bg = 0 cut spans only
**n ∈ [−0.50, +1.54]×10¹² cm⁻²**, well short of the |n| ≳ 2–3×10¹² where the
ABAB and ABCA templates separate (at +1×10¹² ABAB mimics an ABCA singleton
within the scale prior). **The campaign depends on the back gate**, whose lever
arm is measured next (run 6).

**Method note — two estimators, and why one was discarded.** A per-row
"fundamental LL spacing vs B" fit gave c_tg = 0.999× prior; the ray-slope fit
gave 0.900×. The spacing estimator is **wrong** and its own residual says so:
103 mV rms, with per-row d/B values of 0.016 and 0.124 scattered among 0.061–0.064,
because the observed ladder skips filling factors (Δν of 8 and 4 alternating at
2 T) and no "fundamental spacing" heuristic survives that. The ray fit needs no
such heuristic — slopes are ν·α whichever ν happen to be visible — and closes to
1.4%. An earlier *free* two-parameter (V_CNP, α) integer fit was also discarded:
with both floating it returned filling factors {5, 7, 10, 11, 12, 13, 14, …} with
spacings {1, 2, 3, 6}, i.e. it fits anything. **Constrain, then cross-check.**

**Caveat carried forward.** R_xx runs slightly negative at deep minima (≈ −20 Ω),
consistent with a ~0.5% R_xy admixture in the B_1−B_2 pair (h/8e² ≈ 3.2 kΩ at
ν = 8). It does not move minima positions, so the calibration stands — but
separating R_xx from R_xy needs ±B symmetrisation and every run this session is
single-polarity. That belongs in the output contract's hedges and is a real
constraint on the eventual FS-count fan.
