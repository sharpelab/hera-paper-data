# Superconductivity identification and characterization (2D transport)

*Investigation recipe — a decision procedure spanning multiple measurements, not a
single sweep. Scope: gate-tuned 2D superconductivity in graphene and graphene–TMD
proximity systems. It orchestrates `measurements/gatemap.md` / `nD-map.md`,
`bias-spectroscopy.md`, `field-sweep-1d.md`, `fraunhofer.md`, `landau-fan.md` /
`sdh-spot-check.md`, and `temperature-dependence.md` (use the rig-appropriate variants;
rig and device mechanics — magnet discipline, gate wiring, validators — live in the rig
card, device card, and session brief, not here).*

**References** — read before running; cite their panels/benchmarks when you claim a feature:
- `hera/docs/papers/2106.07640/paper.md` — Zhou RTG SC: the prototypical 2D-transport SC
  characterization flow and its epistemics (the constellation standard, the
  failed-SC/anomalous-metal fork, the Tc-extraction ladder, the over-reads to avoid). **Read
  first.**
- `hera/docs/papers/s41586-022-05446-x/paper.md` — Zhang/Polski BLG/WSe₂: the graphene–TMD
  proximity-SC phenomenology and its reads (the flavour-polarised normal state via SdH-FFT,
  the ±D asymmetry, the doping-dependent Pauli-limit violation). The benchmark numbers there
  are **orientation, not targets**.

## What

Establish whether a gate-tuned low-Rxx region is a **superconductor**; separate it from a
**failed superconductor / anomalous metal** and from non-SC mimics; and characterise it
(critical current, critical fields, coherence length, normal-state fermiology, Tc). Output
is a **per-candidate, evidence-cited, hedged call** on the STYLE strength scale plus the
extracted properties — never a bare "SC here."

## When

- A 2D device is loaded and gated, (n, D) calibrated, with ≥ 1 credible four-terminal Rxx
  channel, and either candidate low-Rxx regions appear in the (n, D) map or
  proximity/gate-tuned SC is the campaign goal.

Prerequisites: device alive (`device-init/gate-current-sanity-check.md`, cheap-liveness
branch — the first-session / Gate-C check), gates calibrated with validators committed, a
CNP located, working (n, D) conversion (`device-init/cnp-and-dline-calibration.md`,
`gate-range-finding.md`).

## Why

- **SC is a constellation call** (`2106.07640/paper.md`): no single hallmark suffices.
  Corroborate {4-wire Rxx → 0 · nonlinear V(I) with a critical current · field response
  (B_c⊥, B_c∥) · T-dependence · phase-coherent oscillations · a sensible normal-state
  fermiology}. Each hallmark alone has a confound (Recipe steps); the call is the
  intersection.
- **The fork that sets the bar:** a low-but-finite Rxx region may be a genuine **failed SC /
  anomalous metal** (Kapitulnik–Kivelson–Spivak), not merely an unconfirmed SC. "Doesn't
  reach zero" is a physics fork, not just "weaker evidence" — carry it as its own verdict
  category. [citation]
- **The SC sits on a specific normal state** — the fermiology (fan/FFT) identifies the
  flavour-polarised / parent phase the pairing descends from, and is part of the
  characterisation, not an afterthought.
- **Graphene–TMD proximity systems carry two extra high-leverage reads** (conditional;
  phenomenology in `s41586-022-05446-x/paper.md`, to test against your data, not assume): the
  SC region's **±D asymmetry** (appears for the D sign that polarises carriers onto the TMD),
  and the **in-plane Pauli-limit violation** rising toward low doping (the Ising-SOC
  signature).

## Recipe

*Ordering principle: do everything achievable AT BASE T first; heat up for T-dependence
LAST — the thermal cycle is the expensive step.*

**Step 0 — mine what's already on disk.** Existing maps / IV curves / fans before proposing
any sweep; an hour of analysis routinely replaces a day of fridge time.

**Step 1 — pristine-field gate map, BEFORE energising the magnet.**
- Rxx(n, D) from a gate map (`gatemap.md` / `nD-map.md`); low-Rxx spots = candidates.
  Coarse → fine (maps are slow; reconnoitre coarse, zoom into candidates).
- **Second job — cap ratio.** If the device card flags the geometry prior as
  uncalibrated, the first survey map does double duty: take it **axis-aligned in raw
  (V_tg, V_bg)** (`gatemap.md`) and extract the CNP-ridge slope (`cnp-and-dline-calibration`).
  Candidate (n, D) coordinates, every zoom, and the ±D-asymmetry reads downstream are only
  trustworthy once the cap ratio is pinned.
