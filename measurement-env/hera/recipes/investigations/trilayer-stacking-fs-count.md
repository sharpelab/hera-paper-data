# Trilayer stacking identification by Fermi-surface counting (ABA vs ABC)

*Investigation — a decision procedure one level up from the measurement recipes
it orchestrates (`measurements/gatemap.md`, `measurements/sdh-spot-check.md`,
`measurements/landau-fan.md`), spanning multiple measurements rather than a single
sweep. Use the rig-appropriate variants; rig and device mechanics — magnet
discipline, gate wiring, validators — live in the device card and session brief,
not here.*

**Reference**: `hera/docs/stacking-extraction-survey.md` — the survey that grounds
this recipe, synthesising Datta et al. 2017 (`hera/docs/papers/ncomms14518/paper.md`),
MacDonald et al. 2010 (`hera/docs/papers/1004.1481/paper.md`), and Koshino–McCann
2009 (`hera/docs/papers/0809.0983/paper.md`). Read it first; every band-structure
claim below is grounded there with figure crops you can view.

## What

Classify the stacking order of a trilayer-graphene device — ABA (Bernal) vs ABC
(rhombohedral) — by **counting distinct Fermi surfaces** from Shubnikov–de Haas
frequency content at controlled D ≈ 0, cross-checked by the high-field Landau-level
offset. Output is a **region-resolved, evidence-cited, hedged call**, not a binary.

## When

- A **dual-gated** trilayer device of unknown or unverified stacking is loaded and
  gated, where you can sit at D = 0 and sweep n independently. A single-gated
  device (D ∝ n) uses `trilayer-stacking-id.md` instead.
- Stacking determines everything downstream (ABC hosts the flat-band / correlated
  physics; ABA is conventional), so this is typically among the *first science
  questions* of a trilayer campaign.
- Also worth running when stacking was assigned by optical contrast / Raman only —
  transport is the in-situ check, and trilayer flakes commonly host **mixed
  ABA/ABC domains**, so different contact pairs can disagree. (Reading the Raman
  data itself: `raman-stacking-id.md`; reconciling the two calls:
  `stacking-raman-transport-fusion.md`.)

Prerequisites: gates calibrated with validators committed (device-init recipes),
and at least one four-terminal Rxx channel with credible contacts and quantum
mobility high enough to reach SdH onset in the planned field window (Step 3 decides
this). Step 1 handles CNP identification and the (n, D) conversion — a CNP that
cannot be positively identified is itself an outcome to surface, not a precondition.

## Why

The two stackings differ qualitatively in their Fermi-surface count
(`hera/docs/stacking-extraction-survey.md` §2–3):

- **ABA**: mirror symmetry → a monolayer-like (ML) Dirac band and a bilayer-like
  (BL) quadratic band coexist → **2 distinct Fermi surfaces** (the ML + BL pair) at
  finite n; each is a single pocket at the ~10¹² operating density.
- **ABC**: a single chiral J = 3 band with a **D-dependent Lifshitz transition at
  low density** (trigonal warping; ~10¹¹ cm⁻², MacDonald), below which the Fermi
  surface reconstructs. Above it — at the ~10¹² operating density — **1 Fermi
  surface**.

**The read is the peak set against the Luttinger frequency, not a headline count.**
F_L = (h/g·e)·n is the density's predicted line — predicted, not fit per peak (g = 4,
spin × valley, while degeneracies are unbroken at low field / warmish T). But its
position inherits the lever-arm **scale** uncertainty (geometry prior, ~10–15% when
the AFM thickness is accurate — `device-init/cnp-and-dline-calibration.md`), so F_L is
a **band, not a ceiling**: a tone above *nominal* F_L means the scale prior is low,
not that the tone is spurious. Each stacking predicts a distinct *set* of resolved
peaks relative to F_L:

