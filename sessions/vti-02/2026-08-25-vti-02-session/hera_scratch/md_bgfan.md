## HERA — back-gate calibration fan, measured on the descent from 6 T

`recipe: measurements/landau-fan-vti.md`. Second calibration fan; run 5 gave the
top gate, this gives the back gate, and it does so **on the way home** rather
than as a separate traverse.

**What run 5 settled.** The Landau rays converge on a single point:
seven tracked rays, six of the seven B = 0 intercepts inside ±9 mV, giving
**CNP at V_tg = +0.021 ± 0.007 V** (at V_bg = 0). Their slopes fall in near-exact
ratio **4 : 8 : 12 : 16 : 20 : 24** with slope/ν consistent to **1.4%** across all
seven, giving **α = 0.01540 V/(T·ν)** and hence, from degeneracy alone,
**c_tg = 2.515×10⁻³ F/m², dn/dV_tg = 1.570×10¹² cm⁻²/V** — 0.90× the geometry
prior, implying a top-gate hBN of 10.6 nm against the card's 9.5 nm. This is the
`cnp-and-dline-calibration` Step-5 lever-arm upgrade: the top-gate scale is now
**data-grade, not prior-grade**.

Three things follow, and the third is why this cell exists.

1. **One CNP, not two.** A single convergence point retires the two-doping-domain
   hypothesis, and with it the confound that two domains' SdH tones would
   masquerade as the ABAB two-Fermi-surface signature. That was the question the
   fan was launched to answer.
2. **Neither zero-field ridge is the CNP.** Ridge A (−0.203) and ridge B (+0.113)
   flank the true CNP at +0.021 — which is the shallow R_xx *minimum* visible in
   the very first Gate C leg. R_xx is locally minimal at charge neutrality with
   maxima on either side. That explains everything that failed at zero field: the
   ridge slopes never matched the geometry prior and ridge B was measurably
   curved because **they were never constant-density loci**. A semimetal with
   overlapping electron and hole bands has exactly this shape, and ABAB
   tetralayer is predicted to be one — but the investigation is explicit that CNP
   character is not a stacking read (survey §5 gives three candidate parents), so
   this is an observation to test, not evidence to bank.
3. **The top gate alone cannot reach the design density.** With the measured
   lever arm, the V_bg = 0 cut spans only **n ∈ [−0.50, +1.54]×10¹² cm⁻²**. The
   investigation needs |n| ≳ 2–3×10¹² for the ABAB and ABCA templates to
   separate — at +1×10¹² ABAB genuinely mimics an ABCA singleton within the scale
   prior. **The campaign therefore depends on the back gate**, and c_bg is still
   unmeasured.

**This measurement.** Same method, other gate: V_bg fast at fixed V_tg, B slow.
Fixing V_tg at the measured CNP (+0.0216 V) puts charge neutrality at V_bg = 0,
centring the fast axis on it, and the full committed back-gate window then
reaches **both carrier signs** — roughly n ∈ [−1.8, +2.7]×10¹² on the geometry
ratio, far better coverage than the top-gate cut and the first look at the hole
side the investigation wants spot-checked. Output: c_bg absolutely from LL
spacing, plus a second point on the CNP line, which with run 5's point fixes the
line's slope — the ratio that the zero-field map could not deliver.

**B descends 6 → 1 T in six rows.** The rig card's rule is never to re-traverse
without a reason; the magnet has to come down anyway, so the descent is measured
instead of wasted (the base recipe's "plan the direction so the fan ends where
the next measurement needs it"). Six field rows also give long lever arms for ray
fitting, and ending at 1 T leaves a short ramp to zero for close-out.

**Sampling.** 301 points over the 3.3 V window (11 mV). Predicted LL spacing at
6 T is ≈0.43 V per Δν = 4 on the geometry ratio, so ~8 periods across the window
at ~39 points per period — comfortable, and the *measured* spacing is the output
so a wrong prediction costs resolution, not correctness.

**Cost:** descent 5 T / 0.137 T·min⁻¹ ≈ 37 min, grid 6 × 301 × 0.87 s ≈ 26 min.
**ETA 1h15m.**

**Carried caveat.** R_xx goes slightly negative at deep minima (≈ −20 Ω),
consistent with a ~0.5% R_xy admixture in the B_1−B_2 pair (h/8e² ≈ 3.2 kΩ at
ν = 8). Ordinary Hall-bar geometry imperfection, and it does not move minima
positions — but separating R_xx from R_xy properly needs ±B symmetrisation, and
every run this session is single-polarity. That is a real constraint on the
eventual FS-count fan and belongs in the output contract's hedges.
