# vti-02 stacking-order campaign — plan

*Rebuilt at handoff pickup (2026-08-23): the original plan.md was not present in
scratch; steps 0–3 reconstructed from the notebooks' cited plan steps. Kept
current from here.*

**Goal:** ABAB vs ABCA vs ABCB call for vti-02 (tetralayer graphene), one measured
region (sr1 = B_1−B_2), evidence-cited per the output contract.

## Discriminators

- **ABAB (Bernal):** two bilayer-like bands occupied at all n → two SdH branches
  F_light(n) + F_heavy(n) = F_L(n) = |n|h/4e on both carrier signs; no intrinsic
  CNP gap at D = 0.
- **ABCA (rhombohedral):** one flat-bottomed heavy band → single full-density
  branch F(n) ≈ F_L(n); strong D-tunable CNP gap; heavy m* (LK-dead tones at
  T_e ≈ 8 K in parts of the range).
- **ABCB (mixed):** inversion-asymmetric → gapped CNP even at D = 0; asymmetric
  branch structure (Dirac-like light + heavy), strong e–h asymmetry.

## Steps

0. ✅ Bring-up, gates A/B, VERIFY, E1 grant (notes 2026-08-22).
1. ✅ Gate C liveness (runs 0–3) + 0 T gatemap → CNP + (n, D) calibration
   (run 4 aborted/railed; **run 5**: ratio c_bg/c_tg = 0.773, n_offset
   −0.089×10¹², D_offset −0.013 V/nm; region-B mosaic ridge at +0.43×10¹²;
   D-tunable CNP gap seen — parent ambiguous). Cal in `hera_scratch/cal_run5.json`.
2. ✅ Model/feasibility table (F_L, ABAB/ABCA m* + frequency expectations at the
   spot densities) — in measure cells 39/41 md.
3. ✅ SdH spot checks at D = 0: **run 6** (electron +3.2×10¹², 0→10 T, 10 mT) and
   **run 7** (hole −1.2×10¹², 10→0.3 T, 20 mT). Ana read: multi-tone both signs;
   electron side consistent with ABAB light 7.1 T + heavy ~25.9 T (split 22.2/29.5)
   closing to F_L 33.1; hole side 4.7 + 6.6 (+ 8.5 ≈ region-B F_L, 12.3 ≈ F_L,A).
   Harmonic/combination/mosaic ambiguity → fan required.
4. ▶ **Landau fan at D = 0** (this step): fast co-swept (Vtg, Vbg) along D = 0,
   n = −1.24 → +3.24×10¹² (181 pts), slow B = 0.35 → 10 T (50 mT, 194 rows),
   sr1 100 µV, ~13.5 h, ends at 10 T. Establishes: F(n) branch count + linearity +
   Luttinger sum on both signs; filling-factor line slopes (degeneracies);
   e–h asymmetry; CNP behavior vs B at D = 0.
5. Contingent follow-ups (ride the field down from 10 T, decide on step-4 data):
   - m* on the resolved branches via T-dependence at fixed B (LK), if a mass is
     needed to break an ABAB/ABCB degeneracy — heater ≤ 100 K, ratio 0.95.
   - a D ≠ 0 fan or fixed-B D-sweep if the CNP-gap parentage (step-1 ambiguity)
     is the remaining discriminator.
6. Verdict cell in ana (output contract: per-region verdict + evidence + hedges),
   then `return-to-initial` close-out.

## What would change my mind

- Fan shows a **single** F(n) branch ≈ F_L(n) with the 7.1 T tone tracking as a
  harmonic/fraction of it → ABCA back on the table.
- Branches don't sum to F_L (missing density) → annular/secondary FS or wrong
  cal — re-check calibration before any stacking claim.
- Strong e–h asymmetry + CNP gap at D = 0 growing with B from B = 0 → ABCB lean.
- Leak trip / rail off-ridge / no fan structure by 4 T → abort, re-establish state.
