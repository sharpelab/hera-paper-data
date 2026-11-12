# vti-02 — stacking-order plan (`hera_scratch/plan.md`)

Goal: region-resolved ABAB / ABCA / ABCB call on tetralayer graphene vti-02,
from this session's data only. One measured region (the `sr1` = B_1−B_2 pair);
the gate map already shows a **two-ridge mosaic** under that pair, so the
"region" may itself be two series sub-regions (A and B).

*(Reconstructed at the 2026-08-23 handoff — the prior instance left no
plan.md on disk; steps 0–3 are recorded from the notebooks, 4+ are forward.)*

## Discriminators the call will rest on

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| Fermi surfaces at D = 0, finite n | **two** (light + heavy bilayer-like band), F₁+F₂ = F_L, ratio ≈ m₂/m₁ ≈ 2.2, both → 0 at the same n₀ | **one**, F = F_L (4-fold); low-n trigonal-warping Lifshitz into 3 pockets at F_L/3 | two families that do **not** vanish at a common n₀ — e/h coexistence (band overlap) |
| R_CNP vs D | opens with D | opens with D (larger, flat-band) | weak / asymmetric in ±D (no inversion symmetry) |
| fan symmetry about CNP | roughly e–h symmetric | e–h asymmetric (flat band on one side) | strongly asymmetric |

`F_L ≡ |n|h/4e` (`luttinger_frequency`) is the 4-fold full-density Onsager
frequency; **ΣF_i = F_L is the sum rule** that also checks the n calibration.

## Steps

- **0. Gate C — liveness** (runs 0–3, `gate-current-sanity-check`). Done.
  Contacts alive, gate currents at the pA floor.
- **1. 0 T gate map** (run 4 aborted at first-rows rail → **run 5**,
  `gatemap`). Done. Two parallel CNP ridges (A dominant, B ≈ 0.19 V lower in
  V_tg, electron-doped by 0.43×10¹² vs A). R_CNP(A) 240 Ω at D ≈ 0 → 2.4 kΩ at
  D = +0.25 V/nm.
- **2. `cnp-and-dline-calibration`** (ana on run 5). Done.
  c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m² (9.5 nm geometry prior —
  **absolute n scale is still a prior**), n_offset = −0.089×10¹²,
  D_offset = −0.013 V/nm from the R_CNP(D) vertex. D = 0 line inside the
  validators: n = −1.27 … +3.27×10¹².
- **3. SdH spot checks** (`sdh-spot-check`, runs **6** n = +3.20, **7**
  n = −1.20, both D = 0, 10/20 mT). Done. Strong SdH, onset 0.3–0.7 T, many
  tones. Run 6: 7.1 / 14.1 / 22.1 / 29.5 T — **either** a harmonic comb on a
  7.4 T fundamental **or** a genuine two-pocket ABAB pair (7.5 / 25.6
  predicted) **or** a single F_L = 33.1 T surface. *A 1D trace at one density
  cannot separate these.* → this is what step 4 exists to settle.
- **4. Landau fan at D = 0** (`landau-fan`, **next**). Rxx over
  (n = −1.20…+3.20×10¹², B = 0.3…10 T). Settles step 3's ambiguity three ways:
  (a) **F vs n** — harmonics keep an exact integer ratio at *every* n, real
  pockets do not; (b) **sum rule** ΣF_i(n) = F_L(n) — a straight line through
  the origin of slope h/4e if the calibration is right; (c) **fan origins** —
  one convergence point (single region) or two (the A/B mosaic, offset by
  0.43×10¹²). Plus the ν-resolved gap sequence at high B.
- **5. Follow-up, chosen by step 4** — most likely a finite-D fan (flat-band
  vs bilayer-band response is strongly D-dependent), or a T-dependence at a
  fixed (n, B) for Lifshitz-Kosevich masses if step 4 leaves two candidates
  standing. Field is the expensive axis: whatever step 5 is, it starts from
  wherever step 4 leaves the magnet (10 T).
- **6. Call** — final ana cell, per the brief's output contract.
- **7. Close-out** — `return-to-initial`.

## What would change my mind

- Sum rule fails badly (ΣF_i ≠ F_L by >20 %) → the **absolute n calibration**
  (c_tg geometry prior) is wrong, not the stacking; re-anchor on the ν-line
  slopes in the fan (ν-lines are calibration-free: n = ν·eB/h) before any call.
- Fan shows a single convergence origin but two frequency families with a
  *density-dependent* ratio → not a simple two-band picture; suspect the
  A/B mosaic and say so rather than forcing a stacking label.
- No resolvable structure below ~2 T at low |n| → the read is
  resolution-limited at T_e ≈ 8 K; the honest answer is `cannot tell` on the
  low-density side, with the high-|n| read reported separately.
