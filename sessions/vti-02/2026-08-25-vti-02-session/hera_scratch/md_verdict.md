# The call — vti-02 stacking, session of 2026-08-24

Per `investigations/tetralayer-stacking-fs-count.md` Step 7. All five parts are
mandatory; a calibrated "cannot tell" is a successful outcome and a confident
call without feature-level evidence is a protocol violation.

## 1. Per-region verdict

> **channel B_1−B_2 (the only live four-terminal pair this cooldown):
> ABAB (consistent-with) — NOT a strong call.**

One region only. The device card's other pairs (T_1–T_4) are dead, so there is
no second region and **no mosaic test is possible on this cooldown**. "Per-region"
here means "the one region we can see".

## 2. Evidence

Electron side, D ≈ 0, T = 1.19 K, B ∈ [1.5, 6.0] T, δF = 2.0 T. Frequencies from
a recurrence count over **18 extraction choices** (6 field windows × 3 background
degrees); "seen k/18" is how often a tone survived.

| n (10¹² cm⁻²) | F_L (T) | dominant tone | f/F_L | partner tone | f/F_L |
|---|---|---|---|---|---|
| +1.80 | 18.6 | 17.81 ± 0.37 (15/18) | 0.957 | 13.23 ± 0.75 (6/18) | 0.711 |
| +2.20 | 22.7 | 20.36 ± 1.29 (15/18) | 0.895 | 7.87 ± 0.55 (3/18) | 0.346 |
| +2.60 | 26.9 | 25.06 ± 0.78 (15/18) | 0.932 | 5.32 (3/18), 19.96 (3/18) | 0.198, 0.743 |
| +3.00 | 31.0 | 22.96 ± 1.87 (16/18) | 0.740 | 7.46 ± 0.84 (9/18), 29.99 ± 0.08 (11/18) | 0.240, 0.967 |

**What supports ABAB:**

- **A pair partitioning F_L.** At n = +3.0, 7.46 + 22.96 = 30.42 T against
  F_L = 31.0 — the **Luttinger sum closes to 2%**, and a 2% downward density
  rescale (inside my own 1.4%/6% lever-arm errors) makes it exact. Fractions
  0.245 / 0.755. The same structure appears at n = +2.6 (0.198 / 0.743, sum
  0.94·F_L).
- **The partition tracks the ABAB curves and excludes adjacent-N.** Observed
  partner fraction 0.198–0.257 against the model's ABAB 0.201–0.215 at the same
  densities — and against **trilayer ML+BL's 0.043–0.053, five times too small.**
  The dual overlay the Verify section makes mandatory is therefore passed in
  favour of N = 4, which matters because the corpus records a replay where
  agents mis-mapped a trilayer 0.15/0.85 pair into 4L templates.
- **The F_L tone behaves like a breakdown orbit.** At n = +3.0 the dominant
  tone (29.99 T) is the *sum* of the resolved pair, and the B-window split shows
  it strengthening with field relative to the fundamentals — low-B half: 7.5 and
  22.5 strong; high-B half: only ~29.9 survives. ABAB inter-block breakdown is
  symmetry-allowed at N = 4, so a sum-tone at F_L is *expected here, not exotic*.
- **g = 4 verified in-data.** The calibration fans' LL ray slopes fall in ratio
  4:8:12:16:20:24 (run 5, slope/ν to 1.4%), so the four-fold degeneracy that
  F_L = (h/4e)·n assumes is measured, not assumed — the degeneracy audit passes.
- **Independent, non-stacking corroboration of the semimetal picture:** R_xx is
  locally *minimal* at charge neutrality with maxima on either side (runs 4–5),
  the shape a band-overlap semimetal makes, and ABAB tetralayer is predicted to
  be one. Recorded as **consistent-with at most** — survey §5 gives three
  candidate parents for CNP character and the investigation forbids reading it
  as a stacking call.

**What prevents a strong call — this is the honest weight:**

- **The partner tones reproduce weakly.** 3–9 of 18 extraction choices, against
  15–16/18 for the dominant tone. A tone seen in a sixth of reasonable
  extractions is a candidate, not a measurement.
