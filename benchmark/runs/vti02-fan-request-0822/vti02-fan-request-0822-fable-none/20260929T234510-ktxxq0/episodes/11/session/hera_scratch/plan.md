# vti-02 stacking-order campaign — plan (recreated at handoff pickup, 2026-08-23)

*(The original plan.md did not survive the handoff; recreated from the notebooks,
session_notes, and scratch. Noted in session_notes as PROTOCOL.)*

**Goal:** ABAB vs ABCA vs ABCB call on vti-02 (tetralayer graphene), region-resolved
(one measured pair: sr1 = B_1−B_2), evidence-cited, per the output contract.

**Discriminating physics (D = 0):**
- **ABAB (Bernal 4L):** two bilayer-like conduction bands (light + heavy). SdH shows
  **two fundamentals** whose frequencies both grow with |n| and sum to
  F_L = |n|h/4e; partition ratio set by the mass ratio (~0.2/0.8-ish). Semimetallic
  near CNP (band overlap → multi-pocket low-F tones at low |n|). Gap opens with |D|.
- **ABCA (rhombohedral 4L):** one flat-ish heavy band at low E → **single fundamental
  ≈ F_L** (all density in one FS) until high-|n| Lifshitz features; strongly
  insulating / correlated at CNP, gap sensitive to D of either sign.
- **ABCB (mixed):** one monolayer-like Dirac + one heavy band → asymmetric partition,
  a near-linear light branch with small F, distinct from both.

## Steps

1. **Gate C liveness** (runs 0–3) — DONE. All four contacts alive, no leakage.
2. **0 T gatemap + calibration** (runs 4 aborted / 5) — DONE. `cnp-and-dline-calibration`:
   ratio c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m² (geometry prior), n_offset
   −0.089e12, D_offset −0.013 V/nm → `hera_scratch/cal_run5.json`.
3. **SdH spot checks** (runs 6 electron n=+3.2e12, 7 hole n=−1.2e12, D=0) — DONE,
   analyzed at pickup (`hera_scratch/spot_analysis.py`, spot_fft.png):
   - Run 6: dominant light tone **7.1 T** + strong ~26–33 T spectral weight. Ambiguous:
     harmonic ladder of 7.1 (2×,3×,4× tagged) *or* a genuine heavy band with
     F_light + F_heavy ≈ F_L = 33.1 T (ABAB-like partition 7/26).
   - Run 7 (hole, F_L = 12.4 T): multi-tone low-F content (4.7, 6.6, 9.4 T,
     6.6 ≈ 2×3.4 tag) — near-CNP multi-pocket / semimetal-like.
   - Neither trace alone separates harmonics from bands → the fan does, via F(n) slopes.
4. **Landau fan at D = 0** (THIS STEP — the stacking-call backbone):
   n = −1.25 → +3.20e12 fast (179 pts, Δn = 0.025e12, co-swept TG+BG on the calibrated
   D=0 line), B = 1 → 10 T slow, **uniform in 1/B** (145 rows, δ(1/B) = 0.00625 T⁻¹ →
   F_Nyq = 80 T, per-column ΔF = 1.11 T). Reads: per-column FFT → F(n) branches.
   - **ABAB:** two branches, both ∝ |n|, sum = F_L; harmonics of the light branch
     scale as exact integer multiples (distinguishable from an independent branch by
     slope vs n).
   - **ABCA:** single branch ≈ F_L(n) (slope 10.3 T per 1e12); insulating stripe at CNP.
   - **ABCB:** light branch with Dirac-like character + heavy branch, asymmetric sum.
   Ends at 10 T, gates parked at 0.
5. **Contingent — D response at CNP** (rides the field down): fixed n = 0, sweep D
   (or a small (n,D) map at fixed B, or B=0 D-line already in run 5): ABCA gaps
   steeply with |D| both signs; ABAB gap opens ∝|D| from semimetal; run-5 map already
   shows the D=±0.3 V/nm ridge — quantify R_CNP(D) from run 5 + a targeted check if needed.
6. **Contingent — LK masses**: T-dependence at 1–2 (n, B) spots if the frequency
   partition alone can't separate ABAB from ABCB (m* of the light branch: bilayer-like
   ~0.03–0.06 mₑ vs Dirac-like B-dependent).
7. **Verdict cell** in ana notebook per the output contract; close-out (`return-to-initial`).

## What would change my mind / kill criteria

- Fan first rows: broad railing (>20% of columns clipped) → abort, resize sensitivity.
- Leak trip (>1 nA either gate) → abort (guard does it), notify, reassess.
- F(n) branches not resolvable above ~2 T (smeared columns) → fall back to a few dense
  1D B-sweeps at intermediate n instead of the fan grid.
- If the light-branch "harmonics" track ∝ n with *different* proportionality than the
  fundamental → they're separate bands, revisit assignment.

## Timing calibration (this session)

- run 5: 1.10 s/pt at fast_delay = 1.0, τ = 0.3 s / 24 dB; row flyback ≈ 5.8 s incl. slow_delay 3.
- run 6: 7.46 s per 10 mT field point (4.4 s ramp + 3 s settle + reads).
- Fan price: 145 rows × (179 × 1.1 + 6.5 s) + 9 T ramps (66 min) + settles ≈ 9.6 h,
  headline with the session's +5–10% actuals lesson: **≈ 10 h 30 m**.
