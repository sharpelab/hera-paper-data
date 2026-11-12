# vti-02 — stacking-order campaign plan

*Goal: region-resolved ABAB / ABCA / ABCB call (or calibrated "cannot tell") on
tetralayer graphene vti-02, evidence-cited, landing as the final ana cell.*

*(Reconstructed at the 2026-08-23 handoff — no `plan.md` existed on disk; steps
0–3 are back-filled from the measure/ana notebooks, 4+ is forward. Keep current.)*

## Discriminator logic — what the data has to decide

| | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| Fermi surfaces at D=0 | **two** bilayer-like bands, m* ≈ 0.028 / 0.061 mₑ → two SdH branches, fractions f₁+f₂ = 1 | **one** quartic flat band, m* ≈ 0.074 mₑ → single branch, F = F_Onsager(n) | hybrid: monolayer-like + trilayer-rhombohedral-like → two branches, strongly **e/h asymmetric** |
| F(n) signature | two lines through n=0, slopes summing to h/4e | one line, slope h/4e | two lines, different on the e and h sides |
| CNP vs D | semimetal, weak gapping | **strong** gap opening, R_CNP grows fast with \|D\| | intermediate / asymmetric |
| m* from LK | light + heavy pair | single heavy | mixed |

Primary discriminator = **number and fractions of SdH frequency branches vs n**
(step 4). Secondary = R_CNP(D) (partly banked, step 1) and m* via LK (step 6b).

## Steps

- **0 — bring-up + gate C.** Gates A/B green, kernel probe BOUND, VERIFY ALL GREEN
  (`session_notes.md`). Liveness on the provided pair (T_0 source / B_3 drain /
  sr1 = B_1–B_2): runs 0–3, `gate-current-sanity-check`. **DONE.**
- **1 — 0 T gatemap → `cnp-and-dline-calibration`.** Run 4 aborted (railed),
  run 5 at 100 µV. **DONE.** Yields: c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m²
  (9.5 nm geometry prior — *scale is uncalibrated*), n_offset −0.089e12,
  D_offset −0.013 V/nm. D=0 line inside the validators spans n = −1.26 … +3.24e12.
  **Two CNP ridges**: A (slope −0.773) and B (slope −0.691), offset by
  n_B ≈ −0.43e12 in region-A units → **two regions in series on the measured pair**.
  R_CNP grows from ≈330 Ω at D≈0 to >2.2 kΩ at D = +0.3 V/nm.
- **2 — feasibility model.** F_Onsager(full n) at the e-side spot = 33.1 T; ABAB
  pair predicted 7.5 / 25.6 T, ABCA singleton 33.1 T. **DONE (in-cell).**
- **3 — `sdh-spot-check`, both carrier signs.** Runs 6 (e, n=+3.2e12, 0→10 T) and
  7 (h, n=−1.2e12, 10→0.3 T). **DONE.** Result: strong SdH, onset ≤ 0.3 T
  (e-side tone censored at the record edge), peak R ≤ 590 Ω = 12 % of a 50 µV
  scale, leakage flat, T 1.243 ± 0.032 K. e-side tones 7.1 T (+ 14.1/22.2/29.5
  flagged as its harmonics) with a separate 33.3 T dominating B > 4 T — i.e. the
  **spot check cannot tell a real 2nd Fermi surface at ~26 T from the 3rd harmonic
  of 7.1 T at 21.3 T**. That ambiguity is exactly what step 4 resolves.
- **4 — `landau-fan` at D = 0 (NEXT, run 8).** Rxx(n, B): B slow 0.5 → 10 T
  uniform in 1/B (Δ(1/B) = 0.0125 T⁻¹, ΔB capped 0.25 T, 165 rows); (V_tg, V_bg)
  co-swept fast along D = 0, n = −1.26 → +3.235e12, 101 pts. Establishes:
  (i) F(n) branch count + fractions, per carrier sign; (ii) fan-line slopes →
  filling sequence and zero-LL degeneracy; (iii) separation of the two regions
  (two fan origins, n_A = 0 and n_A ≈ −0.43e12).
  Resolution: df = 0.53 T (separates 21.3 vs 25.6 by 8σ), F_Nyquist = 39 T.
- **5 — read run 8** in ana: raw map vs B and vs 1/B, per-column `sdh_fft` →
  F(n) branch fit, fan-line slope fit near the CNP. This is where the call is
  made or shown to need step 6.
- **6 — contingent follow-ups**, chosen by what step 5 leaves open:
  - **6a — D-dependence of the CNP gap.** Rxx(n, D) at fixed high B, or R_CNP(D)
    line. Cheap (no magnet traverse). Settles ABCA-vs-ABAB if the branch read
    is ambiguous. Rides the magnet down from 10 T on the way to close-out.
  - **6b — LK temperature dependence** at 2–3 selected n, `set_both(T, 0.95)`
    over ~1.3 → 20 K → m* per branch. The mass is the sharpest ABAB/ABCA split
    (0.028/0.061 vs 0.074 mₑ). Expensive (rig card: descents are passive,
    τ ≈ 27 min) — only if step 5 leaves the call at "weak".
  - **6c — fine fan** over a narrow n window if two branches are close.
- **7 — the call** as the final ana cell, per the brief's output contract.
- **8 — close-out `return-to-initial`** (field 0, gates 0, heaters off, readback).

## What would change my mind / kill a step

- Step 4 shows **one** F(n) branch with slope = h/4e across both signs and the
  CNP gaps hard with D → ABCA, strong.
- Step 4 shows **two** branches summing to the full density, symmetric e/h, CNP
  stays metallic → ABAB.
- Two branches with a pronounced e/h asymmetry (different branch count or
  fractions on the two sides) → ABCB.
- The 7.1 T content tracks the harmonic ladder of a single fundamental and no
  independent branch survives → the spot-check "pair" was harmonics; single band.
- **Abandon criteria for run 8**: no oscillation contrast in the first rows at
  200 µV (→ re-run at 50 µV); channel railing at the CNP columns below ~3 T
  (→ interrupt, re-run at 500 µV); no fan structure resolvable in the 0.5–2 T
  landed block at the 3.4 h checkpoint (→ abandon, fall back to 6a/6b).

## Standing caveats

- **Density scale is a geometry prior**, not calibrated: only c_bg/c_tg is from
  data. Every n and F_Onsager number inherits that scale error. The *branch
  fractions* f_i = F_i/ΣF_i are scale-free and therefore the robust read.
- Only one Rxx pair is wired (sr1 = B_1–B_2); "region-resolved" means the two
  CNP ridges seen in series on that pair, not separate contact pairs.
- Rig-card T_e ≈ 8 K is inconsistent with a 0.3 T onset — treat it as stale and
  fit T_e from LK if step 6b runs.
