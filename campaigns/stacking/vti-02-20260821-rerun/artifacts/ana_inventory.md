# ana notebook inventory — 31 cells

| idx | type | exec | appended_at | first line |
|---|---|---|---|---|
| 0 | markdown |  |  | # <DEVICE> — Analysis |
| 1 | code | 2 |  | import numpy as np |
| 2 | markdown |  |  | ## (n, D) — capacitance-based convention |
| 3 | code | 3 |  | # slot: geometry — gate-stack thicknesses from the device card's Gate-stack |
| 4 | markdown |  |  | ## Analysis discipline — raw first, then the read |
| 5 | markdown |  |  | ## Run <id> — <what it measured> |
| 6 | code | None |  | g = run(<id>)                 # open + re-form via helpers |
| 7 | code | None |  | # reduce to the feature (fit / peak / slope) and plot it on the data: |
| 8 | markdown |  |  | **Read:** <what this run shows>. |
| 9 | code | None |  | (empty) |
| 10 | markdown |  |  | ## Runs 0–3 — Gate C: `gate-current-sanity-check` (cooldown liveness, first-session branch |
| 11 | code | 6 |  | # Gate C — gate-current-sanity-check, runs 0-3 (TG 0->+1, 0->-0.3; BG 0->+2, 0->-1.3 V; ot |
| 12 | markdown |  |  | **Read (gate C verdict: PASS).** Device alive on the provided configuration: drain current |
| 13 | markdown |  |  | ## Run 4 — gatemap: full validator box at B = 0 (`gatemap` → `cnp-and-dline-calibration` s |
| 14 | code | 7 |  | # Run 4 — gatemap, full validator box, B = 0, Si = 0, 10 nA. Re-form (TSV, complete rows), |
| 15 | markdown |  |  | **Read.** One strong charge-neutrality ridge crosses the box from (V_tg +1.0, V_bg −1.3) t |
| 16 | markdown |  |  | ## Run 5 — SdH spot check, electron side, D = 0, n_design = +3.0 × 10¹² (`sdh-spot-check`) |
| 17 | code | 8 |  | # Run 5 — sdh-spot-check, electron (n, D) = (+3.0e12, 0) design point, B 0 -> 10 T uniform |
| 18 | markdown |  |  | **Read.** Oscillations are clean from **onset 2.4 T** (`sdh_onset`, carried by the 21-T to |
| 19 | markdown |  |  | ## Runs 6–7 — Si-gate test of the TG-only series segment: two TG linecuts at B = 10 T, V_b |
| 20 | code | 9 |  | # Runs 6-7: TG linecuts at 10 T, Vbg = 0, Si = 0 vs +25 V. Raw R(Vtg) and drain current. |
| 21 | markdown |  |  | **Read.** The V_tg ≈ −0.2 V feature is **Si-insensitive**: R(V_tg) for V_tg ≤ −0.1 V is id |
| 22 | markdown |  |  | ## Run 8 — Landau fan, electron side, D = 0 (`landau-fan-vti`): B 10 → 2.4 T uniform in 1/ |
| 23 | code | 12 |  | # Run 8 — landau-fan-vti, electron, D = 0: B 10 -> 2.4 T uniform 1/B (36 rows) x n 3.4 ->  |
| 24 | code | 10 |  | # F_L-tone origin (investigation Verify): (1) B-window split on run 5 and run 8 columns; ( |
| 25 | markdown |  |  | **Read — F(n) across density (Step 5).** Three spectral features, read per column (δF = 3. |
| 26 | markdown |  |  | ## Runs 10–15 (+ run 5 base) — LK mass ladder at the electron point (`temperature-dependen |
| 27 | code | 11 |  | # Runs 10-15 + run 5 — temperature-dependence-vti Flavor B (LK ladder at the electron poin |
| 28 | markdown |  |  | **Read.** Ladder covered (fp'd T_sample): 1.27, 4.15, 7.13, 10.12, 14.14, 20.16, 28.10 K — |
| 29 | markdown |  |  | ## Session call — vti-02 stacking (investigation `tetralayer-stacking-fs-count`, output co |
| 30 | code | None |  | (empty) |

## Cell 29 (claimed call cell) — verbatim source

```
## Session call — vti-02 stacking (investigation `tetralayer-stacking-fs-count`, output contract)

**1. Per-region verdict.** Channel/pair **sr1 = B_1–B_2 (source T_0, drain B_3): ABAB (Bernal) — strong.** No other R_xx pair is wired this cooldown (sr2/sr3 n.c.), so this is a one-region call; the flake may host other domains elsewhere.

**2. Evidence (all at D ≈ 0, electron side, Si = 0, T_e ≈ 8 K per rig card; global density scale 0.93 ± 0.03 pinned on the whole peak set by the Luttinger sum — design densities ×0.93):**
- Run 5 (spot, n ≈ 2.8): fundamentals **f₁ = 6.2 T, f₂ = 21.8 T**, sum **28.1 T** (= F_L at scale 0.90), difference **15.6 T**; onset 2.4 T; partition 0.78/0.22. Ana cells 16–18.
- Run 8 (fan, n 1.35–3.06 actual, 36 rows × 41 columns, δF 3.1 T): light branch 3.2 → 6.9 T at 0.21–0.22·F_L across the range, on the ABAB light curve (slope ≈ 3.3 T/10¹²; trilayer ML would be ≈ 1); heavy branch 20.8 → 25.2 T ≈ 0.77·F_L on the ABAB heavy curve for n ≳ 2.5 (unresolvable from the F_L tone below); a tone at F_L in every column. Luttinger: f₁ + f₂ = 32.1 vs 33.1 T (n = 3.06), 28.0 vs 28.1 (run 5). Ana cells 22–25 (Onsager overlays with the model curves in cell 23).
- F_L-tone origin: B-window split — sum/heavy 0.26 → 0.70 → 1.15 from low to high windows (run 5), 0.99 → 2.11 (fan column n = 3.16): strengthens with B like a breakdown / intermodulation orbit (cell 24); grid-change (uniform-B vs uniform-1/B) reproduces the set; LK: the F_L tone's mass 0.065 ± 0.004 (joint; 0.051 in 2.4–4.5 T, 0.100 in 3.5–7 T) m_e exceeds both fundamentals (0.039 ± 0.002 light, 0.048 ± 0.003 heavy) and is window-dependent (0.05 low-B → 0.10 mid-B) — consistent with the additive breakdown-orbit mass (≈ 0.085) within the window fork, not with a single pocket of fixed mass. Beat exclusion: the light branch is **lighter** than the heavy one → a genuine second band, not a beat (decisive per the investigation's rule). Ana cells 26–27.
- Degeneracy audit: one global scale (0.93), no 2×/4× multiplicity → g = 4 holds; ν ≈ 16-family rays visible in the raw fan.

**3. Confidence and hedges.** Strong, not decisive: (i) **one contact pair** — mosaic caveat, no cross-region check possible this cooldown; (ii) **mass ratio** — measured heavy/light ≈ 1.2–1.4 vs the model's ≈ 2.2 at this density (φ² limit 2.6): the light tone's LK rests on a 2-period record (6 T in a 0.32 T⁻¹ span) and is the least trustworthy number here; the model masses are semi-quantitative (README). The frequencies/partition/Luttinger/breakdown behaviour carry the call, the masses support "two genuine bands" without confirming the φ² split; (iii) **δF = 3.1 T** — the heavy branch is resolved from the F_L tone only for n ≳ 2.5; the B-window split is a weak null below n ≈ 2.7; (iv) **hole side unmeasured**: the D = 0 line reaches only −1.1 × 10¹² (TG limit) and a V_bg-independent series segment (CNP at V_tg ≈ −0.2 V, Si-insensitive, runs 4/6/7) is driven to neutrality there — geometry-limited on this pair, not a null; (v) **series-segment tone**: its predicted V_tg-only line (12–20 T) is not identified as any branch (the 13–16 T peaks track f₂ − f₁), but cannot be excluded at δF = 3 T; (vi) **absolute layer number**: the peak set matches the 4L ABAB overlay, not the trilayer ML+BL family (light fraction 0.21 vs 0.12–0.15; heavy 0.77 vs 0.87) — N = 4 is what the transport supports; pentalayer not tested; (vii) ABCA: excluded as the sole stacking of this region (a 0.21·F_L branch has no ABCA parent; sub-F_L fundamentals dominate); an ABCA minority domain contributing to the F_L tone is not excluded (mixed-domain confound of the sum tone); ABCB: not supported (light branch linear at 0.21·F_L, no Dirac-like supra-linear shape resolvable; citation-grade template).

**4. What would firm it.** A second R_xx pair on the flake (region cross-check) — operator rewiring; a cleaner R_xx pair without Hall admixture for the QH-ray lever-arm pin and ν = 8/12/16 ladder; a longer 1/B record for the light tone (lower onset: higher mobility cooldown, or mK/lower T_e rig) for the φ² mass split; the hole side at D ≈ 0 on a pair whose path is fully dual-gated; a second-density LK rung set.

**5. Calibration and housekeeping for the card.** c_bg/c_tg = 0.727 (run 4, ratio data-calibrated); absolute scale 0.93 ± 0.03 of the geometry prior (Luttinger, runs 5/8) — i.e. c_tg ≈ 2.60 × 10⁻³ F/m² (≈ 10.2 nm hBN-equivalent) with c_bg ≈ 1.89 × 10⁻³; n_offset −0.07 × 10¹² (design frame); D_offset 0 (gap minimum at geometric D = +0.006 V/nm); CNP ridge gaps to 3 kΩ at D = +0.3 V/nm; series segment CNP at V_tg ≈ −0.2 V (Si-insensitive); SdH onset 2.4 T at n ≈ 2.8 × 10¹² electrons; Hall admixture α ≈ 0.2 on B_1–B_2.

```

**Byte-comparison vs transport-call.md body (whitespace-stripped): MATCH**

## Independence grep (raman/rhombo/ABC/prior vocabulary) — 4 line hits

- cell 18: `Template (investigation Why / Verify): the two fundamentals **sum to 28.0 T = observed 28.1 T** and their difference **15.6 T = observed 15.6 T** — a {f₁, f₂, f`
- cell 25: `**Running verdict (B_1–B_2 region), before the LK split: ABAB — consistent-with → strong candidate.** Two branches on the ABAB curves across density (light ever`
- cell 28: `- F_L tone (29 T): **0.065 ± 0.004 m_e joint, but window-dependent: 0.051 ± 0.003 (2.4–4.5 T) vs 0.100 ± 0.010 (3.5–7 T)** — a fork (STYLE rule 14), not refined`
- cell 29: `**3. Confidence and hedges.** Strong, not decisive: (i) **one contact pair** — mosaic caveat, no cross-region check possible this cooldown; (ii) **mass ratio** `

## Geometry grep (gds/optical/pad/µm frame-bridge vocabulary) — 17 line hits

- cell 3: `# slot: geometry — gate-stack thicknesses from the device card's Gate-stack`
- cell 3: `# geometry (geometry prior — calibrate cnp-and-dline-calibration before`
- cell 11: `# CNP offset on the geometry prior from the two single-gate maxima (V_bg = 0 / V_tg = 0):`
- cell 11: `print(f"n at the R_xx maxima (geometry prior): TG-leg {n_tg*1e-16:+.2f}e12, BG-leg {n_bg*1e-16:+.2f}e12 cm^-2 -> n_offset ≈ {-(n_tg+n_bg)/2*1e-16:+.2f}e12 (to b`
- cell 11: `n at the R_xx maxima (geometry prior): TG-leg -0.35e12, BG-leg -0.38e12 cm^-2 -> n_offset ≈ +0.36e12 (to be replaced by the gatemap ridge fit)`
- cell 12: `Features (geometry prior, uncalibrated): the R_xx maximum sits at V_tg = −0.22 V (V_bg = 0) and at V_bg = −0.25 V (V_tg = 0) — both ≈ −0.38 × 10¹² cm⁻² of gate `
- cell 14: `from scipy.ndimage import gaussian_filter1d`
- cell 14: `print(f"  => c_bg/c_tg = {-slope:.4f} (geometry prior 0.8636 from 11 nm / 9.5 nm)")`
- cell 14: `=> c_bg/c_tg = 0.7271 (geometry prior 0.8636 from 11 nm / 9.5 nm)`
- cell 15: `**CNP-line fit** (axis orientation: ridge position = V_tg, fitted against V_bg rows; rows V_bg −1.25…−0.2 where the ridge has contrast ≥ 1.5 and sits inside the`
- cell 15: `**Second feature — not the channel CNP.** A weaker R_xx maximum (≈ 300 Ω) runs nearly vertically at V_tg ≈ −0.2…−0.3 V for V_bg ≳ 0, independent of V_bg: a regi`
- cell 18: `Template (investigation Why / Verify): the two fundamentals **sum to 28.0 T = observed 28.1 T** and their difference **15.6 T = observed 15.6 T** — a {f₁, f₂, f`
- cell 21: `**Read.** The V_tg ≈ −0.2 V feature is **Si-insensitive**: R(V_tg) for V_tg ≤ −0.1 V is identical at Si = 0 and +25 V (1.7 / 4.4 / 14 kΩ at −0.3 / −0.2 / −0.1 V`
- cell 25: `3. **A tone at F_L in every column** (scale 0.93: 13.5 at n = 1.35 … 33.1 at 3.06; it is the dominant peak for n < 2.5). **Luttinger**: light + heavy = 6.9 + 25`
- cell 25: `**Running verdict (B_1–B_2 region), before the LK split: ABAB — consistent-with → strong candidate.** Two branches on the ABAB curves across density (light ever`
- cell 29: `**3. Confidence and hedges.** Strong, not decisive: (i) **one contact pair** — mosaic caveat, no cross-region check possible this cooldown; (ii) **mass ratio** `
- cell 29: `**5. Calibration and housekeeping for the card.** c_bg/c_tg = 0.727 (run 4, ratio data-calibrated); absolute scale 0.93 ± 0.03 of the geometry prior (Luttinger,`
