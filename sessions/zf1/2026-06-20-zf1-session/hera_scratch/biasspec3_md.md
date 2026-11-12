## HERA — bias spectroscopy point check (CORRECTED for sr2 — supersedes cells 40 & 42)

**Do not run cells 40 or 42** — both used sr3 as the 4T channel and the sr3 operating point. The 4T Rxx is sr2; redone here.

**Why still worth doing** with no candidate on the map: the Step-1 map ran at 0.5 nA AC. If a *fragile* superconductor had Ic < 0.5 nA, the AC drive would have exceeded Ic everywhere and shown the normal-state Rxx (no zero) — i.e. the map *cannot* rule out a sub-0.5 nA-Ic state. This point check, at **lower AC (0.25 nA)**, probes dV/dI vs I_dc near zero bias and is sensitive to a small Ic the map would miss. At the most-conducting point it's the decisive close: ohmic here ⇒ not-SC.

**What:** 1D dV/dI vs I_dc at the lowest-Rxx point **(Vtg −6.48, Vbg −3.73; n≈−8e12 cm⁻², D≈−0.12 V/nm)** — high hole density, the best-conducting metal (3.1 kΩ). **dV/dI = `sr830_2` (4T) / I_ac.** AC excitation lowered to **0.25 nA** (`sr830_1.amplitude` 0.05→0.025; sr2 SNR fine at 0.75 µV). DC bias `dc205_1` through 100 MΩ; V_dc −0.5→+0.5 V = **I_dc −5→+5 nA** (101 pts, 0.1 nA steps — fine near zero).

**Forks:** SC → dV/dI dips toward 0 below an Ic. Metal → flat ohmic ~3 kΩ across all I_dc (expected). Structure → extend range, round-trip, then a 2D bias-vs-n dome.

**No `volt.step` change** (default 5 mV). DC205 ramps slowly at that step → wall-clock **~5–8 min** (smaller ±5 nA range to keep it short); I'll re-price from the first points, interrupt if it drags. `dc205_1.volt → 0` + gates parked in `finally`. **Preconditions** asserted: T base; |B|<5 mT; AC 0.25 nA; gates/dc205 printed.
