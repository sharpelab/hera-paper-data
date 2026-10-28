# Session transcript / log — zf1 SC-figure campaign (toploader)

*Reconstructed chronological log of the hera-tactical session (E0, operator = Aaron), 2026-06-25 → 06-29. Goal: publication-quality figure DATA for the zf1 superconducting state. The raw harness jsonl for this tactical thread was not cleanly accessible, so this is an accurate run-by-run reconstruction (the per-step science lives in `20260625_ana.ipynb`; operational notes in `session_notes.md`).*

---

## Bring-up & precheck gates (Gates A/B/C)
- Read rig card, device card, handoff (`HANDOFF_zf1_SC_figures.md`), recommended recipes.
- **Gate A:** setup cells executed; magnet −0.015 mT, probe MC 33.8 mK, all lock-ins/Keithleys/DC205s connected.
- **Gate B:** SAFETIES committed = device-card limits (TG −7/+6, BG −4/+4.2) + |B|≤100 mT + heater ≤6.5 V.
- Stale-logfile trap cleared (probe = live Probe2/rotator, fresh; fridge logs advancing).
- (n,D) cal verified to roundtrip the optimum (n=−5.0e11, D=−0.64 → V_tg=−5.365, V_bg=+3.987). Noted: deployed cell omits `n_offset`; built explicitly in each cell.

## Run 0 — Gate-C re-entry baseline (constant-D n-cut @ D=−0.64)
Dome reproduced mV-exact: **Rxx = 0.60 Ω at n=−5.00e11**, <2 Ω core n∈[−5.30,−4.90]e11, leakage <75 pA, 34 mK. Device survived handover.

## Runs 1–2 — Step 0: effective-zero field B_eff0
Two one-sided field-kill cuts (+5→0, −5→0 mT), discipline-compliant (cross-zero reserved for Fig 2). **B_eff0 = −0.366 mT** (midpoint/parabola agree to 0.03 mT); B_c half-width ~2.2 mT. Used as "B=0" for all zero-field figures.

## Run 3 — Figure 1: wide (n,D) dome map  ·  *(operator-steered, 4 iterations)*
- v1 (1806 pt, ~1 h): operator **rejected** — "not publication quality."
- v2: operator wanted **~10 h budget**, wide range (n −7→−1, D to extremal), finer than 0.02/0.005. His 0.005/0.001 spec = ~314k pts ≈ 5–8 days; priced it, he set ~10 h.
- v3: operator wanted **symmetric sampling** (drop n/density resolution) + **lower sensitivity**.
- v4 (final): operator corrected me — **"you increased the sensitivity, not dropped it"**; "1K" meant **1 kΩ** not 1 Kelvin. Set 4T full-scale **0.1 mV** (resolve 1 kΩ at 1 nA).
- **Final run:** n[−7,−1]@0.03 × D[−0.69,−0.40]@0.0025 (symmetric), 21,239 pts, 0.1 mV sens, B_eff0, 8.6 h. Verified clean. **Selected widest-D = −0.64, optimal n = −5.0e11.** Pcolormesh reconstructs the boustrophedon/clipped rows.

## Warm-up (cell 40) — heater-block start
Heater→T re-confirmed; free Tc preview from R(T) at optimum suggested ~280 mK (later shown biased). Settle-time data gathered.

## Run 4 — Figure 3 v1 (dynamic, 90 s dwell) — DIAGNOSTIC, discarded
R(T,n) descending map: dome shape good but **T-axis biased** — ~50–80 mK sample-probe lag through the transition (dynamic R 3–5× equilibrium at same recorded T). Tc came out 223 mK. **Surfaced as a data-quality problem.** Operator chose **full settled re-do**.

## Settle test (cell 49) + the dwell correction  ·  *(operator-steered)*
- Settle test (big base→4.5 V jump) showed a slow thermal tail.
- I proposed zero-dwell + up/down averaging; operator corrected firmly: **"~1τ dwell per step + small steps"**, no zero-dwell, no full-settle, **no up/down averaging ("horseshit")**. τ ≈ 3.5 min from the warm-up 1 V settles.

## Run 5 — Figure 3 (settled re-do): R(T,n) @ B_eff0
1τ dwell (210 s) + small 3.7 mK steps, ascending, 120 pts, 11.9 h. Clean dome; per-row drift ~1 mK. **Tc = 235 mK** (50%-normal). Run 5 (up) & run 4 (down) bracket true Tc ~228–235 mK → residual lag few mK. **Corrected the prior 264–290 mK (under-settled, biased high).**