- **ABC**: one tone **at** F_L (the single pocket carries the full density).
- **ABA**: a **pair** partitioning F_L, f_ML + f_BL = F_L. The ML fraction is
  band-structure-dependent and often **small**, so f_BL can sit anywhere from well
  below F_L to nearly at it, and f_ML can be weak.
- **Mixed stacking domains**: the ABC singleton and the ABA pair superposed, each
  grouping checked against the **same** F_L (the domains share the gated density —
  these devices are clean enough that domains do not sit at different densities).
  Peak *amplitudes* track the domains' geometric weighting.
- **A tone at F_L is not automatically ABC**: because the ABA pair sums to F_L, any
  sum tone of the pair — **magnetic breakdown** (a high-B orbit through both pockets,
  F = f_ML + f_BL) or **intermodulation/mixing** — lands exactly at F_L and mimics
  the ABC singleton. A set {f_ML, f_BL, ≈F_L} underdetermines mixed domains;
  discriminate before claiming one (Verify: F_L-tone origin).

So classification is **combinatorial**: enumerate the valid peaks, then match each
subset to a template against F_L. Four disciplines keep it honest:

- **Pin the scale before you reject.** The lever arm is one global number that the
  Luttinger relations pin — an ABC singleton sits at F_L, an ABA pair sums to F_L.
  Fit that single in-band scale to the *whole* peak set *first*, then read tones
  against the refined F_L; a peak is "above F_L" only once the scale is pinned, never
  against the un-pinned prior. More than one population (e.g. mixed domains)
  **over-determines** the scale — leverage, not noise: one scale must satisfy every
  population at once, so pinning off a subset and dropping the rest is wrong. Any
  later scale change is retroactive — re-read the whole set.
- **Classify on frequencies, never amplitudes.** A peak's amplitude folds in field,
  Dingle damping, and domain weighting; it is qualitative at best and never settles
  a count. Frequencies carry the pocket areas — they do the matching.
- **Screen harmonics first.** A real pocket at f throws harmonics at 2f, 3f, … that
  are not pockets; drop any peak at an integer multiple of a stronger fundamental
  (confirm by n-dependence — a harmonic tracks k·f exactly, a real pocket follows
  its own Onsager curve).
- **Read each Rxx channel separately, never averaged.** Each pair probes a region of
  a possibly-mosaic flake: a coherent peak set is a single-domain region, while
  channels that disagree (superposed / incoherent content) flag a stacking mosaic.
  The call is **per region**, and "most channels uninformative" is a normal outcome.

ABA's dominant BL tone nearly coincides with ABC's single tone, so the
discriminating evidence is always the **small ML partner and the partition**, never
the big tone alone.

Two further design facts:

- **D ≈ 0 is the optimal operating point, and the count is robust to small residual
  D** (ML/BL mixing scales as D²; Koshino–McCann) — but D *merges* the surfaces at
  large |D|, so do not run this at finite D.
- **No side prior.** Which side resolves cleaner SdH is device- and density-dependent
  (single-particle expectations: `hera/docs/stacking-extraction-survey.md` §2) — both
  signs get a spot check (Step 3), and the fan follows the spot-check read.

## Recipe

**Step 0 — mine what's already on disk.** Before proposing any sweep: an existing
D = 0 fan with adequate low-field reach already answers most of this via per-column
FFT (Step 4); existing 0 T gate maps answer Step 1.

**Step 1 — B = 0 (n, D) gate map + the (n, D) conversion.** The capacitance ratio
and (n, D) conversion come from `device-init/cnp-and-dline-calibration.md`: fit the
CNP line in the 0 T TG–BG map for the ratio (c_bg/c_tg = −slope), with the absolute
scale from the dielectric geometry until a quantum-Hall lever-arm check upgrades it
(two-tier provenance — ratio data-calibrated, scale geometry-prior). Consume it if
it is current on the device card; if it is absent or the screening operating point
has moved, run/refresh it first. From the calibrated map, identify clean hole- and
electron-side regions and the D = 0 line, and flag contact arms going insulating
(a back gate can deplete/gap a singly-gated arm) — pick voltage pairs that stay
metallic across the planned n-range. This hands Steps 2–4 their starting point:
the (n, D) calibration, the D = 0 line, and the clean side(s) to operate on.

