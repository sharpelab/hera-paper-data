# Trilayer stacking identification (ABA vs ABC)

> **DEPRECATED** — superseded by `trilayer-stacking-fs-count.md` (the
> Fermi-surface-counting approach used in live sessions). Retained only for
> material still cross-referenced elsewhere (the single-gated path, the
> Examples, the STYLE burn-log). Do not extend; see `docs/eng-backlog.md`.

*Investigation recipe — a decision procedure spanning multiple measurements,
not a single sweep. It orchestrates `measurements/gatemap.md` and
`measurements/landau-fan.md` (use the rig-appropriate variants; rig and
device mechanics — magnet discipline, gate wiring, validators — live in the
device card and session brief, not here).*

**Reference**: `hera/docs/papers/ncomms14518/paper.md` — the ingested
technique paper (Datta et al. 2017). Read it before running this
investigation; every feature named below is defined there with figure
crops you can view. Cite its panels when you claim a feature.

## What

Classify the stacking order of a trilayer-graphene device — ABA (Bernal)
vs ABC (rhombohedral) — from magnetotransport: the displacement-field
response of the charge-neutrality point and the Landau-fan crossing
structure. Output is a **region-resolved, evidence-cited, hedged call**,
not a binary.

## When

- A trilayer device of unknown or unverified stacking is loaded and gated.
  Stacking determines everything downstream (ABC hosts the flat-band /
  correlated physics; ABA is conventional), so this is typically the
  *first science question* of a trilayer campaign.
- Also worth running when stacking was assigned by optical contrast/Raman
  only — transport is the in-situ check, and trilayer flakes commonly host
  **mixed ABA/ABC domains**, so different contact pairs can disagree.

