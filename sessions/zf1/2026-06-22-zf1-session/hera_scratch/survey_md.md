## HERA — Step-1 survey gatemap (full box, pristine field) + cap-ratio substrate

The recon de-risked this: cap-ratio **1.176 ≈ prior 1.18** ✓, timing **0.89 s/pt** (measured), CNP magnitudes known (4T ≤ 4.6 kΩ, 2T ≤ 198 kΩ), leakage clean. And the candidate region (D≈−0.5 V/nm, n≈−5×10¹¹ holes-into-TMD) is confirmed in-box at **Vtg≈−3.9, Vbg≈+2.7**.

This is the Step-1 survey — the densest pristine-field first-look, double duty as the `cnp-and-dline-calibration` substrate (105 CNP points → refined cap-ratio across the full TG range). **Magnet untouched** (B≈0) per the field-history protocol.

**Design:**
- **TG slow** `linspace(−7, +6, 105)` (0.125 V), **BG fast** `linspace(−4, +4.2, 83)` (0.1 V) — full validator box, corners included (coverage gate).
- **Swept TG −7→+6 deliberately** so the candidate region (Vtg≈−4 to −5) lands **early** — my checkpoint sits right in it.
- **Sensitivities** (autorange unusable — no-ops <160° phase, our channels ~0°): **sr830_3 (4T, candidate channel) → 5 mV** to resolve low Rxx to ~50 Ω (CNP clips at high D — acceptable, candidates are *away* from CNP); **sr830_2 (2T) → 0.5 V**, corner-safe, carries the CNP/cap-ratio.
- `slow_delay=2, fast_delay=0.5` (recon-validated). Gate currents fp'd + live-plotted for leakage.

**Cost: ~2.2 hr** (8715 pts × 0.89 s/pt, measured rate).

**Checkpoint @ ~row 30 (~35 min, ~28%)** — by then TG has covered the full candidate region. I read (via the armed `hera-watch` per-row digests): (1) a low-Rxx arc near Vtg≈−3.9, Vbg≈+2.7? (2) CNP ridge tracking the recon slope; (3) leakage < threshold; (4) sr830_3 not pathologically clipping in the candidate region. **Fork:** clean landscape → continue to full map; clear candidate already resolved → may abandon early and pivot to bias spectroscopy; leakage/clip problem → interrupt and adjust. An early call saves ~1.5 hr.
