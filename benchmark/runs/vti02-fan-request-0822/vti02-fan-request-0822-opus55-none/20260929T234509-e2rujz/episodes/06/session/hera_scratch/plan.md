# vti-02 stacking call — plan (rebuilt 2026-08-23 05:30 at instance handoff; the prior instance's plan.md was not on disk)

Goal: ABAB / ABCA / ABCB call for the one measured pair (sr1 = B_1−B_2; hardwired, the only Rxx pair),
evidence-cited, or a calibrated "cannot tell".

## Discriminators (what each stacking predicts in what we can measure)
| handle | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed, polar) |
|---|---|---|---|
| SdH tones at D = 0, high n | **two** tones (light + heavy bilayer-like bands, λ = 0.618 / 1.618), F_light + F_heavy = F_L, both ∝ n, fraction ~0.25 / 0.75 | **one** tone F ≈ F_L (single low-energy band above Lifshitz; three F_L/3 pockets at very low n) | band-asymmetric, model-dependent; tone set differs e vs h |
| e/h symmetry of the fan | roughly symmetric | roughly symmetric | asymmetric |
| R_CNP vs D | semimetal at D=0 (γ2 overlap), weak D growth | small/zero gap at D=0, strong D-opened gap | intrinsic gap at D ≈ 0 and **±D asymmetry** (built-in polarization) |
| QH at low ν | LL crossings of two families (dense crossing grid) | ν = 0 strong; 16-fold zero-energy manifold, first strong gaps ±8 | ±D-asymmetric LL crossings |

## Steps
0. **Gate C** — liveness + leakage (runs 0–3). DONE: alive, no leakage, two series CNP maxima.
1. **0 T gatemap → CNP + (n, D) calibration** (run 5). DONE: ridge A slope 0.773 (c_tg = geometry prior 9.5 nm);
   n_offset −0.089; D_offset −0.013 V/nm from the R_CNP(D) vertex (**assumes ±D symmetry — circular for ABCB; hedge**);
   region B (parallel ridge) electron-offset by +0.43e12. R_CNP(D) 240 Ω → 2.4 kΩ at D = 0.25 V/nm.
2. **Feasibility / model tones** (prior instance's table, as quoted in the step-3 cells): n=+3.2: F_L 33.1, ABAB 7.5/25.6, ABCA 33.1;
   n=−1.2: F_L 12.4, ABAB 5.3/7.1, ABCA 12.4 (m* ~1, LK-dead).
3. **SdH spot checks** (runs 6, 7). DONE: e-side 7.1 + 30.0 T (sum 37 vs F_L 33.1 → scale error or region B);
   h-side 6.8 dominant + 12.3 ≈ F_L + weaker tones. QH (R→0) from ~2 T. Leans two-band, not a call.
4. **Landau fan at D = 0** (NOW, run 8): B slow 1 → 9 T (uniform-1/B 1–4 T for the per-n FFT, 0.2 T steps 4–9 T for the QH picture),
   n fast −1.25 … +3.25e12 at 0.025e12. Establishes: F(n) for each tone → count of tones vs n, slopes (sum = F_L? → absolute
   density calibration), zero-intercepts (region A at n_A = 0 vs region B at n_A = −0.43), e/h symmetry, LL-crossing pattern.
   ~6.7 h, ends at 9 T.
5. **D-dependence** (after the fan; design from the fan): candidates (a) n–D map at fixed B ≈ 9 T (start where the fan ends):
   LL crossings vs D, ν = 0 vs D, ±D symmetry (ABCB); (b) short ±D fans at one n. Pick the cheapest one that answers what the fan leaves open.
6. **Call** — final ana cell per the output contract.

## What would change my mind
- Fan shows a single tone following F_L across n (e and h) → ABCA; a two-tone decomposition at run 6 was then region B / artefact.
- Tones whose F(n) extrapolates to n_A = −0.43 → region B (series mosaic), assign per region; one pair can end up "cannot tell" for one region.
- Strong e/h asymmetry or ±D asymmetry of the CNP / LL crossings → ABCB.
- Tones sum to F_L only with a rescaled c_tg → recalibrate density scale from the fan (lever-arm check) before comparing to models.
