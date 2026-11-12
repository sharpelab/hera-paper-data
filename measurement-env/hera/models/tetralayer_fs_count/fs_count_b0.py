#!/usr/bin/env python3
"""
B=0 Fermi-surface counting: tetralayer graphene ABAB vs ABCA (and ABCB).

Backs recipes/investigations/tetralayer-stacking-fs-count.md and the survey
docs/tetralayer-stacking-extraction-survey.md. Computes, at B=0, for BOTH
carrier signs (sign of the input density selects electron n>0 / hole n<0):
Fermi-surface count, Onsager frequencies F(n) = (hbar/2 pi e)*A_k, and
cyclotron masses m* = (hbar^2/2 pi) dA/dE.

Stackings:
  ABAB (Bernal)  -> two bilayer-like parabolic pairs. SWMcC 2N-band Hamiltonian
                    (Koshino-McCann PRB 83,165443 Eq.1), graphite parameters.
                    gamma3=0 by default (keeps rotational symmetry -> radial
                    solve; gamma3 touches only low-|n| BL fine structure).
  ABCA (rhombo)  -> single post-cascade pocket. 8-band continuum model of
                    arXiv:2606.05356 S15 Eqs.8-14, parameter Set 1. gamma3 ON
                    (trigonal warping drives the low-density Lifshitz cascade).
                    Interlayer potential u_D via the onsite U_l structure.
  ABCB (mixed)   -> qualitative only; built when it falls out of the linkage
                    rule (see abcb_fs). Cubic + renormalized-Dirac pair.

A single sequence-parameterized Hamiltonian builder underneath (build_h) takes
letter strings ('ABAB','ABCA','ABA','ABC',...): alternating stacking sense ->
Bernal blocks, monotonic sense -> rhombohedral blocks. This lets the frozen
trilayer sequences run for backtests.

Solvers raise ValueError outside the solved density domain (never clamp).
No external deps beyond numpy/scipy.
Run: uv run --no-project --with numpy --with scipy python3 fs_count_b0.py
"""
import importlib.util
import sys
from dataclasses import dataclass, replace
from pathlib import Path
import numpy as np
import scipy.constants as cst
from scipy.ndimage import label

HBAR, E, ME = cst.hbar, cst.e, cst.m_e
A0 = 0.246e-9
KT = np.sqrt(3) / 2 * A0            # k~ prefactor: k~^pm = KT*(kx +- i ky)


def F_from_area(A_k):
    """Onsager frequency (Tesla) from a k-space area (1/m^2)."""
    return HBAR * A_k / (2 * np.pi * E)


@dataclass(frozen=True)
class Params:
    """SWMcC hopping set (eV). g5/dp used by Bernal; delta/D2/g3 by rhombo."""
    g0: float
    g1: float
    g2: float
    g3: float
    g4: float
    g5: float = 0.0
    dp: float = 0.0        # Delta' — Bernal dimer-site onsite
    delta: float = 0.0     # rhombo dimer-site onsite
    D2: float = 0.0        # rhombo Delta2


# ABAB — Koshino-McCann graphite set (PRB 83,165443); gamma3 default OFF.
ABAB = Params(g0=3.0, g1=0.4, g2=-0.02, g3=0.0, g4=0.04, g5=0.04, dp=0.05)
# ABCA — arXiv:2606.05356 S15 Set 1 (meV -> eV).
ABCA = Params(g0=3.1, g1=0.38, g2=-0.015, g3=0.29, g4=0.141,
              delta=0.0105, D2=0.002)
# Trilayer backtest sets, read from the frozen models/trilayer_fs_count model.
ABA_TRI = Params(g0=3.1, g1=0.39, g2=-0.028, g3=0.0, g4=0.04, g5=0.01, dp=0.021)


def _senses(seq):
    """Per-link stacking sense: +1 cyclic (A->B->C->A), -1 anticyclic."""
    pos = {"A": 0, "B": 1, "C": 2}
    c = [pos[s] for s in seq]
    return [1 if (c[i + 1] - c[i]) % 3 == 1 else -1 for i in range(len(c) - 1)]


# ---------------- Hamiltonian builders (vectorized over k) ----------------

def _ktilde(kx, ky):
    kx = np.asarray(kx, float); ky = np.asarray(ky, float)
    return KT * (kx + 1j * ky), KT * (kx - 1j * ky)   # ktp, ktm


