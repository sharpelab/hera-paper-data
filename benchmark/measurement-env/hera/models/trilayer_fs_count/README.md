# Trilayer FS-count forward model — ABA vs ABC

Backs the `recipes/investigations/trilayer-stacking-fs-count.md` investigation.
This model computes the **B = 0 Fermi-surface count**, the **Onsager
frequencies F(n, D)**, and the **cyclotron masses m\*(n)** the FS-count read
overlays on data — ABA ≥ 2 coexisting surfaces (ML Dirac + BL parabolic) vs
ABC's single post-Lifshitz pocket — plus the high-field ABA LL/Streda
complement (`ll_sequence.py`). **Both carrier signs**: the sign of the input
density selects electron (n > 0) or hole (n < 0) doping.

The survey that grounds it (band structure, the three ingested papers, the
feasibility numbers) is `docs/stacking-extraction-survey.md`; read it for the
physics. This README covers what the tools are and how to run them.

## Files

| File | What it does |
|---|---|
| `fs_count_b0.py` | B = 0 FS count + Onsager F(n, D) + m\*(n), both carrier signs. **ABA** from the continuum 6-site SWMcC Hamiltonian via a signed-density solve (electron pockets +k²/π, hole pockets −k²/π; annular pockets emerge automatically); **ABC** from the MacDonald PRB 82, 035409 (2010) effective two-band model, both branches E⁺ (conduction) and E⁻ (valence), with trigonal warping → the 3-pocket → annulus → single-pocket Lifshitz cascade on each side. Counts distinct extremal-orbit frequencies F = (ℏ/2πe)·A_k, F positive/area-based for electron- and hole-like orbits alike. Pure numpy/scipy. |
| `ll_spectrum.py` | The validated ABA SWMcC LL spectrum (per-valley LL energies, ML/BL tagging) — the shared physics core `ll_sequence.py` builds on. Same parameter set as `fs_count_b0.py`. |
| `plots.py` | Renders `{aba_bands_linecut, abc_bands_linecut, abc_bands_contour, luttinger_vs_n}.png` from `fs_count_b0`. |
| `ll_sequence.py` | High-field complement: ABA Landau-level fan + QH/Streda sequence (the pseudo-decoupled ML Dirac band offsets the Chern sequence; non-dispersing ML N=0 doublet). Imports `ll_spectrum.py`. Outputs `aba_LL_fan.png`, `aba_wannier.png`. |
| `*.png` | Generated figures (band linecuts, ABC contour, Luttinger-sum check, LL fan, Wannier diagram). |
| `rmg-fft-snapshot/` | Frozen copy of the RMG SdH-FFT analysis pipeline (background-subtract in B → interp to 1/B → window → FFT, with the stability-sweep hygiene). A **reference snapshot, not a standalone package** — see its `PROVENANCE.md`; reconcile into `hera.analysis.sdh_fft` later. |

## API (call shapes)

- `aba_fs(n, U=0.0) -> (E_F, [(F, kF), ...])` — every Onsager orbit at E_F,
  sorted by F.
- `abc_fs(n, ud=0.0) -> (E_F, topo, n_components, n_freq, F_tot)`.
- `aba_mstar(n, U=0.0) -> [(F, m*/m_e), ...]` — per-orbit cyclotron masses,
  m\* = (ℏ²/2π)·dA/dE, same orbits/order as `aba_fs`.
- `abc_mstar(n, ud=0.0) -> (F_tot, m*/m_e)` — from dn/dE_F on the same solve;
  in the multi-pocket cascade region this is the pocket-summed mass.
- `E_abc(kx, ky, ud=0.0, band=+1)` — band = +1 (E⁺) / −1 (E⁻).

Masses are positive for electron- and hole-like orbits alike; the carrier sign
comes from the input n.

## Domain — loud, never clamped

