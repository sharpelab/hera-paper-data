# vti-02 — plan (stacking order: ABAB vs ABCA vs ABCB)

*Reconstructed at the 2026-08-23 handoff (the prior instance left no `plan.md`
— see session_notes TOOLING). Steps 0–3b are done; step 4 is the live one.*

## The discriminant

At D = 0 the three stackings differ in **how many Fermi surfaces carry the
density**, and in what fraction each carries:

| stacking | D = 0 band structure | SdH signature at density n |
|---|---|---|
| **ABCA** (rhombohedral) | one quartic flat band, 4-fold spin/valley | **one** tone at F = F_L = nh/4e |
| **ABAB** (Bernal) | two bilayer-like subbands, different m*, semimetallic overlap | **two** tones, F₁+F₂ = F_L, ratio set by the mass ratio |
| **ABCB** (mixed) | monolayer-like ⊕ trilayer-like, **non-centrosymmetric → gapped already at D = 0** | two tones, different ratio; + a D = 0 gap |

So the call rests on: (a) the **tone count and the F/F_L fractions**, (b) whether
the CNP is **gapped at D = 0**, (c) the Landau-level **filling sequence** (gap
slopes dn/dB = νe/h).

Everything hinges on an absolute n scale — which the fan supplies itself
(ν from the LL slopes), independent of the geometry prior.

## Steps

- **0. Gate C — liveness** (runs 0–3, done). Alive, no leakage, Rxx 60–330 Ω.
  Two resistance maxima per 1D leg → two series regions.
- **1. 0 T gatemap** (run 5, done; run 4 railed). Two **parallel** CNP ridges →
  a series mosaic of two domains (A, B) with the same lever arms, B electron-doped
  by 0.43×10¹² vs A. Calibration: c_bg/c_tg = 0.773 (data), c_tg from the 9.5 nm
  geometry prior (absolute scale **uncalibrated**), n_offset −0.089×10¹²,
  D_offset −0.013 V/nm from the R_CNP(D) symmetry vertex.
  **Read for the call:** R_CNP(D = 0) = 240 Ω — metallic, *no* D = 0 gap; grows
  to ~2.4 kΩ by D ≈ +0.25 V/nm. Argues against ABCB; does not separate ABAB/ABCA.
- **2. Feasibility model** (done, in-cell). F_L = 33.1 T at n = +3.2×10¹².
- **3 / 3b. SdH spot checks** (runs 6, 7, done — analysed 2026-08-23).
  Strong oscillations from ≲ 1 T to 10 T, 80–600 % peak-to-peak of the local
  background. Multi-tone and harmonic-rich; a single-density FFT **cannot**
  separate real Fermi surfaces from harmonics, from the A/B mosaic, or from
  window artefacts. → the fan is required. Sets B_lo ≈ 1 T and the sensitivity.
- **4. Landau fan (LIVE)** — B slow (uniform in 1/B, 1→10 T) × n fast along
  D = 0, n = −1.20 … +3.20×10¹². The one measurement that decides the call:
  - **F vs n per tone.** Real subbands → lines **through the origin**, slopes
    summing to 1. The A/B mosaic → lines of the **same slope, offset** by
    0.43×10¹² (≈ 4.4 T). Harmonics → exact integer multiples. The n lever arm
    (−1.2 → +3.2) is what separates slope from offset.
  - **LL gap slopes** dn/dB = νe/h → integer ν → absolute n calibration (fixes
    the 9.5 nm prior) and the degeneracy sequence.
  - **CNP column at high B** → is the ZLL gapped, and with what degeneracy.
- **5. (conditional) Lifshitz / low-n structure or a D-scan of the fan**, if
  step 4 leaves ABAB vs ABCA open — e.g. an annular-FS signature (ABCA) vs a
  subband-crossing signature (ABAB).
- **6. (conditional) LK mass ladder** at one density, if the tone assignment
  needs m* to close. Expensive (hours of T settling); only if it decides.
- **7. Close-out** `return-to-initial`, then the call as the final ana cell.

## What would change my mind

- **A single tone tracking F_L across the whole n range** → ABCA, strong.
- **Two tones through the origin with slopes summing to 1** → ABAB (or ABCB if
  the CNP also proves gapped at D = 0 — but step 1 says it is not).
- **Two tones of equal slope, offset ≈ 4.4 T** → that is the A/B mosaic, not a
  band-structure fact; the tone count reverts to one.
- **LL slopes not landing on integers** → the n scale is wrong; recalibrate
  before any fraction is quoted.
- **A rail, or R_CNP running away at high B** → abort, re-size, re-run.
