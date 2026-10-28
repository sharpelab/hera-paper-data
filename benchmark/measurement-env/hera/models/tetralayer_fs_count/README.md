# Tetralayer FS-count forward model — ABAB vs ABCA (vs ABCB)

Backs the `recipes/investigations/tetralayer-stacking-fs-count.md` investigation.
This model computes the **B = 0 Fermi-surface count**, the **Onsager
frequencies F(n)** (and vs interlayer potential u_D for ABCA), and the
**cyclotron masses m\*(n)** the FS-count read overlays on data — ABAB a pair
partitioning F_L (≈ 0.72 / 0.28 with φ²-split masses in the decomposition
limit; the key table below carries the real F(n)) vs ABCA's single
post-cascade pocket at F_L, with ABCB a qualitative cubic + Dirac pair.
**Both carrier signs**: the sign of the input density selects electron
(n > 0) or hole (n < 0) doping.

The survey that grounds it (band structure, the four ingested papers, the
feasibility framing) is `docs/tetralayer-stacking-extraction-survey.md`; read
it for the physics. This README covers what the tools are and how to run them.

## Files

| File | What it does |
|---|---|
| `synth_fan.py` | Synthetic Rxx(n, B) fan generator on the model's F(n)/m\*(n): LK thermal + Dingle dressing, 2nd harmonics, background, noise; optional lever-arm scale error, breakdown sum-tone, mixed-domain superposition. Ground truth per column in `truth.json`. |
| `synth_eval.py` | Mechanical recipe evaluator over the synthetic fans (pipeline FFT → Luttinger-aware harmonic screen → global scale pin → template match → B-window split → adjacent-N). Six-case suite + `RESULTS.md` in `$HERA_DATA/tetralayer-synth-validation/`. |
| `JULIA_CROSSCHECK.md` | Independent-implementation eigenvalue comparison (machine precision; see Validation). |
| `fs_count_b0.py` | B = 0 FS count + Onsager F(n) + m\*(n), both carrier signs. **ABAB** from the 2N-band SWMcC Hamiltonian (Koshino–McCann PRB 83, 165443 Eq. 1, N = 4), graphite parameters, via a rotationally-symmetric signed-density radial solve (electron pockets +k²/π, hole pockets −k²/π; the two bilayer-like blocks emerge automatically). **ABCA** from the 8-band continuum model of arXiv 2606.05356 S15 (Eqs. 8–14), parameter Set 1, on a 2D k-grid (trigonal warping → the low-density three-pocket → annulus → single Lifshitz cascade); interlayer potential u_D via the onsite U_l structure. **ABCB** qualitative, via the generic linkage builder. A generic `build_h(kx, ky, seq, p, ud)` dispatches any stacking string ('ABAB','ABCA','ABA','ABC',…) to a Bernal / rhombohedral / mixed block builder by link sense, so trilayer sequences run for backtests. Counts distinct extremal-orbit frequencies F = (ℏ/2πe)·A_k, positive/area-based for electron- and hole-like orbits alike. Pure numpy/scipy; `selftest()`/`__main__` runs every validation gate and prints the key tables. |

## API (call shapes)

- `abab_fs(n, ud=0.0) -> (E_F, [(F, kF), ...])` — every ABAB Onsager orbit at
  E_F, sorted by F.
- `abab_mstar(n, ud=0.0) -> [(F, m*/m_e), ...]` — per-orbit cyclotron masses,
  m\* = ℏ²k_F/|dE/dk|, same orbits/order as `abab_fs`.
- `abca_fs(n, ud=0.0) -> (E_F, topo, n_components, n_freq, F_total)` — topology
  from connected components of the Fermi sea (single / annulus / k-pocket).
- `abca_mstar(n, ud=0.0) -> (F_total, m*/m_e)` — from dn/dE_F on the same solve;
  pocket-summed in the cascade region.
- `abcb_fs(n, ud=0.0) -> (E_F, [(F, ncomp), ...])` — **qualitative**, electron
  side only: the two low-energy conduction tones (cubic J = 3 + Dirac J = 1).
- Generic underneath: `bernal_fs`/`bernal_mstar`/`rhombo_fs`/`rhombo_mstar`
  take a sequence + `Params`; `build_h(kx, ky, seq, p, ud)` returns the
  Hamiltonian; `ABAB`, `ABCA`, `ABA_TRI` are the parameter sets.

