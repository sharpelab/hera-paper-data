## HERA — Figure 1 (FINAL) — wide **symmetric** dome map · **supersedes cells 31 & 33**

**Run THIS (this cell). Do not run cell 31 or 33.** Two changes from cell 33, per your call:

**1. Symmetric sampling (dropped density/n resolution).** Cell 33 over-resolved n: step ratio 3.75:1 (n:D) while the dome's own aspect is ~11:1, so n was ~3× oversampled vs D. Now **n step 0.03 (201 pts) × D step 0.0025 (117 rows)** — ratio ~12:1 ≈ the dome aspect. The dome is resolved **~27 n-pts × ~28 D-pts** (was 53 × 18), pixel aspect **1.7:1** (was 5.5:1) → ~square pixels, equal resolution both ways. Full range kept (n[−7,−1], D extremal→−0.40). **21,239 pts.**

**2. Lower 4T sensitivity: 1 mV → 5 mV.** You're right it was too sensitive for a wide map — at 1 mV the ceiling is ~10 kΩ, and this map runs toward the CNP (n≈−1) where the bilayer gap broadens with |D| and Rxx climbs into the 10s–100s of kΩ, which would rail. At 5 mV the ceiling is ~50 kΩ: the dome + valence-band landscape sit comfortably in range; only the extreme n≈−1 / high-|D| gap corner may saturate (off-scale insulating — fine for a landscape). Trade: the sub-Ω SC floor is coarser than at 1 mV, but the dome shape/contours are still clear, and the fine SC detail lives in the dV/dI figures. Say the word if you want 10 mV (more gap headroom) or to keep 1 mV.

**~8.5 h** (21,239 pts × ~1.44 s/pt at delay 1.3; priced off run 0's 1.34 s/pt + margin → ~8.5–9.5 h). Within your ~10 h budget; the symmetry trim freed ~2 h vs cell 33. B held at B_eff0 = −0.366 mT, AC 1 nA, DC bias 0. Max V_bg = 4.20 (cap-safe).

**Noted for later:** we won't go above ~1 K — the heater block (Figs 3–5) ceilings at 6.5 V ≈ 489 mK anyway, so that's already inside; I'll plan the T-ladder accordingly.

**D ordered extremal → −0.40** so the dome core (D≈−0.66→−0.59) lands in the **first ~2 h** for an early go/no-go. **Checkpoints:** first ~5 min (leakage <1 nA, no rail, advancing); ~hourly thereafter (dome core by ~hr 1.5–2 → confirm before finishing). Preconditions printed+asserted at top. Ends with gates at the optimum, B held at B_eff0.
