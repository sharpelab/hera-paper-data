## HERA — rasterized (n,D) zoom to map the SC-candidate extent

Map the extent of the candidate state around the run-5 dip (n ≈ −0.465 e12 cm⁻², D ≈ −0.65 V/nm) at the sampling density needed to resolve it (the dip FWHM is ~0.027 e12 / ~0.017 V — a uniform raster at that spacing over the quadrant is impractical, so this is a *tight* rasterized polygon focused on the dip).

**Method (`nD-map`):** `sweep.raster.rasterize` a rectangle in **(n,D)** → project to gates via `calculate_gate_voltages` (device hBN dtg 23.6 / dbg 20 nm, κ=3) → `sanitize_tg_bg` to the validators. Caps are data-validated (CNP slope 1.19), so the (n,D) projection is trustworthy.

**Box:** n ∈ [−0.63, −0.28] e12 × D ∈ [−0.67, −0.50] V/nm, **71×35 raster ≈ 0.005 e12 × 0.005 V/nm** (~5 pts across the dip FWHM — maximizing sampling here). 2380 pts, **1.4% clipped** at V_bg=4.2 (preview: `hera_scratch/nd_design.png`). **Both `sr830_2` (Rxx) and `sr830_3` (the sharp marker)** read.

**Reach caveat:** V_bg=4.2 caps the negative-D edge at ~−0.67 V/nm — the dip sits right at it, so the dome's *more-negative-D* side is gate-inaccessible at this density; the map extends toward less-negative D (where it's open).
**Field caveat:** at B=0 nominal (~2 mT trapped), same as run 5 — this maps the *as-found* extent; a field-suppressed SC would be deeper/wider at the effective zero (the field follow-up).

**Price ~50 min** (2347 in-range pts × ~1.3 s, multisweep delay 1.2). **Checkpoint ~20 min:** the dip's D is the first raster rows, so it appears early — I'll confirm it reproduces in 2D and read its (n,D) shape. Drive 0.5 nA, no `volt.step` change, gates park at end. Preconditions asserted (T base, |B|<5 mT, drive).
