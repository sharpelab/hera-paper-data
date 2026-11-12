# vti-02 stacking-order plan (ABAB / ABCA / ABCB) — living doc

*Rewritten 2026-08-23 05:30 by the incoming instance (no plan.md was on disk at handoff);
steps 0–3 reconstructed from the notebooks / session_notes, steps 4+ are forward.*

## Discriminants (what each stacking predicts on the one wired pair, B_1–B_2)
| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed/polar) |
|---|---|---|---|
| SdH at D=0, high n | **two** tones F1+F2 = F_L, light/heavy ≈ 0.28/0.72 (bilayer-like bands λ=1.618γ1, 0.618γ1) | **one** tone at F_L (4-fold) away from the CNP | two-ish bands, not a clean BLG pair; gap at CNP |
| D=0 Landau fan | two interleaved LL ladders → **crossings**, irregular ν sequence, Δ(1/B) of minima non-uniform | clean 4-fold ladder from CNP at high n; broken-symmetry near CNP; ν=±8 first gap | CNP gapped at B=0; LL structure asymmetric in ±D |
| R_CNP(D) | semimetal: weak growth with |D| | strong growth (gap opens) — even spontaneous gap at D=0 | gap, **minimum shifted from D=0 / asymmetric in ±D** |

## Done
0. Gate C (runs 0–3): alive, leak ≤ 0.2 nA, R 60–320 Ω.
1. Gatemap run 5 (run 4 railed, aborted): CNP ridge A slope → c_bg/c_tg = 0.773 (prior 0.864); ridge B parallel, offset −0.43e12 (second region / contact doping in the pair?). R_CNP 300 Ω @ D≈0 → 2.4–3 kΩ @ D=+0.3 V/nm (strong D growth; only +D side covered by the window). D_offset −0.013 from R_CNP(D) vertex (NB: symmetry-defined D=0 would hide an ABCB offset — hedge).
2. (model table — frequencies per stacking; see spot-check markdowns in measure cells 39/41)
3. Spot checks runs 6/7 (ana cells 14–16): e-side tones 7.1 + 22.2 (sum 29.3 ≈ 0.89 F_L) + 29.5 T; minima non-periodic in 1/B. ABAB-leaning, harmonic ambiguity unresolved. Density scale reads ~11 % high (c_tg prior) → fan calibrates it.

## Next
4. **D=0 Landau fan (run 8)** — n fast along the calibrated D=0 line, −1.25…+3.24e12 (cal units; TG limit caps the e-side at 3.24), 150 pts; B slow 1→10 T, uniform-1/B (Δ=0.01 T⁻¹) to 3.1 T then 0.1 T steps to 10 T, 137 rows; ~9 h; ends at 10 T.
   Establishes: (a) the density scale from QH fan-line slopes (ν = n h/eB) → calibrated n; (b) per-n FFT: number of tone families, F_i(n), and whether ΣF_i = F_L(n); (c) LL crossings (ABAB) vs clean 4-fold ladder (ABCA); (d) CNP behaviour vs B (ν=0 gap).
   Checkpoints: first 2 rows (rail at CNP? leak? CNP at n≈0?); ~row 45 (B≈1.8 T, ~2.5 h): partial per-column FFT over 1–1.8 T for the light tone vs n; ~row 90 (B≈5 T, ~5.5 h): fan-line slopes → density scale, crossing presence.
5. **Finite-D fan or fixed-B n–D map, riding the field down from 10 T** (never re-traverse). Choice after step 4: if ABAB-like, a fixed-B (e.g. 6–8 T) n–D map shows D-driven LL crossings; if ABCA-like, a D≠0 fan shows layer-polarized gaps. Also cover −D at B=0 on the way (R_CNP(D) symmetry — ABCB test) — cheap: an n–D cut through the CNP spanning ±D inside the validators.
6. Call in ana (output contract), close-out.

## What would change my mind
- Fan FFT shows a single family at ΣF = F_L with no crossings at n > 1e12 → ABCA; the 7.1 T tone would then be a harmonic artefact / second region.
- Tone-sum ≠ F_L (after fan density calibration) or tones varying non-monotonically with n → mixed regions (ridge B) contaminating the pair → region-hedged / "cannot tell".
- R_CNP(D) clearly asymmetric about the geometry D=0 → ABCB candidate.