**Step 2 — feasibility (a back-of-envelope, not a calculation).** The reference
frequency is **F_L = (h/4e)·n** — what a single four-fold pocket carrying all the
gated density would give (g = 4). It is a one-line algebraic conversion, and it is
both the line every tone is read against (Why) and an upper bound on the fastest
tone the sampling must resolve. Two design numbers fall out of it:

- the **1/B resolution Δ(1/B)** — Nyquist on F_L: Δ(1/B) ≤ 1/(2·F_L). Predicted here,
  **confirmed by the spot check** (Step 3), and it **carries over to the fan**.
- the **field window** — the 1/B span (1/B_lo − 1/B_hi) = N/F (N periods of a tone at
  frequency F), so a modest low-field reach already buys several periods.

The **onset field** is not worth computing — keep a rough heuristic (~100 mT scale,
rising with base temperature) as an expectation, but **measure it explicitly in
Step 3**. Everything here is provisional; Step 3 pins it empirically.

**Step 3 — SdH spot checks (`sdh-spot-check.md`).** Take two spot checks — one at
**large hole, one at large electron density** (push |n| as high as the device safely
allows — periods scale with n, so more is cleaner — within the gate limits and any
contact-stress ceiling the device card flags) — each a fixed-(n, D = 0) sweep
**uniform in 1/B** over [B_lo, B_hi] (`field_invB`; see `sdh-spot-check.md`), B_lo a low
floor below the expected onset that still **cleanly resolves the SdH**.
Set the **Δ(1/B) from the Step-2 back-of-envelope** (Nyquist on F_L); the low floor reads
the **onset** directly. From the FFT of each (the F_L
combinatorics, Why): which tones are present, and **which side — hole or electron —
gives the cleaner SdH** (take the fan there). A clean spot check can be **decisive on
its own**, not merely a gate; lock its sampling, settling, and sensitivity and hand
them, with the measured onset, to Step 4.

**Step 4 — full Landau fan + per-column FFT (`landau-fan.md`).** Pick the side — hole
or electron — that gave the **cleaner SdH in Step 3**, and take a fan (n vs B at
D = 0) over a **decently large density window** on that side (low |n| out to high |n|).
**The field range comes from Step 3**: start at the measured onset (B_lo), and set the
high end (B_hi) by **counting periods in the spot checks** and extrapolating (F ∝ n) to
the **low-density edge of the fan** — lowest F_L, longest period, fewest oscillations,
so it is the binding case for resolving the tones. Inherit the spot check's Δ(1/B) and
settling. FFT each n-column and read it by the F_L combinatorics (Why): per-column **peak set** vs F_L, the **Luttinger
partition** Σf = n, and the tones' **n-dependence** in one object. A fan is the *dense*
version of the Step-3 spot checks, not a higher-quality one — where a column shares a
density with a spot check, compare them (Verify).

**Step 5 — F(n) across density (the refinement).** The single-density combinatorics
already separates an ABC singleton from an ABA pair; tracking F(n) refines it two ways
one density cannot. **(1) Partition robustness** — check f₁(n) + f₂(n) = F_L(n) across
density: this is **algebraic** (against the F_L line, no model), and a coincidental
one-density match will not hold. **(2) ML-vs-BL labeling** — overlay on the predicted
Onsager curves (Verify: forward-model comparison) and assign by *shape* (Dirac vs
parabolic). The binary call (ABA pair vs ABC singleton) needs only (1); (2) is just
which-is-which. (Harmonics are caught by the integer-multiple screen, Why, not by
curve-tracking.)

