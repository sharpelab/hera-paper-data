**Read — calibration established (two-tier provenance).**

- **Ratio (data-calibrated)**: c_bg/c_tg = 1.2774 (sr1 −1.2650, sr2 −1.2899; 2 % cross-channel spread, larger than the per-channel fit error → possibly mild spatial variation between the T3–T4 and B4–B5 regions; per-channel numbers kept above, channel mean used for the device calibration). Geometry-sanity: prior ratio 15.6/12 = 1.300 — agreement to 1.7 %, well inside the tens-of-percent alarm band.
- **Absolute scale (geometry prior)**: c_tg anchored at the 15.6 nm hBN stack value (both gates are simple hBN; TG anchored, BG set by the fitted ratio). Upgrade path: quantum-Hall lever-arm check when fan data lands — ray slopes must quantize (dn/dB = ν·e/h).
- **Offsets**: n_offset = −0.036×10¹² cm⁻² (tiny intrinsic doping, CNP at V_tg ≈ +0.034 V); D_offset = 0 — *assumed*, no feature yet physically locates D = 0.
- **Quality**: ridge-to-fit rms < 20 mV ⇒ δn ≈ 0.02×10¹² cm⁻². Railed rows (2e-5 rail = 4.37 kΩ) handled by plateau-centering; CNP peak R above the rail is *unmeasured* here (floor: R_CNP ≥ 4.4 kΩ at |D| ≳ 0.2 V/nm, rising with |D|; un-railed near D ≈ 0 at ~1.5 kΩ).
- **Realized D = 0 window**: n ∈ [−6.4, +6.3]×10¹² cm⁻² inside the validators — comfortably covers the SdH operating densities.
- **Region survey**: both hole and electron sides metallic (R_xx < 130 Ω at |n| > 2×10¹²) on both channels; drain current ≥ 4.75 nA everywhere → no insulating contact arms in the window. One feature: a **vertical stripe at V_tg ≈ +0.55 V** (TG-only-gated arm regions at neutrality), crossing D = 0 at n ≈ +1.2×10¹² cm⁻² — a known series-R artifact line for electron-side columns, not a bulk feature.

**Next** (investigation Step 2→3): F_L(6×10¹²) = 62 T → Δ(1/B) = 1/(3F_L) ≈ 5.4×10⁻³ T⁻¹; SdH spot checks at n = −6 and +6 (D = 0), uniform in 1/B over [0.25, 8] T.
