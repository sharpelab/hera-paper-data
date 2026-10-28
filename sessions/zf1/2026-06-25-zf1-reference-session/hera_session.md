# zf1 / toploader — session brief: publication-quality figure data

*This covers the SC-figure data campaign — the six paper figures below are fully specified and
ready to run. Built on the prior session's handoff and this device's in-session results.
Protocol, gates, and boundaries live in the agent prompt; the physics method lives in the
recipes; this brief names the goal, the targets, and the device-specific facts.*

> **Prior-session dir** — all `HANDOFF` / `data/` / `hera_scratch` paths below resolve here:
> `~/measurements/aaron/20260624-4-zf1/`

## Contract

- **HERA** — drives the session: proposes paired markdown+code cells, reads every sweep from
  disk, commits to the next step. Protocol/gates/boundaries: the agent prompt.
- **Aaron — operator.** At the keyboard. Executes every cell; running a cell IS the approval;
  declining is the veto; interrupting is always his prerogative.

## Autonomy — E0 this round

- **Mode: E0 (collaborative).** The operator runs the rig; HERA proposes and waits. No
  autonomous instrument writes. (Last session ran E1; this one is E0 unless a grant is given.)
- **Notify:** Aaron — `hera-notify --user ASHARPE` (proposal-landed-while-idle / run-completion).

## Campaign goal

**Gather publication-quality figure DATA for the zf1 superconducting state.** This session is a
deliberate **revisit, armed with our own characterization data** — the prior session's figures
are good for *identification* but **too low-resolution for paper figures**. Every measurement
here is a higher-resolution / cleaner re-take aimed at "work of art" final figures. We already
know where the SC is and its scale (below); spend the resolution there, not on searching.

## What we already know (from `~/measurements/aaron/20260624-4-zf1/HANDOFF_zf1_SC_figures.md` — read it first)

- **SC dome** at **n ≈ −5.0×10¹¹ cm⁻², D ≈ −0.64 V/nm** (V_tg=−5.365, V_bg=+3.987).
  Dome (Rxx<2 Ω core) spans ~n∈[−5.5,−4.7]×10¹¹, D∈[−0.66,−0.59]; it **tilts** (n-center moves
  negative as |D| grows) and is **cut off at high |D| by the BG +4.2 V validator** (V_bg≈4.0 at
  the dome) — the widest accessible part sits near **D ≈ −0.64 to −0.65**.
- **Ic(base) ≈ 26–28 nA**, switching peaks at **±36 nA**, symmetric, non-hysteretic.
- **B_c⊥ ≈ 1.8 mT** (ξ ~ 0.4 µm, order-of-mag); effective-zero field ≈ controller 0.
- **Tc ≈ 0.26–0.29 K** (Ic(T)→0 / R0=50%·normal). Normal-state dV/dI ~ 45–57 Ω.
- **(n,D) calibration (USE EXACTLY):** `GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0,
  n_offset=-0.362e11*1e4)` — ratio data-pinned (c_tg/c_bg=0.844), absolute scale = geometry
  prior. Inverse (n,D)->(V_tg,V_bg) in the handoff §1.
- **Data access:** full — the handoff, the prior data (`data/0`–`20`), the device card, the
  reusable scratch scripts (`hera_scratch/*.py`). This is NOT a data-isolated session.

## Recommended recipes

- `measurements/nD-map.md` — Figure 1 (high-res dome zoom).
- `measurements/fraunhofer.md` + `bias-spectroscopy.md` — Figure 2 (Fraunhofer), Figure 5
  (dV/dI vs I_dc,T). **Read `fraunhofer.md` before proposing Figure 2 — not used last session.**
