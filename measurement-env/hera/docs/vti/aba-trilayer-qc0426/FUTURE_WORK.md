# ABA forward model — what the live run taught us, and where to take it

*Companion to `README.md`. Written after the model's first live deployment:
the 2026-06-10 HERA session on QC0426 (VTI), where the session brief made it
"the primary arc-reading method — model-overlay first, always" (raw-render
vision and untemplated ridge detection were both demonstrated-unreliable on
these features). This doc records how it actually performed and proposes a
prioritized roadmap, each item tied to a concrete pain point from that session.*

## What the model was good at (keep doing this)

- **It was most valuable as a skeptic, not a confirmer.** Its two highest-value
  acts in the session were *rejections*:
  - rejected run-3's second ray family as a crossing chain — the in-window chains
    would have needed a density rescale ~2, outside the plausible lever-arm band,
    so the family is a real second fan (aliasing/superposition), not a chain;
  - helped reject run-4's non-dispersing minimum at n≈1.02×10¹² as an N_M=0 dark
    channel — the model co-located only at rescale 0.75–0.87, and that plus
    minima-not-maxima / single-feature / 0.75 T-extent killed the claim.
  A forward model that places *concrete, falsifiable loci* lets a candidate be
  argued down. That is the durable win — bake it into the verify discipline.
- **It works mid-fan**, on however many B-rows have landed, which fit the
  checkpoint-the-long-sweep workflow that emerged as the day's best behavior.

## What limited it (the roadmap targets these)

1. **The free global density rescale α is the central weakness.** Every verdict was
   softened to "co-located at α≈0.8." The session's own conclusion: *the α-fork
   (lever-arm ambiguity) cannot be closed by grid density — it needs plateaus
   (lower T) or a known-density anchor.* Until α is pinned, the model can reject
   but rarely confirm.