def h_bernal(kx, ky, seq, p, ud=0.0):
    """2N x 2N Bernal SWMcC Hamiltonian (eV), basis A1,B1,A2,B2,...,AN,BN.
    Vectorized: kx,ky scalars or arrays of shape S -> H shape (*S, 2N, 2N).
    Adjacent links alternate V, V^dagger (even-N has no mirror plane); gamma2
    on A-A / gamma5 on B-B second neighbors (alternating W, W')."""
    ktp, ktm = _ktilde(kx, ky)
    S = ktp.shape
    N = len(seq)
    H = np.zeros(S + (2 * N, 2 * N), complex)
    lay = np.arange(N) - (N - 1) / 2.0
    for l in range(N):
        A, B = 2 * l, 2 * l + 1
        H[..., A, B] += p.g0 * ktm
        H[..., B, A] += p.g0 * ktp
        H[..., A, A] += lay[l] * ud
        H[..., B, B] += lay[l] * ud
        if l % 2 == 0:            # odd layer (1-indexed): Delta' on B
            H[..., B, B] += p.dp
        else:                     # even layer: Delta' on A
            H[..., A, A] += p.dp
    vp = np.zeros(S + (2, 2), complex)     # V+ = [[-g4 ktm, g3 ktm],[g1,-g4 ktm]]
    vp[..., 0, 0] = -p.g4 * ktm
    vp[..., 0, 1] = p.g3 * ktm
    vp[..., 1, 0] = p.g1
    vp[..., 1, 1] = -p.g4 * ktm
    vpd = np.conj(np.swapaxes(vp, -1, -2))
    for l in range(N - 1):
        blk = vp if l % 2 == 0 else vpd
        i = 2 * l
        H[..., i:i + 2, i + 2:i + 4] += blk
        H[..., i + 2:i + 4, i:i + 2] += np.conj(np.swapaxes(blk, -1, -2))
    for l in range(N - 2):
        i = 2 * l
        d = (p.g2 / 2, p.g5 / 2) if l % 2 == 0 else (p.g5 / 2, p.g2 / 2)
        H[..., i, i + 4] += d[0]
        H[..., i + 4, i] += d[0]
        H[..., i + 1, i + 5] += d[1]
        H[..., i + 5, i + 1] += d[1]
    return H


def h_rhombo(kx, ky, seq, p, ud=0.0):
    """2N x 2N rhombohedral continuum Hamiltonian (eV), 2606.05356 S15 Eqs.8-14.
    All adjacent links cyclic (single V block); gamma2 on A_l-B_{l+2} (W).
    Onsite: delta on every dimer site, +Delta2 outer layers / -Delta2 inner,
    linear layer potential V_l = l*ud (so u_D = V_{l+1}-V_l)."""
    ktp, ktm = _ktilde(kx, ky)
    S = ktp.shape
    N = len(seq)
    H = np.zeros(S + (2 * N, 2 * N), complex)
    for l in range(N):
        A, B = 2 * l, 2 * l + 1
        H[..., A, B] += p.g0 * ktm
        H[..., B, A] += p.g0 * ktp
        d2 = p.D2 if (l == 0 or l == N - 1) else -p.D2
        vl = l * ud
        H[..., A, A] += d2 + vl
        H[..., B, B] += d2 + vl
        if l != 0:              # A_l is a dimer site for l>0
            H[..., A, A] += p.delta
        if l != N - 1:          # B_l is a dimer site for l<N-1
            H[..., B, B] += p.delta
    vp = np.zeros(S + (2, 2), complex)     # V = [[-g4 ktm,-g3 ktp],[g1,-g4 ktm]]
    vp[..., 0, 0] = -p.g4 * ktm
    vp[..., 0, 1] = -p.g3 * ktp
    vp[..., 1, 0] = p.g1
    vp[..., 1, 1] = -p.g4 * ktm
    vpd = np.conj(np.swapaxes(vp, -1, -2))
    for l in range(N - 1):
        i = 2 * l
        H[..., i:i + 2, i + 2:i + 4] += vp
        H[..., i + 2:i + 4, i:i + 2] += vpd
    for l in range(N - 2):      # W = [[0, g2/2],[0,0]] : A_l - B_{l+2}
        i = 2 * l
        H[..., i, i + 5] += p.g2 / 2
        H[..., i + 5, i] += p.g2 / 2
    return H