- **Heuristic zoom, not blind search.** Use the priors to aim, locate with linecuts, then
  map tight.
  - **Priors:** (1) **carrier polarity toward the TMD** — the proximity SOC that stabilises
    the SC wants holes pushed into the TMD layer; the D sign that does this is set by the
    stack and convention (e.g. for BBG above WSe₂, **D < 0** in our convention).
    (2) **Expected region** for BBG/WSe₂-type proximity SC — an arc at **|D| ≳ 0.5 V/nm**,
    **n ≈ −4 to −6 ×10¹¹ cm⁻²** (n shifts with D), arc **width ~5×10¹⁰ cm⁻²**
    [paper-data: `s41586-022-05446-x`, enhanced SC in proximitized BLG].
  - **Locate with linecuts first.** The arc is narrow, so a blind polygon wastes points or
    steps over it. Take a few 1D **n-linecuts at fixed D**, scanning an n range **wider than
    the nominal expected band** so the dip isn't missed if the prior is slightly off (cuts in
    (n, D) — caps now pinned); pin where the low-Rxx arc actually sits and how it tracks with D.
  - **Then map it tight.** Place a rasterized **(n, D) polygon** (`nD-map.md`) following the
    located arc — not an axis-aligned gate map — with the **n-step fine enough to resolve the
    ~5×10¹⁰ arc width** (several points across it, not one or two).
  - Provided the trapped flux is small (the usual case), this stands on the priors + linecuts
    alone and **does not need the trapped-flux value** to locate the region.
- **Coverage gate — required before any "no candidate / not-SC" call.** Cover the
  accessible (n, D) region to the validators, **corners/edges included**. The
  committed (V_tg, V_bg) box maps to an (n, D) **parallelogram**; compute its corner
  coordinates (the |D| and |n| extrema) from the validators and use them as the
  coverage target — judge coverage against that envelope, not against where your cuts
  happened to reach. The extremal-|D| corners lie on a validator edge — reach them
  with an **edge sweep** (pin one gate at its cap, sweep the other); a constant-D /
  constant-n cut is an interior chord that tops out short of the corner (the failure
  mode: a wide-n constant-D line caps at modest |D|, never the gate corner). A
  corner/edge left unexplored **by choice** caps the verdict at
  `cannot-tell (coverage-limited)`, naming the gap; only instrument-limited gaps may
  be passed. `not-SC (strong)` requires full-envelope coverage.
- **Field-history protocol (load-bearing):** if the field source retains remanent /
  trapped flux on return toward zero (rig fact — magnitude in the rig card), the magnet's
  nominal zero is **not** true zero field, and a stray field of that scale can erase a
  fragile SC. **Take the first map before touching the field controller** — once you sweep
  it you inject remanence. *(Magnitude / loading-reset behaviour = rig fact → rig card;
  map-first ordering = protocol → here.)*

**Step 2 — nonlinear characterisation (base T).** dV/dI vs I_dc on each candidate
(`bias-spectroscopy.md`); a critical-current-like ridge is the target.
- **Drive discipline:** the AC sense excitation and the DC-bias step must stay well below the
  critical-current scale, or they smear the IV and can suppress the fragile state. 0.5 nA AC
  works for most vdW superconductors; rare fragile states need smaller. [heuristic]
- **Bracket $I_c$ wide first — it can far exceed reference values.** Proximity-SC $I_c$
  is ~20 nA in the reference [paper-data: `s41586-022-05446-x`, Fig 1d], but real devices
  can run several× higher. **Start the DC-bias sweep an order of magnitude above the
  reference $I_c$** (≈±200 nA here; $V_{dc}^{max}/R_{bias}$ may cap the reachable current);
  confirm $dV/dI$ rises to values comparable to nearby normal-metal resistances at both
  ends — the SC-to-normal transition shows a sharp **switching peak** at ±Ic, so the
  window must bracket past it to the normal state, not stop short. $I_c$ is largest at base $T$,
  effective-zero field, optimum $(n, D)$; size to that maximum.
- **Confound — dV/dI peak is not SC-specific:** non-equilibrium criticality
  (Zener–Schwinger; Berdyugin–Geim 2022) and quantum-Hall breakdown also produce
  SC-mimicking nonlinear I–V with sharp dV/dI peaks. **consistent-with, not evidence-for**
  on its own. [citation]

**Step 3 — field characterisation (base T).**
- **Find the SC's own field maximum.** Once any remanence is present, locate the field at
  which the SC is strongest / Rxx is minimum — that, not the controller's nominal zero, is
  the operating field. In proximity-SOC / valley-Zeeman systems this **effective** zero can
  sit at a nonzero applied field. [heuristic]