- **The pair is not consistent across density.** Only n = +2.6 and +3.0 give a
  clean partition. At n = +1.8 and +2.2 the pairing does not close the Luttinger
  sum (1.67 and 1.24 × F_L for the obvious pairings). The investigation's own
  refinement test — f₁(n) + f₂(n) = F_L *across* density, which is algebraic and
  cannot hold coincidentally — therefore passes at two densities out of four.
- **The single robust cross-density feature is one tone near F_L** (0.957,
  0.895, 0.932, 0.967; a single ~6% rescale puts all four at 1.00). Read alone,
  that is the **ABCA singleton** template. The ABAB reading depends entirely on
  the weakly-reproducing partners being real.
- **The F_L-origin discrimination is not passed, only suggested.** The high-B
  window has δF = 10 T while the tones differ by 8 T, so "only the F_L tone
  survives at high B" may be a resolution artifact. Grid-change reproduction was
  not run; the decisive per-branch LK mass was not measured.

## 3. Confidence and hedges

**Confidence: low-to-moderate, and asymmetric** — the evidence excludes trilayer
and is consistent with ABAB, but does not exclude ABCA-plus-artifact.

- **Resolution.** δF = 2.0 T over the usable record. The ABAB heavy tone
  (24.35 T predicted) and the ABCA singleton (31.02 T) differ by 6.7 T ≈ 3.3 δF
  and *are* separable — but the observed dominant tone sits between them at
  22.96–29.99 T depending on density and window, which is why the call will not
  firm up.
- **Side and density.** Electron side only, |n| ≤ 3.1×10¹². The **hole side is
  gate-window-limited to −0.97×10¹²**, inside the exception regime where the ABAB
  pair is close and balanced and reads beat-like on short 1/B records — the
  n = −0.9 point is reported as range-limited, **not as a null**. This is a
  constraint of the committed top-gate window (D = 0 forces V_bg = 1.20·V_tg and
  V_tg stops at −0.3 V), not of the device.
- **Searched-and-absent vs not-resolvable.** The ABAB light tone is predicted at
  2.9–4.2 T for n ≤ 2.2, i.e. at or below δF — **not resolvable**, so its absence
  there is not evidence.
- **R_xy admixture, single polarity.** R_xx runs negative at deep LL minima
  (≈ −20 Ω at ν ≈ 8, ≈ −100 Ω at ν ≈ 4), scaling as h/νe² — about 1% Hall
  admixture. Every run this session is single field polarity, so no ±B
  symmetrisation was possible. A sawtooth-like R_xy leak can *manufacture*
  harmonic structure, and unexplained tones at 50.2 and 55.5 T (n = +3.0) remain
  on the books. **This is the most serious systematic and it is unaddressed.**
- **Absolute layer number.** Transport here supports **N = 4 over N = 3** via the
  partner fraction (5× discrimination). Pentalayer (2+2+1) was not tested.
- **Mosaic.** Untestable — one live pair.

## 4. What would firm the call

1. **±B symmetrisation** to remove the R_xy admixture. Cheapest, and it directly
   attacks the leading systematic. Doubles fan cost.
2. **Per-branch LK masses** (`temperature-dependence-vti`, Flavor B). The
   investigation calls this **decisive**: ABAB's two branches differ by ≈ φ² ≈ 2.6×
   in mass, which cleanly separates two genuine bands from one band plus an
   artifact. This is the single highest-value next measurement.
3. **A longer 1/B record** — lower B_lo (onset is already below 1.5 T, so there
   is room) to shrink δF and turn the weakly-reproducing partners into
   measurements.
4. **Grid-change reproduction** (uniform-1/B instead of uniform-B) to retire
   sampling-alias origins for the partner tones.
5. **A wider negative top-gate range**, if −0.3 V is a conservative provided
   limit rather than a physical one, to bring the hole side into the design
   window and give the second carrier sign the investigation wants.

## 5. Status

**This is a "consistent-with", not a call.** The stacking of vti-02 is **not
determined** by this session. What *is* determined is the (n, D) frame it must be
measured in, the feasibility envelope, and a specific, ranked list of what to do
next — and the leading hypothesis (ABAB with symmetry-allowed inter-block
breakdown) is now concrete enough to be falsified by measurement 2 above.