Masses are positive for electron- and hole-like orbits alike; the carrier sign
comes from the input n.

## Domain — loud, never clamped

The solvers raise `ValueError` (naming the covered range) for any density
outside the solved table; E_F rows whose Fermi contour would cross the k-grid
edge are excluded from the table on both sides. Solved coverage at u_D = 0:
ABAB ≈ −17.7…+17.1 ×10¹² cm⁻², ABCA ≈ ±11.5 ×10¹² cm⁻² — comfortably beyond
the ±8×10¹² cm⁻² design target.

## Parameters and validity

**Semi-quantitative — trust topology, shape, and partition, not absolute
frequencies.** The discriminating outputs are the FS count, the ABAB partition
and its φ²-split masses, and the model-independent Luttinger sum
Σ±f = (h/4e)|n|. Absolute frequencies inherit the hopping-parameter error bars.

- **ABAB**: Koshino–McCann graphite SWMcC set {γ₀ = 3.0, γ₁ = 0.4, γ₂ = −0.02,
  γ₄ = 0.04, γ₅ = 0.04, Δ′ = 0.05 eV}, all remote couplings ON. **γ₃ = 0**:
  the BL-contour trigonal warping is neglected so the solve stays radial (same
  precedent and caveat as the trilayer ABA treatment — γ₃ touches only the
  low-|n| BL fine structure). The 0.724 / 0.276 partition and φ² ≈ 2.618 mass
  ratio are the **low-n parabolic (decomposition) asymptote**; two effects
  distort them away from it — non-parabolicity (the bilayer bands bend toward
  linear) pulls the ratio *down* with rising |n|, while the γ₂-scale
  band-bottom offset dominates at low |n| and washes out with rising |n|. In
  the full model the electron-side partition passes through ≈ 0.73 near
  |n| ≈ 6×10¹²; the hole side runs lower (≈ 0.64) from the Δ′/γ₄ e–h asymmetry
  and the near-CNP semimetal overlap (§ below). Even-N has no mirror plane, so
  the two bilayer blocks are mixed by γ₂/γ₅ at the ~20 meV scale and inter-block
  magnetic breakdown is symmetry-allowed — the two-FS picture is exact only
  above that scale.
- **ABCA**: arXiv 2606.05356 S15 Set 1 {γ₀ = 3.1, γ₁ = 0.38, γ₂ = −0.015,
  γ₃ = 0.29, γ₄ = 0.141, δ = 0.0105, Δ₂ = 0.002 eV}, **γ₃ ON** (trigonal
  warping is the physics of the low-density cascade, not fine structure).
  u_D enters as a linear interlayer potential V_l = l·u_D (no Hartree screening).
  At operating density (|n| ≳ 2×10¹²) the pocket is single and F(n) is
  Luttinger-solid ((h/4e)|n| by area conservation), insensitive to the
  parameter error bars.
- **ABCB**: qualitative only, via the mixed-linkage builder run on the ABCA
  hopping magnitudes. Reproduces the J = 3 cubic main band + J = 1 Dirac-like
  partner rising from the ~δ (≈ 10 meV) gap; the two tones Luttinger-sum to
  F_L. **Absolute frequencies and the partition are not calibrated** — trust
  the two-tone topology and order of magnitude only. Not gated.
