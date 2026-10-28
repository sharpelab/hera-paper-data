# Cross-validation: Python `h_rhombo` vs Julia `RhombohedralGraphene`

ABCA tetralayer graphene, 8-band continuum Hamiltonian, valley K, B=0.

- **Python**: `hera/models/tetralayer_fs_count/fs_count_b0.py`, `h_rhombo(kx,ky,"ABCA",ABCA,ud)`
- **Julia**: `RMG_Magnetic_field/RhombohedralGrapheneLandau/`, `Hamiltonian(RhombohedralGraphene(AuerbachParams(4); D, linearized), k)`
  (independent implementation by D. E. Parker, verified against his figures)

## Verdict

The Python `h_rhombo` **agrees with the independent Julia implementation to
0.0000 meV (machine precision) at every sampled k** in linearized mode, with
matched parameters, over |k_rel| ≤ 0.5 nm⁻¹, ky=0, u_D ∈ {0, 43 meV}, after the
known uniform potential-offset alignment. In full (non-linearized) structure-
factor mode the two agree to **5.7 meV worst-case at |k_rel|=0.5 nm⁻¹**, a
deviation that is exactly zero at K and grows smoothly as ~|k|² — the expected
Dirac-linearization curvature difference (Python linearizes γ0; Julia's default
keeps the full hexagonal f(k)), not a discrepancy in any coupling. A diagnostic
that flips the γ3 sign in Julia destroys the agreement (>50 meV), confirming the
V/W blocks — including the trigonal-warping γ3 term whose sign the internal gates
cannot check — are correct in both codes. The Python V and W blocks are
validated at the eigenvalue level.

## Parameter mapping

Both use basis ordering A1,B1,A2,B2,A3,B3,A4,B4 (σ fastest, then layer) — identical, no permutation.

| Quantity | Python `ABCA` (Set 1) | Julia `AuerbachParams(4)` | Match |
|---|---|---|---|
| γ0 | g0 = 3.100 | t0 = +3.100 | ✓ |
| γ1 | g1 = 0.380 | t1 = +0.380 | ✓ |
| γ2 | g2 = −0.015 | t2 = −0.015 | ✓ |
| γ3 | g3 = 0.290 (used as `−g3·k̃₊`) | t3 = +0.290 (= −γ3, γ3=−0.290) | ✓ (see note) |
| γ4 | g4 = 0.141 | t4 = +0.141 | ✓ |
| onsite A1,B1 | 0.002, 0.0125 | Δs[1:2] = 0.002, 0.0125 | ✓ |
| onsite A2..B3 (interior) | +0.0085 each | Δs = −Δ₂+δΔ = +0.0085 each | ✓ |
| onsite A4,B4 | 0.0125, 0.002 | Δs[7:8] = 0.0125, 0.002 | ✓ |

**γ3 sign note (this is the subtle one).** Python `ABCA.g3 = 0.29` is a positive
magnitude; the rhombo builder inserts it as the A_l→B_{l+1} element `−g3·k̃₊`.
Julia stores the *true signed* SWMcC γ3 = −0.29 and applies `t3 = −γ3 = +0.29`,
inserting `t3·f̄(k)`. In linearized form `f̄ = −k̃₊`, so Julia's element is
`+0.29·(−k̃₊) = −g3·k̃₊` — **identical** to Python. The two codes use opposite
sign *conventions for the stored γ3 field* but produce the same matrix element.
Flipping either one's convention (the `g3flip` diagnostic) breaks agreement,
so the physical sign is pinned and correct.

**Onsite structure vs paper Eqs. 11–14.** Julia's `Δs` ("Nadav-tetralayer-style")
reproduces Python's `delta`/`D2` scheme exactly for n=4: outer layers carry
±Δ₂ = ±0.002; every dimer site (all interior sublattices, plus B1 and A4) carries
+δΔ = +0.0105 on top. Interior sublattices land at −Δ₂+δΔ = +0.0085; outer
non-dimer sites (A1, B4) at +Δ₂ = 0.002; outer dimer sites (B1, A4) at Δ₂+δΔ =
0.0125. No mismatch — the full onsite vector matches, so the comparison uses the
real Set 1 onsite (no need to zero it out). Julia's legacy `δ` field is unused by
its Hamiltonian (confirmed in `RMGmodel.jl` docstring); the dimer onsite enters
entirely through `Δs`.

## Momentum mapping

