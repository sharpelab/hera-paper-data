# raman_stacking — future work

Prioritized from the validation pass (2026-07-17); re-rank after first live
use on device Raman data.

1. **ERS-region metric** [PI-endorsed, 2026-07-17]. The Nemes deposit's
   trilayer identification runs on the flat-band electronic-Raman continuum
   (3200–6600 cm⁻¹), with labeled trilayer spectra in the deposit — a
   second, independent discriminator the tool doesn't read yet, and the
   high-wavenumber peak shifts by ~100s of cm⁻¹ per layer, so it doubles as
   a layer-number check (Carbon 224, 119113). Would convert the deposit's
   16 ERS-only exports from unusable to a trilayer-specific gate.
2. **Layer-aware segmentation.** FWHM rises with layer number (validated:
   PKU ABC 67→80 cm⁻¹, N = 3–10), so the two-population split confounds
   thickness with stacking on multi-terrace flakes. Given a thickness map
   (optical contrast / AFM / G-2D intensity ratio), split per terrace.
3. **6-Lorentzian sub-peak fit** (fixed 25 cm⁻¹ widths — Lui SI, Cong):
   the finer read for boundary work and for excitations where FWHM contrast
   is marginal. Deliberately deferred from v1; the validation shows FWHM
   alone carries the labeled sets.
4. **G-band channel.** FWHM(G) is an independent confirming map (ABC
   narrower — Cong Fig. 6) — unused so far because the FLG_37 map export is
   2D-only. Wire it up when a full-range map arrives.
5. **Confirm the PKU 4A/4B label assumption** against the paper ("Step
   geometry–guided growth of rhombohedral graphene") once indexed.
6. **Reference library growth.** Add same-instrument labeled spectra as they
   arrive (device Raman with adjudicated stacking); the mixed-spectrum
   decomposition (`decompose_mixed`) is only as good as its references.
