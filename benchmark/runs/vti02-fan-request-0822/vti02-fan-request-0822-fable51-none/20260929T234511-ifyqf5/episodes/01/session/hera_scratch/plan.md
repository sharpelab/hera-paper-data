# vti-02 — stacking-order campaign plan (HERA)

*Goal: ABAB vs ABCA vs ABCB for tetralayer vti-02, region-resolved (one wired pair: sr1 = B_1−B_2), evidence-cited. Written 2026-08-23 ~05:30 by the second instance (the first instance's plan file was not on disk — reconstructed from its cell markdowns, session_notes and the data).*

## What discriminates the stackings (what the fan must show)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| low-energy bands at D = 0 | two bilayer-like parabolic bands (light + heavy), band overlap → semimetal | one flat quartic band, E ∝ k⁴ | monolayer-like linear + trilayer-like cubic, offset |
| SdH at fixed n | **two** fundamental tones, F₁+F₂ = n·h/4e | **one** tone at n·h/4e (heavy → weak at T_e ≈ 8 K) | two tones, very different masses; Lifshitz transition vs n |
| zero-mode LL count (total) | 16, split 8 + 8 between blocks | 16 in one ladder (N = 0..3) | 16 = 4 (mono) + 12 (ABC-trilayer) |
| strong QH gaps at low B | ν = ±8 (block gap) and multiples of 4; level crossings between blocks | ν = ±16 first; ν = ±4, ±8, ±12 from splitting the N = 0..3 manifold | ν = ±4 (Dirac N = 0) and ±12, ±16 |
| ν = 0 at D = 0, high B | insulating (layer-antiferro/quantum-Hall ferro) | insulating | weak |
| CNP gap vs D | opens (bilayer-like), both blocks | opens strongly (flat band → largest R) | asymmetric in D |

The Landau fan (Rxx vs n and B at D = 0) delivers items 2–4 at once; the 0 T gatemap (run 5) already gave the D-dependence of R_CNP (gap opens with D — three candidate parents, not discriminating on its own).

## Steps

1. **Gate C / liveness** (`gate-current-sanity-check`, runs 0–3) — DONE. Alive on the provided pair, no leakage to any limit, Rxx 60–330 Ω; two series regions (double peaks).
2. **0 T gatemap → CNP + (n, D) calibration** (`gatemap`, run 4 aborted / run 5) — DONE. Ridge A (main) slope → c_bg/c_tg = 0.773; c_tg anchored at the 9.5 nm prior; n_offset −0.089×10¹², D_offset −0.013 V/nm (R_CNP(D) vertex). Ridge B = second region, 0.43×10¹² more electron-doped (series mosaic confound). D = 0 line inside the validators: n = −1.27 … +3.27×10¹² (TG-limited).
3. **SdH spot checks at D = 0** (`sdh-spot-check`, runs 6 electron +3.2, 7 hole −1.2) — DONE (measured), read in ana on 08-23. Clear SdH from ~1 T on both sides, QH minima (Rxx → 0) by 2.3 T at n_geo = 3.2. Electron side Δν = 4 periodicity at F ≈ 29.5 T vs F_L(geo) = 33.1 → **density scale ≈ 10 % high** (c_tg prior too large) — the fan's LL indexing recalibrates the absolute scale. Broad Rxx maximum 7.8–9.5 T at n_geo 3.2 (level crossing / gap collapse candidate).
4. **Landau fan at D = 0** (`landau-fan`) — **NEXT** (operator's request). n fast along the calibrated D = 0 line, −1.25 … +3.2×10¹² at 0.025 (179 pts); B slow 0.5 → 4.0 T at 0.1 T then 4.2 → 10 T at 0.2 T (66 rows), magnet starts at 0 so the fan climbs. Establishes: LL fan index → absolute n calibration; which ν carry the strong gaps (8 vs 16 hierarchy; ν = 4 presence at low B); one vs two SdH ladders (line families converging on the CNP with different slopes); ν = 0 behaviour; hole/electron asymmetry. ~5.5 h.
5. **Fan read + first call draft** in ana: re-formed fan, ν-indexed lines, per-B n-cuts, tone extraction vs n (F(n) slopes summing to h/4e or not), density recalibration.
6. **Decide by the data** (ride the magnet down from 10 T — never re-traverse):
   - if two tone families / ν = 8 hierarchy → ABAB candidate: confirm with a **finite-D fan cut** (D ≈ +0.15 V/nm, hole+electron) — Bernal blocks split differently from a rhombohedral gap;
   - if a single ladder with a 16-fold zero manifold and heavy-mass damping → ABCA candidate: confirm with **T-dependence of the CNP gap at finite D** (`set_both`, ratio 0.95, ≤ 30 K) and of the SdH amplitude at fixed n (mass);
   - if the ladders show a Lifshitz-type change in tone count with n → ABCB candidate: a **dense fixed-n 1/B series** across the transition.
7. **Region B check** (the second series region): the fan carries it as a ×1.13-density replica of every feature; if the replica is resolvable it is the "second region" line of the verdict; otherwise state it as unresolved.
8. **Call** as the ana notebook's last cell (per-region verdict, evidence with run ids and numbers, hedges), then `return-to-initial` close-out.

## What would change my mind / abort criteria for step 4
- First rows: sr1 railing beyond the CNP (≥ 0.9 fs across > 5 points/row) → interrupt, re-size sensitivity. Gate current excess > 100 pA sustained → interrupt (guard trips at 1 nA automatically).
- Rows at 2 T featureless (no minima along n) while runs 6/7 showed oscillations at 2 T → something changed (contacts, T) → stop, re-read state.
- T_sample drifting > 1.5 K at high B → pause (the T-B interaction the rig card flags).
- If by 4 T the fan already reads cleanly (ν-lines indexed, tone families obvious), the high-B half still runs — the ν = 0 / low-ν sector at high B is where ABAB and ABCA differ most.