def h_mixed(kx, ky, seq, p, ud=0.0):
    """Qualitative ABCB builder: nearest-neighbor V by per-link sense (cyclic
    -> V, anticyclic -> V^dagger, rhombo convention), remote gamma2/gamma5 only
    between letter-aligned same-index-2 layers. Marked qualitative — not gated."""
    ktp, ktm = _ktilde(kx, ky)
    S = ktp.shape
    N = len(seq)
    sn = _senses(seq)
    H = np.zeros(S + (2 * N, 2 * N), complex)
    dimerA = [False] * N        # A_l participates in a gamma1 bond below
    dimerB = [False] * N        # B_l participates in a gamma1 bond above
    for l, s in enumerate(sn):
        if s > 0:
            dimerB[l] = True; dimerA[l + 1] = True
        else:
            dimerA[l] = True; dimerB[l + 1] = True
    for l in range(N):
        A, B = 2 * l, 2 * l + 1
        H[..., A, B] += p.g0 * ktm
        H[..., B, A] += p.g0 * ktp
        vl = (l - (N - 1) / 2.0) * ud
        H[..., A, A] += vl + (p.delta if dimerA[l] else 0.0)
        H[..., B, B] += vl + (p.delta if dimerB[l] else 0.0)
    vp = np.zeros(S + (2, 2), complex)
    vp[..., 0, 0] = -p.g4 * ktm
    vp[..., 0, 1] = -p.g3 * ktp
    vp[..., 1, 0] = p.g1
    vp[..., 1, 1] = -p.g4 * ktm
    for l, s in enumerate(sn):
        blk = vp if s > 0 else np.conj(np.swapaxes(vp, -1, -2))
        i = 2 * l
        H[..., i:i + 2, i + 2:i + 4] += blk
        H[..., i + 2:i + 4, i:i + 2] += np.conj(np.swapaxes(blk, -1, -2))
    for l in range(N - 2):      # remote coupling only between letter-aligned layers
        if seq[l] == seq[l + 2]:
            i = 2 * l
            H[..., i, i + 4] += p.g2 / 2
            H[..., i + 4, i] += p.g2 / 2
            H[..., i + 1, i + 5] += p.g5 / 2
            H[..., i + 5, i + 1] += p.g5 / 2
    return H


def build_h(kx, ky, seq, p, ud=0.0):
    """Dispatch a stacking sequence to its Hamiltonian builder by link sense."""
    sn = _senses(seq)
    if all(s > 0 for s in sn):
        return h_rhombo(kx, ky, seq, p, ud)
    if all(sn[i] == -sn[i - 1] for i in range(1, len(sn))):
        return h_bernal(kx, ky, seq, p, ud)
    return h_mixed(kx, ky, seq, p, ud)


def is_radial(seq):
    """True when the stacking's builder is rotationally symmetric at gamma3=0
    (Bernal / mixed with gamma3=0)."""
    return not all(s > 0 for s in _senses(seq))


# ---------------- domain-checked interpolation ----------------

def _interp_domain_checked(n_target, nvals, EFs, model):
    if not (nvals[0] <= n_target <= nvals[-1]):
        raise ValueError(
            f"{model}: requested n = {n_target:.3e} m^-2 is outside the solved "
            f"density domain [{nvals[0]:.3e}, {nvals[-1]:.3e}] m^-2 "
            f"(E_F/k grid limited) — extend the grids; do not clamp.")
    return np.interp(n_target, nvals, EFs)


# ---------------- radial solve (Bernal / rotationally symmetric) ----------------

def _radial_table(seq, p, ud, kmax, nk, ef_max, nef):
    """Signed-density table n(E_F) from a radial spectrum. Returns
    (kg, Eb, EFs, nvals). E_F rows whose Fermi contour would cross kmax are
    dropped so out-of-range requests raise instead of silently clamping."""
    kg = np.linspace(1e3, kmax, nk)
    Eb = np.linalg.eigvalsh(build_h(kg, 0.0, seq, p, ud))     # (nk, 2N)
    Eb = Eb.T                                                  # (2N, nk)
    nb = Eb.shape[0]
    EFs = np.linspace(-ef_max, ef_max, nef)
    rising_edge = (Eb[:, -1] > Eb[:, -2])[:, None]
    occ_edge = Eb[:, -1][:, None] < EFs[None, :]
    EFs = EFs[~np.any(occ_edge == rising_edge, axis=0)]

    def density(EF):
        tot = 0.0
        for b in range(nb):
            cross = np.where((Eb[b, :-1] - EF) * (Eb[b, 1:] - EF) < 0)[0]
            for c in cross:
                sgn = 1.0 if Eb[b, c + 1] > Eb[b, c] else -1.0
                tot += sgn * kg[c] ** 2 / np.pi
        return tot
    nvals = np.array([density(ef) for ef in EFs])
    return kg, Eb, EFs, nvals


def _radial_orbits(kg, Eb, EF):
    """Every Onsager crossing at EF: list of (F, kF, band, index)."""
    out = []
    for b in range(Eb.shape[0]):
        cross = np.where((Eb[b, :-1] - EF) * (Eb[b, 1:] - EF) < 0)[0]
        for c in cross:
            out.append((F_from_area(np.pi * kg[c] ** 2), kg[c], b, c))
    return out


