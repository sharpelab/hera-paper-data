# vti-02 stacking-order plan — reconstructed at handoff (2026-08-23)

*(plan.md was absent at the instance handoff; reconstructed from the notebooks'
markdown, which cite these steps. Steps 1–3 are done; this file is current going
forward.)*

Goal: ABAB vs ABCA vs ABCB, region-resolved, evidence-cited (output contract in the brief).

## Steps

1. **[done] Gate C — liveness + gross gate safety** (`gate-current-sanity-check`, runs 0–3).
   Contacts alive, leakage at noise floor, R(V_tg) peaks ≤ 330 Ω at D≈0.
2. **[done] 0 T gatemap → (n, D) calibration** (`gatemap` runs 4 (aborted, railed) + 5;
   `cnp-and-dline-calibration`, ana cell 13, `hera_scratch/cal_run5.json`).
   ratio c_bg/c_tg = 0.773 (data), c_tg anchored at 9.5 nm prior, n_offset −0.089e12,
   D_offset −0.013 V/nm. D=0 window inside validators: n = −1.27 … +3.27e12 (TG-limited).
   **Region-B mosaic**: parallel CNP ridge, electron-doped +0.43e12 vs A — expect doubled
   fan branches offset in n.
3. **[done] SdH spot checks at D = 0** (`sdh-spot-check`, runs 6 electron +3.2e12, 7 hole −1.2e12;
   ana cell 15). Electron side: light fundamental 7.1 T (21 % of density), heavy budget 26 T
   ambiguous between harmonics (21.3/30.2 ≈ 3×/4×7.1) and fundamentals. Hole side: balanced
   multi-tone, no clean read. Oscillations to 0.3 T, SNR to 100 → fan is well-conditioned.
   Single-density read cannot separate harmonic (slope k·dF/dn) from independent band
   (own slope, sum rule ΣF = 10.34 T per 1e12 cm⁻²) → step 4.
4. **[NOW] Landau fan along D = 0** (`landau-fan`): fast = (V_tg, V_bg) co-swept on the
   calibrated D=0 line, n = −1.27 … +3.27e12, 66 cols; slow = B 0.45 → 10 T uniform in 1/B,
   256 rows (Δ(1/B) = 8.32e-3 → Nyquist 60 T, ΔF = 0.47 T). Deliverables: R(n, B) fan chart;
   per-column FFT → F(n) branch map. Decision logic:
   - one branch tracking 10.34·n alone → ABCA-like single surface;
   - light + heavy branches with independent slopes summing to 10.34·n → ABAB (two
     bilayer-like pairs) vs ABCB (monolayer-like + bilayer-like) separated by the branch
     count, slope partition, and low-n behavior (monolayer-like pocket persists to low n);
   - harmonics identified by exact k× slope; region-B ghosts by +0.43e12 n-offset;
   - ν=0/CNP stripe vs B (gap opening) as corroborating evidence.
5. **[next, contingent] D ≠ 0 discrimination** — sized by the fan read (e.g. repeat fan at
   |D| ≈ 0.2 V/nm, or R_CNP(D, B) map): ABCA's D-tunable gap vs ABAB's weaker D response;
   the run-5 ridge already shows a D-tunable gap (240 Ω → 2.4 kΩ at +0.25 V/nm) — a fan
   at finite D or a T-dependence of the CNP gap can separate parents if step 4 is ambiguous.
6. **Close-out** (`return-to-initial`): field 0, gates 0 at committed pacing, heaters off,
   readback → session_notes; verdict cell in ana per the output contract.

## What would change my mind / kill criteria

- Fan first-rows: leakage > 1 nA, rail beyond the expected ν=0 wedge, or a dead channel → abort.
- If by ~3 T of fan data the F(n) branch map is already unambiguous, the remaining high-B half
  still runs (heavy tones sharpen there); if the magnet or T drifts, stop and reassess.
- If branches don't satisfy the sum rule at any n → question the run-5 calibration (lever-arm
  error) before questioning the physics; cross-check slope of the ν=0 stripe apex.
