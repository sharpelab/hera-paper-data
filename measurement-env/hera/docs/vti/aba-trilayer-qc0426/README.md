# Paper-faithful ABA-trilayer crossing model — QC0426

*SCORER / SUPPORT-SIDE — not for agent view. QC0426 campaign analysis;
the shared physics core (`ll_spectrum.py`) lives in
`hera/models/trilayer_fs_count/`.*


Forward model of the ABA (Bernal) trilayer-graphene Landau-level spectrum,
following the methodology of **Datta et al., Nat. Commun. 8:14518 (2017)**, used
to test whether the curved dark arcs in the QC0426 run-80 Landau fan are
ML×BL Landau-level **crossing chains** (→ ABA stacking) or something else.

This is the *forward-model* path (compute the spectrum the paper computed, derive
the crossing pattern, overlay on data). A sibling subtask (`fan-crossing-detector`)
owns the data-driven detector; nothing here touches it.

## Files

| File | What it does |
|---|---|
| `ll_spectrum.py` | 6-site SWMcC Hamiltonian (γ0,γ1,γ2,γ5,δ) built directly in the Landau-level ladder basis; diagonalized per B; both valleys; each level tagged ML/BL by mirror-parity projection + orbital index. `selftest()` validates the 2 meV / 14 meV splittings. |
| `crossing_model.py` | Energy→density via LL filling (eB/h, referenced to CNP); `ml_trajectories()` (density at which ML level N_M sits vs B = a crossing chain); `crossing_loci()` (explicit ML×BL coincidences); `dos_map()` (calculated DOS on the (n,B) plane). |
| `validate.py` | Reproduces Datta Fig 3a (E vs B) and Fig 2b (N_M=0 vertical + N_M≥1 parabola chains). |
| `compare_qc0426.py` | Re-forms run-80 Rxx(n,B) (sr1), digitizes Qingrui's 5 green arcs from the annotated PNG, overlays model chains, fits a global density-scale α, and renders the paper-style measured-vs-calculated panel. |
| `figures/` | All output PNGs (also pushed to ZeeRef `fan-vision`). |

## Run

```bash
cd hera/models/aba_trilayer
uv run --no-project --with numpy --with scipy python3 ll_spectrum.py     # validation arithmetic
uv run --no-project --with numpy --with scipy --with matplotlib python3 validate.py
uv run --no-project --with numpy --with scipy --with matplotlib --with pillow python3 compare_qc0426.py
```
(The lab env can't `uv sync` here because the worktree's submodules aren't
checked out; `--no-project` pulls just numpy/scipy/matplotlib/pillow.)

## Model — what was built and how it was validated