def bernal_fs(n_target, seq="ABAB", p=ABAB, ud=0.0,
              kmax=6e8, nk=7000, ef_max=0.3, nef=12001):
    """(E_F, [(F, kF), ...]) for signed density n_target (m^-2) on a Bernal
    stacking. Signed radial density: rising crossing = electron pocket
    (+kF^2/pi), falling = hole pocket (-kF^2/pi), g_s g_v = 4. Raises out of
    the solved domain."""
    kg, Eb, EFs, nvals = _radial_table(seq, p, ud, kmax, nk, ef_max, nef)
    EF = _interp_domain_checked(n_target, nvals, EFs, seq)
    fs = [(F, kF) for F, kF, _, _ in _radial_orbits(kg, Eb, EF)]
    return EF, sorted(fs)


def bernal_mstar(n_target, seq="ABAB", p=ABAB, ud=0.0,
                 kmax=6e8, nk=7000, ef_max=0.3, nef=12001):
    """Per-orbit (F, m*/m_e), same orbits/order as bernal_fs. m* = hbar^2 kF /
    |dE/dk| at each isotropic crossing; positive for both carrier signs."""
    kg, Eb, EFs, nvals = _radial_table(seq, p, ud, kmax, nk, ef_max, nef)
    EF = _interp_domain_checked(n_target, nvals, EFs, seq)
    out = []
    for F, kF, b, c in _radial_orbits(kg, Eb, EF):
        dEdk = abs(Eb[b, c + 1] - Eb[b, c]) / (kg[c + 1] - kg[c]) * E   # J*m
        out.append((F, HBAR ** 2 * kF / dEdk / ME))
    return sorted(out)


def abab_fs(n_target, ud=0.0):
    """ABAB Onsager orbits at signed density n_target (m^-2)."""
    return bernal_fs(n_target, "ABAB", ABAB, ud)


def abab_mstar(n_target, ud=0.0):
    """ABAB per-orbit cyclotron masses at signed density n_target (m^-2)."""
    return bernal_mstar(n_target, "ABAB", ABAB, ud)


# ---------------- 2D solve (rhombohedral, trigonal warping) ----------------

def _rhombo_band_grid(seq, p, ud, band_idx, kmax, ng, chunk=40000):
    """Energy (eV) of one band index on a square k-grid, chunked eigvalsh.
    Returns (Egrid (ng,ng), dk). band_idx counts from the bottom (0..2N-1)."""
    kx = np.linspace(-kmax, kmax, ng)
    KX, KY = np.meshgrid(kx, kx)
    kxf, kyf = KX.ravel(), KY.ravel()
    out = np.empty(kxf.size)
    for s in range(0, kxf.size, chunk):
        e = s + chunk
        H = build_h(kxf[s:e], kyf[s:e], seq, p, ud)
        out[s:e] = np.linalg.eigvalsh(H)[:, band_idx]
    return out.reshape(ng, ng), kx[1] - kx[0]


def _rhombo_table(seq, p, ud, band, kmax, ng, nef):
    """Density table n(E_F) for the lowest conduction (band>0) or highest
    valence (band<0) band. Returns (Egrid, dk, EFs, nvals). E_F window stops
    where the Fermi contour touches the grid edge (no clamp)."""
    N = len(seq)
    band_idx = N if band > 0 else N - 1
    Egrid, dk = _rhombo_band_grid(seq, p, ud, band_idx, kmax, ng)
    Esort = np.sort(Egrid.ravel())
    edge = np.concatenate([Egrid[0], Egrid[-1], Egrid[:, 0], Egrid[:, -1]])
    if band > 0:
        EFs = np.linspace(Egrid.min(), edge.min(), nef)
        nvals = 4 * (np.searchsorted(Esort, EFs) * dk * dk) / (2 * np.pi) ** 2
    else:
        EFs = np.linspace(edge.max(), Egrid.max(), nef)
        nempty = Esort.size - np.searchsorted(Esort, EFs, side="right")
        nvals = -4 * (nempty * dk * dk) / (2 * np.pi) ** 2
    return Egrid, dk, EFs, nvals