- ABAB is semimetallic near the CNP: for small |n| tiny electron and hole
  pockets coexist (the two blocks' band bottoms are offset at the γ₂ scale),
  the orbit list reports all of them, and only the **signed** sum of
  frequencies equals (h/4e)|n| there.

## Validation

All six gates pass (`selftest()`); residuals quoted are the actual run.

- **Gate 1 — ABAB decomposition limit**: with γ₂ = γ₅ = Δ′ = γ₄ = γ₃ = 0 the
  k = 0 spectrum is {±0.618γ₁, ±1.618γ₁, 0×4} (λ = 2cos2π/5, 2cos π/5) to
  1.7×10⁻¹² eV; the high-density Onsager partition → 0.7236 / 0.2764 and mass
  ratio → 2.618 in the low-n parabolic limit (0.722 / 2.574 at |n| = 0.25×10¹²,
  monotonically degrading with non-parabolicity: 0.692 / 2.01 at 6×10¹²).
- **Gate 2 — Luttinger sum** Σ±f = (h/4e)|n| reproduces on **both carrier
  signs** for ABAB (signed) and ABCA (single pocket) at every density tested
  (worst residual 0.015 T, grid discretization).
- **Gate 3a — ABCA higher-order vHS**: the analytic E₂ (S15 Eq. 17) crosses
  zero at the critical u_D solving Eq. 18, u_D = 42.82 meV; the numerical
  lowest-conduction-band k → 0 curvature flips sign at 43 meV, tracking E₂ to
  ≤ 0.3% across u_D ∈ [30, 55] meV.
- **Gate 3b — ABCA Lifshitz cascade**: at u_D = 43 meV the Fermi sea passes
  **three-pocket → annulus → single** as n grows (topology sequence matches
  Fig S29-c). Boundaries land at n ≈ 1.5 / 2.6 ×10¹² — ~2–4× above the S29-c
  digitization; **qualitative agreement only** (topology + order of magnitude),
  as scoped by the survey.
- **Gate 4 — trilayer backtest**: the generic builder run as 'ABA' with the
  frozen `models/trilayer_fs_count` parameters reproduces that model's
  `aba_fs` F(n) at n = ±{1,2,3,6}×10¹² to **≤ 0.17%** (e.g. +6×10¹²:
  [7.01, 55.03] vs [7.02, 55.02] T; −3×10¹²: [4.35, 26.66] vs [4.35, 26.67] T).
  The generic 'ABC' single-pocket F(n) matches (h/4e)|n| to 0.01% (Luttinger —
  the frozen ABC is a MacDonald two-band projection, so only its
  Luttinger-pinned F is comparable).
- **Gate 5 — m\* identities**: ABAB per-orbit masses satisfy the thermodynamic
  DOS identity dn/dE = (2/πℏ²)·Σ±m\* against the density table (worst 0.2%);
  ABCA m\* matches an independent finite-difference of E_F(n) (worst 1.7%).
- **Synthetic-fan recovery** (`synth_fan.py` + `synth_eval.py`; artifacts in
  `$HERA_DATA/tetralayer-synth-validation/RESULTS.md`): six dressed synthetic
  fans (clean ABAB hole/electron incl. the low-n trap, clean ABCA, breakdown
  sum-tone adversarial, 12% lever-arm scale error, trilayer-mislabeled-4L) all
  classified correctly by the mechanical recipe logic; global scale pinned to
  ≤ 2% (the 1.12 case recovered exactly); claimed-tone frequency error < 0.5%
  median; every trap navigated (low-n ambiguity flagged not called; breakdown
  identified by B-window split; adjacent-N fired on the mislabeled case).
  Method findings folded into the recipe: Luttinger-aware harmonic screen,
  cross-column adjacent-N consensus, narrow-window breakdown resolvability.
- **Agent-in-harness replay (rung 3b + adjacent-N amendment)** — three
  classification-frontier fixtures
  (`hera/test-cases/{2026-05-14-QC0512,2026-05-21-QC0531,2026-02-17-RPL19}-stacking-fan`)
  through `hera-replay`, n = 3 each, production HERA tier: the F_L-tone-origin
  discrimination fires 3/3 (breakdown fixture — ABAB strong, no eager ABCA);
  operating-point discipline holds 3/3 (real D = 1 fan declined); the
  adjacent-N guard fires 3/3 name-blind on the trilayer-carded-4LGr fixture
  under the recipe's binding dual-overlay gate, with no over-correction
  (genuine-ABAB replay 1/1; mechanical suite 6/6). Not elicited: the
  degeneracy audit (agents disqualify off-operating-point fans on D first).
  Scoring + prereg: `$HERA_DATA/tetralayer-replay-3b/`.
- **Julia cross-check** (`JULIA_CROSSCHECK.md`): `h_rhombo` agrees with the
  independent `RhombohedralGrapheneLandau.jl` implementation at the
  eigenvalue level to **machine precision** (linearized γ₀, matched Set-1
  parameters, valley K, |k| ≤ 0.5 nm⁻¹, u_D ∈ {0, 43 meV}); full-f(k) mode
  differs ≤ 6 meV at the window edge, the expected Dirac-linearization
  curvature (zero at K, ~|k|²). A γ₃-sign flip blows the comparison to
  > 50 meV — the trigonal-warping term the internal gates can't check is
  confirmed. Sign-convention note: julia stores signed γ₃ = −0.29 with
  t₃ = −γ₃; this model stores the magnitude with the sign in the builder —
  same matrix element.

### Key output table (u_D = 0)

Predicted F(n) and m\*(n) — feed the investigation recipe's feasibility step.

| n [10¹² cm⁻²] | ABAB F [T] (light, heavy) | ABAB m\* [m_e] | ABCA F [T] | ABCA m\* [m_e] |
|---|---|---|---|---|
| +1 | 0.6, 9.8 | 0.022, 0.057 | 10.3 | 0.135 |
| +2 | 3.6, 17.1 | 0.024, 0.058 | 20.7 | 0.089 |
| +3 | 6.7, 24.4 | 0.027, 0.060 | 31.0 | 0.076 |
| +6 | 16.7, 45.4 | 0.034, 0.067 | 62.0 | 0.069 |
| −1 | 4.4, 5.9 | 0.074, 0.033 | 10.3 | 1.114 |
| −2 | 9.1, 11.6 | 0.033, 0.075 | 20.7 | 0.208 |
| −3 | 12.3, 18.7 | 0.035, 0.077 | 31.0 | 0.134 |
| −6 | 22.3, 39.8 | 0.041, 0.082 | 62.0 | 0.096 |

ABAB's two tones sum to F_L at every row (Luttinger). The near-CNP hole rows
(−1, −2) sit in the semimetal-overlap regime — the tones are close and the
0.72 / 0.28 partition is not yet resolved there; it emerges at higher |n|.
ABCA's singleton is F_L exactly; its m\* rises sharply toward the flat-band
edge on the hole side (1.11 m_e at −1×10¹²).

### Real-data validation (RPL_19 / arXiv:2606.05356)

Validated against real Landau fans from RPL_19 (the paper's rmg19 device;
identity from matching gate-calibration constants + sweep-ids). Scripts
`rpl19_load.py` / `real_eval.py` / `lf_crosscheck.py` reuse the pipeline above;
memo + tables in `$HERA_DATA/tetralayer-rpl19-validation/MEMO.md`.

- **CQM** (D=1, n≳0.78): single tone n_SdH = n (f_ν = 1.01) → degeneracy audit
  reads g=1; **0.2% median** agreement with the paper's own `Lf_analysis` on
  data/1840.
- **Multitone** (near cCSC): tones with f_ν > 1 flagged non-Onsager — the
  Luttinger sum fails honestly, as the recipe requires.
- **Flavor cascade** g=4/2/1 read directly from tone position (S21 method).
- **LK m\*** at (n=1, D=1) = 0.32 m_e vs paper 0.39–0.7 (semi-quantitative;
  window-averaged B_eff bias).
- **Stacking read** only weakly exercised: this device's data is mostly high-D
  and flavor-polarized (a degeneracy read, not a stacking read); at the D=0.2,
  g=4 columns it is ABCA-consistent (weak), matching the known ABCA.

## Run

```bash
cd hera/models/tetralayer_fs_count
uv run --no-project --with numpy --with scipy python3 fs_count_b0.py   # all gates + tables
```
(`--no-project` pulls just numpy/scipy — the worktree's submodules aren't
checked out, so `uv sync` can't run here. Full run ≈ 60 s.)

## Gap / future work

- **No 4L Landau-level models**: the high-field face is qualitative (survey § 4;
  the chirality sum rule already makes the ν = 8,12,16 ladder stacking-blind, so
  the trilayer Streda-offset discriminator does not carry to N = 4).
- **ABCB is qualitative**: the mixed-linkage builder reproduces the cubic + Dirac
  topology on borrowed ABCA hoppings, but its absolute frequencies, the
  intrinsic-gap magnitude, and the J = 1 velocity renormalization are not
  calibrated — a dedicated ABCB parameter set (e.g. Wirth et al.,
  arXiv:2203.07971, not yet ingested) would be needed to make it quantitative.
- The Gate 3b boundary densities sit ~2–4× above the Fig S29-c digitization;
  reconciling that (Hartree-screened V_l(D) vs bare linear u_D, exact u_D
  reading) would upgrade the ABCA cascade from qualitative to quantitative.