Full 6-site SWMcC Hamiltonian at one valley, basis (A1,B1,A2,B2,A3,B3), keeping
γ0=3.1, γ1=0.39, γ2=−0.028, γ5=0.01, δ=0.021 eV (Datta's fitted values), γ3=γ4=0.
The Dirac term v·π is the LL ladder operator (Γ_B = v√(2ℏeB), v = √3·a₀·γ0/2ℏ =
1.003×10⁶ m/s, Γ_B = 36.4 meV·√(B/T) — the textbook monolayer scale). Constant
terms (γ1, γ2/2, γ5/2, δ, layer potential) couple equal ladder levels. Anomalous
zero-energy LLs fall out of the truncated ladder automatically (no special cases).

**Validation gates passed:**
- On-site assignment pinned by the paper's two splittings: ML band split
  δ+γ2/2−γ5/2 = **2.00 meV**, BL band split |γ2|/2 = **14.0 meV** — both reproduced
  exactly (`ll_spectrum.selftest`).
- LL spectrum E(B) shows the ML (√B) and BL (≈linear) ladders crossing — the
  structure of Datta Fig 3a (`figures/fig3a_spectrum.png`).
- Crossing loci in (n,B) reproduce Datta Fig 2b: **N_M=0 = a near-vertical chain
  at n≈0.8×10¹² cm⁻²**, N_M=1,2,3,4 = parabola-like chains displaced to higher
  density (`figures/fig2b_loci.png`). This is the paper's fingerprint, generated
  from first principles rather than matched by eye.

## QC0426 comparison (run 80, D = +0.25 V/nm, B 8→0 T)

Re-formed Rxx(n,B) from the sr1 channel with the device-card lever arm
(c_tg = ε₀·3/15.6 nm, c_bg = ε₀·3/12 nm). Digitized Qingrui's 5 green dark-arc
traces from the annotated PNG via the detected axis calibration. Computed the
model's ML-level crossing chains across the same window.

**Result (`figures/qc0426_overlay_afit.png`, `qc0426_data_vs_dos_a1p00.png`):**

- The model produces a **fan of crossing chains (N_M=0…4) occupying the same
  region of the (n,B) plane as the measured dark arcs**, with the **same fan-out
  topology and the same curvature sign** (density rises with B, chains splay to
  higher n for higher N_M).
- A **single global density rescale α = 0.82** (i.e. true lever arm ≈ 0.82× the
  nominal capacitances — well within the stated capacitance uncertainty; the
  device card itself flags the lever arm as needing a ν-cross-check) brings the
  model chains onto the arc fan. After α: **4 of the 5 arcs are matched within
  median |Δn| < 0.1×10¹² cm⁻²**; the rightmost/shortest arc is off by 0.64.

## Dark-vs-bright follow-up (the half-period question)

In Rxx, a level coincidence (ML=BL) is a DOS(E_F) maximum → Rxx *maximum*
(bright); a gap coincidence is a DOS(E_F) minimum → Rxx *minimum* (dark). The
QC0426 arcs are dark, so the natural question was whether they track the model's
**gap-coincidence (dark)** loci rather than its **level-coincidence (bright)**
chains, half a period away. `crossing_model.dos_at_fermi()` builds the
compressibility map DOS(E_F)(n,B) (`figures/qc0426_dosEF_map.png`) and
`bright_dark_loci()` extracts both families.

**Two findings:**

1. **The gap-vs-level (half-period) distinction is NOT resolvable here — honest
   negative.** At QC0426 densities the fan is densely tiled: ~3500 bright + ~3600
   dark loci spaced ≈0.1×10¹² cm⁻² apart, finer than the arc width and the
   disorder broadening. A single global α puts the arcs within median
   |Δn|≈0.011×10¹² of *both* families (saturated metric). So the model cannot say
   the arcs are specifically gap- vs level-coincidences
   (`figures/qc0426_dark_vs_bright.png`).

2. **But the decisive, resolvable signal is across-ray cutting.** A straight ν-ray
   has constant filling factor ν=n·h/(eB) along its length (span 0) — this is the
   feature the previous data-driven detector mistakenly re-traced. Each measured
   arc instead **sweeps 28–85 filling factors** along its length (arc0: ν 27→112;
   arc4: ν 110→154), i.e. it cuts diagonally across many rays. The model crossing
   chains do the same (N_M=0..4 span ν 66→174). This is exactly the
   crossing-chain fingerprint and is *not* what a constant-ν ray or a straight
   beat fringe produces (`figures/qc0426_cuts_across.png`).

## Verdict

**Consistent with — and supportive of — an ABA crossing-chain origin for the dark
arcs, but not a stand-alone proof of stacking.** The paper-physics forward model,
with the paper's own band parameters and no per-arc tuning (one global α),
reproduces a family of LL crossing chains co-located with QC0426's dark arcs in
position, fan-out topology, curvature sign, and B-range. Decisively, **both the
arcs and the model chains cut across constant-ν rays (sweeping 28–85 / 66–174
filling factors along their length)** — the crossing-chain fingerprint, and the
single feature that distinguishes a real chain from the straight-ν-ray the prior
data-driven detector mistakenly re-traced. A two-domain beat-fringe / mosaic
origin would not naturally produce this specific ML×BL chain family, with this
across-ray cutting, from the ABA band parameters — so the agreement is non-trivial.

**Honest caveats — why this is "consistent with" and not "confirmed":**

1. **Permissive metric.** The Δn residuals use nearest-chain distance: with five
   model chains fanning across the same region as five arcs, small min-distances
   partly reflect family co-location, not one-to-one arc↔chain identity. The
   *topological* agreement (across-ray cutting, shape, curvature, count, fan-out)
   is the stronger claim.
2. **Dark vs bright (the half-period question) — investigated, unresolvable here.**
   A level coincidence is an Rxx maximum (bright); the arcs are DARK, so they
   should be the complementary gap-coincidence channels ~half a BL-level period
   away. The DOS(E_F) map (`dos_at_fermi`) was built to test this, but at QC0426
   densities the fan is densely tiled with both families (≈0.1×10¹² spacing,
   finer than the arc width / disorder broadening), so the half-period assignment
   cannot be resolved — both families fit equally (saturated metric). This
   sub-question needs either a lower-density window or a higher-mobility device,
   not more modelling.
3. **D = 0 model vs D = +0.25 V/nm data.** The model is the paper's mirror-symmetric
   D≈0 fingerprint. Finite D breaks mirror symmetry and hybridizes ML/BL (the
   `delta_field` knob is wired but unused here), shifting crossing positions.
   A D-series check (runs 81/82/83/84 at D = +1/−1/−0.25/−0.5) is the decisive
   experiment: ABA crossings move and proliferate with D; under the discriminating
   D≈0 condition ABA has two symmetry-guaranteed ladders and ABC has one.
4. **Disorder.** QC0426 resolves fan rays only above ~2 T (vs <0.5 T in the paper's
   500k-mobility device), so fine crossing/bead structure is washed out — the dark
   arcs are the coarse, eye-visible envelope, consistent with item-2's note about
   log-scale single-color renders.

**Recommended live-session moves (HERA):** (i) take a D≈0 fan and look for the
**N_M=0 vertical crossing chain** at fixed density — the cleanest single ABA marker,
and one this model places concretely; (ii) compare arcs across the D-series to test
the move-with-D behavior; (iii) a lower-density / lower-B window (where LLs are
sparse enough to resolve individual gaps) is the only way to settle the bright vs
dark half-period assignment — at the run-80 density it is below resolution.
