# Tetralayer stacking identification by Fermi-surface counting (ABAB / ABCA / ABCB)

*Investigation — a decision procedure one level up from the measurement recipes
it orchestrates (`measurements/gatemap.md`, `measurements/sdh-spot-check.md`,
`measurements/landau-fan.md`), spanning multiple measurements rather than a single
sweep. Use the rig-appropriate variants; rig and device mechanics — magnet
discipline, gate wiring, validators — live in the device card and session brief,
not here. Trilayer devices use the sibling `trilayer-stacking-fs-count.md`; the
device card's material line routes.*

**Reference**: `hera/docs/tetralayer-stacking-extraction-survey.md` — the survey
that grounds this recipe, synthesising Min–MacDonald 2008
(`hera/docs/papers/0711.4333/paper.md`), Koshino–McCann 2011
(`hera/docs/papers/1104.0794/paper.md`), Grushina et al. 2015
(`hera/docs/papers/1501.06764/paper.md`), and Kalantre et al. 2026
(`hera/docs/papers/2606.05356/paper.md`). Read it first; every band-structure
claim below is grounded there.

## What

Classify the stacking order of a tetralayer-graphene device — ABAB (Bernal),
ABCA (rhombohedral), or ABCB (mixed) — by **counting distinct Fermi surfaces**
from Shubnikov–de Haas frequency content at controlled D ≈ 0, read as a peak
set against the Luttinger frequency. Output is a **region-resolved,
evidence-cited, hedged call**, not a headline.

## When

- A **dual-gated** tetralayer device of unknown or unverified stacking is loaded
  and gated, where you can sit at D = 0 and sweep n independently. (No
  single-gated tetralayer procedure exists in the corpus — a single-gated 4L
  device is an uncovered case to flag, not to improvise.)
- Stacking determines everything downstream (ABCA hosts the flat-band /
  correlated / superconducting physics; ABAB is conventional; ABCB is a
  metastable gapped oddity), so this is typically among the *first science
  questions* of a tetralayer campaign.
- Also worth running when stacking was assigned optically / by Raman only —
  transport is the in-situ check, and exfoliated multilayer flakes commonly
  host **mixed stacking domains**, so different contact pairs can disagree.
  (Raman side: `raman-stacking-id.md`; reconciling: `stacking-raman-transport-fusion.md`.)

Prerequisites: gates calibrated with validators committed (device-init
recipes), and at least one four-terminal Rxx channel with credible contacts and
quantum mobility high enough to reach SdH onset in the planned field window
(Step 3 decides this). Step 1 handles CNP identification and the (n, D)
conversion — a CNP that cannot be positively identified is itself an outcome to
surface, not a precondition.

## Why

The three stackings differ in Fermi-surface count *and* in where their tones
sit (`hera/docs/tetralayer-stacking-extraction-survey.md` §1–2):

- **ABAB**: two bilayer-like parabolic bands (effective interlayer couplings
  1.618γ₁ / 0.618γ₁) coexist → **2 Fermi surfaces**, densities partitioning
  ∝ mass.
- **ABCA**: a single chiral J = 4 quartic band with trigonal-warping Lifshitz
  structure confined to low density → **1 Fermi surface** at the ~10¹²
  operating density.
- **ABCB**: a cubic band plus a Dirac-like band over an intrinsic ~9 meV CNP
  gap → **2 Fermi surfaces** with a light, velocity-renormalized Dirac partner
  (citation-grade — no validated model backs quantitative ABCB reads).

**The read is the peak set against the Luttinger frequency.** F_L = (h/4e)·n
(g = 4, spin × valley, unbroken at the operating point — Verify: degeneracy
audit) is the predicted line, inheriting the lever-arm **scale** uncertainty
(geometry prior ~10–15% — `device-init/cnp-and-dline-calibration.md`), so F_L
is a **band, not a ceiling**. The templates:

- **ABCA**: one tone **at** F_L (the single pocket carries the full density).
- **ABAB**: a **pair** partitioning F_L at ≈ **0.72 / 0.28** (the φ² mass
  ratio; decomposition-limit values — the model's F(n) table is the design
  authority). Two exception regimes [our-model]: at low *electron* density
  the light pocket nearly empties and the heavy tone rides at ≈ 0.95·F_L —
  where ABAB genuinely mimics an ABCA singleton within the scale prior —
  and the near-CNP *hole* pair is close and balanced (beat-like on short
  1/B records). Both wash out by |n| ≳ 2–3×10¹².
