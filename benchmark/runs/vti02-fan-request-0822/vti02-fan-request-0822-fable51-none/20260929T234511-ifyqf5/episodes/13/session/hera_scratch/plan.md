# vti-02 — stacking-order campaign plan (HERA)

*Goal: ABAB vs ABCA vs ABCB, region-resolved (one measured pair: sr1 = B_1−B_2), evidence-cited.
Written 2026-08-23 05:xx by the second instance, reconstructing steps 0–3 from the record (the
first instance did not land a plan.md — see session_notes PROTOCOL). Kept current as data lands.*

## Discriminants (what the data has to show)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| bands at D = 0 | two bilayer-like parabolic bands, light + heavy (m* ≈ 0.03 / 0.06 mₑ); semimetallic overlap | one very flat quartic band (m* large near CNP), 16-fold zero-energy LL manifold | no inversion symmetry → intrinsic gap at D = 0 (~10 meV class), monolayer-like + bilayer-like pieces |
| Landau fan at D = 0 | two fans (two SdH frequencies with F₁+F₂ = F_L) → LL crossings / beating; lowest gaps at ν = ±4 (8-fold zero LL per block, blocks offset) | single fan, first gaps at ν = ±8 (16-fold zero LL) then interaction-split; LL energies ∝ B² at low index | Dirac-like √B ladder + parabolic ladder, ν = 0 gapped at all B, e/h asymmetric |
| R_CNP vs D at B = 0 | weak, slow gap opening; symmetric in ±D | strong exponential gap opening, symmetric in ±D | gap already at D = 0, **asymmetric** in ±D |
| T-dependence of R_CNP | metallic/semimetallic (weak) | insulating at finite D, activated | insulating at D = 0 |

## Steps

0. **Gate C — liveness / leakage** (`gate-current-sanity-check`) — DONE, runs 0–3. Alive, 60–330 Ω, no leakage. Two series CNPs (regions A, B).
1. **0 T gatemap → CNP + (n, D) calibration** (`gatemap`, `cnp-and-dline-calibration`) — DONE, run 5 (run 4 railed). Ratio c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m² (9.5 nm prior — *absolute scale unverified*), n_offset −0.089×10¹², D_offset −0.013 V/nm. Region B parallel ridge, +0.43×10¹² electron-doped. R_CNP(D): 297 Ω at D ≈ 0 → 2.4 kΩ at +0.25 V/nm, only −0.08…+0.30 V/nm covered.
2. **Feasibility model** — DONE (in the run-6 proposing markdown): model SdH frequencies per stacking at the spot densities.
3. **SdH spot checks e/h at D = 0** (`sdh-spot-check`) — DONE, runs 6 (0 → 10 T) and 7 (10 → 0.3 T). QH regime from ~2 T; dominant 7.1–7.4 T tone on both sides (n-independent — light band or ungated region), n-dependent content too. Not a read by itself.
4. **Landau fan at D = 0** (`landau-fan`) — **NEXT** (operator request). Fast: n = −1.25 … +3.25×10¹² along the calibrated D = 0 line (131 pts, Δn = 0.035×10¹², TG −0.291…+0.998 V, BG −0.484…+1.185 V — TG-limited both ends). Slow: B 0.4 → 10 T in 0.2 T (49 rows). sr1 100 µV (10 kΩ FS; the ν = 0 state at high B may rail — accepted, the rail is itself a read). ≈ 3h20m priced (1.10 s/pt from run 5; 0.134 T/min from run 6), ends at 10 T.
   Establishes: (i) the LL fan slopes → **absolute n calibration** (ν = n h / eB fixes c_tg, closing step 1's open end); (ii) the degeneracy sequence out of the CNP (±4 vs ±8); (iii) whether the 7.2 T tone fans from the CNP (a band) or is a horizontal stripe (ungated region); (iv) crossings (two-band ABAB) vs a single fan; (v) e/h asymmetry.
5. **D-dependence at high B** (ride 10 T down): (n, D) map at fixed B = 10 T over the validator box, or a D-sweep at the CNP — the ν = 0 / small-ν gaps vs D discriminate ABAB (weak) from ABCA (strong layer-polarized) from ABCB (asymmetric). Design after step 4's read. ~1.5–2 h.
6. **R_CNP(D) at B = 0 across ±D symmetrically** and/or **T-dependence of R_CNP** (heater ladder ≤ 100 K, ratio 0.95) if the call still hinges on gap size/asymmetry. Optional; ~2 h.
7. **Call** in the ana notebook (output contract), then **close-out** (`return-to-initial`).

## What would change my mind
- Fan shows n-independent horizontal stripes → the 7.2 T tone is a parasitic region; discount it, read the fanning lines only; consider whether B_1−B_2 sees region B in series (two CNPs → two fans offset by 0.43×10¹²).
- ν = 0 rails and the fan's low-|n| structure is unreadable → re-run a narrow low-|n| fan at 500 µV or step 5 with autorange.
- Fan lines don't extrapolate to the run-5 CNP → n_offset/scale wrong; recalibrate from the fan before any (n, D) claims.
- T_sample drifts > 1.5 K or gate current > 1 nA → guards trip; stop and notify.

## Bans honored
No probing of gate limits (all vectors ≥ 2 mV inside validators); no Si survey (Si held at 0 V throughout).