Prerequisites: gates calibrated with validators committed (device-init
recipes), a CNP located, working (n, D) conversion, and at least one
four-terminal Rxx channel with credible contacts. Dual gates are required
for step 1 (single-gated devices skip to step 3 with reduced power —
see the paper's "single-gated ⇒ D ≈ 0 fingerprint" note).

## Why

The two stackings differ qualitatively, not quantitatively
(`paper.md#discriminators`):

- **ABA**: mirror symmetry → coexisting monolayer-like + bilayer-like LL
  ladders → **crossing chains** in the fan (curved arcs of Rxx maxima
  cutting across the straight ν-rays; the N_M = 0 chain is a vertical
  series at fixed n). Semimetallic CNP that D does **not** gap.
- **ABC**: single cubic ladder → clean fan, 12-fold zero-energy LL
  (ν = ±6-centered sequence), and a **CNP gap that grows strongly with
  |D| already at B = 0**.

One caveat governs the logic order — stated carefully, because both
halves matter: **crossing *presence* at finite D is not ABA evidence**
(ABC also develops LL crossings under D — paper.md, ABC-contrast
section, Lee et al.), but **crossing *pattern* still discriminates**: a
family of parallel chains co-locating with the predicted ML×BL loci
(Verify: forward-model comparison) remains ABA evidence at finite D,
weakening as |D| grows (the D = 0 model degrades, and ABC's own
crossing structure becomes richer). D ≈ 0 is where the inference is
clean; finite-D fans are pattern-testable, not uninformative. The
CNP-vs-D response discriminates at any B and needs no LL resolution at
all. Hence the ladder below runs cheapest-and-most-robust first.

## Recipe

**Step 0 — mine what's already on disk.** Before proposing any sweep:
existing 0 T gate maps answer step 1, existing fans answer steps 2–3.
An hour of analysis routinely replaces a day of magnet time.

**Step 1 — CNP resistance vs displacement field, B = 0.** From a TG–BG
gate map (`gatemap.md`) or a dedicated D-line family: extract Rxx at the
CNP as a function of D over the full safe |D| range.
- CNP Rxx grows **orders of magnitude** with |D| → D-gappable
  (rhombohedral) material is present **in the measured path**. Flat /
  weakly varying / *decreasing* → ABA-leaning (band overlap).
- **Confound — the mosaic/series-path caveat**: a four-terminal segment
  gaps if ABC domains span the channel *anywhere between the voltage
  probes*, even when the same path also hosts ABA domains. Growth is
  therefore **strong** evidence for "gappable (rhombohedral) content in
  this path" but only **consistent-with** "the device is ABC" — in a
  mixed flake, *every* pair can show growth. Magnitude
  helps but doesn't settle it: a clean tens-of-meV ABC gap should go
  MΩ-insulating at ~1 K; a modest ceiling (10⁴–10⁵ Ω) suggests small
  gaps, in-gap conduction, or ABA regions shunting in parallel — i.e.
  mosaic. The whole-device vs per-region question is settled by the
  fan structure (steps 2–3), not by this step alone.
- This is the cheapest discriminator, robust to disorder (no LL
  resolution needed), and works at base T of any rig.
- Control: verify the extraction follows the CNP as it shifts in gate
  space (track the Rxx maximum per D-line, don't read a fixed gate point).

**Step 2 — channel triage.** On any 2D map or fan, re-form **every Rxx
channel separately from the TSV — never average channels**. Rank
clean → mixed: a stacking-mosaic region shows superposed/smeared fan
structure and features that don't extrapolate to sensible filling
factors; a single-domain region shows one coherent fan. Run the
classification per channel and expect disagreement — *the call is per
region, and "4 of 5 regions uninformative" is a normal outcome.*

**Step 3 — Landau fan at D ≈ 0 on the cleanest channel** (`landau-fan.md`;
electron side first, B to the rig/device cap). The hunt, in order of
evidentiary weight (`paper.md#discriminators`, Figs. 2a/2b, 3d/3e):
1. **N_M = 0 vertical crossing series** — Rxx maxima at ~fixed n,
   climbing in B. **Decisive at D ≈ 0**; at finite D its weight drops
   like the chains' (ABC's zero-energy triplet is also non-dispersing,
   and under D its split levels can cross too — pattern-check against
   the model rather than crediting presence). Confounds: a fixed-n
   feature climbing in B can also be a contact resonance or the
   CNP-column shoulder — check it sits at the model-predicted n and is
   absent in the other Rxx pair only if the regions genuinely differ.
   **Dispersion floor** *(burn: anomaly E3, 2026-06 live session)*: no
   verticality or dispersion claim from fewer than ~8 B-rows spanning
   ≥ 1.5 T — below that, log the feature as an anomaly to re-measure,
   never as a candidate that shapes the session arc.
2. **Curved crossing chains** — ≥ 2 roughly parallel smooth arcs cutting
   across the ν-rays. **Search both signs**: the chains manifest as
   bright beads ON successive rays (level coincidences — the paper's
   literal "crossings = Rxx maxima") *and* as **dark curved channels**
   where the ray bundles fade or terminate (gap coincidences /
   anti-alignment of the two ladders). The dark phase is often the more
   eye-visible one in a log-scale render. Beads-on-rays or dark arcs
   with a smooth curved envelope IS the feature — do not dismiss either
   as grid artifact without the Verify checks below.
3. **ν bookkeeping** — strong-minima sequence: all-integer or
   Δν = 4-dominated structure vs a ν = ±6-centered 12-fold pattern.
4. **Model overlay** — read every candidate arc against the predicted
   ML×BL crossing loci (Verify: forward-model comparison) before
   claiming it; co-location with prediction is what upgrades "curved
   feature" to "crossing chain".
5. **SdH-FFT two-pocket test** — when B-resolution permits (≳ 80 rows
   spanning a 2–3× B range): per n-column, FFT log|Rxx| in 1/B
   (`hera.analysis.sdh_fft` — sorted interp, detrend, window). Two
   coexisting frequency scales with intermodulation satisfying
   **f₁ + f₂ = f_tot** is the ABA two-pocket signature — at moderate
   mobility the *pockets*, not the crossing chains, are the most
   sensitive single-particle discriminator, and can surface structure
   no (n, B)-plane arc-hunting will. Caveat: f_low's **n-dependence is
   extraction-window-sensitive** — fit branches with continuity
   tracking, and don't over-claim slopes (STYLE rule 14: a claim that
   flips under extraction parameters is a fork to report, not refine).

**Step 4 — iterate by outcome.**
- **CNP-vs-D ambiguous** (growth ×3–10, or growth that saturates low,
  or pairs disagreeing in trend) → do NOT round to a lean. Extend the
  |D| range, check per-pair consistency, and carry *both* readings
  forward explicitly — the fan evidence (steps 2–3) then carries the
  call.
- Chains visible but ragged → densify B (and/or n) in the window where
  the chains live; re-run the model overlay on the partial fan as rows
  land. *Stopping rule: if the finer grid resolves **no new minima**,
  the strong-gap set is complete at this T/mobility — more density buys
  nothing. The lever-arm fork needs plateaus (lower T) or a
  known-density anchor, not grid.*
- Nothing at D ≈ 0 with rays well resolved → fan at modest |D| watching
  the CNP gap evolve (ABC: ν = 0 insulator strengthens fast with D);
  at finite D, crossing *presence* alone is not ABA evidence — but a
  chain pattern matching the model loci still is, with weight
  decreasing as |D| grows (Why section).