2. **On a moderate-mobility device the (n,B) crossing structure is partly below
   resolution.** QC0426 at 1.2 K resolves rays only above ~2 T (vs <0.5 T in the
   paper's 500k-mobility device). The model's home turf — fine crossing chains —
   is exactly what disorder washes out. The result that *did* discriminate came
   from a different primitive: **SdH pockets, not chains.**
3. **It is a D = 0, T = 0, disorder-free model**, compared against D = +0.25 V/nm
   data at finite T with real broadening. Each of those is a modellable gap.

---

## Roadmap (priority = leverage on the next real session)

### P1 — Predict the SdH two-pocket signature (highest leverage)

**What.** Extend the model from "(n,B) crossing loci" to "B = 0 Fermi-surface
pockets and their quantum-oscillation frequencies." From the same band structure:
compute the carrier density in each band (ML, BL) vs total n, convert pocket area
→ SdH frequency f_i = (ħ/2πe)·A_i = (h/4e)·n_i (per spin/valley), and predict
f₁(n), f₂(n), and the sum rule **f₁ + f₂ = f_tot** that maps the total density.

**Why.** This is the discriminator that actually worked. Run-5's per-column FFT in
1/B found two coexisting frequencies + intermodulation — *"arguably the most
sensitive single-particle discriminator on a moderate-mobility device (pockets,
not chains, are the primitive)."* Right now the model predicts the thing that's
hard to see (chains) and says nothing about the thing that's measurable (pockets).
Closing that is the single most useful change: it lets the model **quantitatively
interpret** the FFT — ABA predicts two pockets summing to f_tot with a specific
ratio and n-dependence; ABC predicts a different split. Pairs directly with the
already-landed `hera.analysis.sdh_fft` (the measurement side).

**Effort.** Small–medium. The B=0 band structure is already in `ll_spectrum` (set
B→0 limit or integrate the LL DOS); pocket densities fall out of the same filling
code. ~Half a day.

**Unblocks.** Turns the model into the interpreter for the session's best
discriminator; gives every future moderate-mobility trilayer a quantitative
ABA-vs-ABC pocket test, not just a chain-overlay.

### P2 — Close the lever-arm fork (quantum-Hall ν anchoring)

**What.** Add a routine that, given any assignable incompressible feature (a gap
the model flags as strong, or an operator-supplied known filling), pins
n = ν·eB/h there and thereby fixes α — collapsing the fork. The model already
knows which gaps are deepest/most assignable; surface that as "anchor here."

**Why.** Directly removes the weakness in §2.1. Converts "consistent with at
α≈0.8" into "registered." The session flagged this as the only way to close the
fork short of lower T.

**Effort.** Small. Mostly a helper + a UI/printout for "candidate anchors, ranked
by gap strength," then refit α with the anchor as a hard constraint.

**Unblocks.** Lets the model *confirm*, not only reject.

### P3 — Finite-D modeling (the `delta_field` knob, currently wired but unused)

**What.** Turn on the layer-potential term, calibrate it to the device's D (V/nm)
via the gate capacitances, and predict how crossings move across the D-series
(runs 81–84 already on disk; this session's campaign shape is exactly D-stepped
fans). Output: crossing-loci shift vs D, and which features survive to D≈0.

**Why.** The discriminating regime is D≈0 (where ABA's two ladders are
symmetry-guaranteed and ABC has one); *crossings at finite D no longer uniquely
count as ABA.* The data is at D=+0.25, so we are reading a slightly-broken-symmetry
fan with a D=0 model. Modeling the D-dependence (a) tells us how much to trust the
+0.25 overlay and (b) makes the D-series a quantitative move-with-D test, which is
the cleanest remaining experimental discriminator.

**Effort.** Medium. The term exists; needs the D↔potential calibration and a
D-series driver + validation against runs 81–84.

**Unblocks.** The D-series as a real test instead of a qualitative gesture.

### P4 — Device-specific band-parameter fit

**What.** Let γ₂, γ₅, δ float to QC0426's measured crossing/pocket positions — the
exact procedure Datta et al. used (Supplementary Note 3) — instead of the single
global α. Emit fitted parameters as a device deliverable.

**Why.** Turns co-location into a fit and yields reusable, device-specific band
parameters. **Caveat learned live:** this needs enough *resolved* crossings, and
QC0426 at 1.2 K may not provide them (run-4 densification added zero new minima —
the strong-gap set was already complete). So gate this on the P5 realism check;
on this device the pocket fit (P1) is likely the better-constrained handle than
the crossing fit.

**Effort.** Medium. A least-squares wrapper around the existing loci, with
identifiability diagnostics so we don't over-fit underdetermined parameters.

### P5 — Resolution/realism layer (Dingle + thermal broadening)

**What.** Replace the flat Lorentzian broadening with a quantum-mobility (Dingle)
damping and thermal (df/dE) smearing, parameterized by the device's measured
mobility and T. Output a "what's actually resolvable" prediction: which crossings,
rays, and pockets should be visible at this B, T, and disorder.

**Why.** The session repeatedly hit *"the feature is absent because of disorder,
not physics,"* and once spent a fine-grid run that couldn't help because the
strong-gap set was already complete. A realism layer predicts the resolution
ladder up front — it would have said "don't densify, it can't surface more" — and
keeps absence-of-evidence claims honest (the paper's resolution-ladder table,
made device-specific).

**Effort.** Medium. Broadening is a localized change; the value is in calibrating
it to a measured Dingle temperature / mobility per device.

**Unblocks.** Expectation-setting that saves rig hours and disciplines negatives.

### P6 — Productize into `hera.analysis`

**What.** Fold the model into the `hera.analysis` package (which now hosts the data
layer — `fan_grids`, `resistance_grids`, `sdh_fft` — landed during the session) as
a first-class predictor with a clean API: `(n,B window, params) → {loci, DOS,
pocket_freqs}`. Retire the standalone `compare_qc0426.py` entry-point pattern in
favor of an importable predictor the recipe/agent calls directly.

**Why.** The model is now the sanctioned primary method; it should live next to the
data layer it consumes, with a stable API, so future sessions invoke it without
hand-rolling overlays. Legibility + reuse.

**Effort.** Small–medium, mostly packaging and an API surface.

---

## Suggested sequence

1. **P1 (pockets)** and **P2 (anchoring)** first and together — they convert the
   model from skeptic to confirmer on exactly the device class (moderate mobility)
   where it currently struggles, and they target the two things the live session
   said were missing.
2. **P5 (realism)** next — cheap insurance that disciplines every subsequent claim
   and gates P4.
3. **P3 (finite-D)** when a D-series re-analysis is on the table.
4. **P4 (param fit)** only where resolution supports it (per P5).
5. **P6 (productize)** whenever the API churn settles — ideally fold P1's pocket
   predictor in at birth rather than retrofitting.

## One-line verdict on the tool itself

It did its job: on the hardest possible target (moderate mobility, finite D, a
single ambiguous fan) it kept the team from over-claiming, and the campaign's real
signal came from a measurement (SdH pockets) the model can be taught to predict.
P1 is how it stops being only a skeptic.
