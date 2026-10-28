# THE CALL (revised after run 8) — vti-02 stacking

Supersedes the run-7 verdict above, which read **ABAB (consistent-with)**. Run 8
converts that to a call. Output contract per
`investigations/tetralayer-stacking-fs-count.md` Step 7, all five parts.

## 1. Per-region verdict

> **channel B_1−B_2: ABAB (strong).**
>
> Tetralayer Bernal stacking, with symmetry-allowed inter-block magnetic
> breakdown producing the tone at F_L.

The investigation's stated criterion for *strong* is "two branches on the ABAB
curves **and** the F_L-tone origin passed". Both are met below.

One region only — T_1…T_4 are dead, so there is a single live four-terminal pair
and **no mosaic test is possible on this cooldown**. "Per-region" means "the one
region we can see".

## 2. Evidence

Electron side, D ≈ 0, T ≈ 1.20 K, B = 1 → 8 T uniform in 1/B, δF = 1.143 T,
57 density columns, τ = 300 ms.

**(a) A pair partitioning F_L, reproducible in every extraction.** Recurrence
over 18 extraction choices (6 field windows × 3 background degrees):

| n (10¹² cm⁻²) | F_L (T) | light | heavy | sum tone |
|---|---|---|---|---|
| 2.29 | 23.7 | 4.9 T (18/18, 0.21) | 17.7 T (18/18, 0.75) | 22.3 T (18/18, 0.94) |
| 2.69 | 27.8 | 5.9 T (18/18, 0.21) | 20.4 T (18/18, 0.74) | 26.3 T (18/18, 0.95) |
| 3.05 | 31.5 | 7.6 T (18/18, 0.24) | 22.5 T (18/18, 0.71) | 29.9 T (18/18, 0.95) |

**18/18 reproducibility**, against 3–9/18 for the same partner tones in run 7.
The Luttinger sum closes (< 8%) in **39 of 57 columns**.

**(b) The F_L tone is a breakdown orbit, not an ABCA singleton.** This is the
discrimination the investigation makes *mandatory* before any singleton call, and
which run 7 could not perform. Splitting the record at its 1/B midpoint (B =
1.778 T) gives two halves of equal δF = 2.29 T, and comparing the sum tone's
amplitude against the heavy fundamental in each half:

| n (10¹²) | low-B half | high-B half | ratio | verdict |
|---|---|---|---|---|
| 2.55 | 0.27 | 7.79 | 29.4 | breakdown |
| 2.72 | 0.74 | 8.36 | 11.3 | breakdown |
| 2.88 | 0.33 | 2.60 | 7.8 | breakdown |
| 3.05 | 0.54 | 3.59 | 6.7 | breakdown |

**13 testable columns: 10 breakdown-like, 0 pocket-like, 3 flat; median ratio
6.66.** The tone at F_L strengthens 5–30× with field relative to the
fundamentals, while a genuine pocket would keep its own Dingle envelope. **Zero
columns behave like a real pocket.** ABAB inter-block breakdown is
symmetry-allowed at N = 4 (no parity protection between the two bilayer-like
blocks), so this is the expected configuration, not an exotic one.

**(c) The partition tracks the ABAB curves across density, and excludes
adjacent-N.** The mandatory dual overlay:

| n (10¹²) | measured frac | ABAB-4L | trilayer ML+BL |
|---|---|---|---|
| 1.60 | 0.169 | 0.141 | 0.015 |
| 2.26 | 0.210 | 0.186 | 0.034 |
| 2.92 | 0.240 | 0.213 | 0.051 |
| 3.05 | 0.252 | 0.216 | 0.054 |

Mean |measured − model|: **ABAB-4L 0.025 vs trilayer 0.175 — tracks ABAB by
6.9×**. The partner fraction *rises* with density along the ABAB curve; this is
the trajectory test the investigation demands, not a single-point ratio match
(it warns the fractions cross near |n| ≈ 2×10¹², so magnitude alone cannot
decide). Transport supports **N = 4 over N = 3** decisively.