- **B_c⊥** (a field sweep at the operating point, `field-sweep-1d.md`) → ξ via Hc2 = Φ₀/2πξ²
  (**order-of-magnitude only** — B_c⊥(T) rounds near base).
- **Field-killing:** a small B⊥ that removes the low Rxx **while the normal state stays ≈
  unchanged** is **consistent-with** SC — one hallmark in the constellation, not strong on
  its own. Sweep **continuously across zero** (−B⊥ → +B⊥ in one pass, not a one-sided
  value→0 ramp); the minimum-Rxx point locates the effective zero and the kill mirrors
  about it. [heuristic]
- **Phase-coherent (Fraunhofer-like) oscillations** vs B⊥ (`fraunhofer.md`) — attempt this:
  scan B⊥ out to B_c⊥ with the bias axis spanning **well past ±Ic** (the wide Step-2 bracket,
  not a narrow window at Ic — the lobe modulation only shows across the full current range).
  Report as **consistent-with phase
  coherence**, extract the implied area (Φ₀/area); do **not** name it "Fraunhofer" or
  over-read the microscopic origin (weak-link vs finite-size geometry are both viable).
  [citation: `2106.07640` over-read note]
- **B_c∥** and its T-dependence. **Pauli caveat:** B_c∥ exceeding 1.86 T/K·Tc means "not
  weak-coupling singlet BCS," **not** a triplet/exotic signature on that basis alone, and the
  quoted B_c∥ is a **lower limit** under any in-plane misalignment (a leaked B⊥ component
  understates it — alignment matters). [paper-data: `s41586`]
- **Graphene–TMD conditional reads** (phenomenology in `s41586/paper.md`, to test): the SC
  region's **±D asymmetry** (present for one D sign only), and the **Pauli-violation ratio
  B_c∥⁰/(1.86·Tc) vs doping** — a ratio ≫ 1 rising toward low doping is the Ising-SOC read.
  [paper-data: `s41586`]

**Step 4 — temperature characterisation (HEAT UP — last)** (`temperature-dependence.md`).
- **Span the T-ladder past Tc and resolve the transition.** The top rung reaches the
  recovered normal state (Ic→0) so Tc is bracketed; the finest rungs sit across the
  Ic-collapse to pin Tc.
- **Size the I_dc window to the base-T Ic.** Ic is widest at base and only shrinks toward
  Tc, so this base-T sizing covers every rung. The I_dc sweep must reach past ±Ic to
  normal-state dV/dI at both ends, so any coherence peaks flanking the SC→normal transition
  are captured.
- Tc / T_BKT via the extraction ladder (`2106.07640/paper.md`): the V ∝ Iᵅ exponent crossing
  α = 3 is the rigorous BKT read; the %-of-normal-state threshold is a stated convention; a
  Halperin–Nelson R(T) fit is often poor for a non-ideal 2D SC (a poor fit is information —
  hedge any T_BKT). State which definition you used. [paper-data]
- ξ from Hc2(T) is the proper route but rounds (→ underestimated T-dependence) and quantum
  geometry also affects ξ → keep ξ **order-of-magnitude**.

**Step 5 — iterate by outcome.**
- **Constellation incomplete** (e.g. dV/dI ridge present but Rxx not to zero) → do NOT round
  to "SC." Carry the **failed-SC / anomalous-metal** fork explicitly and design the
  measurement that separates it (T-dependence of the residual R, field response).
- **Candidate confirmed at base T** → proceed to the full field + fermiology + T
  characterisation; a ~Tc/2 map reads the dome melting and the parent state spatially.
- **Nothing resolvable** → resolution-limited; state the base-T / field / alignment / mobility
  limit, a rig/device question, not more sweeps.

**Step 6 — the call.** Output contract (all five parts mandatory):
1. Per-candidate verdict on the STYLE strength scale (decisive / strong / weak /
   consistent-with / uninformative): `region X: superconductor (strong) | failed-SC /
   anomalous-metal (consistent-with) | not-SC — <confound> (strong) | uninformative` — every
   verdict carries its weight word; a bare lean is not a verdict (`recipes/STYLE.md`).
2. Evidence list: each hallmark with (n, D, B, T) coordinates and the paper panel / benchmark
   it matches.
3. Confidence + specific hedges (which hallmarks present, which searched-and-absent vs
   not-resolvable).
4. What would firm the call (next sweep, lower T, in-plane alignment, different contacts).
5. **A reasoned "cannot tell" / "failed-SC fork unresolved" is a successful outcome. A
   confident "SC" without the hallmark constellation is a protocol violation.**

## Verify

