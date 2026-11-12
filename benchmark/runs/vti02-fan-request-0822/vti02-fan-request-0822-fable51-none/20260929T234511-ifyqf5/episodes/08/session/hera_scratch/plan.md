# vti-02 — stacking-order campaign plan (ABAB / ABCA / ABCB)

*Rebuilt 2026-08-23 05:25 by the second HERA instance: the first instance's
`plan.md` was not on disk at handoff. Steps 0–3 are reconstructed from the
measure/ana notebooks and `data/`; steps 4+ are this instance's plan.*

## Goal → what discriminates the three stackings (transport, one Rxx pair)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| B = 0 bands at D = 0 | two bilayer-like massive bands (light + heavy), semimetallic overlap | one flat-bottomed band (∝k⁴), CNP touching | Dirac-like + massive bands, small intrinsic gap |
| SdH at fixed n | **two** fundamentals, F₁ + F₂ = F_L(n) = nh/4e | **one** fundamental at F_L(n) (4-fold) until symmetry breaking | mixed: light Dirac tone + massive tone |
| R_CNP(D) at B = 0 | gap opens with D, modest (kΩ), saturating | gap opens strongly (≫ 10 kΩ, MΩ at 0.3 V/nm) | weak D dependence |
| Landau fan at D = 0 | two interpenetrating 4-fold LL ladders → **level crossings**, zero-LLs of both ladders (8+8) | **16-fold zero-energy LL** → first strong gaps at ν = ±8 (then ±12, ±16; ±4 only via symmetry breaking) | ν = ±2 (Dirac) among 4-fold steps |

The fan is decisive: the filling-factor sequence of the strong minima, the
presence/absence of LL crossings, and the zero-LL degeneracy are read directly.
The fan slopes (n = ν e B / h) also pin the absolute density scale, which so far
rests on the geometry prior for c_tg.

## Steps

0. **Bring-up / VERIFY** — done (measure [16]–[17], `VERIFY: ALL GREEN`; grant in `session_notes.md`).
1. **Gate C liveness + gate safety** (`gate-current-sanity-check`, runs 0–3) — done: alive on
   T_0→B_3 / B_1−B_2, Rxx 60–330 Ω, gate currents at the pA floor to every limit.
2. **0 T gatemap → CNP + (n, D) calibration** (`gatemap`, run 5; run 4 railed) — done (ana cell 13):
   ridge A slope → c_bg/c_tg = 0.773 (prior 0.864); c_tg anchored at the 9.5 nm prior;
   n_offset −0.089e12; D_offset −0.013 V/nm from R_CNP(D) symmetry. R_CNP: 240 Ω (D≈0) → 2.4 kΩ
   at D ≈ +0.25 V/nm, saturating — a modest, saturating D-gap (leans ABAB/ABCB over ABCA, not decisive).
   Second, parallel, fainter ridge B: a second region 0.43e12 electron-doped vs A (series region).
3. **SdH spot checks at D = 0** (`sdh-spot-check`, runs 6 e-side n=+3.2e12 / 7 h-side n=−1.2e12) — done,
   analysed 05:20 (`hera_scratch/sdh_spots.py`, to land in ana): run 7 → 5.3 + 7.1 T fundamentals and
   their sum 12.4–12.6 T (= F_L); run 6 → 7.3 T and 29.4 T (sum 36.7 vs F_L 33.1 T, +11%). Two tones
   summing to F_L = two-band read → disfavours ABCA; the 11% is the c_tg scale to be fixed by the fan.
4. **Landau fan at D = 0** (`landau-fan`) — **NEXT** (operator's request). Fast axis: (Vtg, Vbg) co-swept
   along the calibrated D = 0 line, n = −1.275 … +3.25e12 in 0.025 steps (182 pts; hole side limited by
   TG −0.3 V). Slow: B 1.0 → 10.0 T in 0.2 T (46 rows), ascending from 0 T where the magnet sits.
   fast_delay 1 s (run-5 calibrated 1.17 s/pt), sr1 200 µV (20 kΩ FS: ν = 0 at 10 T may be insulating).
   ≈ 4 h 15 m; ends at 10 T with gates parked at 0. Establishes: ν of strong minima (4 / 8 / 12 …),
   crossings, zero-LL degeneracy, and dn/dB slopes → absolute n scale.
5. **Fan analysis** — re-form (fan_grids), log R map in (n, B) and (n, 1/B); trace minima; fit ν lines
   n = ν e B/h + n₀ → density-scale correction; compare the ν sequence against the table above.
   Land in ana with the running verdict.
6. **Conditional follow-ups (priced when reached, riding the magnet down from 10 T):**
   a. If the D = 0 fan is ambiguous between ABAB and ABCA (e.g. ν = ±4 and ±8 both strong):
      a D ≠ 0 fan (|D| ≈ 0.15–0.2 V/nm) — ABCA's 16-fold zero LL splits into layer-polarized
      octets (ν = ±8 stays, ν = 0 gap opens hard); ABAB shows the light/heavy ladders shifting.
   b. If the two-band picture holds: T-dependence of the two SdH amplitudes (LK masses) at one n —
      the light/heavy mass ratio is a stacking-model check (`set_both`, ratio 0.95, ≤ 20 K).
7. **Call** — final ana cell per the output contract (one region: B_1−B_2; the series region B is
   noted as a hedge, not a separately measured pair).
8. **Close-out** on the operator's `return-to-initial`.

## What would change my mind

- Fan shows a **single** 4-fold ladder with ν = ±8 as the first strong gap and no crossings → ABCA,
  and the spot-check "two tones" must be re-read as a split single band (spin/valley).
- Strong ν = ±2 minima (Dirac-like ladder) mixed with 4-fold steps → ABCB.
- Features that do not move with n (horizontal in the fan) → a parallel ungated region / contact
  artefact; the 7.1–7.3 T tone common to runs 6 and 7 is the thing to check for this.
- Region B (second ridge) contaminating the pair: a second, offset copy of every feature shifted by
  0.43e12 in n.