**(d) The whole peak set closes under one global scale.** The sum tone sits at
0.95·F_L rather than 1.00. A **single global density rescale of 1.05** — inside
my own lever-arm error (1.4% on c_tg, 6% on c_bg) and far inside the recipe's
0.8–1.2 band — puts the set at **0.22 / 0.78 with the sum at 1.00**, against the
ABAB model's **0.216 / 0.784**. The scale was fitted to the whole set, not to one
tone.

**(e) g = 4 verified in-data.** The calibration fans' LL ray slopes fall in ratio
4:8:12:16:20:24 with slope/ν consistent to 1.4% (run 5), so the four-fold
degeneracy underlying F_L = (h/4e)·n is measured. Degeneracy audit passes.

## 3. Confidence and hedges

**Confidence: high for ABAB on this region and this carrier sign.** The three
independent legs — reproducible pair, breakdown-discriminated F_L tone,
ABAB-tracking trajectory — agree, and each individually excludes a different
alternative (noise, ABCA, adjacent-N).

Hedges, each of which remains genuinely open:

- **The decisive per-branch mass test was not done.** ABAB's branches differ by
  ≈ φ² ≈ 2.6× in cyclotron mass, and the investigation calls the LK mass split
  *decisive* for separating two genuine bands from one band plus an artifact.
  Everything here is frequency-domain. This is the single biggest gap.
- **Single field polarity, ~1% R_xy admixture** (R_xx runs negative at deep
  minima, scaling as h/νe²). No ±B symmetrisation was possible. R_xy is periodic
  in 1/B at the *same* fundamental, so it distorts harmonic content but does not
  create new fundamentals — the pair positions and the partition are robust to
  it; the harmonic tones (≈ 1.8–1.9·F_L, and 15.0 T ≈ 2 × 7.6 T at n = 3.05) are
  not, and no claim rests on them.
- **Electron side only.** The hole side is gate-window-limited to −0.97×10¹²,
  inside the exception regime where the ABAB pair is close and balanced. Not
  measured in this fan at all. **Reported as unmeasured, not as a null.**
- **Absolute density scale rests on assigning Δν = 4 to the lowest LL ray.** The
  ray ratios fix the spacing, not the absolute; the cross-check is the implied
  top-gate hBN of 10.56 nm against the card's 9.50 (Δν = 6 → 7.0 nm, Δν = 3 →
  14.1 nm, both far worse). A consistency argument, not a measurement — and it is
  load-bearing, since the 1.05 rescale in (d) is only defensible because the
  lever arm came from exact LL degeneracy.
- **18 of 57 columns do not close the Luttinger sum**, and only 13 columns were
  testable for the breakdown discrimination (a resolvable sum tone plus a closing
  pair in *both* halves is a demanding requirement). The call rests on the
  columns that pass, and the failures are concentrated at low |n| where the light
  tone approaches δF.
- **One region, no mosaic test.** A single live pair cannot detect stacking
  domains elsewhere on the flake.

## 4. What would firm it further

1. **Per-branch LK masses** (`temperature-dependence-vti`, Flavor B) — the
   decisive test, and the obvious next session. Expect ≈ 2.6× between branches.
2. **±B symmetrisation** to remove the R_xy admixture and clean the harmonic
   structure.
3. **Hole side**, which needs a wider *negative* top-gate range — worth checking
   whether −0.3 V was a conservative provided limit or a physical one.
4. **A second Rxx pair** (operator rewiring at the breakout) to make a
   mosaic/per-region statement possible at all.

## 5. Status

**This is a call, not a lean.** vti-02, in the region probed by B_1−B_2, on the
electron side at D ≈ 0, is **Bernal (ABAB) tetralayer graphene** exhibiting
symmetry-allowed inter-block magnetic breakdown. Per the investigation's `Next`:
ABAB-confirmed means conventional tetralayer — the flat-band / correlated /
superconducting physics that motivates ABCA hunting is **not** here, and campaign
value lies in QH degeneracy-lifting or even-N interaction physics if the device is
clean enough, otherwise deprioritise.