- Nothing resolvable at all → classification is resolution-limited:
  consult the **resolution ladder** (`paper.md#resolution-ladder`) and
  state *which* missing feature was resolvable and which wasn't. The
  reference resolved every classification feature at **1.5 K with
  500k cm²/Vs mobility** — onset field of the rays calibrates where your
  device sits, and "needs colder" is only true for the interaction
  extras, not the fingerprint.

**Step 5 — the call.** Output contract (all five parts mandatory):
1. Per-region verdict using the STYLE strength scale (decisive /
   strong / weak / consistent-with / uninformative):
   `channel/pair X: ABA (strong) | ABC (weak) | mixed-domain
   (consistent-with) | uninformative` — every verdict carries its
   weight word; bare leans are not verdicts (`recipes/STYLE.md`).
2. Evidence list: each feature claimed, with (n, B) coordinates, the
   paper panel it matches, and the model-overlay artifact backing it.
3. Confidence + the specific hedges (resolution limits, finite-D caveat,
   features searched-and-absent vs not-resolvable).
4. What would firm the call (next sweep, or different rig/temperature,
   or different contacts).
5. **A "cannot tell" with reasons is a successful outcome. A confident
   call without feature-level evidence is a protocol violation.**

## Verify

- **TSV-first is mandatory for any classification-grade read.** Rendered
  monitor PNGs alias the dense ray family and can both hide real chains
  and manufacture moiré that mimics them; re-form Rxx(n, B) from the
  data at native grid resolution (correct channel arithmetic per the
  device card) before any feature claim.
