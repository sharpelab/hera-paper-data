# Session notes — QC0426 / vti

Operational log (not a science notebook).

## Session log
- **2026-06-20 — E1 GRANT.** Operator (Zack) said "go for autonomy" after gates
  A (instruments alive, readbacks sane) and B (SAFETIES = device-card limits,
  cap 8.0 T) verified green. Engaged E1 (autonomous). Re-entry requires a fresh
  explicit grant after any E0 drop.
- **OBS — vaporizer Cernox (LS335 input B) reads 0.0 K** at bring-up
  (non-physical). Input B is control-only + rig-card-documented curve anomaly;
  sample T (input A) = 1.153 K healthy. Non-blocking (no T ladders this session).
- **OBS — Step 1 gate map (run 0) voltage channels RAIL at the CNP** with the
  device-card-designated gate-map sensitivity 2e-5 (full-scale 20µV / 5nA =
  4.0kΩ; observed rail 4.37kΩ). Peak R > 4.4kΩ is clipped — narrow plateau
  (~6–11/105 pts/row), so ridge *position* (calibration) is unaffected, but
  true CNP height is lost. If peak height ever matters, gate map wants a coarser
  voltage-channel sensitivity (e.g. 1e-4) or autorange. Possible device-card /
  recipe note. Run-0 checkpoint (row ~10): CNP slope ≈ −1.15, leakage BG 0.25nA
  / Si 0.59nA, ridge mid-window → CONTINUE.

## Calibration write-back (for device card — established in-session, run 0)
- **(n, D) calibration from run 0** (0 T gate map, `cnp-and-dline-calibration`),
  ana cells 11–13. **ratio c_bg/c_tg = 1.293** (data-calibrated; sr1 1.295 /
  sr2 1.292, agree 0.2% → single device calibration, both Rxx regions coherent).
  **c_tg = 1.703e-3 F/m²** (geometry anchor, 15.6 nm hBN), **c_bg = 2.202e-3 F/m²**
  (ratio). **CNP intercept b = +0.136 V** (V_tg @ V_bg=0); **n_offset = −0.144e12
  cm⁻²**; **D_offset = 0 (assumed** — no ±D-symmetric feature; stated). Closure
  max|n| @ ridge ≤ 0.15 (sr1) / 0.47 (sr2) e12. Source: run 0, fast=DC_bias (TG),
  slow=k_2400_volt (BG).
- **Two-tier provenance**: ratio data-calibrated; **absolute scale geometry-prior
  (~10–15%)** until a QH lever-arm check (ray slopes dn/dB=νe/h on the fan) upgrades
  it. D=0 line gate-limited |n| ≤ 12e12; Onsager overlay valid ≤3.5e12.

## SdH spot checks (Step 3) — hole side
- **Run 1** (hole n=−3.4e12 D=0, B 0.1→2 T, 2V/20nA, dwell 2.5s): **inconclusive** — strong
  MR (55→200Ω), onset ~1.3 T, **no resolved tones ≤2 T**. Device SdH is **high-field**
  (consistent with warm T_e ~8 K). `sdh_onset` floor-hit (unreliable on weak data).
- **Run 2** (hole continuation 2→8 T, no re-traverse; sr1 railed >7 T masked): SdH **resolves
  strongly** above ~1.3 T. Stitched 0.1–8 T FFT (ana cells 17–19), stability-checked across
  windows + bg_degree: **two robust tones, ~20 T and ~35 T (≈F_L)** in both Rxx channels; the
  ~9–11 T peak is an **envelope/MR-residual artifact**. Tone at F_L + one at ~0.57·F_L
  **disfavors clean single-pocket ABC**; leans ABA / mixed-domain. Partition unresolved at one
  density → Step 4 fan.
- **PROTOCOL/RECIPE note**: `sdh-spot-check` ~0.1–0.3 T onset heuristic badly mismatched this
  device (onset ~1.3 T); measuring onset + extending to the 8 T cap was the fix. `sdh_onset`
  returns nan/floor-hit on gradual-onset SdH — needs a documented visual fallback.
- **Run 3** (Step 4 fan, launched): `landau-fan-vti`, hole D=0, n −3.5→−1.5e12 ×31, B 8→1.4 T
  ×65 uniform-1/B, sens 1e-4 (worst-corner sized), dwell 1.8s (6τ), 2.0 h, not interrupted.

## STACKING CALL (Step 7) — ABA (Bernal), strong; ABC excluded (decisive)
- **Result (ana cells 20–22):** dominant SdH fundamental at **F_L/2** across the fan, both Rxx
  channels (median F_dom/F_L = 0.54), ∝n, + 2nd harmonic at F_L. F_L/2 ⟹ density split among
  **≥2 Fermi surfaces** (single g=4 pocket → F_L; `abc_fs` confirms ABC=1 pocket=F_L here) ⟹
  **ABA**, not ABC. Confirmed two ways: per-column FFT + direct 9-period count (n=−3.37e12,
  F_L=35T → 17T).
- **Load-bearing cross-check — QH lever-arm:** ν_gate/ν_Hall = 0.97–1.01 across all (n,B) →
  density scale verified to 2–3%, **rules out the factor-2 scale error** (the only path back to
  ABC). Upgrades (n,D) calibration geometry-prior → QH-verified.
- **Both Rxx regions coherent** (no mosaic). **Hedges:** ML/BL pair not individually resolved
  (balanced ≈F_L/2, hole side); LK-mass deciding cross-check unavailable (temperature-dependence
  blocklisted); hole side only. **What would firm strong→decisive:** LK-mass series (unblock T-dep),
  resolve ML/BL (finer 1/B / lower T), electron-side fan.
- **PRIMARY CAMPAIGN GOAL MET.** Field+gates parked to 0 (run after fan). Magnet idle.
- **CHIRON note:** strong session for `trilayer-stacking-fs-count` — the F_L/2 (balanced hole-side
  ABA) presentation differs from the survey's electron-side asymmetric BL≈F_L/ML-tiny picture;
  worth a recipe Example. Also: `fs_count_b0` clamps |n|>3.5e12 and is electron-side only (no hole
  pockets) — flagged for the model TODO.
- **RECIPE/PROTOCOL — fan worst-corner sizing under-estimated.** Sized sens 1e-4 for ~2.3kΩ
  (R∝1/n from the n=3.4e12 spot check), but the real low-|n|×8T R is ~5.5kΩ (R grows faster
  than 1/n near the low-|n| edge — MR×density stacking steeper than linear). Result: lowest
  ~3–5 |n| columns (n −1.5..−1.9e12) clip at B>6.5T. Clean range n −2.0..−3.5e12 intact →
  CONTINUE, exclude clipped columns. **Two fixes for next time:** (1) anchor the worst-corner R
  on a measured low-|n| high-B point, not a 1/n extrapolation from high |n|; (2) the launch
  overload assert checked the *first* fast point (high |n|, small R) — must check the
  worst-corner end (low |n|) of the n-sweep, or both.
