# vti-02 — stacking-order campaign plan

*Goal: ABAB (Bernal) / ABCA (rhombohedral) / ABCB (mixed) for vti-02 tetralayer
graphene, evidence-cited, on the one wired pair (sr1 = B_1–B_2). One contact
pair is wired → the "per-region" verdict is one line; that is a stated hedge,
not a choice.*

*Reconstructed 2026-08-23 at handoff — the original file did not survive. Steps
1–3b are read back from the measure notebook (cells 33–42) and the data; step 4
onward is mine.*

## Discriminators I am buying

| observable | ABAB | ABCA | ABCB |
|---|---|---|---|
| # Fermi surfaces at D = 0 | **2** (two bilayer-like bands), F₁+F₂ = F_L | **1**, F = F_L | hybrid — mono-like + trilayer-like, generally 2 with a very different split |
| SdH frequency vs n | two branches, each ∝ n, different slopes summing to the Onsager line | single branch **on** the Onsager line | two branches, asymmetric |
| fan-line families | two interleaved sets of slopes | one set, Δν = 4 | two, and a D = 0 gap (no inversion symmetry) |
| CNP at D = 0 | metallic/semimetallic | metallic at D = 0, gaps fast with D | intrinsic gap already at D = 0 |

The Onsager line is the anchor: `F_L = |n|h/4e` from the *session's own* (n, D)
calibration. "One Fermi surface carrying the full density" vs "two sharing it"
is the primary call; the ABCB/ABAB separation leans on the split ratio and on
the D = 0 CNP behaviour.

## Steps

1. **`gatemap`, B = 0** — CNP line + (n, D) calibration. → runs 4 (aborted,
   railed), **5**. *Done.* Gives c_bg/c_tg = 0.773 (data), c_tg from the 9.5 nm
   geometry prior, n_offset −0.089e12, D_offset −0.013 V/nm. Two CNP ridges
   (A main, B offset) — a second region under the pair, carried as a hedge.
2. **Feasibility model table** — F_L and the predicted ABAB/ABCA tone
   structure at the two reachable spots. *Done in-head by the prior instance;
   **never landed on the page** — re-derive and land it (see Debt).*
3. **`sdh-spot-check`, D = 0, two densities** — cheap test that SdH is
   resolvable at all, and a first tone count. → runs **6** (n = +3.20e12,
   B 0→10 T) and **7** (n = −1.20e12, B 10→0.3 T). *Done; analysed 2026-08-23,
   not yet landed in ana (Debt).* Read: oscillations are strong and clean,
   onset **0.3–0.7 T**, minima reaching R ≈ 0, and the tone lists are
   **harmonic-confounded** — 22.2 / 29.5 T flagged as 3×/4× of 7.1 T at
   n = +3.2e12. Suggestive of a 7 T + 26 T pair on the 33.1 T Onsager line
   (ABAB-like), but *not* decisive from a fixed-n FFT: a harmonic and a second
   Fermi surface are degenerate at one density.
4. **`landau-fan`, D = 0, B 0 → 10 T** ← *next; this is the decisive step.*
   Density on the fast axis breaks the harmonic degeneracy step 3 could not:
   a real Fermi surface has F ∝ n with its own slope through the CNP, a
   harmonic sits at an exact integer multiple of its parent **at every n**.
   Same run gives the fan-line families and the filling sequence around the
   CNP directly off the image. Establishes: (a) one branch or two, (b) the
   split ratio if two, (c) the Δν step and the ν-width of the gapless CNP
   region.
5. **D-dependence** — a fan or a set of spot checks off D = 0 (or a
   `gatemap` at fixed high B). Tests the CNP gap-vs-D behaviour, which
   separates ABCB (gap at D = 0) from ABAB, and sizes ABCA's fast gap
   opening. Sized after step 4 says which question is still open.
6. **Call** — final ana cell, per the brief's output contract.

## What would change my mind

- Step 4 resolves **one** F-branch tracking the Onsager line across the whole
  density range, Δν = 4 fan lines, no second family → ABCA, and step 5 becomes
  a confirmation (gap opens fast with D) rather than a discriminator.
- Step 4 resolves **two** branches summing to F_L → ABAB vs ABCB, and step 5
  (D = 0 CNP gap) becomes the decider.
- Fan lines index at Δν = 8, or the CNP gapless region is not 4N-wide → my
  degeneracy model is wrong; stop and re-derive before claiming anything.
- No resolvable fan structure by B ≈ 2.5 T at this density step → the density
  axis is too coarse, not the physics; re-grid rather than conclude.

## Debt (carried, land when the fridge is busy)

- Step-2 model table is not on the page — re-derive and land in ana.
- Runs 6/7 analysis is not on the page — land it (raw first, then the read).
- Ridge B from run 5 (second CNP, offset in n) is an un-chased hedge: it means
  the pair spans two doping regions. Must appear in the confidence section.