**Step 6 — high-field Streda/Chern offset (complement / fallback).** Where the small
low-field tone is marginal, use the high-field face of the same ML+BL coexistence:
the ML Dirac band offsets the QH sequence (non-dispersing N = 0 zero-mode doublet at
the Dirac energy; Chern sequence shifted by the Dirac filling) vs ABC's ν = ±6-centred
12-fold zero LL. The gaps are bigger (several meV) → **resolvable at higher T / lower
mobility** than the small low-field pocket, at the cost of reaching the QH regime.
(Quantitative ABC LL overlay pending the ABC LL model — survey §9.)

**Step 7 — the call.** Output contract (all five parts mandatory):

1. Per-region verdict on the STYLE strength scale (decisive / strong / weak /
   consistent-with / uninformative): `channel/pair X: ABA (strong) | ABC (weak) |
   mixed-domain (consistent-with) | uninformative` — every verdict carries its
   weight word; bare leans are not verdicts.
2. Evidence list: each tone claimed, with its frequency, the (n, D) coordinates and
   density side, the Onsager-overlay artifact backing it, and the Luttinger check.
3. Confidence + the specific hedges (resolution limits, which side/density, features
   searched-and-absent vs not-resolvable, domain/mosaic caveat).
4. What would firm the call (next sweep, other side, LK mass split, the Streda
   complement, or a different rig/temperature).
5. **A "cannot tell" with reasons is a successful outcome. A confident call without
   feature-level evidence is a protocol violation.**

## Verify

- **TSV-first is mandatory for any classification-grade read.** Re-form Rxx(n, B)
  from the data at native grid resolution (correct channel arithmetic per the device
  card) before any frequency claim; rendered monitor PNGs alias the SdH structure.
- **Onsager forward-model overlay.** Tool: `hera/models/trilayer_fs_count/fs_count_b0.py`
  (B = 0 FS count + Onsager F(n, D); ABA SWMcC + ABC MacDonald — semi-quantitative;
  validity stance in the model README). Overlay measured per-column F(n) on the predicted curves allowing a **single
  global density rescale** (lever-arm uncertainty; ~0.8–1.2 is plausible, a rescale
  far outside that band is a red flag, not a fit). Branches co-locating with the
  predicted ML and BL curves and summing to the total is **strong** ABA evidence for
  that region; a single branch on the ABC curve is **strong** ABC. Confound: **mixed
  stacking domains** superpose an ABC singleton and an ABA pair, both referenced to
  the same F_L — resolve by the combinatorics (Why), the harmonic screen, and reading
  each Rxx channel separately (Why).
- **FFT stability sweep.** Vary detrender (Butterworth high-pass vs poly +
  Butterworth) and window; a real peak **sharpens** as the 1/B record lengthens, an
  artifact **wanders** (an aliased fast tone is a common cause). The detrender
  *choice* is not load-bearing; its *scale* is. A frequency whose value or n-slope
  flips across reasonable extraction choices is a **fork to report, not refine**
  (STYLE rule 14).
- **Acquisition quality is empirical — compare at a shared density.** Quality
  (resolution, settling, sampling) is a property of how a column was acquired, never
  of "spot check" vs "fan." Where a fan column and a spot check share a density,
  compare them directly: a visibly degraded column (under-settled, aliased) cannot
  overturn the cleaner measurement, and the comparison localizes the cause. A
  lower-quality measurement never overturns a higher-quality one, regardless of
  dimensionality — and the peak set is read by the full combinatorics (Why) even on
  imperfect data, never collapsed to the dominant tone. **Stopping rule**: when finer
  B resolves no new frequency content the count is complete at this T/mobility — but
  only on adequately acquired data; a tone absent from an under-settled or
  under-sampled measurement is **unresolved, not absent** (consult the resolution
  ladder, `hera/docs/papers/ncomms14518/paper.md#resolution-ladder`, for what is
  resolvable at this T/mobility), so fix the acquisition before reading a null as a
  count.
