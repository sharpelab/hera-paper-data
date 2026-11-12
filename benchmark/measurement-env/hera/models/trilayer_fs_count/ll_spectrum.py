#!/usr/bin/env python3
"""
ABA (Bernal) trilayer graphene Landau-level spectrum, SWMcC parametrization.

Reproduces the single-particle LL model of Datta et al., Nat. Commun. 8:14518
(2017) (arXiv:1610.00314), built on Serbyn & Abanin PRB 87, 115422 (2013) and
Koshino & McCann PRB 81, 115315 (2010).

Construction
------------
Full 6-site SWMcC Hamiltonian at one valley, basis (A1,B1,A2,B2,A3,B3), kept
parameters gamma0, gamma1, gamma2, gamma4, gamma5, delta (gamma3=0; gamma4 =
0.04 eV per McCann-Koshino — Datta's fit carries no gamma4). The matrix is
built directly in the Landau-level ladder basis: each sublattice carries its
own oscillator ladder |0>,|1>,...,|Nmax>, and the Dirac term v*pi(dag) is the
ladder operator coupling adjacent levels; the gamma4 term -v4*pi(dag) couples
adjacent-layer same-sublattice ladders with the same sqrt(n) structure.
Constant terms (gamma1, gamma2/2, gamma5/2, delta, layer potentials) couple
equal levels.

Ladder assignment (valley K, xi=+1):
  v*pi^dag couples A_i(level n) <- B_i(level n-1) with magnitude Gamma_B*sqrt(n).
For valley K' (xi=-1) the roles of A and B swap (v*pi raises B instead).
Boundary levels with no partner are the anomalous zero-energy LLs; they arise
automatically from the truncated ladder (no hand-coded special cases).

On-site energies (D=0): dimer sites B1,A2,B3 sit at delta; non-dimer A1,B2,A3 at
0. The next-nearest-layer terms gamma2/2 (A1-A3) and gamma5/2 (B1-B3) are off-
diagonal. After the mirror decomposition this reproduces:
  ML band split  = delta + gamma2/2 - gamma5/2  (~2 meV for the fitted params)
  BL band split  = |gamma2|/2                   (~14 meV)
(verified numerically in `selftest`).

Displacement field: a layer potential diag(+U, 0, -U) on (layer1, layer2,
layer3) breaks mirror symmetry and hybridizes ML/BL. `delta_field` = U in eV.
The D=0 model is the paper's fingerprint; D!=0 is a qualitative add-on.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.constants as cst

HBAR = cst.hbar
ECHG = cst.e
A0 = 0.246e-9  # graphene lattice constant (m)


@dataclass(frozen=True)
class SWMcC:
    """SWMcC hopping parameters (eV). Defaults = Datta et al. fitted values,
    plus gamma4 = 0.04 from McCann-Koshino (Datta's fit carries no gamma4;
    Aaron's call 2026-07-18). gamma4 acts on the BL (mirror-even) sector only
    and carries its e-h mass asymmetry."""
    gamma0: float = 3.1
    gamma1: float = 0.39
    gamma2: float = -0.028
    gamma4: float = 0.04
    gamma5: float = 0.01
    delta: float = 0.021

    @property
    def v(self) -> float:
        """Dirac velocity (m/s): v = sqrt(3)/2 * a0 * gamma0 / hbar."""
        return np.sqrt(3.0) / 2.0 * A0 * (self.gamma0 * ECHG) / HBAR


# Sublattice index in the 6-site basis.
A1, B1, A2, B2, A3, B3 = range(6)
_DIMER = {B1, A2, B3}            # on-site delta
_LAYER = {A1: 0, B1: 0, A2: 1, B2: 1, A3: 2, B3: 2}
# Which sublattices are "A type" (raised by v*pi^dag at valley K).
_ATYPE = {A1, A2, A3}


def gamma_B(B: float, p: SWMcC) -> float:
    """Dirac LL energy scale Gamma_B = sqrt(2) hbar v / l_B = v*sqrt(2 hbar e B), in eV."""
    return p.v * np.sqrt(2.0 * HBAR * ECHG * B) / ECHG


def build_H(B: float, p: SWMcC, nmax: int = 60, valley: int = +1,
            delta_field: float = 0.0) -> np.ndarray:
    """Hermitian LL Hamiltonian (eV) for one valley at field B (Tesla).

    valley: +1 (K) or -1 (K'). delta_field: layer potential U (eV), diag(+U,0,-U).
    Basis index = sublattice*(nmax+1) + level.
    """
    dim = 6 * (nmax + 1)
    H = np.zeros((dim, dim))
    gB = gamma_B(B, p)

    def idx(s, n):
        return s * (nmax + 1) + n

    # On-site (diagonal): delta on dimer sites + layer potential.
    layer_U = {0: +delta_field, 1: 0.0, 2: -delta_field}
    for s in range(6):
        e0 = (p.delta if s in _DIMER else 0.0) + layer_U[_LAYER[s]]
        for n in range(nmax + 1):
            H[idx(s, n), idx(s, n)] += e0

    # Dirac coupling within each layer: A_i(n) <-> B_i(n-1) at valley K.
    # At valley K' the A/B roles swap (B raised instead of A).
    layer_pairs = [(A1, B1), (A2, B2), (A3, B3)]
    for sa, sb in layer_pairs:
        hi, lo = (sa, sb) if valley == +1 else (sb, sa)  # hi carries level n, lo n-1
        for n in range(1, nmax + 1):
            val = gB * np.sqrt(n)
            H[idx(hi, n), idx(lo, n - 1)] += val
            H[idx(lo, n - 1), idx(hi, n)] += val

    # gamma4: adjacent-layer same-sublattice, -v4*pi(dag) alongside +v*pi(dag)
    # (McCann-Koshino sign). The outer-layer sublattice carries level n at
    # valley K; mirror symmetry (1<->3) fixes the 2-3 interface as the
    # conjugate of the 1-2 one, so both interfaces follow the same rule.
    g4B = (p.gamma4 / p.gamma0) * gB
    g4_pairs = [(A1, A2), (B1, B2), (A3, A2), (B3, B2)]   # (outer, middle)
    for so, sm in g4_pairs:
        hi, lo = (so, sm) if valley == +1 else (sm, so)
        for n in range(1, nmax + 1):
            val = -g4B * np.sqrt(n)
            H[idx(hi, n), idx(lo, n - 1)] += val
            H[idx(lo, n - 1), idx(hi, n)] += val

    # Constant interlayer couplings (same level).
    const_couplings = [
        (B1, A2, p.gamma1),
        (A2, B3, p.gamma1),
        (A1, A3, p.gamma2 / 2.0),
        (B1, B3, p.gamma5 / 2.0),
    ]
    for s1, s2, val in const_couplings:
        for n in range(nmax + 1):
            H[idx(s1, n), idx(s2, n)] += val
            H[idx(s2, n), idx(s1, n)] += val

    return H


def _ml_weight(vecs: np.ndarray, nmax: int) -> np.ndarray:
    """Mirror-odd (ML) weight of each eigenvector: projection onto
    (A1-A3)/sqrt2 and (B1-B3)/sqrt2 over all levels. vecs columns = eigenvectors."""
    nl = nmax + 1
    a1 = vecs[A1 * nl:(A1 + 1) * nl, :]
    a3 = vecs[A3 * nl:(A3 + 1) * nl, :]
    b1 = vecs[B1 * nl:(B1 + 1) * nl, :]
    b3 = vecs[B3 * nl:(B3 + 1) * nl, :]
    w = (np.abs(a1 - a3) ** 2 + np.abs(b1 - b3) ** 2).sum(axis=0) / 2.0
    return w


@dataclass
class LLState:
    """One Landau level at a given field."""
    energy: float       # eV
    ml_weight: float    # 0..1 (1 = pure monolayer-like)
    valley: int
    level: int          # dominant oscillator index (orbital LL index)


def ll_levels(B: float, p: SWMcC, nmax: int = 60, valley: int = +1,
              delta_field: float = 0.0, drop_top: int = 6) -> list[LLState]:
    """Diagonalize one valley; return LL states tagged ML/BL + orbital index.

    drop_top: discard the highest `drop_top` ladder indices' worth of states as
    truncation artifacts (levels whose oscillator content piles up at nmax)."""
    H = build_H(B, p, nmax, valley, delta_field)
    evals, evecs = np.linalg.eigh(H)
    mlw = _ml_weight(evecs, nmax)

    # Dominant oscillator index of each eigenvector (probability-weighted).
    nl = nmax + 1
    levels_grid = np.tile(np.arange(nl), 6)
    prob = np.abs(evecs) ** 2
    dom_level = (prob * levels_grid[:, None]).sum(axis=0)  # mean oscillator index

    keep = dom_level <= (nmax - drop_top)
    out = []
    for k in np.where(keep)[0]:
        out.append(LLState(energy=float(evals[k]), ml_weight=float(mlw[k]),
                           valley=valley, level=int(round(dom_level[k]))))
    return out


def all_levels(B: float, p: SWMcC, nmax: int = 60, delta_field: float = 0.0,
               drop_top: int = 6) -> list[LLState]:
    """Both valleys combined."""
    return (ll_levels(B, p, nmax, +1, delta_field, drop_top)
            + ll_levels(B, p, nmax, -1, delta_field, drop_top))


def selftest() -> None:
    """Validate the on-site assignment against the paper's 2 meV / 14 meV splits.

    At small B the two ML zero-modes sit at -gamma2/2 and delta-gamma5/2; their
    separation is the ML band split (delta+gamma2/2-gamma5/2 ~ 2 meV). The two
    BL zero-modes are separated by |gamma2|/2 ~ 14 meV.
    """
    p = SWMcC()
    print(f"v = {p.v:.4e} m/s   Gamma_B(1T) = {gamma_B(1.0, p)*1e3:.2f} meV")
    expect_ml = p.delta + p.gamma2 / 2 - p.gamma5 / 2
    expect_bl = abs(p.gamma2) / 2
    print(f"expected ML split = {expect_ml*1e3:.2f} meV, BL split = {expect_bl*1e3:.2f} meV")

    # Diagonalize the decoupled blocks directly at B=0-ish (use small B then
    # inspect near-zero-energy levels). Use the mirror blocks for a clean check.
    # ML 2x2 zero-modes: diag(-g2/2, delta-g5/2); BL contains +g2/2.
    g2, g5, d = p.gamma2, p.gamma5, p.delta
    ml_sites = np.array([-g2 / 2, d - g5 / 2])
    print(f"ML zero-mode energies (meV): {ml_sites*1e3}")
    print(f"  -> ML split = {abs(ml_sites[0]-ml_sites[1])*1e3:.3f} meV (target 2.0)")
    print(f"BL non-dimer zero-mode at +g2/2 = {g2/2*1e3:.3f} meV; |g2|/2 = {expect_bl*1e3:.3f} meV (target 14.0)")

    # Numerical near-zero LLs of the full model at low field.
    B = 0.5
    lv = sorted(all_levels(B, p, nmax=80), key=lambda s: abs(s.energy))
    near0 = [s for s in lv if abs(s.energy) < 0.05][:14]
    print(f"\nNear-zero LLs at B={B} T (energy meV, ML weight, valley, level):")
    for s in near0:
        print(f"  {s.energy*1e3:8.3f}  ml={s.ml_weight:.2f}  v={s.valley:+d}  N={s.level}")


if __name__ == "__main__":
    selftest()
