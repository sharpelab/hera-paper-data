# Phase 2 — STACKING CALL (QC0426, D=0, this session)

**Device-level: ABC (rhombohedral) — weak-to-moderate.** The resolvable single-particle discriminators all point ABC and agree across both probed regions; short of *strong* pending the chain-region fan and a temperature/LK cross-check. Not ABA, not resolved-mosaic.

### 1. Per-region verdict (STYLE strength scale)
- **sr1 / T3–T4: ABC (weak).**
- **sr2 / B4–B5: ABC (weak).**
- **Both regions agree** on every discriminator below → **no mosaic disagreement detected** (step-2 triage). Device-level lean firmer than either region alone: ABC, moderate.

### 2. Evidence (feature → coordinates → reference → artifact)
- **CNP Rxx vs D, B=0** (file_id 18): ×90 / ×83 growth, D∈[−0.98,+1.15] V/nm, 0.8→78 kΩ, both channels. → ABC D-gap fingerprint (paper §discriminators / ABC contrast, ref. 5 Bao 2011). ana cell 15.
- **SdH-FFT two-pocket test** (file_id 20, B 3–8 T): **one** frequency branch per n-column (0/52 columns with two peaks), tracking single-band f_tot (g=4) within ~20%. → single Fermi surface; **against** the ABA ML+BL two-pocket signature (recipe step 3.5 — the sensitive discriminator at this mobility). ana cell 18.
- **D=0 fan structure** (file_id 20): single clean fan of straight ν-rays, both channels; no resolved curved crossing chains. ABA chains N_M≥1 predicted at **n>4 — outside the measured window** (forward model hera/models/aba_trilayer, ml_trajectories). No N_M=0 vertical Rxx-maximum series at the predicted n≈0.7 (but that sits on the CNP-column edge — confound-limited).
- **Hall** (file_id 20): classical (Rxy≈B/ne, sloping, dRxy/dn≠0) — no QHE plateaus. Moderate mobility (onset ~2.5–3 T).

### 3. Confidence + hedges
Moderate confidence ABC. Explicit hedges:
- **ABA crossing-chain region (n>4) was NOT measured** — the apparent chain-absence is a window limitation, not established absence.
- **No QHE plateaus** (moderate mobility) → no ν=±6-vs-integer test and no Rxy-quantization lever-arm.
- **Absolute n/D scale is geometry-prior** (SdH freqs consistent with g=4 to ~20%, not pinned).
- **Two-pocket exclusion not yet cross-checked** with an LK mass / beat-damping temperature series.

### 4. What would firm the call
1. **Higher-n D=0 fan (n≈3.5→8), riding the magnet down from 8 T** — covers where the ABA chains live; chain-absence there would firm ABC (proposed next).
2. **Temperature-dependence (LK mass)** on one SdH branch — a single mass confirms single-band (recipe's two-pocket cross-check).
3. **Lower T** for QHE plateaus → ν sequence (ν=±6-centered ⇒ ABC) + a real lever-arm.
4. D-gap systematics (gap vs |D|, B=0) — already strongly ABC-positive.

### 5. Status
This is a hedged, feature-cited **ABC (weak-to-moderate)** call, not a confident/decisive one — appropriate to the resolution. Firming step (1) is queued; (2)/(3) are next-session / temperature-work items.