- **Luttinger sum.** Σf = n (with the right degeneracy) across the fan is the
  model-independent consistency check on the count — and the constraint that pins the
  global density scale (Why: pin the scale before you reject). Solve the single global
  scale against it before reading any tone as supra-F_L.
- **F_L-tone origin (breakdown | ABC domain | mixing).** For an ABA pair plus a tone
  at ≈F_L: (1) **B-window split** — FFT the low-B and high-B halves separately; a
  breakdown/mixing tone strengthens with B relative to the fundamentals, a real
  pocket keeps its own Dingle envelope (cheap, partial); (2) **grid-change
  reproduction** (`sdh-spot-check.md` Verify) retires the sampling-alias origin;
  (3) the per-branch **LK mass** (below) is decisive. An unresolved remainder is a
  fork to report (STYLE rule 14).
- **LK mass split + beat exclusion** *(our-measurement)*: when two frequencies coexist, the deciding cross-check is a per-branch
  **LK mass** (`temperature-dependence` Flavor B): two distinct masses confirm two
  genuine bands, one mass says one band. Label ML vs BL against model masses at
  E_F, never a light/heavy prior: the ML Dirac mass grows with |n| and can meet
  the BL mass at operating density. Independent exclusion — a **beat** damps with the **sum** of the
  parent masses, so a coexisting component **lighter** than the main branch cannot be
  a beat (decisive); a mass at or above the parents' is consistent-with a beat and
  decides nothing alone.
- **Lever-arm / Nyquist at design time.** Ray slopes / frequencies must quantize
  against the (n, D) calibration; the B-axis SdH period (ΔB ≈ (g·e/h)·B²/n) sets the
  fan's B-row spacing — a fan that fails the `landau-fan.md` Nyquist check in the
  claim window is uninformative there, re-measure.
- **Domain / mosaic caveat — magnitude is not a clean read.** Under D, a CNP
  resistance that **caps** below MΩ is *consistent-with* small-domain ABC shunted by
  ABA (the channel averages over domains; the ceiling tracks domain size vs channel
  length), **not** evidence against ABC. Feed CNP-vs-D into the per-channel read (Why),
  never as a standalone per-device call (`hera/docs/stacking-extraction-survey.md` §5).

## Examples

*(our-measurement — mechanical lessons only.)*

- A per-column SdH-FFT on a fan surfaced frequency structure that (n, B)-plane
  arc-hunting had missed; a slow tone whose n-dependence was
  extraction-window-sensitive was reported as a fork (Verify / STYLE rule 14),
  with the per-branch LK mass as the deciding follow-up.
- A clean single-density `sdh-spot-check` resolved tones a same-session fan —
  run under-settled and at a coarser B-step — did not: the worked case for "a
  noisier fan does not overturn a cleaner spot check" (Verify) and for locking
  acquisition on spot checks before the fan (Step 3).
- Channel facts (current channel + gain division, the Rxx/Rxy pair wiring, glitch
  rows) are device-card / notebook-index data — read them there, never from a recipe
  (STYLE rule 11).

## Next

- **ABA-confirmed** (the ML+BL pair, Luttinger-consistent, Onsager-tracking, distinct
  LK masses): conventional trilayer; campaign value is QHF / interaction physics — needs
  quality and lower T; otherwise deprioritise.
- **ABC-leaning** (single tone on the ABC Onsager curve, D-gap at CNP): the
  interesting outcome — flat-band / correlated candidate. Verify with the D-gap
  systematics (per-channel, domain-aware) and plan the low-T campaign (mK rig) the
  physics deserves.
- **Mixed-domain device**: map which pairs probe which stacking; decide whether any
  single-domain region supports the science goal before more magnet time.
- **Resolution-limited cannot-tell**: state the onset-field / mobility number and what
  side, density, or temperature would change it — a device-quality / rig choice, not
  more sweeps on this rig.