- **Forward-model comparison — the paper-faithful test and the primary
  arc-reading method.** Tool: `hera/docs/vti/aba-trilayer-qc0426/`
  (`ll_spectrum.py` = SWMcC LL Hamiltonian with the paper's fitted
  parameters; `crossing_model.py` = predicted ML×BL crossing loci in a
  given (n, B) window; `compare_qc0426.py` = worked overlay example;
  run with `uv run --no-project --with numpy --with scipy --with
  matplotlib --with pillow`). Method: predict the crossing-chain loci,
  overlay them on the TSV re-formed Rxx(n, B) — partial fans included
  (the prediction doesn't care how many B-rows have landed) — allowing
  a **single global density rescale** (lever-arm uncertainty; ~0.8–1.2
  is plausible, a rescale far outside that band is a red flag, not a
  fit). Measured curved arcs co-locating with predicted chains —
  matching fan-out topology, curvature sign, B-range, residuals small
  vs chain spacing — is strong ABA evidence *for that region*. Check
  the half-period question explicitly: dark arcs should sit at
  gap-coincidence loci, offset half a period from the bright
  level-coincidence chains. Purely data-driven ridge detection without
  the model is NOT trusted for this — a prior attempt confidently
  re-traced the straight ν-rays as "chains"; the model template is
  what makes the search well-posed.
- **Aliasing robustness — both axes**: the measurement grid can beat
  against the LL structure on the n-axis (ray spacing, near-Nyquist
  below ~2 T at typical 100–200-pt n-lines) *and* on the B-axis (SdH
  period ΔB ≈ (g·e/h)·B²/n — coarse B-rows alias the fan into blocky
  texture; see `landau-fan.md` grid-design check, which belongs at
  design time, not here). A claimed chain must survive n-grid
  decimation (2×) and B-row subsetting — real features persist,
  sampling beats move. A fan that fails the design-time Nyquist check
  in the claim window is uninformative for chains there; don't rescue
  it post-hoc, re-measure.
- **Superposed-fan (mosaic) alternative**: before reading real chains as
  ML×BL crossings, test the competing explanation — a **second
  straight-ray family** from a second device region in the voltage path
  (offset CNP and/or different lever arm). Two superposed fans produce
  curved beat fringes that mimic crossing arcs. Discriminators: ML×BL
  chains drift to **lower** ν as B grows (and their geometry follows the
  SWMcC parameters, `paper.md`); density-offset beat tracks drift **up**
  in ν (q(B) ≈ ν′ + n₀/B), require the second family to be findable in
  the residual after removing the main fan, and persist with similar
  geometry across D, whereas crossing chains reorganize with D.
- **Lever-arm cross-check**: ray slopes must quantize (dn/dB per ray =
  ν·e/h). If the Δν spacing comes out non-integer, the capacitances are
  wrong and every ν claim inherits the error — recalibrate before
  classifying.
- **Two-frequency follow-ups — LK mass split + beat-damping exclusion**
  *(our-measurement, QC0426 2026-06 live session)*: when the SdH FFT
  (step 3.5) shows two coexisting frequencies, the deciding verify is a
  per-branch **LK mass extraction** (`temperature-dependence` Flavor B:
  amplitude-vs-T per frequency branch) — two regions of the same
  material give one mass; ML (light, Dirac) vs BL (heavy) differ by
  design. Independent cross-check — **beat exclusion**: beat/intermod
  components damp with the **sum** of the parent masses (their LK
  factors multiply), i.e. faster than either parent — so a coexisting
  low-f component whose measured mass is **lighter than the main
  branch cannot be a beat** (decisive exclusion, no fit to the
  fundamentals needed); a mass at or above the parents' is
  consistent-with beat and decides nothing alone — fall back to the
  other legs.
  Third leg where reachable: **D-pinning** — a region beat keeps fixed
  geometry under displacement field; band pockets hybridize and
  reorganize. Three independent discriminators beat re-arguing one
  ambiguous extraction (STYLE rule 14).
- **Hall plateau check — flatness, never value-match.** The Rxy *value*
  at an Rxx minimum trivially equals h/(ν_app·e²) when the Hall is
  classical — that's the B/ne identity with ν_app computed from the
  same n, and it looks exactly like plateau confirmation while being
  none. A plateau claim requires **dRxy/dn ≈ 0 across the minimum**
  (and ideally flatness along the ray in B). A value that matches with
  visible slope is the classical line crossing the right number,
  nothing more. (Burned: run-3 analysis, 2026-06-10 — caught before the
  call.)
- **CNP sanity**: compare CNP Rxx scale against the paper's semimetallic
  ~250 Ω benchmark (geometry-corrected). Orders-of-magnitude tension is
  itself evidence — feed it into step 1 rather than ignoring it.

## Examples

*(QC0426 campaign, VTI, 2026-06 — mechanical facts only.)*

- Campaign shape: 0 T TG–BG gate map → D = 0 fan → Si-screening variants
  → D-series fans. Notebook index:
  `hera/docs/notebook-indexes/notebook-index-QC0426-3LGr.md`.
- Fan runs and their D values (derived from the gate-line math):
  27 (D = 0, 0→8 T), 31 (D = 0, 13→0 T; Si-screening variant of 27),
  80 (+0.25), 81 (+1), 82 (−1), 83 (−0.25), 84 (−0.5) — 8 T fans.
  Si-screening settings are calibration data — read them from each
  run's `measurement_config` / the notebook index, never from a recipe
  (STYLE rule 11).
- **Metadata trap**: runs 81–83 metadata comments all say "D=0.25" —
  stale copy-paste. Derive D from the designed gate line, never from
  comments.
- **Channel facts**: current channel `sr0` with mandatory gain division
  (gain −1e6); two Rxx pairs (`sr1`, `sr2`) + `sr3` as Rxy in the
  D-series wiring; run 83's `sr1_X` carries glitch rows. Three
  four-terminal pairs ⇒ three regions for step 2 triage.
- Paper exemplar panels: fingerprint = `paper.md` fig2; vertical series
  = fig3 d/e; ABA CNP benchmark = fig1 d.
- **Worked rejection — anomaly E3 (run 4):** non-dispersing Rxx
  *minimum* at n ≈ 1.02e12, 7.25–8 T, initially read as a possible
  N_M = 0 dark channel. Killed on four counts: wrong sign (the N_M = 0
  series is Rxx **maxima**); single feature, not a series climbing in
  B; 0.75 T extent only; model co-location only at rescale 0.75–0.87
  (bottom edge of the plausible band — a red flag, not a fit). Logged
  as an anomaly in the call, not evidence. The kill used only standing
  Verify checks — this example exists because the adjudication was
  close.

## Next

- **ABA-confirmed**: conventional trilayer; campaign value is QHF /
  interaction physics (paper Figs. 3f, 5) — needs quality and lower T;
  otherwise deprioritize.
- **ABC-leaning**: the interesting outcome — flat-band/correlated
  candidate. Verify with the D-gap systematics (gap vs |D| at B = 0),
  then plan the low-T campaign (mK rig) the physics deserves.
- **Mixed-domain device**: map which contact pairs probe which stacking;
  consider whether any single-domain region supports the science goal
  before investing magnet time.
- **Resolution-limited cannot-tell**: state the onset-field number and
  what mobility/temperature would change; the decision is then a
  device-quality / rig-choice question, not more sweeps on this rig.