- `measurements/temperature-dependence.md` — Figures 3–5 (the T axis; Flavor A R(T,n) maps).
- `measurements/field-sweep-1d.md` — field positioning for Figure 4.
- `investigations/sc-characterization.md` — the governing context (Steps 2–4) and the over-read
  guards (Fraunhofer: claim phase-coherence + Φ₀/area, don't name the microscopic origin).

## Step 0 — effective-zero (B=0) calibration (do ONCE, use everywhere)

With B_c⊥ ≈ 1.8 mT, paper-grade "B=0" must **compensate the cooldown's trapped flux**, not trust
the controller's nominal 0. The trapped flux is **fixed at these field scales** (operator) → this
is a **one-time** calibration; **no re-locating** after Fig 4 / the Fraunhofer.

- **Measure once, at the optimum** (the prior-known n≈−5.0×10¹¹, D≈−0.64, V_tg=−5.365, V_bg=+3.987
  is good enough — B_eff0 is a magnet/flux offset, ~gate-independent; the dip bottom is flat over
  ~±1 mT). Zero DC bias, AC sense.
- **Scan:** Rxx vs B⊥ over **±5 mT at 0.1 mT steps, ~3–5 s dwell/point** so each field step
  thermalizes (flux-motion heating, worst near 0) → clean base-T Rxx. Bracket the minimum from
  both sides: two one-sided cuts (+5→0 and −5→0) stitched [discipline-compliant], **or** a single
  cross-zero −5→+5 pass if authorized (cleaner center — avoids the inter-half remanence mismatch
  that gave the +1.4/−2.15 mT asymmetry in runs 11/12).
- **Extract `B_eff0`** = the symmetric-dip center (fit the dip; don't argmin the flat noisy
  bottom). ±0.1–0.2 mT precision is plenty (well inside the flat bottom).
- **Use `B_eff0` as "B=0"** for every zero-field figure (Figs 1, 3, 5, Fraunhofer center). For
  Fig 4, set fields `B_eff0 + {1, 2, 4 mT}` and **log `B_eff0` in the run comments** so the true
  sample field is documented per file.
- Prior evidence: at ≤±15 mT excursions B_eff0 sat within ~±0.5 mT of nominal 0 (~0.4 mT best
  estimate; runs 11/12); after a 50 mT excursion the offset grew (Rxx(0)=6.6 Ω, run 10) — but at
  this campaign's ≤few-mT scales it's stable, hence once.

## Figure targets

**Table is in EXECUTION ORDER** (the `Fig #` is the figure's identity, kept stable). Figure 1
first — it pins the dome and selects the **widest-point fixed-D line** + the **optimal-doping n**
that Figures 3/4/5 and the Fraunhofer all ride. Figures 3/4/5 are the heater (T-axis) block;
**Fraunhofer (Fig 2) is LAST**, at the **same doping as the dV/dI (Fig 5)**. "Upgrade" = vs this
session's run. **Cheap-verify-before-expensive:** Figs 5 and 2 each get a quick 1D check first
(see ⚑ rows) — confirm the state is good before the multi-hour 2D sweep.

| exec | Fig # | Figure | Measurement | Concrete high-res target (refine on the page) | Upgrade vs prior |
|---|---|---|---|---|---|
| 1 | **1** | **Zoomed gatemap of the dome** | `nD-map` Rxx(n,D), tight window | n∈[−6.0,−4.3]×10¹¹ fast (**~0.02×10¹¹ step**, ~86 pts) × D∈[−0.66,−0.56] slow (**~0.005 step**, ~21 pts); delay ~2; 4T sens 1 mV | run 8 was 0.05×0.01, delay 1.2 → ~2.5× finer |
| 2 | **3** | **R(T,n) across the dome at its widest point** | `temperature-dependence` Flavor A (heater slow × n-line fast), **fixed D = widest point** (≈−0.64, confirm from Fig 1), **B = 0** | n across the dome **into normal both sides** (~n∈[−6.5,−4.0]×10¹¹, ~0.02 step); **~100 T-points base→~490 mK** (past Tc≈0.28 K) | new (prior T = 1D Ic(T), 8 pts) |
| 3 | **4** | **Fig-3 cuts at 4 fields** | repeat Fig 3 at **4 fixed B⊥** (Fig 3 = the B=0 member) | B⊥ ≈ **0, 1, 2, 4 mT** (SC→≈B_c→suppressed→normal); hold each field fixed during the T-map | new |
| 4a | ⚑ | **verify before Fig 5** | cheap 1D dV/dI vs I_dc at base, at the optimum | ±80 nA, ~1 min — confirm clean Ic≈28 nA / switching before the 2D | — |
| 4b | **5** | **dV/dI vs (I_dc, T) at optimal doping** | `bias-spectroscopy` 2D at the dome center **on the Fig-3 D-line** | I_dc **±80 nA** fast; **T slow, same ~100-pt axis as Fig 3**; AC 0.5 nA | run 9 was 1D, base only |
| 5a | ⚑ | **verify before Fig 2** | cheap 1D dV/dI confirms the supercurrent recovered post-thermal-cycle (B_eff0 reused, NOT re-measured — trapped flux fixed) | dV/dI ±80 nA at base — proceed only if clean | — |
| 5b | **2** | **Fraunhofer (base T) — LAST** | `fraunhofer`: 2D dV/dI vs (I_dc, B⊥), **same doping as Fig 5**, centered on **B_eff0** | I_dc **±80 nA** fast (~2 nA step); B⊥ **−5→+5 mT single cross-zero pass** [authorized] at **0.1 mT step, ~3–5 s/pt**; AC 0.5 nA | new measurement |

**Notes on the targets (decisions to settle on the page):**
- **Widest-point D:** provisionally **D ≈ −0.64 V/nm**; **Figure 1 selects it precisely** (dome
  widens toward the BG-cap-limited −0.66 — don't chase past the validator). **Optimal-doping n**
  = Rxx-minimum on that D-line (≈ −5.0×10¹¹); Figs 5 and 2 sit there.
- **"~100 cuts in T":** with **small heater steps the per-step thermalization is short**
  (each ΔT is small, so equilibration is quick), so **a ~100-step equilibrated ladder is
  practical** — favor many small steps with brief dwells over a few big steps with long dwells.
  Read T back from data; gate dwell on settling (dT/dt), not an absolute T. Flavor-A
  `multimegasweep` with the heater as the dense slow axis is the shape.
- **Bias range:** ±80 nA brackets Ic (≈28 nA) + switching (±36 nA) into normal at both ends
  (confirmed run 9) — used for Figs 5, 2, and both verify cuts.
- **Sensitivity / SNR:** figure-grade → favor longer per-point delays + fixed (autorange-off)
  sensitivity sized to the largest R in frame; mind the SR830 near-zero negative-X quirk
  (the ~0 Ω values aren't negative R — handoff §5).

## Field discipline — this session (carry-over, load-bearing)

**Session field cap: |B| ≤ 100 mT** (committed). All figure fields are mT-scale.
Per the rig magnet behavior (crossing B=0 injects heat; reversal leaves ~mT remanence):
**default: take every quantitative B-sweep one-sided and monotonically toward 0** (ramp to
extreme |B|, settle, sweep down); **never increase |B| through 0 while measuring**.
Consequences here:
- **Figure 2 (Fraunhofer) — cross-zero is AUTHORIZED** (operator, this session): take the
  Fraunhofer as a **single continuous −5→+5 mT pass** (the standard lobe-symmetric scan), not
  two halves. This is the one sanctioned exception to the one-sided rule; everything else stays
  one-sided. (Effective zero ≈ controller 0 from runs 11/12, so lobes center near B=0.)
- **Figure 4** holds each field *fixed* during its T-map (holding ≠ sweeping; fine); position
  each field (`B_eff0 + {1,2,4 mT}`) one-sided and **read `magnet.field()` back**. Trapped flux
  is fixed at these scales → **`B_eff0` does NOT need re-locating** between fields (Step 0 once).
- **Cadence:** quantitative field scans use **0.1 mT steps with ~3–5 s/point** so each step
  thermalizes (flux-motion heating is worst near 0) — applies to Step 0 and the Fraunhofer B-axis.
- Ramp heating measured **negligible** last session (T held 35 mK through a 50 mT ramp+sweep,
  rate 1.0 mT/s) — settles can be modest, but keep the mandatory post-ramp settle.

## Heater / T discipline — this session (carry-over)

Open-loop heater (`heater.volt`, Keithley); **read T back from the data `T` column, never the
setpoint**. Ramp in **≤1 V steps with an equilibration hold each** (~15 min/1 V baseline,
longer >4 V); confirm `heater.curr` is drawing. Device-card map (measured last session):
heater 0/1/2/3/4/5/6/6.5 V → **34/54/102/158/230/321/431/489 mK**. **Ceiling 6.5 V sustained**
(→ ~490 mK ≈ 1.7 Tc, enough to reach well into the normal state; 7 V one-shot only). Heating can
destabilize the fridge — watch the fridge MC, interrupt on runaway. T-work is the expensive,
least-reversible axis → **do all base-T and field work (Figs 1, 2) BEFORE heating; Figs 3–5 last.**

## Session arc (suggested)

1. **Bring-up + gates A/B/C** (precheck gates; SAFETIES = device card limits, field cap 100 mT).
   Re-entry baseline: a fast cut at (D≈−0.64) reproduces Rxx→0 near n≈−5×10¹¹ (cf. runs 5–8).
2. **Step 0 — `B_eff0` calibration** (see the Step-0 section): locate the effective zero **once**,
   at the prior optimum. `B_eff0` is "B=0" for everything below.
3. **Figure 1** — high-res dome zoom at **B = B_eff0**. **Select the widest-point D-line and the
   optimal n** used by everything downstream.
4. **Heater (T-axis) block** — heat up once, get all the T-data before cooling back:
   - **Figure 3** — R(T,n) at the widest D, **B = B_eff0**.
   - **Figure 4** — the same R(T,n) at **B_eff0 + {1, 2, 4 mT}** (Fig 3 is the 0-field member);
     position each field one-sided, read it back (no B_eff0 re-cal needed).
   - **⚑ verify**, then **Figure 5** — a cheap base dV/dI(I_dc) at the optimum confirms Ic is
     clean → then the dV/dI vs (I_dc, T) 2D on the same T-axis.
   - (Order Figs 3/4/5 to minimise heater cycles — they share the T-ladder.) Then heater → 0.
5. **Cool to base** (~1 h). **⚑ verify** — a cheap dV/dI(I_dc) confirms the supercurrent recovered
   after thermal cycling (B_eff0 reused, not re-measured).
6. **Figure 2 — Fraunhofer, LAST**, at the **same doping as Figure 5**, single cross-zero
   −5→+5 mT pass (authorized) **centered on B_eff0**; its central lobe self-checks B_eff0.
   Proceed only if the step-5 verify is clean.

## [VERIFY] at session start

- [ ] Magnet at 0 T (read `magnet.field()`); note any remanence.
- [ ] SAFETIES committed = device-card gate limits + |B| ≤ 100 mT + heater ≤ 6.5 V.
- [ ] Base (probe) T holding (mK); logfile mtime advancing + probe-vs-fridge cross-read
      (the 2026-06-23 stale-logfile trap; rig card).
- [ ] (n,D) calibration loaded as in the handoff §1; a quick cut reproduces the dome.
- [ ] Contact wiring reads cleanly; 4T Rxx (30-31) live.

## Session notes
Maintain `session_notes.md` (RECIPE FIX / TOOLING / PROTOCOL / FEEDBACK). `fraunhofer.md` is new
surface this session — RECIPE FIX entries expected. The one-sided-Fraunhofer adaptation (field
discipline vs the recipe's cross-zero idiom) is a likely PROTOCOL/RECIPE-FIX note.