The solvers raise `ValueError` (naming the covered range) for any density
outside the solved table; E_F rows whose Fermi contour would cross the k-grid
edge are excluded from the table on both sides. Solved coverage at D = 0:
ABA ≈ −14.9…+14.3 ×10¹² cm⁻², ABC ≈ ±11 ×10¹² cm⁻² — comfortably beyond the
±8×10¹² cm⁻² design target (QC0426's reachable |n| ≈ 6.4×10¹²).

## Parameters and validity

**Semi-quantitative — trust topology, shape, and partition, not absolute
frequencies.** The discriminating outputs are the FS count, the
Dirac-vs-parabolic branch *shape*, and the model-independent Luttinger sum
Σ±f = (h/4e)|n|. Absolute frequencies inherit the hopping-parameter error bars
— the SWMcC set (Datta fit included) and the two-band projection both carry
wide ones — so overlay measured F(n) by shape and a single global density
rescale, never by absolute position.

- **ABA**: Datta-fit SWMcC {γ₀, γ₁, γ₂, γ₅, δ} plus **γ₄ = 0.04 eV from
  McCann–Koshino** (Datta's fit carries no γ₄; Aaron's call 2026-07-18). γ₄
  carries the BL-sector e-h mass asymmetry and preserves rotational symmetry,
  so the radial solve is exact. **γ₃ = 0**: BL-contour trigonal warping is
  neglected (matters only for the low-|n| BL fine structure). Both γ₃ and γ₄
  act on the mirror-even (BL) sector only — **the ML discriminator tone is
  exact either way**. `ll_spectrum.py` carries the same γ₄ (ladder-basis
  −v₄π† terms; validated: 2 / 14 meV k=0 splittings unchanged, BL N=0
  zero-mode pinned at 0).
- **ABC**: MacDonald Table I, both E± branches of the two-band projection.
  The **hole-side Lifshitz cascade region is qualitative** — the cascade lands
  at ≈ −1.5×10¹² cm⁻² (3-pocket → annulus → single), an order of magnitude
  above the electron side's ~10¹¹, and MacDonald reports no hole-side anchor
  to validate against. At operating density (|n| ≳ 2×10¹²) the pocket is
  single and **F(n) is Luttinger-solid** ((h/4e)|n| by area conservation),
  insensitive to the two-band model's asymmetry accuracy. A continuum model
  is the candidate longer-term upgrade (with the ABC LL model below).
- ABA is semimetallic: for |n| ≲ 0.5×10¹² (electron side) tiny electron and
  hole pockets coexist (ML valence top overlaps BL conduction bottom by
  ~14 meV), the orbit list reports all of them, and only the **signed** sum
  of frequencies equals (h/4e)|n| there.

## Validation

- **Luttinger sum** Σ±f = (h/4e)|n| reproduces on **both carrier signs** in
  both models at every density tested (residuals ≤ ~25 mT, grid
  discretization).
- `fs_count_b0` reproduces MacDonald's electron-side trigonal-warping Lifshitz
  cascade location (~10¹¹ cm⁻²).
- Hole-side anchors (QC0426 capstone-2 / session-3): ABA at n = −3×10¹² gives
  [4.35, 26.67] T (measured f_ML 4.0–4.3, f_BL 27–28); at −6×10¹² the sum is
  62.0 T = (h/4e)·6×10¹⁶ (measured partition sum 62–66 T).
- m\* cross-checks: ML orbit mass matches the analytic Dirac ℏk_F/v; ABA
  per-orbit masses satisfy the thermodynamic-DOS identity
  dn/dE = (2/πℏ²)·Σ±m\* against the density table; ABC m\* matches an
  independent finite-difference of E_F(n). BL holes heavier than electrons
  (γ₄), e.g. 0.063 vs 0.056 m_e at |n| = 3×10¹².
- `ll_sequence` builds on the already-validated `ll_spectrum.py`
  (the 2 meV / 14 meV band splittings gate that model).

## Run

```bash
cd hera/models/trilayer_fs_count
uv run --no-project --with numpy --with scipy python3 fs_count_b0.py              # FS count + Onsager + m* tables
uv run --no-project --with numpy --with scipy --with matplotlib python3 plots.py # band/Luttinger figures
uv run --no-project --with numpy --with scipy --with matplotlib python3 ll_sequence.py  # high-field Streda fan
```
(`--no-project` pulls just numpy/scipy/matplotlib — the worktree's submodules
aren't checked out, so `uv sync` can't run here.)

## Gap / future work

A quantitative **ABC** Landau-level model is **not yet built** — only ABA is
computed, so the high-field Streda/Chern contrast (recipe Step 6) is qualitative
on the ABC side. See `docs/stacking-extraction-survey.md` §9. Candidates: adapt
Dan Parker's `RhombohedralGrapheneLandau.jl` (N-layer rhombohedral, incl. R3G;
lab clone: `github.com/sharpelab/RMG_Magnetic_field`), or build it alongside a
continuum ABC model (which would also retire the two-band hole-side cascade
caveat above).