- **Constellation corroboration** — no single-hallmark SC call. The intersection of
  {4-wire Rxx → 0, an Ic that collapses at Tc, a B_c that quenches it, T-dependence} is the
  minimum; a dV/dI peak or a low-R dome alone is consistent-with, not evidence-for.
- **Effective-zero-field via the SC, field-history aware** — the operating field is the
  SC's own maximum, located after the remanence state is known (Step 1/3), not the
  controller's nominal zero.
- **FFT stability sweep for any fermiology claim** — per `sdh-spot-check.md` /
  `landau-fan.md` (vary detrender + window; a real peak sharpens as the 1/B record lengthens,
  an artefact wanders; the field window is bounded both ends).
- **Over-read guards:** Pauli (1.86·Tc is the weak-coupling yardstick, B_c∥ is a misalignment
  lower limit), Fraunhofer (claim phase coherence + extract Φ₀/area, don't name the
  microscopic origin), ξ (order-of-magnitude).
- **TSV-first** — re-form Rxx from the data with the device-card channel arithmetic (4-wire,
  gain division) before any feature claim; rendered monitor PNGs alias structure.

## Examples

*(Mechanical facts only — non-eval devices: RPL_10 / RPL_19, rhombohedral-graphene SC on the
toploader. Cells are 0-indexed per the cited index; `notebook-index-RPL10.md`,
`notebook-index-RPL19.md`.)*

- **Candidate-ID gate map / SC dome** — RPL_19 `20251103_measure.ipynb` §"Gatemap of SC"
  (cell 63), the first n×D megasweep of the dome; per-dome zooms in `20251220_measure.ipynb`
  §"Nice maps of SC1 and SC1'" (cells 77–81). RPL_10 `241207_measure.ipynb` §"Gatemap"
  (cell 43), then SC1 maps in `241230_measure.ipynb` (cells 109 / 115).
- **Field-history / trapped-flux check** — RPL_19 `20251103` §"should check trapped flux
  first" (cell 130) and `20251220` §"Checking trapped flux" (cell 85): Step 1's
  map-before-energise discipline in practice.
- **Nonlinear dV/dI / Ic** — RPL_10 `241207` §"Some I_dc against gate" (cell 94), I_dc
  linecuts at D = 0.35 / −0.21; RPL_19 `20251103` §"Determine Ic at zero field" (cell 86) and
  `20260217` bias spectroscopy (cells 144 / 156 / 215).
- **Field response / phase-coherent oscillations** — RPL_19 `20251103` §"2D fraunhofer"
  (cell 97) with a reversed-direction pass (cell 101); RPL_10 `250201` coherence-length
  extraction (§"SC1, extracting coherence length", cell 124 on) — systematic B_eff sweeps
  (0 → 3 mT), each preceded by an effective-zero-field calibration.
- **T-dependence / Tc** — RPL_10 `250201` §"I_dc against T, SC1'" (cell 30), the dense
  Idc-vs-T series, and `241230` gate maps at the T = 300 / 200 / 115 / 50 mK series (cell 211);
  RPL_19 `20260112` §"Temp dependence cutting across dome" (cell 63).
- **Normal-state fermiology** — RPL_10 `241230` §"Quantum oscillations discovery journey"
  (cells 44 / 49, n-vs-B at D = 0.31) and `250201` effective-mass QO fans (cell 86,
  D = ±0.345, base → V_heater 4.5 V); RPL_19 `20260124` §"Small fan to check if oscillations
  are real" (cell 173) and §"Landau fans" (cell 278). FFT pipeline lives in the `_ana`
  notebooks (`notebook-index-RPL19-ana.md`).
- **Gaps (no clean worked example in the corpus):** an in-plane critical-field / Ic(θ) rotator
  sweep, and an explicit BKT (V ∝ I³) fit workflow.

## Next

- **SC-confirmed:** the full characterisation campaign (field, fermiology, T) → the physics
  (parent state, pairing-symmetry reads, the proximity-SOC reads for graphene–TMD).
- **Failed-SC / anomalous-metal-leaning:** the interesting fork — design the measurements
  that separate it from true SC (residual-R T-dependence, field/bias response).
- **Resolution-limited cannot-tell:** state the base-T / field / alignment / mobility limit;
  a rig/device-quality question, not more sweeps on this rig.
- **Normal-state fermiology (deferred — long measurement):** Landau fan Rxx(n, B⊥) → SdH-FFT
  for the parent phase the SC descends from (`sdh-spot-check.md` / `landau-fan.md`; for
  flavour-polarised graphene–TMD systems normalise to f_norm = n·h/e and identify the parent
  phase, taxonomy in `s41586/paper.md`).
