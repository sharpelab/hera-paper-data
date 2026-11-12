## HERA — Figure 1 (FINAL, corrected sensitivity) · **supersedes 31, 33, 35 — run THIS**

My mistake on cell 35: I moved the 4T full-scale 1 mV → 5 mV (a *bigger* range = less sensitive), the opposite of what you asked, and I'd misread "1K" as 1 Kelvin — you meant **1 kΩ**.

**Corrected:** 4T (sr830_3) full-scale = **0.1 mV** (1e-4 V). Resolve **1 kΩ at 1 nA**: V = R·I·G = 1000 Ω × 1 nA × 100 = 0.1 mV. This puts fine resolution on the dome/SC R-scale (sub-Ω → 1 kΩ) and **rails above ~1 kΩ** as the map nears the CNP gap (n≈−1) — which we don't care about. ~50× finer on the dome than the erroneous 5 mV.
- 2T (sr830_2) kept at 5 mV — it's just the contact-R monitor (~13 kΩ); at 0.1 mV it would rail. Say so if you want it dropped too.

**Everything else unchanged from cell 35:** symmetric grid n[−7,−1] step 0.03 (201) × D[−0.69,−0.40] step 0.0025 (117) = 21,239 pts, dome resolved ~27 × 28 pts; B = B_eff0 = −0.366 mT; AC 1 nA; delay 1.3; D ordered extremal→−0.40 (dome core in first ~2 h); **~8.5 h**.

**Correction to my earlier note:** the "1 K" was 1 kΩ, not temperature — so it carries no T-ceiling implication. The Figs 3–5 T-ladder still runs base → ~490 mK (heater ceiling 6.5 V), past Tc≈0.28 K into the normal state, per the brief.

**Checkpoints:** first ~5 min (leakage <1 nA, no rail on 4T *within the dome/metal*, advancing); ~hourly (dome core by ~hr 1.5–2 → go/no-go). Preconditions asserted at top. Ends with gates at the optimum, B at B_eff0.
