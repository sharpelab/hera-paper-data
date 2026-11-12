# SESSION VERDICT — zf1 bottom device (2026-06-24)

**Campaign question: does this device superconduct?**

## Candidate C1 — n = −0.55×10¹² cm⁻² (−5.5×10¹¹), D = −0.60 V/nm, holes

### 1. Verdict (STYLE strength scale)
**Consistent-with superconductivity — a compelling proximity-SC candidate (leaning strong).** The graphene–WSe₂ proximity-SC interpretation is favoured. **The failed-SC / anomalous-metal fork is explicitly unresolved** (zero-bias Rxx is low but not → 0), and the decisive T-dependence is not yet measured — so this is NOT a confident "superconductor."

### 2. Evidence (each hallmark with coordinates + benchmark)
- **Cap-ratio calibration** — CNP fit c_bg/c_tg = 1.183 (0.3% from the 1.18 geometry prior); (n,D) ratio data-backed, absolute scale still geometry-prior. [data/4]
- **4-wire Rxx dip** → ~6–7 Ω at (n=−0.55, D=−0.60, B≈0, T=34 mK), ~4× below the ~25 Ω metallic surroundings; localized. [data/6 linecut, data/9 zero-bias]
- **Critical-current nonlinearity** — dV/dI dips to ~7.5 Ω at zero bias and rises through **sharp switching peaks at ±Ic ≈ 12–15 nA** to the ~45–51 Ω normal state; symmetric, no fwd/bwd hysteresis. Ic comparable to the ~20 nA proximity reference (paper s41586-022-05446-x, Fig 1d). [data/9]
- **±D asymmetry** — the low-Rxx dip appears for D<0 (holes→WSe₂) and is replaced by a resistance PEAK at D=+0.5 (same n) — the proximity-SOC carrier-polarization signature (s41586-022-05446-x). [data/5–8]
- **Field-kill (B_c⊥)** — Rxx(B⊥) is a symmetric V centered at B≈0, suppressed by ±B⊥ on a ~few-tens-of-mT scale, while the normal state is field-insensitive. [data/10–11]

### 3. Confidence + hedges
Four corroborating hallmarks at base T + field → a compelling candidate. Hedges:
- Zero-bias Rxx is **finite (~7 Ω, not → 0)** → failed-SC / anomalous-metal fork open.
- A dV/dI peak alone is **confound-prone** (non-equilibrium criticality; QH breakdown) — corroborated here by field-kill + ±D asymmetry, but not alone decisive.
- **Ic(T)→0 at Tc not measured** — the missing minimum-constellation element.
- **B_c⊥ not cleanly quantified** — the 50 mT excursion left ~10 mT remanence, so controller-0 ≠ true zero; the pristine dip was not recovered.
- **QAH not excluded by R_xy** — no Hall pair was routed this session (config has only 4T-long 30-31 and 2T 5-4).

### 4. What would firm the call
1. **T-dependence (decisive):** Ic(T) collapse → Tc; zero-bias dV/dI(T) toward the normal-state trend. Heat up LAST (~3 h). First **re-zero the magnet** (degauss/thermal) to recover the SC optimum and quantify B_c⊥(0).
2. **Route a Hall pair (R_xy)** to exclude a QAH mimic.
3. **Lower-AC (0.5 nA) bias-spec** at the optimum — does the zero-bias floor drop? (bears on the failed-SC fork).
4. **Tight nD-map** around C1 to pin the true optimum (n,D) and the arc width.

### 5. Status
A **successful, calibrated outcome**: a compelling proximity-SC candidate with four base-T + field hallmarks, with the confirmation step (T-dependence) and the failed-SC-fork resolution explicitly identified as the remaining work. A confident "SC" call without the T-collapse and with Rxx not → 0 would be a protocol violation; this hedged call is the honest read.

*Normal-state fermiology (Landau fan / SdH) deferred — needs Tesla-scale field, out of this round's 100 mT cap.*
