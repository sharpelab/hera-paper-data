# Phase 2 — STACKING CALL (QC0426, D=0, this session)

**Device-level: ABC (rhombohedral) — moderate.** Every resolvable single-particle discriminator points ABC, agrees across both probed regions, and the ABA-specific features are absent where the forward model places them. Short of *strong* only for device/rig-inherent reasons (no QHE plateaus at this mobility/T; no LK-mass cross-check). Not ABA; no mosaic disagreement.

### 1. Per-region verdict (STYLE strength scale)
- **sr1 / T3–T4: ABC (moderate).**
- **sr2 / B4–B5: ABC (moderate).**
- **Both regions agree** on every discriminator → no mosaic disagreement (step-2 triage).

### 2. Evidence (feature → coordinates → reference → artifact)
- **CNP Rxx vs D, B=0** (file_id 18): ×90 / ×83 growth, D∈[−0.98,+1.15] V/nm, 0.8→78 kΩ, both channels → ABC D-gap fingerprint (paper §discriminators / ABC contrast, ref. 5 Bao 2011). ana cell 15.
- **SdH-FFT single Fermi surface** (file_id 20 n=1–4, file_id 21 n=3.5–10): ONE frequency per n-column tracking single-band f_tot (g=4) across the **full n=1–10 range** in the clean field window (B 4–8 T): 0 columns with a genuine second pocket. → against ABA ML+BL two-pocket (recipe step 3.5). ana cells 18, 21.
  - *Robustness*: an apparent second low-f peak at high n (8 columns, b-range 3–8 T) **vanishes for B≥4 T** → a sub-onset (3–4 T) artifact, not a pocket (STYLE rule 14 fork, tested and resolved).
- **No ABA crossing chains** (file_id 21): with the N_M=1 (n≈6.8) and N_M=2 (n≈10) model chains now **inside** the measured window, the data shows straight ν-rays (single ladder) with no curved arcs co-locating with the predicted loci (forward model hera/models/aba_trilayer, ml_trajectories). ana cell 21.
- **Hall** (file_id 20): classical (Rxy≈B/ne, sloping) — no QHE plateaus → moderate mobility (onset ~2.5–3 T).

### 3. Confidence + hedges
Moderate confidence ABC. Remaining hedges (device/rig-inherent, not coverage gaps):
- **No QHE plateaus** (moderate mobility) → no ν=±6-vs-integer test and no Rxy-quantization lever-arm.
- **Absolute n/D scale is geometry-prior** (SdH freqs consistent with g=4 to ~20%, not pinned to a quantized lever-arm).
- **No LK-mass / beat-damping temperature cross-check** of the single-pocket result (the decisive ABA-vs-single-band follow-up).
- The chain-region coverage gap from the first pass is **closed** (file_id 21).

### 4. What would firm to *strong*
1. **Temperature-dependence (LK mass)** on one SdH branch — a single mass confirms single-band (recipe's two-pocket cross-check); requires vaporizer T-craft (operator).
2. **Lower T** for QHE plateaus → ν sequence (ν=±6-centered ⇒ ABC) + a quantized lever-arm. The resolution ladder says this is a disorder/T limit, not a fingerprint limit.
3. D-gap systematics (gap vs |D|, B=0) — already strongly ABC-positive.

### 5. Status
A hedged, feature-cited **ABC (moderate)** call across both regions, with the ABA discriminators (two-pocket, crossing chains) tested in-window and absent. Not decisive — strong would need plateaus/LK, which need lower T / temperature work. The interesting outcome per the recipe's Next: ABC is the flat-band/correlated candidate → a low-T (mK) campaign is what the physics deserves.