## Runs 6,7,9,10 — Figure 4: dome collapse vs field  ·  *(operator-steered)*
- Run 6 (+1 mT): Tc 166 mK, floor 4 Ω. (Cross-zero field ramp → startup transient, first ~5 rows; added R-settle for later members.)
- Run 7 (+2 mT): Tc 113 mK, floor 12 Ω. Operator: +2 mT already non-SC → **drop +4 mT (worthless)**, add intermediates.
- Run 8 (+1.25 mT): **operator interrupted** (non-monotonic T — diagnosed as a one-off thermometer glitch).
- Run 9 (+1.25 mT re-run): glitch-free (0/8190), Tc 148 mK.
- Run 10 (+0.75 mT): operator requested **+1-hour base dwell** for thermalization. Tc 179 mK.
- **Operator asked to "extract ξ" (clarified from T_BKT).** B_c2(T) from the 5 points (0/0.75/1/1.25/2 mT → Tc 236/179/166/148/113) is linear: dB_c2/dT = −16 mT/K, B_c2(0)=3.7 mT → **ξ_GL(0) = 0.30 µm** (brackets 0.3–0.4 µm with the direct base field-kill).

## Run 11 — Fig 5 verify: 1D dV/dI @ base, B_eff0
Operator: "propose the next measurement." Cheap dV/dI verify: textbook supercurrent — plateau |I|<25 nA, sharp switching ±36 nA, **non-hysteretic**, field at B_eff0. Ic clean → proceed.

## Run 12 — Figure 5: dV/dI(I_dc, T) @ optimum, B_eff0
Heater 1τ-settled slow × bias fast, 8.9 h. Supercurrent dome in (I,T): **Ic(base) = 36 nA, Ic(T)→0 at 216 mK** — independent Tc, consistent with Fig 3's 235 mK; both below the biased prior.

## Run 13 — Figure 2: Fraunhofer dV/dI(I_dc, B_⊥) @ optimum, base T
Single cross-zero pass B_eff0 ± 5 mT (authorized) × bias, 5.3 h, base held 33–34 mK. **Single central lobe, Ic = 37 nA exactly at B_eff0 (true 0.000 mT)** → supercurrent recovered post-cycle AND B_eff0 validated to <0.05 mT. Ic→0 by ±1.5 mT (~B_c), **no side lobes** → claim phase-coherence + Φ₀/area (~1 µm², single-lobe estimate), NOT a microscopic junction (per guardrails).

---

## Final results (all in `20260625_ana.ipynb`)
| Quantity | Value | Source |
|---|---|---|
| SC dome optimum | n=−5.0e11, D=−0.64 (V_tg=−5.365, V_bg=+3.987) | Fig 1 |
| B_eff0 | −0.366 mT | Step 0 |
| **Tc** | **235 mK** (R-50%) / **216 mK** (Ic→0) — *below prior 264–290* | Figs 3, 5 |
| **Ic** (base 34 mK) | **36 nA**, switching ±36 nA, non-hysteretic | Figs 5, verify |
| **ξ_GL(0)** | **0.30 µm** (0.3–0.4 µm bracket) | Fig 4 B_c2(T) |
| B_c2(0) / dB_c2/dT | 3.7 mT / −16 mT/K | Fig 4 |
| Fraunhofer | central lobe at B_eff0; ~1 µm² coherence area; no side lobes | Fig 2 |

## Key methodology / lessons (full in `session_notes.md`)
- **T-dependence dwell (recipe fix):** ~1τ dwell + small steps; NOT zero-dwell / full-settle / up-down averaging. Dynamic fast ladders bias the T-axis via sample-probe lag (~50–80 mK here).
- **This campaign corrected Tc downward** (prior was under-settled), not just higher-res.
- Sensitivity sizing: 0.1 mV resolves the ~1 kΩ SC R-scale at 1 nA; let the high-R CNP gap rail.
- Probe MC throws occasional T=0/glitch spikes (masked T<10 mK in analysis).
- Field positioning one-sided + read back; cross-zero only for Fig 2 (authorized) and B_eff0 repositioning.

*Rig left safe-idle: gates at optimum, B=B_eff0, base T, heater off, dc205=0.*
