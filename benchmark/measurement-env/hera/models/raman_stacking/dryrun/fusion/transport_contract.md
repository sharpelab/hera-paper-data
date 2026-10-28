# Transport stacking call — device Y (LOCKED 2026-01-19, before any Raman data was seen)

Produced per the trilayer FS-count investigation's output contract.
Channel regions per device.md (ch_A x 3–13, ch_B x 17–27, ch_C x 31–41,
ch_D x 44–54; all y 10–20 µm). This call was locked and archived before
the Raman document was unsealed; no Raman evidence is cited anywhere
below.

## 1. Per-region verdicts

- **ch_A: ABA (strong).** Two SdH tones at D = 0, f_BL = 41.2 T and
  f_ML = 7.6 T at n = −2.5×10¹² cm⁻² (runs 31–33), partition
  f_ML + f_BL = F_L within 3% across n = −1.5 to −3×10¹²; branches track
  the predicted ML/BL Onsager curves under a single global rescale 0.94.
- **ch_B: ABA (weak).** Dominant tone at ≈ F_L with a marginal slow
  shoulder (f ≈ 6–9 T, ~2.5× noise floor) in runs 35–36; partition not
  resolvable at this mobility (SdH onset 0.9 T). Consistent-with an ABA
  pair with the ML tone under-resolved; single-pocket ABC not excluded by
  frequency content alone, but the CNP shows no D-tunable gap
  (R_CNP < 4 kΩ at |D| ≤ 0.3 V/nm, run 38) — weak ABA overall.
- **ch_C: ABC (strong).** Single tone at F_L across n = −1 to −3×10¹²
  (runs 41–44), Luttinger-consistent with one four-fold pocket; strongly
  D-tunable insulating CNP (R_CNP > 2 MΩ at D = 0.4 V/nm, run 45);
  no crossing-chain structure in the D ≈ 0 fan (run 47) despite
  resolution adequate per the reference resolution ladder.
- **ch_D: ABC (weak).** Single tone at F_L (run 51, one density only);
  gate leakage above |V_TG| > 3 V restricted the D range — D-tunable gap
  test incomplete.

## 2. Evidence

Run ids above; fan and FFT artifacts archived in the campaign ana
notebook (`ana.ipynb` cells 40–68); Onsager overlays from the validated
FS-count forward model (single global rescale 0.94).

## 3. Confidence + hedges

Lever-arm scale prior ±12%; ch_B's slow shoulder is
extraction-window-sensitive (reported as a fork; LK mass split is the
deciding follow-up); ch_D single-density.

## 4. What would firm

ch_B: lower-T spot check + per-branch LK mass. ch_D: restore D range
(regate) and repeat the gap test.

## 5. Protocol statement

Verdicts carry weight words; cannot-tell outcomes would have been
reported as such.