def rhombo_fs(n_target, seq="ABCA", p=ABCA, ud=0.0, kmax=6.5e8, ng=601, nef=6000):
    """(E_F, topo, n_components, n_freq, F_total) for signed density n_target
    on a rhombohedral stacking. Topology from connected components of the Fermi
    sea (single / annulus / k-pocket). Raises out of the solved domain."""
    band = 1 if n_target >= 0 else -1
    Egrid, dk, EFs, nvals = _rhombo_table(seq, p, ud, band, kmax, ng, nef)
    ng = Egrid.shape[0]
    EF = _interp_domain_checked(n_target, nvals, EFs, seq)
    occ = (Egrid < EF) if band > 0 else (Egrid > EF)
    _, ncomp = label(occ)
    center = occ[ng // 2, ng // 2]
    A_occ = occ.sum() * dk * dk
    if center and ncomp == 1:
        topo, nfreq = "single", 1
    elif (not center) and ncomp == 1:
        topo, nfreq = "annulus", 2
    else:
        topo, nfreq = f"{ncomp}-pocket", 1
    return EF, topo, ncomp, nfreq, F_from_area(A_occ)


def rhombo_mstar(n_target, seq="ABCA", p=ABCA, ud=0.0,
                 kmax=6.5e8, ng=601, nef=6000, fit_mev=0.6):
    """(F_total, m*/m_e) at signed density n_target. m* = (pi/2) hbar^2
    |dn/dE_F| from the density table (pocket-summed in the cascade region)."""
    band = 1 if n_target >= 0 else -1
    Egrid, dk, EFs, nvals = _rhombo_table(seq, p, ud, band, kmax, ng, nef)
    EF = _interp_domain_checked(n_target, nvals, EFs, seq)
    win = np.abs(EFs - EF) <= fit_mev * 1e-3
    if win.sum() < 10:
        raise ValueError(
            f"{seq}: m* fit window (+-{fit_mev} meV) falls off the solved E_F "
            f"table at n = {n_target:.3e} m^-2 — too close to the domain edge.")
    slope = np.polyfit(EFs[win], nvals[win], 1)[0] / E
    occ = (Egrid < EF) if band > 0 else (Egrid > EF)
    return F_from_area(occ.sum() * dk * dk), np.pi / 2 * HBAR ** 2 * abs(slope) / ME


def abca_fs(n_target, ud=0.0, kmax=6.5e8, ng=601, nef=6000):
    """ABCA FS topology + Onsager frequency at signed density n_target (m^-2),
    interlayer potential ud (eV)."""
    return rhombo_fs(n_target, "ABCA", ABCA, ud, kmax, ng, nef)


def abca_mstar(n_target, ud=0.0, kmax=6.5e8, ng=601, nef=6000):
    """ABCA cyclotron mass (F_total, m*/m_e) at signed density n_target."""
    return rhombo_mstar(n_target, "ABCA", ABCA, ud, kmax, ng, nef)


# ---------------- ABCB (qualitative) ----------------

def abcb_fs(n_target, ud=0.0, kmax=6.5e8, ng=601, nef=6000):
    """QUALITATIVE ABCB electron-side read via the mixed-linkage builder: the
    two low-energy conduction bands (J=3 cubic main tone + J=1 renormalized-
    Dirac partner rising from the ~δ intrinsic gap) at a shared E_F. Returns
    (E_F, [(F, ncomp) per occupied low-energy band]). Not gated — uses ABCA
    hopping magnitudes on the ABCB linkage; trust the two-tone topology and
    order of magnitude only, not absolute frequencies. Electron side only."""
    if n_target < 0:
        raise ValueError("ABCB: qualitative electron-side (n>0) read only.")
    N = 4
    g4 = _rhombo_band_grid("ABCB", ABCA, ud, N, kmax, ng)[0]
    g5, dk = _rhombo_band_grid("ABCB", ABCA, ud, N + 1, kmax, ng)
    both = np.sort(np.concatenate([g4.ravel(), g5.ravel()]))
    edge = np.concatenate([g4[0], g4[-1], g4[:, 0], g4[:, -1]])
    EFs = np.linspace(g4.min(), edge.min(), nef)
    nvals = 4 * (np.searchsorted(both, EFs) * dk * dk) / (2 * np.pi) ** 2
    EF = _interp_domain_checked(n_target, nvals, EFs, "ABCB")
    out = []
    for g in (g4, g5):
        occ = g < EF
        if occ.any():
            _, ncomp = label(occ)
            out.append((F_from_area(occ.sum() * dk * dk), ncomp))
    return EF, out


# ---------------- analytic ABCA vHS (Eq.17/18) ----------------

def abca_E2(ud, p=ABCA):
    """E2 coefficient of E = E0 + E2 k~^2 + ... (2606.05356 Eq.17), eV per k~^2.
    ud in eV. E2 -> 0 at the higher-order vHS."""
    return p.g0 * (p.g0 * p.g2 ** 2 - 3 * p.g0 * ud ** 2
                   + 3 * p.g0 * ud * (p.delta - 2 * p.D2)
                   + 6 * p.g1 * p.g4 * ud) / (3 * p.g1 ** 2 * ud)


def abca_vhs_ud(p=ABCA):
    """Critical ud (eV) solving Eq.18 (E2=0); positive root."""
    a = -3 * p.g0
    b = 3 * p.g0 * (p.delta - 2 * p.D2) + 6 * p.g1 * p.g4
    c = p.g0 * p.g2 ** 2
    roots = np.roots([a, b, c])
    return float(max(r.real for r in roots if abs(r.imag) < 1e-12 and r.real > 0))


def _abca_curv_num(ud, p=ABCA, kmax=6e7, nk=41):
    """Numerical k~^2 coefficient of the lowest conduction band at k->0 (eV)."""
    kg = np.linspace(0.0, kmax, nk)
    Eb = np.linalg.eigvalsh(h_rhombo(kg, 0.0, "ABCA", p, ud))[:, 4]
    kt = KT * kg
    A = np.vstack([kt ** 2, kt ** 4, np.ones_like(kt)]).T
    coef, *_ = np.linalg.lstsq(A, Eb, rcond=None)
    return coef[0]


# ---------------- self-test / validation gates ----------------

def _load_frozen():
    """Import the frozen trilayer model by path (read-only backtest source)."""
    fp = (Path(__file__).resolve().parent.parent
          / "trilayer_fs_count" / "fs_count_b0.py")
    spec = importlib.util.spec_from_file_location("trilayer_frozen", fp)
    assert spec is not None and spec.loader is not None, fp
    mod = importlib.util.module_from_spec(spec)
    prev = sys.dont_write_bytecode
    sys.dont_write_bytecode = True             # never write a .pyc into the frozen dir
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = prev
    return mod


def selftest():
    F_L = lambda n: F_from_area((2 * np.pi) ** 2 * abs(n) / 4)
    ok = []

    print("=" * 74)
    print("GATE 1 — ABAB decomposition limit (g2=g5=Dp=g4=g3=0)")
    bare = replace(ABAB, g2=0.0, g5=0.0, dp=0.0, g4=0.0, g3=0.0)
    ev0 = np.linalg.eigvalsh(h_bernal(1e3, 0.0, "ABAB", bare))
    lam = np.array([2 * np.cos(np.pi / 5), 2 * np.cos(2 * np.pi / 5)])
    want = np.sort(np.concatenate([lam * ABAB.g1, -lam * ABAB.g1, [0, 0, 0, 0]]))
    err = np.max(np.abs(np.sort(ev0) - want))
    print(f"  k=0 eigenvalues (eV): {np.round(np.sort(ev0), 4)}")
    print(f"  expected  ±0.618γ1,±1.618γ1,0×4: {np.round(want, 4)}")
    print(f"  lambda = {lam[1]:.4f} (0.618), {lam[0]:.4f} (1.618); max err {err:.2e} eV")
    print("  partition heavy/total and m*_heavy/m*_light vs n (decomposition"
          " limit is the low-n parabolic asymptote → 0.7236 / 2.618):")
    part = mratio = 0.0
    for n in (0.25e16, 1e16, 3e16, 6e16):
        fr = sorted(F for F, _ in bernal_fs(n, "ABAB", bare)[1])
        ms = sorted(mm for _, mm in bernal_mstar(n, "ABAB", bare))
        p_ = fr[-1] / sum(fr)
        r_ = ms[-1] / ms[0]
        print(f"    n={n/1e16:5.2f}e12  partition={p_:.4f}  m*ratio={r_:.4f}")
        if n == 0.25e16:
            part, mratio = p_, r_
    g1 = (err < 1e-6 and abs(part - 0.7236) < 0.01 and abs(mratio - 2.618) < 0.06)
    ok.append(("1 ABAB decomposition", g1))

    print("=" * 74)
    print("GATE 2 — Luttinger sum  Σ(signed) f = (h/4e)|n|  (both signs)")
    worst = 0.0
    kg, Eb, EFs, nvals = _radial_table("ABAB", ABAB, 0.0, 6e8, 7000, 0.3, 12001)
    for n in (-6e16, -3e16, -1e16, 1e16, 3e16, 6e16):
        EF = _interp_domain_checked(n, nvals, EFs, "ABAB")
        ssum = 0.0
        for F, _, b, c in _radial_orbits(kg, Eb, EF):
            sgn = 1.0 if Eb[b, c + 1] > Eb[b, c] else -1.0
            ssum += sgn * F
        worst = max(worst, abs(ssum - np.sign(n) * F_L(n)))
    for n in (-6e16, -3e16, -1e16, 1e16, 3e16, 6e16):
        _, _, _, _, Ft = abca_fs(n)
        worst = max(worst, abs(Ft - F_L(n)))
    print(f"  worst |Σf - F_L| across ABAB(signed) + ABCA(single): {worst:.3f} T")
    g2 = worst < 1.0
    ok.append(("2 Luttinger sum", g2))

    print("=" * 74)
    print("GATE 3a — ABCA higher-order vHS (Eq.18 E2=0)")
    ud_c = abca_vhs_ud()
    print(f"  analytic critical u_D = {ud_c * 1e3:.2f} meV")
    print("  u_D[meV]  E2_analytic[eV]  curv_num[eV]  sign")
    flip = None
    prev = None
    for udm in (30, 35, 40, 42, 43, 45, 50, 55):
        ud = udm * 1e-3
        e2 = abca_E2(ud)
        cn = _abca_curv_num(ud)
        s = "+" if cn > 0 else "-"
        print(f"    {udm:5.0f}   {e2:+.4e}    {cn:+.4e}   {s}")
        if prev is not None and (cn > 0) != (prev > 0):
            flip = udm
        prev = cn
    print(f"  numerical curvature sign flips near u_D ≈ {flip} meV "
          f"(analytic {ud_c*1e3:.1f})")
    g3a = 40 <= ud_c * 1e3 <= 46 and flip is not None and abs(flip - ud_c * 1e3) < 6
    ok.append(("3a ABCA vHS", g3a))

    print("=" * 74)
    print("GATE 3b — ABCA Lifshitz cascade vs n at u_D in [35,60] meV (Fig S29)")
    print("  topology sequence as n grows (grid built once per u_D):")
    seqs = {}
    for udm in (43, 50):
        Egrid, dk = _rhombo_band_grid("ABCA", ABCA, udm * 1e-3, 4, 3.2e8, 801)
        ng = Egrid.shape[0]
        Esort = np.sort(Egrid.ravel())
        edge = np.concatenate([Egrid[0], Egrid[-1], Egrid[:, 0], Egrid[:, -1]])
        EFs = np.linspace(Egrid.min(), edge.min(), 4000)
        nn = 4 * (np.searchsorted(Esort, EFs) * dk * dk) / (2 * np.pi) ** 2
        row = []
        for n12 in (0.3, 0.8, 1.3, 1.8, 2.3, 2.8):
            if n12 * 1e16 > nn[-1]:
                row.append((n12, "oob"))
                continue
            EF = np.interp(n12 * 1e16, nn, EFs)
            occ = Egrid < EF
            _, ncomp = label(occ)
            center = occ[ng // 2, ng // 2]
            topo = ("single" if (center and ncomp == 1)
                    else "annulus" if (not center and ncomp == 1)
                    else f"{ncomp}-pocket")
            row.append((n12, topo))
        seqs[udm] = row
        print(f"  u_D={udm} meV: " + "  ".join(f"{n:.1f}:{t}" for n, t in row))
    t43 = [t for _, t in seqs[43]]
    order = [t for t in t43 if t != "oob"]
    # sequence must show a multi-pocket, then an annulus, then single, in order
    i_multi = next((i for i, t in enumerate(order) if "pocket" in t), None)
    i_ann = next((i for i, t in enumerate(order) if t == "annulus"), None)
    i_sing = next((i for i, t in enumerate(order) if t == "single"), None)
    g3b = (i_multi is not None and i_ann is not None and i_sing is not None
           and i_multi < i_ann < i_sing)
    print(f"  ordered cascade 3-pocket→annulus→single present: {g3b} "
          f"(boundaries ~1.5–2.6e12; ~2–4× Fig S29-c digitization, qualitative)")
    ok.append(("3b ABCA Lifshitz", g3b))

    print("=" * 74)
    print("GATE 4 — trilayer backtest (generic builder vs frozen model)")
    frozen = _load_frozen()
    print("  ABA: F(n) generic-Bernal 'ABA' vs frozen aba_fs")
    print("   n[1e12]   generic F[T]          frozen F[T]         max Δ%")
    worst_pct = 0.0
    for n in (1e16, 2e16, 3e16, 6e16, -1e16, -2e16, -3e16, -6e16):
        _, gfs = bernal_fs(n, "ABA", ABA_TRI)
        _, ffs = frozen.aba_fs(n)
        gf = sorted(F for F, _ in gfs)
        ff = sorted(F for F, _ in ffs)
        m = min(len(gf), len(ff))
        pcts = [abs(gf[i] - ff[i]) / max(ff[i], 1e-6) * 100
                for i in range(m) if ff[i] > 0.5]
        wp = max(pcts) if pcts else 0.0
        worst_pct = max(worst_pct, wp)
        print(f"    {n/1e16:+5.1f}   {np.round(gf,2)}   {np.round(ff,2)}   {wp:.2f}%")
    print("  ABC: single-pocket F(n) (Luttinger-pinned) via generic rhombo 'ABC'")
    worst_abc = 0.0
    for n in (2e16, 3e16, 6e16, -2e16, -3e16, -6e16):
        _, topo, _, _, Ft = rhombo_fs(n, "ABC", ABCA, kmax=6.5e8, ng=601)
        if topo == "single":
            worst_abc = max(worst_abc, abs(Ft - F_L(n)) / F_L(n) * 100)
    print(f"    single-pocket max |F - F_L|/F_L = {worst_abc:.2f}%")
    g4 = worst_pct < 5.0 and worst_abc < 3.0
    ok.append(("4 trilayer backtest", g4))

    print("=" * 74)
    print("GATE 5 — m* DOS identity  dn/dE = (2/πħ²) Σ± m*  (ABAB) + ABCA FD")
    worst_id = 0.0
    _, _, EFs, nvals = _radial_table("ABAB", ABAB, 0.0, 6e8, 7000, 0.3, 12001)
    for n in (1e16, 3e16, 6e16, -3e16, -6e16):
        EF = _interp_domain_checked(n, nvals, EFs, "ABAB")
        summ = sum(m for _, m in bernal_mstar(n, "ABAB", ABAB)) * ME
        dndE_thermo = 2 / (np.pi * HBAR ** 2) * summ                 # per J per m^2
        i = np.searchsorted(EFs, EF)
        lo, hi = max(i - 40, 0), min(i + 40, len(EFs) - 1)
        dndE_tab = (nvals[hi] - nvals[lo]) / ((EFs[hi] - EFs[lo]) * E)
        rel = abs(dndE_thermo - dndE_tab) / abs(dndE_tab)
        worst_id = max(worst_id, rel)
    print(f"  ABAB DOS identity worst relative error = {worst_id*100:.1f}%")
    worst_fd = 0.0
    for n in (2e16, 3e16, 6e16):
        _, mc = abca_mstar(n)
        dn = 0.05e16
        EFp = rhombo_fs(n + dn, "ABCA", ABCA)[0]
        EFm = rhombo_fs(n - dn, "ABCA", ABCA)[0]
        dnde_fd = 2 * dn / ((EFp - EFm) * E)
        m_fd = np.pi / 2 * HBAR ** 2 * dnde_fd / ME
        worst_fd = max(worst_fd, abs(m_fd - mc) / mc)
    print(f"  ABCA m* vs finite-difference E_F(n) worst rel error = {worst_fd*100:.1f}%")
    g5 = worst_id < 0.10 and worst_fd < 0.10
    ok.append(("5 m* identities", g5))

    print("=" * 74)
    print("KEY OUTPUT TABLE  (u_D = 0)")
    print("  n[1e12]   ABAB F[T] (light,heavy)      ABAB m*        ABCA F[T]  m*")
    for n in (1e16, 2e16, 3e16, 6e16, -1e16, -2e16, -3e16, -6e16):
        fs = sorted(bernal_fs(n, "ABAB", ABAB)[1])
        ms = bernal_mstar(n, "ABAB", ABAB)
        fstr = ", ".join(f"{F:.1f}" for F, _ in fs)
        mstr = ", ".join(f"{m:.4f}" for _, m in ms)
        Fa, ma = abca_mstar(n)
        print(f"    {n/1e16:+5.1f}   [{fstr}]   [{mstr}]   {Fa:6.1f}   {ma:.4f}")

    print("=" * 74)
    print("ABCB (qualitative, ungated) — two low-energy conduction tones")
    for n in (1e16, 3e16, 6e16):
        EF, tones = abcb_fs(n)
        tstr = ", ".join(f"F={F:.1f}T(cc{c})" for F, c in tones)
        print(f"    n={n/1e16:+.0f}e12  EF={EF*1e3:.1f}meV  [{tstr}]  "
              f"ΣF vs F_L={sum(F for F, _ in tones):.1f}/{F_L(n):.1f} T")

    print("=" * 74)
    print("out-of-domain (must raise, not clamp)")
    for fn, n in ((abab_fs, 3e17), (abab_fs, -3e17),
                  (abca_fs, 3e17), (abca_fs, -3e17)):
        try:
            fn(n)
            print(f"    {fn.__name__}({n:+.0e}): NO ERROR — BUG")
        except ValueError:
            print(f"    {fn.__name__}({n:+.0e}): ValueError ok")

    print("=" * 74)
    for name, passed in ok:
        print(f"  GATE {name}: {'PASS' if passed else 'FAIL'}")
    return all(p for _, p in ok)


if __name__ == "__main__":
    selftest()
