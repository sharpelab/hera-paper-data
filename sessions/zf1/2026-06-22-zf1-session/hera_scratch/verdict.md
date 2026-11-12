# ★ Per-candidate SC verdict — zf1 (bottom device), 2026-06-22

**Candidate R1 — `superconductor (DECISIVE)`** at **n ≈ −4.65×10¹¹ cm⁻², D ≈ −0.65 V/nm** (V_tg=−5.444, V_bg=+4.053), base T ≈ 39 mK, effective-zero field ≈ +1 mT. Hole-doped, D<0 (holes-into-TMD) — the BBG/WSe₂ proximity-SC window.

*(STYLE strength scale; the call is the intersection of the constellation, not any single hallmark — `2106.07640` standard.)*

## 1. Verdict
Region **R1: superconductor (decisive)**. A fragile gate-tuned proximity superconductor; the full hallmark constellation is present, mutually consistent, and located where BBG/WSe₂ proximity SC is expected.

## 2. Evidence (each: coordinate + benchmark)
| Hallmark | Result | (n, D, B, T) | benchmark |
|---|---|---|---|
| 4-wire **Rxx → 0** | 0.52 Ω (offset/resolution-limited; raw dips <0) | n=−4.65e11, D=−0.65, B≈0, T≈34 mK | constellation [2106.07640] |
| **Critical current** (supercurrent lobe) | dV/dI≈1.7 Ω below |Ic|; Ic⁺=17.8 / Ic⁻=18.8 nA; switching peaks ~80 Ω; normal ~55 Ω | same point, run 5 | Ic≈20 nA [s41586 Fig 1d] |
| **Field-kill**, normal unchanged | Rxx→flat 48.7 Ω; **B_c⊥≈2.5 mT**; effective-zero≈+1 mT | run 6, T≈34 mK | strong field-kill criterion |
| **Ic(T) melting** | Ic 24 nA (39 mK) → 0 at **Tc≈234 mK**, monotonic dome | run 7, B≈0 | Tc ladder [2106.07640] |
| **Sensible normal state** | clean single-CNP bilayer map; SC = narrow hole-side arc at large −D | survey run 2; cap-ratio 1.185 | proximity phenomenology [s41586] |

Derived: **ξ ~ 360 nm** (Hc2=Φ₀/2πξ², order-of-magnitude only). D-line designer / cap-ratio: c_bg/c_tg = 1.185 (data-confirmed).

## 3. Confidence + hedges
**Decisive** — {Rxx→0 ∩ Ic lobe ∩ B-kill w/ flat normal ∩ Ic(T)→0} is the required constellation; no single-hallmark over-read; Step-2 confounds (non-equilibrium criticality / QH breakdown) excluded by the flat-zero plateau + field-kill + thermal melting. Hedges (provenance honest):
- **Absolute (n, D) scale is geometry-prior** — cap *ratio* data-confirmed (1.185); absolute n/D pending a QH lever-arm. Coordinates are ratio-grade.
- **Tc is open-loop heater-T** (Probe1 readback, ±~10% absolute); the finite-Tc and dome shape are robust, the absolute value approximate. **Not** a BKT determination (V∝Iᵅ, α=3 not measured) — `%-of-normal/threshold` convention, stated.
- **ξ order-of-magnitude only** (B_c⊥(T) rounds near base; quantum-geometry caveat).
- **Optimum at the D-validator edge** — D≈−0.65 is ~the most-negative D reachable at this n (BG cap +4.2 V); the edge sweep still read 2.5 Ω at D=−0.676, so the true optimum may lie just beyond reach (instrument-limited coverage caveat).
- **QAH not excluded by an Rxy read** (no transverse pair wired); residual risk low — supercurrent lobe + B-kill + Ic(T) melting are not QAH phenomenology and QAH is not expected at B≈0.
- **−B-side field-kill & Fraunhofer not measured** (the +side is conclusive; phase-coherent-oscillation read deferred — B_c⊥≈2.5 mT makes it sub-mT-fragile).
- **Thermometry caveat**: session-configured probe (Probe2) was dead; all T from live Probe1 (runs 0–6 at genuine base; run 7 reassigned by timestamp).

## 4. What would firm / extend the call
- **Rxy (dVxy/dI)** on a transverse pair → explicitly exclude QAH.
- **QH lever-arm** (Tesla-scale, deferred round) → absolute n & filling ν.
- **BKT V∝Iᵅ ladder** → rigorous T_BKT; **finer Tc ladder** near 234 mK.
- **Effective-zero zoom + −B-side** field-kill; **Fraunhofer Ic(B)** for phase coherence.
- **±D-asymmetry** check (proximity-SC signature — appears for one D sign): confirm absence at D>0.
- Repoint thermometry to Probe1 / restart Probe2 worker.

## 5. Outcome
The campaign question — *does zf1 superconduct, and if so characterise it* — is answered: **YES.** A fragile gate-tuned **proximity superconductor** at n≈−4.65×10¹¹, D≈−0.65 V/nm, with **Ic ≈ 18–24 nA** (base), **B_c⊥ ≈ 2.5 mT**, **Tc ≈ 234 mK**, **ξ ~ 360 nm** (o.o.m.), on a clean bilayer normal state — consistent with the BBG/WSe₂ proximity-SC phenomenology [s41586-022-05446-x]. The determination rests on the full hallmark constellation, with provenance-honest hedges; it is a confident, evidence-cited call, not a single-hallmark lean.
