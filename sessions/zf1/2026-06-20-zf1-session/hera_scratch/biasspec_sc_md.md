## HERA — bias spectroscopy at the SC dip (measure Ic) — retract not-SC

The 0.5 nA AC maps can't see a supercurrent with Ic ≲ 0.5 nA (the probe exceeds Ic → reads the normal-state Rxx). This goes *below* Ic: **dV/dI vs I_dc** at the dip, low AC.

**Operating point:** V_tg = −5.61, V_bg = 4.17 (n ≈ −0.48 e12, D ≈ −0.67 V/nm — feature center, max accessible D). **AC lowered to 0.1 nA** (`sr830_1.amplitude` 0.05→0.01) to sit below a sub-nA Ic. DC bias `dc205_1`/100 MΩ → I_dc = V_dc/1e8; sweep V_dc −0.5→+0.5 V = **I_dc −5→+5 nA** (101 pts). **dV/dI read on both sr2 and sr3.** No `volt.step` change.

**Expected if SC:** dV/dI ≈ 0 (low) for |I_dc| < Ic, rising sharply at the critical current — a supercurrent lobe.

**Parameters I'm guessing — please correct, you know this SC:**
- **Field:** this cell is at B=0 *nominal* (~2 mT trapped). If the SC is field-sensitive, the trapped flux may suppress Ic here — should we **find the effective zero first** (or sweep dV/dI vs B)? Your call.
- **AC level (0.1 nA)** and **bias range (±5 nA)** — set to your known Ic scale; I'll widen/narrow.

`dc205→0` at end; gates stay at the dip for follow-up. ~7–8 min. Preconditions asserted.
