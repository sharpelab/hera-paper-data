# HERA plan — vti-02 stacking-order call (2026-08-23)

Goal: ABAB vs ABCA vs ABCB (or calibrated "cannot tell") for the one measured
pair (sr1 = B_1−B_2, source T_0, drain B_3). Evidence must be this session's
`data/<id>` only.

## Physics discriminators (what each stacking should show)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| R_CNP(D) at B=0, base T | modest rise with abs(D) (semimetal → small gap; ~×2–10) | strong, exponential rise (insulating, ≫MΩ by abs(D)~0.2–0.3 V/nm); often already resistive at D=0 | gap opens asymmetrically: R(+D) ≠ R(−D) (no inversion / mirror) |
| D → −D symmetry | symmetric (inversion) | symmetric (inversion) | **asymmetric** — the ABCB fingerprint |
| activation gap Δ(D) from R_CNP(T) | few meV, weakly D-dependent, may stay metallic | tens of meV, ~linear in abs(D), large | intermediate; asymmetric in D sign |
| Landau fan near CNP (Rxx minima) | two bilayer-like sectors: ν=±4 strong, LL crossings, non-monotonic gap sizes vs B | 16-fold zero-energy LL group → first robust gaps at ν=±8 (then ±12, ±16); ν=±4 weak/absent at low B; zero-LL splits readily with D | Dirac-like + quadratic sectors → mixed ν sequence; asymmetric in D |
| CNP at D=0 | low R (band overlap), R_CNP(T) weak | large R, R_CNP(T) strongly insulating | moderate |

Absolute n scale: the LL fan slopes (n = ν e B / h) calibrate c_tg+c_bg;
the CNP-line slope calibrates c_bg/c_tg (geometry prior: 0.864); the CNP
offsets set n_offset, D_offset.

## Gate box (device card) in (n, D) — geometry prior only

c_tg = 2.80e-3 F/m² (1.75e12 cm⁻²/V, 0.316 V/nm per V), c_bg = 2.41e-3 F/m²
(1.51e12 cm⁻²/V, 0.273 V/nm per V). Full box: n ∈ [−2.5, +4.8]e12 cm⁻²,
D ∈ [−0.32, +0.34] V/nm. Along n=0 (if offsets≈0): V_bg = −1.16·V_tg,
D from −0.095 (V_tg=−0.3) to +0.316 V/nm (V_tg=1.0). The negative-D side
is short — the D-symmetry test is confined to abs(D) ≲ 0.09 V/nm unless the
CNP offset helps. State this on the page when it bites.

## Settings (state0, measure cell 27)

Drive 1 V / 100 MΩ = 10 nA; sr0 gain −1e6 (10 mV at sr0 for 10 nA; sens
20 mV OK); sr1 sens 2 µV (= 200 Ω full scale → will rail; set 1 mV +
autorange hook); τ = 0.3 s @ 24 dB/oct on sr0/sr1 → ~2–3 s/pt dwell needed.
Ask: set τ = 30 ms (dwell 0.25 s/pt) in the gate-C cell — flagged to the
operator, restored at close-out from state0.

## Steps

0. **Gate C — liveness** (~5 min). 0D measure at V=0 (I, phase, Rxx);
   1D TG sweep at V_bg=0, −0.3→1.0→−0.3 V at 5 mV (hysteresis + leakage
   on k_tg.curr/k_bg.curr). Establishes: contacts alive, R scale, lock-in
   ranges, first CNP sighting. Kill: I_drain ≈ 0 / phase wrong → rewiring
   problem, flag.
1. **1D BG sweep** at V_tg=0, −1.3→2.0→−1.3 V at 10 mV (~4 min). Second CNP
   sighting → rough slope check vs 0.864.
2. **Coarse gate map** full box, TG fast 20 mV × BG slow 100 mV (66×34,
   ~15 min, B=0). Establishes CNP line (slope → c_bg/c_tg; intercept →
   offsets), R_CNP(D) coarse, D-symmetry first look. → set cal offsets.
3. **CNP D-line** (multisweep V_tg,V_bg along n=0, ~200 pts, both
   directions, ~2 min) + **fine map** around the CNP line (TG 10 mV × BG
   50 mV in a reduced box, ~30 min). Establishes R_CNP(D) precisely,
   asymmetry ratio R(+D)/R(−D), gap-vs-D shape. Drop excitation to 0.1 V
   if R_CNP > 1 MΩ (10 nA × 1 MΩ = 10 mV ≫ kT).