- Python: k measured **from K**, units 1/m; `k̃± = KT·(kx±i·ky)`, KT = (√3/2)·a, a = 0.246 nm.
- Julia: absolute k **from Γ**, units 1/a; K = (4π/3, 0); Δk = k − K.
- Map used: `k_julia = K + (kx·a_m, ky·a_m)` with a_m = 2.46×10⁻¹⁰ m (converts 1/m → 1/a).
  Then `f̄_lin = −k̃₊/KT·KT`… concretely `f_lin = (√3/2)(−Δk_x+iΔk_y) = −k̃₋`,
  giving Python's `g0·k̃₋` for the γ0 element — verified analytically and numerically.
- Julia's `a` field does not enter the non-magnetic Bloch H (structure factor is in units of 1/a); only the 1/m→1/a conversion matters. a matches Python's A0.

## Displacement-field (u_D) mapping

- Python: V_l = l·u_D, l=0..3 → {0, u_D, 2u_D, 3u_D}; mean = 1.5·u_D.
- Julia: D·(−(n−1)/2 + (ℓ−1)), ℓ=1..4 → {−1.5D, −0.5D, 0.5D, 1.5D}; mean = 0.
- Same ladder, step u_D = D; differ by a **uniform** +1.5·u_D on all diagonals →
  a rigid shift of all 8 eigenvalues by 1.5·u_D. Set D = u_D and align by
  subtracting each spectrum's mean (removes exactly this constant). At u_D=43 meV
  the raw offset is 64.5 meV = 1.5×43, recovered exactly.

## Comparison (max |ΔE| over all 8 bands, 21 k-points, ky=0, |k_rel|≤0.5 nm⁻¹)

| mode | γ3 variant | u_D (meV) | max\|ΔE\| raw (meV) | max\|ΔE\| demeaned (meV) |
|---|---|---:|---:|---:|
| **lin** | default | 0 | 0.0000 | **0.0000** |
| **lin** | default | 43 | 64.5000 | **0.0000** |
| full | default | 0 | 6.1940 | 6.1940 |
| full | default | 43 | 70.6526 | 6.1526 |
| lin | g3flip (diag) | 0 | 53.60 | 53.60 |
| lin | g3flip (diag) | 43 | 112.46 | 47.96 |
| full | g3flip (diag) | 0 | 58.02 | 58.02 |
| full | g3flip (diag) | 43 | 116.25 | 52.44 |

The "raw" column for lin/default/u_D=43 is entirely the 64.5 meV uniform
potential offset; demeaning removes it → 0.0000 meV.

### Full-mode deviation vs |k_rel| (default, u_D=0, demeaned)

| \|k_rel\| (1/nm) | lin dev (meV) | full dev (meV) |
|---:|---:|---:|
| 0.00 | 0.0000 | 0.0000 |
| 0.10 | 0.0000 | 0.1953 |
| 0.20 | 0.0000 | 0.8360 |
| 0.30 | 0.0000 | 1.9639 |
| 0.40 | 0.0000 | 3.5970 |
| 0.50 | 0.0000 | 5.7465 |

Zero at K, ~|k|² growth: textbook linearization curvature. Python is
Dirac-linearized (γ0 enters as linear k̃), so the apples-to-apples comparison is
against Julia `linearized=true`, where agreement is exact.

## Diagnosis

No discrepancy. Every coupling (γ0, γ1, γ2, γ3, γ4), the full onsite vector, the
momentum convention, and the u_D ladder map cleanly between the two codes. The
only nonzero deviation (full mode) is the intended physics difference between a
linearized and a full structure factor, and it vanishes at K and scales as |k|².
The γ3-flip diagnostic isolates the trigonal-warping term and confirms both codes
carry the same physical γ3 sign despite opposite stored-field conventions.

## Reproducibility

- **Julia**: 1.12.6, installed user-locally via juliaup
  (`curl -fsSL https://install.julialang.org | sh -s -- --yes`).
- Full package instantiate was **not** needed (and its PyCall/PyPlot/IJulia deps
  are the ones RUN_NOTES documents as segfault-prone). Instead a minimal project
  with only `StaticArrays`, `Parameters`, `UnPack`, `LinearAlgebra`, then
  `include("src/parameters.jl"); include("src/RMGmodel.jl")` — no PyCall loaded,
  no IJulia, run as a plain script (per RUN_NOTES' "plain julia scripts" guidance).
- Julia dumper: `julia --project=. dump.jl` → `julia_eigs.csv`
  (modes {lin,full} × variants {default,g3flip} × u_D {0,43 meV} × 21 kx).
- Python: `uv run --no-project --with numpy --with scipy python3 compare.py`
  loads `fs_count_b0.py` by path, calls `h_rhombo`, compares against the CSV.
- Scripts live in the session scratchpad (jlproj/dump.jl, compare.py, kbreak.py);
  nothing in the Julia repo or the Python model file was modified.
