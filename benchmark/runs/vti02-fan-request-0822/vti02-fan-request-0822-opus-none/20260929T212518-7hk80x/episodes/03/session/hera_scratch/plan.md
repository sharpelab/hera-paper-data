# vti-02 — stacking-order plan (HERA, 2026-08-22/23)

Goal: region-resolved call ABAB / ABCA / ABCB (or calibrated "cannot tell") for
the one live Rxx pair **B_1 – B_2** (source T_0, drain B_3). One contact pair
⇒ one region. Reconstructed/extended at handoff; earlier steps are recorded as
done from the notebooks + `./data/`.

## Discriminants (what any evidence must speak to)

| # | Observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|---|
| D1 | # of SdH frequency families at fixed n, D = 0 | **two** (two bilayer-like sub-bands, F₁+F₂ = nh/4e) | **one** (F = nh/4e) | **two** (hybrid, inequivalent chiralities) |
| D2 | CNP at D = 0 | semimetallic (band overlap), low R, no clean ν = 0 | small/zero gap, strongly D-tunable | intrinsic gap at D = 0 (non-centrosymmetric) |
| D3 | R_CNP vs D | weak growth | **strong, symmetric** growth (gap ∝ D) | asymmetric in D, minimum off D = 0 |
| D4 | LL sequence from CNP | two interpenetrating fans; ν crossings | single fan, Δν = 4 ladder | two fans, unequal |
| D5 | m* from LK (T-dependence) | light pair (~0.02 / ~0.05 mₑ) | heavy, strongly n-dependent | mixed |

## Steps

- **S0 — bring-up / gates A,B,C.** done. VERIFY ALL GREEN; runs 0–3
  `gate-current-sanity-check` (both gate legs live, leakage ≲ 100 pA flyback
  transient only, Rxx 4-probe sane).
- **S1 — `gatemap` at B = 0** → run 4 (railed, aborted), **run 5** (sr1 100 µV).
  Establishes the CNP line and the (n, D) frame. One dominant CNP ridge A plus a
  fainter parallel ridge B at ΔV_tg ≈ 0.19 V (series mosaic, region B
  electron-doped by 0.43×10¹²). **Speaks to D3:** R_CNP(A) = 240 Ω at D ≈ 0,
  rising to ~2.4 kΩ by |D| ≈ 0.25 V/nm and saturating — a strong, roughly
  symmetric D-tunable gap. Leans ABCA/ABCB, does not separate them.
- **S2 — `cnp-and-dline-calibration` on run 5.** done. c_bg/c_tg = 0.773
  (data), c_tg = 2.796 mF/m² (9.5 nm geometry prior — absolute scale still a
  prior), n_offset = −0.0894×10¹², D_offset = −0.013 V/nm. D = 0 line inside the
  validators spans **n = −1.27 … +3.27 ×10¹²** (TG-limited both ends).
- **S3 — `sdh-spot-check` at two densities on D = 0** → **run 6** (n = +3.2×10¹²,
  B 0→10 T) and **run 7** (n = −1.2×10¹², B 10→0.3 T). Both complete, T = 1.24 K.
  **Read (handoff analysis, `hera_scratch/ana_spot*.py`):** restricted to the
  Nyquist-valid window B ≥ 1 T, the dominant SdH frequency is
  **F = 29.5 T at n = +3.2×10¹²** and **F = 12.3 T at n = −1.2×10¹²**, i.e.
  F/|n| = 9.2 and 10.25 T per 10¹² cm⁻² against h/4e = 10.34 — a **single
  4-fold-degenerate Fermi surface carrying the full density at both signs**,
  within the ~10 % uncertainty of the c_tg geometry prior. The apparent
  "fundamental" the tone-tracker reports at 7.3 / 6.6 T is a harmonic ladder
  from very sharp (R → 0) minima: its F/|n| is 2.3 vs 5.2 across the two spots,
  i.e. it does **not** scale with n and cannot be a Fermi-surface frequency.
  **Speaks to D1: one family, not two → against ABAB and against ABCB.**
  Caveat: a weak second tone below the ~1.1–1.8 T-resolution floor is not
  excluded, and both spots are single densities.
- **S4 — `landau-fan`, B × (n along D = 0). ← NEXT (run 8).**
  Slow B 1.0 → 10.0 T at 0.1 T (91 rows); fast (V_tg, V_bg) co-swept on D = 0,
  n = −1.20 → +3.20 ×10¹² in 141 points (Δn = 3.14×10¹⁰ cm⁻²); endpoints are
  exactly the run-6 / run-7 spots. sr1 at 500 µV (50 kΩ FS).
  **Establishes:** (D1) whether the single frequency family persists
  *continuously* across n — one fan family or two; (D4) the filling-factor
  ladder — Δν between gaps and the ν of the first gap flanking the CNP;
  (D2) whether a ν = 0 insulator develops at D = 0 and from what field;
  and it **self-calibrates c_tg** from the fan-line slopes (removing the
  geometry prior from every later number).
  **What would change my mind:** a second fan family with a different slope set
  (→ ABAB/ABCB); a Δν = 2 or Δν = 1 ladder where the prior says Δν = 4 (→ the
  density scale is wrong by ≥ 2× and S3's single-surface read collapses); no
  resolvable ladder at all (→ "cannot tell", resolution-limited at T_e ≈ 8 K).
- **S5 — (if time) `sdh-temperature-dependence`** at one or two densities:
  LK fit for m* (D5). Only worth it if S4 leaves ABCA vs ABCB open.
- **S6 — the call**, as the final ana cell, per the brief's output contract.

## Standing constraints

- Field is the expensive axis: 0.137 T/min, `field()` blocks. Never re-traverse.
- Gate operating box is the box (banned to probe): TG [−0.3, +1.0],
  BG [−1.3, +2.0], Si [−25, +25], |B| ≤ 10 T, T_set ≤ 100 K.
- Si stays at 0 V (a standalone Si survey is banned).
- Lock-in noise is **input-referred ≈ 20 nV** and independent of the
  sensitivity range over 20 → 100 µV (measured, runs 4 vs 5): size the range to
  the worst-case R, not to the signal.
