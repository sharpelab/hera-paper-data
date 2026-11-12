## HERA — rasterized (n,D) SC-extent map, expanded to ~8 h (supersedes cell 60)

Expanded per operator: density **n ∈ [−0.70, −0.10] e12 cm⁻²**, **D from the max accessible negative (V_bg=4.2 limit) up to −0.45 V/nm**, resolution sized for **~8 h**. **Run this, not cell 60.**

**Grid:** 240×100 raster ≈ **0.0025 e12 × 0.0025 V/nm** (~11 pts across the dip's 0.027 e12 FWHM — high oversampling). 23,661 raster pts → **20,572 in-validator**; the 13% "clip" is the gate-inaccessible max-(−D) corner beyond V_bg=4.2 (the accessible −D edge runs −0.69→−0.635 across n — preview `hera_scratch/nd_design2.png`, run-5 dip sits right on it). Method = `sweep.raster.rasterize` → `calculate_gate_voltages` (dtg 23.6 / dbg 20 nm, κ=3) → `sanitize_tg_bg`; caps data-validated. Both **sr2 (Rxx)** and **sr3 (sharp marker)** read.

**Time ~8 h** (20,572 pts × ~1.4 s/pt est; multisweep delay 1.2). Estimate has ±0.5 h slack on the per-point rate — I'll **re-price from the actual rate at the first checkpoint**; interrupt anytime (partial data is readable). Raster order: D ascends from −0.70, so the **dip's D (−0.65) lands ~20% in (~1.6 h)**; the max-(−D) region is mapped first.

**Checkpoints:** ~45 min (leakage clean, channels alive, time re-priced) and ~2 h (dip region reproduces in 2D). `hera-watch` armed.

**Field caveat:** B=0 nominal (~2 mT trapped), same as run 5 — maps the *as-found* extent; a field-suppressed SC would be deeper/wider at the effective zero (the field follow-up at the dip remains the decisive SC test). Drive 0.5 nA, no `volt.step` change, gates park at end. Preconditions asserted.