- **ABCB**: a pair partitioning F_L with a *light Dirac* partner — a
  shape-discriminated variant of the two-tone case (citation-grade).
- **Mixed stacking domains**: templates superposed, each grouping checked
  against the **same** F_L (domains share the gated density). Peak
  *amplitudes* track the domains' geometric weighting.
- **A tone at F_L is not automatically ABCA**: an ABAB pair sums to F_L, so a
  **magnetic breakdown** orbit through both pockets or an intermodulation tone
  lands exactly at F_L and mimics the ABCA singleton — and unlike the trilayer
  case, ABAB inter-block breakdown is **symmetry-allowed** (no parity
  protection between the two bilayer-like blocks), so treat the sum-tone
  confound as *expected*, not exotic. A set {f₁, f₂, ≈F_L} underdetermines
  mixed domains; discriminate before claiming one (Verify: F_L-tone origin —
  mandatory for any singleton call where partner tones are resolved).

Against the trilayer read, this one is structurally **easier at design
densities |n| ≳ 2–3×10¹²**: the dominant tones themselves separate (ABAB's
biggest tone at ≈ 0.72–0.79·F_L vs ABCA's at F_L), and the ABAB partner tone
carries ~21–28% of F_L rather than a few percent. The discriminating
evidence is the dominant-tone *position* plus the partition — not a
small-tone hunt. The advantage evaporates in the low-|n| exception regimes
above — design around them (Step 2).

Four disciplines keep it honest (unchanged from the trilayer method; stated
here because this recipe runs standalone):

- **Pin the scale before you reject.** The lever arm is one global number the
  Luttinger relations pin — a singleton sits at F_L, a pair sums to F_L. Fit
  that single in-band scale to the *whole* peak set first; a peak is "above
  F_L" only after the scale is pinned. Multiple populations (mixed domains)
  over-determine the scale — leverage, not noise. Any later scale change is
  retroactive — re-read the whole set.
- **Classify on frequencies, never amplitudes.** Amplitudes fold in field,
  Dingle damping, and domain weighting; frequencies carry the pocket areas.
- **Screen harmonics first — and Luttinger-aware.** Drop any peak at an
  integer multiple of a stronger fundamental (confirm by n-dependence — a
  harmonic tracks k·f exactly; a real pocket follows its own Onsager curve),
  but never discard a tone as a harmonic when doing so breaks the partition
  sum: the ABAB pair's ratio ≈ 2.6 drifts through 3× with density, and a
  ratio-only screen eats the real heavy tone exactly there [our-model,
  synthetic replay]. The n-dependence screen plus the sum decide, not the
  ratio alone.
- **Read each Rxx channel separately, never averaged.** Each pair probes a
  region of a possibly-mosaic flake; the call is **per region**, and "most
  channels uninformative" is a normal outcome.

Two design facts:

- **D ≈ 0 is the operating point.** Finite D gaps ABCA, reshapes ABAB's
  overlap and hybridizes its blocks, and splits ABAB valleys. A quantitative
  small-residual-D robustness statement is pending the model — treat residual
  D as "keep it small," a heuristic, not a guarantee (survey §3).
- **No side prior.** Both signs get a spot check (Step 3); the fan follows the
  cleaner side.

## Recipe

**Step 0 — mine what's already on disk.** An existing D = 0 fan with adequate
low-field reach already answers most of this via per-column FFT (Step 4);
existing 0 T gate maps answer Step 1.

**Step 1 — B = 0 (n, D) gate map + the (n, D) conversion.** As in the trilayer
sibling, verbatim: calibration from `device-init/cnp-and-dline-calibration.md`
(ratio data-calibrated, scale geometry-prior); identify clean hole- and
electron-side regions and the D = 0 line; flag arms going insulating; pick
voltage pairs metallic across the planned n-range. One tetralayer addendum: an
insulating CNP at D ≈ 0 is **not** a stacking read — it has three candidate
parents (ABCB intrinsic gap; ABCA under residual D; interaction-gapped ABAB in
ultraclean devices) — record it and move on (survey §5).

**Step 2 — feasibility (binding: compute, don't eyeball).** The reference
frequency is **F_L = (h/4e)·n**. From it and the template partitions, compute
the three design numbers before any sweep:

- **Δ(1/B) resolution** — Nyquist on F_L (the fastest expected tone):
  Δ(1/B) ≤ 1/(2·F_L).
- **Tone separation** — the binding resolution case is separating the ABAB
  heavy tone from an ABCA singleton (F_L), and resolving the ABAB partner
  with ≥ ~5 periods: (1/B_lo − 1/B_hi) ≥ 5/f_partner. Take both tones'
  frequencies from the **model's F(n) table**
  (`hera/models/tetralayer_fs_count/`), not the bare 0.72/0.28 ratios — and
  pick design densities |n| ≳ 2–3×10¹² where the templates separate: at
  +1×10¹² the ABAB heavy tone sits within ~5% of F_L and the partner at
  ~0.6 T is unresolvable in any practical window [our-model].
- **The field window** — onset is measured in Step 3, not computed; keep the
  ~100 mT-scale heuristic as an expectation only.

**Step 3 — SdH spot checks (`sdh-spot-check.md`).** Two spot checks — large
hole and large electron density (push |n| high within gate limits and any
contact-stress ceiling) — each fixed-(n, D = 0), uniform in 1/B, Δ(1/B) from
Step 2. From each FFT: which tones are present, and which side is cleaner. A
clean spot check can be **decisive on its own**; lock its sampling, settling,
and sensitivity and hand them, with the measured onset, to Step 4.

**Step 4 — full Landau fan + per-column FFT (`landau-fan.md`).** Fan on the
cleaner side over a decently large density window at D = 0. Field range from
Step 3 (onset → B_lo; period-count extrapolation to the low-density edge sets
B_hi — the ABAB partner tone at the lowest fan density is the binding case).
Inherit the spot check's Δ(1/B) and settling. FFT each n-column; read peak set
vs F_L, the Luttinger partition, and each tone's n-dependence in one object.

**Step 5 — F(n) across density (the refinement).** (1) **Partition
robustness** — f₁(n) + f₂(n) = F_L(n) across density is algebraic (no model);
a coincidental one-density match will not hold. (2) **Branch labeling** —
overlay measured F(n) on the model curves (Verify: forward-model comparison):
ABAB branches are *both parabolic* and are labeled by the frequency ratio and
per-branch mass (Verify: LK), **not** by shape; a light *Dirac-shaped* branch
(supra-linear F(n) at low n against the model) points at ABCB's J = 1 partner
[citation-grade — report as candidate, hedge accordingly]. The binary
ABAB-pair vs ABCA-singleton call needs only (1) plus the F_L-tone origin
discrimination.

**Step 6 — high field (weak complement only).** There is **no tetralayer
Streda/Chern offset discriminator**: every 4L stacking carries 16 zero-energy
LLs — a ν = ±8, 12, 16 low-field ladder confirms the *layer number*, not the
stacking (survey §4; the layer-number check is itself useful — Verify:
adjacent-N). Stacking-dependent LL *fine structure* (two interleaved bilayer
ladders with mod-3 anticrossings vs a single bunched ladder) is qualitative —
no validated 4L LL model — so weight anything from it ≤ weak.

**Step 7 — the call.** Output contract (all five parts mandatory):

1. Per-region verdict on the STYLE strength scale: `channel/pair X: ABAB
   (strong) | ABCA (weak) | ABCB-candidate (consistent-with) | mixed-domain
   (consistent-with) | uninformative` — every verdict carries its weight word;
   bare leans are not verdicts.
2. Evidence list: each tone claimed, with frequency, (n, D) coordinates and
   density side, the Onsager-overlay artifact, and the Luttinger check.
3. Confidence + specific hedges (resolution limits, side/density, features
   searched-and-absent vs not-resolvable, domain/mosaic caveat, **absolute
   layer number** — if the peak set matches neither 4L template, the
   adjacent-N hypothesis belongs here before exotic explanations).
4. What would firm the call (other side, LK mass split, degeneracy audit,
   independent N-ID, a different rig/temperature).
5. **A "cannot tell" with reasons is a successful outcome. A confident call
   without feature-level evidence is a protocol violation.**

## Verify

- **TSV-first is mandatory for any classification-grade read.** Re-form
  Rxx(n, B) at native grid resolution (channel arithmetic per the device card)
  before any frequency claim; rendered monitor PNGs alias the SdH structure.
- **Onsager forward-model overlay.** Tool: `hera/models/tetralayer_fs_count/`
  (B = 0 FS count + Onsager F(n) + m*(n); ABAB SWMcC + ABCA 8-band continuum —
  semi-quantitative; validity stance in the model README). Overlay measured
  per-column F(n) allowing a **single global density rescale** (~0.8–1.2
  plausible [heuristic — lever-arm prior]; far outside that band is a red
  flag, not a fit) — fit that one scale to the **whole** peak set before
  reading any tone against a template; a lone tone forced onto a template by
  a private rescale while a resolved partner closes the Luttinger sum at
  scale 1 is a mis-read, not a fit. **A pair summing to F_L is necessary,
  not sufficient, for ABAB.** For any two-tone pair, compute **both**
  overlays — the ABAB curves *and* the trilayer ML+BL curves
  (`hera/models/trilayer_fs_count/`) — and report which family the branches
  track across density; **do not absorb a partition mismatch as model error**
  (the partition is a trusted model output — README validity stance): a pair
  tracking the trilayer curves is an adjacent-N read (Adjacent-N check
  below), not off-model ABAB [our-measurement, harness replay 2026-07-20 —
  agents mapped a trilayer 0.15/0.85 pair into 4L templates]. Partition
  magnitude alone cannot decide — the ABAB partner fraction sweeps
  ~0.06–0.44 with density and crosses the trilayer ~0.11–0.15 near
  |n| ≈ 2×10¹² [our-model]; the discriminator is the trajectory, not a
  ratio. Two branches on the ABAB curves *and* the F_L-tone origin passed is
  **strong** ABAB; a single branch on the ABCA curve with the origin
  discrimination passed is **strong** ABCA. Confound: mixed domains
  superpose templates on one F_L — resolve by the combinatorics, harmonic
  screen, and per-channel reads (Why).
- **F_L-tone origin (breakdown | ABCA domain | mixing) — mandatory before any
  singleton call where partner tones are resolved** (ABAB breakdown is
  symmetry-allowed, Why): (1) **B-window split** — FFT low-B and high-B halves
  separately; a breakdown/mixing tone strengthens with B relative to the
  fundamentals, a real pocket keeps its own Dingle envelope — but a *null*
  split in a narrow field window is weak: breakdown with onset scale above
  the window top is unresolvable there (absence claims cite resolvability)
  [our-model, synthetic replay]; (2) **grid-change
  reproduction** (`sdh-spot-check.md` Verify) retires sampling-alias origins;
  (3) the per-branch **LK mass** (below) is decisive. An unresolved remainder
  is a fork to report (STYLE rule 14).
- **LK mass split + beat exclusion** *(our-model expectation)*: the ABAB
  branches' masses differ by ≈ φ² ≈ 2.6× — per-branch LK masses
  (`temperature-dependence` Flavor B) cleanly separate two genuine bands from
  one band plus artifact; compare against the model's m*(n), never a
  light/heavy prior alone. Beat exclusion as in the trilayer sibling: a
  coexisting component **lighter** than the main branch cannot be a beat
  (decisive); at-or-above decides nothing alone.
- **Degeneracy audit.** F_L = (h/4e)·n assumes the symmetric 4-fold metal —
  expected at D ≈ 0, |n| ~ 10¹², kelvin-scale temperatures (survey §6), but
  verify in-data: after the scale is pinned on the full set, a peak set
  sitting at 2× or 4× its g = 4-predicted positions reads as flavor
  polarization (g = 2 / g = 1) and **suspends the g = 4 combinatorics** —
  escalate with the survey §6 reference rather than reading tones as
  supra-F_L pockets.
- **Adjacent-N check.** If the peak set matches neither 4L template **as a
  model overlay** — including a pair that sums to F_L but tracks the trilayer
  ML+BL curves rather than the ABAB curves (dual overlay above; a lopsided
  pair still passes the loose "pair partitioning F_L" template) — run the
  trilayer templates (ML+BL pair with a *small* partner; ABC singleton) and
  the pentalayer expectation (2+2+1) before anything exotic — optical-contrast
  N-assignment can misassign absolute layer number while resolving steps well
  (survey §7). Confound [our-model, synthetic replay]: a heavily damped
  singleton (large-m\* regions — e.g. the ABCA flat-band edge) plus a noise
  peak mimics the small-partner trilayer template on *single columns* — the
  adjacent-N call is a **cross-column consensus read**: the claimed partner
  must track its own Onsager curve across density and clear the local noise
  floor, never a one-column fit. A ν = 8, 12, 16 QH ladder (Step 6) or
  magneto-Raman G-band anticrossings (`hera/docs/papers/1501.06764/paper.md`)
  are independent N checks; state which N the transport actually supports in
  the hedges.
- **FFT stability sweep.** Vary detrender and window; a real peak sharpens as
  the 1/B record lengthens, an artifact wanders. Detrend on even-in-B data
  **before** interpolating to 1/B (detrending after manufactures
  low-frequency artifacts — paper-data, `hera/docs/papers/2606.05356/paper.md`
  resolution ladder). A frequency whose value or n-slope flips across
  reasonable extraction choices is a **fork to report, not refine** (STYLE
  rule 14).
- **Acquisition quality is empirical — compare at a shared density.** As in
  the trilayer sibling, verbatim: quality is a property of how a column was
  acquired; a lower-quality measurement never overturns a higher-quality one;
  the stopping rule (finer B resolves no new tones ⇒ count complete at this
  T/mobility) holds only on adequately acquired data. Resolution-ladder
  anchor: SdH from ≈ 0.1 T needs μ ≳ 10⁵ cm²/Vs (paper-data, Grushina — a
  suspended-device benchmark; expect a higher onset at lower quantum
  mobility, and read onset empirically in Step 3).
- **Luttinger sum.** Σf = n (g = 4) across the fan is the model-independent
  consistency check and the constraint that pins the global scale. A peak set
  that **cannot** satisfy the sum after the harmonic screen and stability
  sweep is a reportable state, not an extraction failure — R4G hosts
  documented non-Onsager regimes, though concentrated at large |D| / low n
  (survey §6); at the D ≈ 0 operating point treat it first as a degeneracy or
  N-assignment problem (audits above).
- **CNP magnitude is not a stacking read.** Insulating-CNP behavior has three
  candidate parents at N = 4 (survey §5) on top of the domain-shunting
  confound — feed it into the per-channel picture as consistent-with at
  most, never a standalone call.
- **Lever-arm / Nyquist at design time.** As in the trilayer sibling: ray
  slopes / frequencies must quantize against the (n, D) calibration; the
  B-axis SdH period sets the fan's B-row spacing — a fan failing the
  `landau-fan.md` Nyquist check in the claim window is uninformative there,
  re-measure.

## Examples

*(No live tetralayer sessions yet — this section seeds from the first
campaign/replay burns. Channel facts stay in device cards and notebook
indexes, never here — STYLE rule 11.)*

## Next

- **ABAB-confirmed** (pair partitioning F_L, Onsager-tracking, φ²-split LK
  masses): conventional tetralayer — campaign value is QH degeneracy-lifting /
  even-N interaction physics (ultraclean devices only); otherwise deprioritise.
- **ABCA-leaning** (singleton at F_L with the origin discrimination passed):
  the interesting outcome — flat-band / correlated / superconducting candidate
  at high D and mK temperatures (`hera/docs/papers/2606.05356/paper.md` for
  the phase-diagram map). Verify with D-gap systematics (per-channel,
  domain-aware) and plan the low-T campaign the physics deserves.
- **ABCB-candidate** (light Dirac partner + intrinsic-gap constellation):
  rare and citation-grade — what would firm it: Raman G-peak position and
  near-field imaging on the region, plus a model upgrade before any strong
  transport claim.
- **Mixed-domain device**: map which pairs probe which stacking; decide
  whether any single-domain region supports the science goal before more
  magnet time.
- **Resolution-limited cannot-tell**: state the onset-field / mobility number
  and what side, density, or temperature would change it — a device-quality /
  rig choice, not more sweeps on this rig.