4. **Landau fan** (B slow 0→8 T, 0.1 T rows; fast = n-line at D≈0 across the
   box, ~150 pts) ≈ 2 h measured (ramp 58 min bare + rows). Establishes the
   ν sequence near CNP (±4 vs ±8), LL crossings, absolute n calibration.
   Checkpoints: first 3 rows (rails/leak), then every ~30 min. Optional
   second fan at finite D on the way down (never re-traverse for free —
   sweep 8→0 with a different D-line).
5. **T ladder of the CNP D-line** at B=0: {base, 3, 5, 8, 12, 20, 30, 50} K
   via set_both(T, 0.95), accept on stability (2–5 min settles; +1.4 K
   overshoot up-steps). ~1 h. Establishes Δ(D) (Arrhenius) and its D-sign
   asymmetry. Last because the descent to base is passive and slow.
6. **Call** in ana notebook per the output contract; close-out on ask.

## What changes my mind

- Gate C shows a dead/floating pair → stop, flag rewiring; no detour.
- CNP outside the box on either gate → work with the reachable D range,
  state coverage loss; if no CNP visible at all → "cannot tell" path.
- Leakage (>100 pA excess) on either Keithley → shrink the used range,
  never the limit; note it.
- R_CNP ≫ MΩ at D≈0 already → ABCA-leaning; prioritise T ladder over fan.
- Strong D asymmetry in step 2 → ABCB-leaning; extend the fine map on both
  D signs and add a fan at ±D.

## Status log

- 2026-08-23: gates A/B green on disk (measure cells 2–27 executed). Probe +
  VERIFY landed; awaiting "go for autonomy".
- Run 0 (gate-c-liveness, TG at BG=0): alive, Rxx 40–370 Ω, no CNP in cut; 0.30 s/pt @ delay 0.2. Step 0 done.
- Run 1 (bg-sweep-1d, BG at TG=0, τ 100 ms/delay 0.5): running 20:33, ~0.68 s/pt.
- Run 1 (bg-sweep-1d): two Rxx peaks at V_bg −0.25 / +0.12 V (310/275 Ω), shoulder +0.5 V, no hysteresis. Step 1 done.
- Run 2 (gatemap-coarse, full box 34×66): started ~20:45, ETA ~21:12.
- Run 2: plotter-crash stub (discard). Run 3 (gatemap-coarse): CNP line V_tg = 0.10 − 0.691·V_bg (c_bg/c_tg 0.69); R_CNP 320 Ω → 2.8 kΩ saturating past D≈+0.25 V/nm; ±D roughly symmetric; weak parallel 2nd line 0.4 V lower in V_bg. Lean: ABAB. Step 2 done.
- Run 4 (cnp-band-map, 39 rows × ±0.15 V TG @5 mV): started ~21:17, ETA ~21:45. Then: Landau fan (step 4) along the CNP-line n-axis at D≈0; T ladder (step 5) of the D-line.
- Run 4 (cnp-band-map): R_CNP min 248 Ω at (0.11, 0.00) = D0 (D_geo +0.017); symmetric ±D to ~5 %; ×14 rise to 3.4 kΩ, saturating past D−D0≈0.23; FWHM 200→45 mV. Slope c_bg/c_tg 0.71. Step 3 done. Lean: ABAB (moderate).
- Next: run 5 landau-fan-up (0→8 T continuous ramp, D0 line, ~62 min); then fan-down at D−D0≈+0.28 (8→0); then T ladder of the D-line at B=0.
- Run 6 (landau-fan-up, D≈0, 0.6→8 T): ν=0 insulating stripe grows non-monotonically (dips at ~2.4 and ~7.2 T → zero-LL crossings, Bernal fingerprint); clean QH fan both carrier signs. Extracting ν assignments + n-scale. Run 7 (fan-down at D−D0≈+0.20) running.
- Run 6 ν-fit: n = 0.82 × n_geo; minima at ν = −12,−8,−4,+4,+8,+12,+16,+20 (4-fold); ν=±4 robust to lowest B → Bernal LL structure. ν=0 dips at ~2.4 / ~7.2 T (crossings).
- Run 7 (fan-down at D−D0≈+0.20): ν = ±2, ±4, +6, ±8 (steps of 2 — D-split), ν=0 monotonic 1 kΩ→73 kΩ. Step 4 done. Remaining: T ladder (step 5) → call → close-out on ask.
- Runs 8–18 (cnp-t-ladder): Δ = 1.8 meV (+0.28), 1.2 meV (+0.19), ~0 (|D|≤0.11); flat below 7 K. Step 5 done.
- FINAL CALL landed in ana: ABAB (Bernal), strong, single measured pair. Awaiting operator ask for return-to-initial close-out.
