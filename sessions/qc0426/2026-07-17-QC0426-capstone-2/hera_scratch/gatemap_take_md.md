**Read (run 4):** Clean single CNP line across the full box; no leakage
anywhere (|I_gate| ≤ ~110 pA incl. offsets, all 10201 pts); T stable
1.165–1.170 K; sweep complete. **Calibration contract**
(`cnp-and-dline-calibration` step 5, written to `device_card.md`):

- **Ratio (data-calibrated)**: c_bg/c_tg = **1.2863** — per-channel slopes
  −1.2829 (sr1, 49/101 rows, 20 mV resid) / −1.2897 (sr2, 46/101 rows,
  19 mV resid); 0.5 % cross-channel agreement (within resid) → one device
  calibration, no mosaic signal at this level. Geometry-prior ratio 1.300
  agrees to −1.1 % (Verify: geometry sanity ✓).
- **Absolute scale (geometry prior)**: C_TG = 1.7027e−3 F/m² anchored on the
  single-dielectric 15.6 nm hBN prior → C_BG = 2.1903e−3 F/m². *Pending
  quantum-Hall lever-arm upgrade* (fan ray slopes / SdH Luttinger pin).
- **Offsets**: N_OFFSET = −0.052×10¹² cm⁻² (intercept +0.049 V);
  **D_OFFSET = 0** — *cited feature*: R_CNP(V_bg) minimum sits at
  V_bg ≈ 0.00/+0.09 V (D ≈ 0.005 V/nm), the symmetric-±D response.
- **Closure**: n ≡ 0 along fitted ridge to numerical precision.

**Physics note (hint, not a call):** R_CNP is strongly D-tunable — 1.3 kΩ
(sr1) / 0.6 kΩ (sr2) at D = 0 rising >10× by |V_bg| ~ 2 V along the ridge,
both channels, both D signs. Consistent-with a D-induced CNP gap
(ABC-leaning or mixed-domain); per the investigation this is fed into the
per-channel read, never a standalone call — the FS count decides. Both
density signs look clean and metallic away from CNP → both sides eligible
for SdH spot checks.

**Next:** investigation step 2 (F_L back-of-envelope) + step 3 SdH spot
checks at large |n|, D = 0, both signs (`sdh-spot-check`).
