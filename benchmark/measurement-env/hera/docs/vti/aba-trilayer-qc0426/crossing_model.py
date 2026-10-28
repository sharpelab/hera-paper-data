#!/usr/bin/env python3
"""
ABA-trilayer LL crossing model: energy spectrum -> density, crossing loci, and
calculated DOS(n, B) for direct overlay on a measured Landau fan.

Pipeline (Datta et al. Fig 2b / Fig 3a methodology):
  1. ll_spectrum.all_levels(B): LL energies per valley, tagged ML/BL + orbital N.
  2. fill to a Fermi energy -> carrier density n(E_F, B) via eB/h degeneracy,
     referenced to charge neutrality (n=0 at E_F=0).
  3. crossing loci: ML level N_M degenerate with a BL level -> a point (n, B);
     all crossings of one N_M trace a chain (parabola for N_M>=1, vertical for
     N_M=0).
  4. dos_map: broadened DOS remapped onto the (n, B) plane -> the calculated fan.

Density units: n in 1e12 cm^-2 throughout the public API (`*_n12`).
"""
from __future__ import annotations

import numpy as np
import scipy.constants as cst

# ll_spectrum moved to hera/models/trilayer_fs_count (2026-07-16); make it importable
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "..", "..", "models", "trilayer_fs_count"))
from ll_spectrum import SWMcC, all_levels, ll_levels, LLState

E = cst.e
H = cst.h
SPIN_DEG = 2.0           # spin degeneracy (no Zeeman at low B)
M2_PER_CM2 = 1e4         # 1 cm^-2 = 1e4 m^-2 ... n[m^-2] = n[cm^-2]*1e4


def deg_per_area(B: float) -> float:
    """LL degeneracy per unit area per (spin,valley,orbital): eB/h  [m^-2]."""
    return E * B / H


def n12_from_density(n_m2: float) -> float:
    """m^-2 -> 1e12 cm^-2."""
    return n_m2 / M2_PER_CM2 / 1e12


# ---------------------------------------------------------------------------
# Filling: density as a function of Fermi energy at fixed B
# ---------------------------------------------------------------------------

def density_of_EF(EF: float, levels: list[LLState], B: float) -> float:
    """Carrier density (m^-2, signed) at Fermi energy EF, referenced to CNP.

    n = SPIN_DEG * (eB/h) * [ #(E_k < EF) - #(E_k < 0) ]."""
    g = SPIN_DEG * deg_per_area(B)
    en = np.array([s.energy for s in levels])
    n_below_EF = int(np.count_nonzero(en < EF))
    n_below_0 = int(np.count_nonzero(en < 0.0))
    return g * (n_below_EF - n_below_0)


def filling_curve(levels: list[LLState], B: float):
    """Return (sorted energies, cumulative density-at-each-level n12) for one B.

    n_k = density when E_F has just passed level k (referenced to CNP)."""
    en = np.sort(np.array([s.energy for s in levels]))
    g = SPIN_DEG * deg_per_area(B)
    n_below_0 = int(np.count_nonzero(en < 0.0))
    # after passing level k (0-indexed), #below = k+1
    nk = g * (np.arange(1, len(en) + 1) - n_below_0)
    return en, n12_from_density(nk)


# ---------------------------------------------------------------------------
# Crossing loci: ML x BL level coincidences -> (n, B) points
# ---------------------------------------------------------------------------

def crossing_loci(p: SWMcC, B_grid, nmax: int = 60, delta_field: float = 0.0,
                  ml_thresh: float = 0.6, e_window: float = 0.5,
                  emax: float = 0.18):
    """Find ML x BL level coincidences across B_grid.

    Returns list of dicts: {B, n12, energy, N_M, N_B}. A crossing is an ML-like
    level (ml_weight > ml_thresh) and a BL-like level (< 1-ml_thresh) within
    `e_window` * mean-level-spacing in energy. Restricted to |E| < emax eV.
    """
    out = []
    for B in B_grid:
        levels = all_levels(B, p, nmax, delta_field)
        levels = [s for s in levels if abs(s.energy) < emax]
        if not levels:
            continue
        en_all = np.sort([s.energy for s in levels])
        spacing = np.median(np.diff(en_all)) if len(en_all) > 1 else 1e-3
        tol = e_window * spacing
        ml = [s for s in levels if s.ml_weight > ml_thresh]
        bl = [s for s in levels if s.ml_weight < (1 - ml_thresh)]
        # density lookup for this B
        for sm in ml:
            for sb in bl:
                if sm.valley != sb.valley:
                    continue
                gap = abs(sm.energy - sb.energy)
                if gap < tol:
                    Ecross = 0.5 * (sm.energy + sb.energy)
                    n_m2 = density_of_EF(Ecross, levels, B)
                    out.append(dict(B=float(B), n12=n12_from_density(n_m2),
                                    energy=float(Ecross), N_M=sm.level,
                                    N_B=sb.level, valley=sm.valley,
                                    gap=float(gap)))
    return out


# ---------------------------------------------------------------------------
# ML-level filling trajectories: where ML level N_M sits in (n, B)
# ---------------------------------------------------------------------------

def ml_trajectories(p: SWMcC, B_grid, nmax: int = 130, delta_field: float = 0.0,
                    ml_thresh: float = 0.6, nm_max: int = 4, emax: float = 0.16):
    """Density trajectory of each electron-side ML Landau level vs B.

    A crossing chain (Datta Fig 2b) is the locus where ML level N_M coincides
    with BL levels; equivalently it is the carrier density at which ML level
    N_M sits as a function of B (its kinks are the BL crossings). For each B we
    pick the ML-like levels (ml_weight > thresh) with E>0, order them by energy
    as N_M = 0,1,2,..., and record n(E_ML, B).

    Returns {N_M: (n12_arr, B_arr)} for the electron side.
    """
    traj = {nm: ([], []) for nm in range(nm_max + 1)}
    for B in B_grid:
        levels = all_levels(B, p, nmax, delta_field)
        ml_pos = sorted([s for s in levels
                         if s.ml_weight > ml_thresh and 0 <= s.energy < emax],
                        key=lambda s: s.energy)
        # two valleys per orbital N_M: average their densities
        for nm in range(nm_max + 1):
            sel = ml_pos[2 * nm:2 * nm + 2]
            if not sel:
                break
            dens = [density_of_EF(s.energy, levels, B) for s in sel]
            traj[nm][0].append(n12_from_density(float(np.mean(dens))))
            traj[nm][1].append(float(B))
    return {nm: (np.array(v[0]), np.array(v[1])) for nm, v in traj.items() if v[0]}


# ---------------------------------------------------------------------------
# Calculated DOS on the (n, B) plane  (Datta Fig 2b analog)
# ---------------------------------------------------------------------------

def dos_map(p: SWMcC, n12_grid, B_grid, nmax: int = 60, delta_field: float = 0.0,
            broaden_meV: float = 1.2):
    """Calculated DOS(n, B). For each B, broaden LLs in energy, remap E->n.

    Returns 2D array shape (len(B_grid), len(n12_grid)).
    """
    out = np.zeros((len(B_grid), len(n12_grid)))
    gE = broaden_meV * 1e-3
    for i, B in enumerate(B_grid):
        levels = all_levels(B, p, nmax, delta_field)
        en, n12 = filling_curve(levels, B)
        # E_F as a function of target n via the (monotonic) filling curve.
        # n12 is the density just after each level; invert to get E(n).
        # DOS(n) ~ sum of gaussians in n centered where E_F crosses each level.
        # Use n-position of each level = n12[k] - 0.5*step (mid of its plateau).
        g = SPIN_DEG * deg_per_area(B)
        dn12 = n12_from_density(g)               # density per level
        n_centers = n12 - 0.5 * dn12             # center of each LL's contribution
        # width in density: convert energy broadening via local dn/dE.
        # local dn/dE ~ g / spacing; use a floor to avoid div by zero.
        spacing = np.gradient(en)
        spacing = np.where(np.abs(spacing) < 1e-5, 1e-5, spacing)
        sigma_n = np.abs(n12_from_density(g) * gE / spacing)
        sigma_n = np.clip(sigma_n, 0.02, 1.0)
        for nc, sg in zip(n_centers, sigma_n):
            out[i, :] += np.exp(-0.5 * ((n12_grid - nc) / sg) ** 2)
    return out


# ---------------------------------------------------------------------------
# DOS at the Fermi level vs (n, B)  — the "what Rxx sees" observable
# ---------------------------------------------------------------------------
#
# Rxx tracks the DOS at E_F: high DOS(E_F) = compressible/dissipative = Rxx
# MAXIMUM (bright); a gap at E_F = incompressible = Rxx MINIMUM (dark). A
# level coincidence (ML x BL) is a local DOS(E_F) maximum -> bright crossing
# chain. A gap coincidence is a local DOS(E_F) minimum -> DARK arc. So to test
# whether the measured DARK arcs are an ABA signature we compare them to the
# minima (not the maxima) of this map.

def dos_at_fermi(p: SWMcC, n12_grid, B_grid, nmax: int = 150,
                 delta_field: float = 0.0, broaden_meV: float = 1.2,
                 e_lo: float = -0.06, e_hi: float = 0.30, nE: int = 3000):
    """DOS at the Fermi level as a function of (n, B).

    For each B: build DOS(E) = sum of Lorentzian-broadened LLs (weight eB/h per
    spin), integrate to n(E) (CNP-referenced), then resample DOS onto the target
    density grid via E_F(n). Returns array (len(B_grid), len(n12_grid)).
    """
    Egrid = np.linspace(e_lo, e_hi, nE)
    gamma = broaden_meV * 1e-3
    out = np.zeros((len(B_grid), len(n12_grid)))
    for i, B in enumerate(B_grid):
        levels = all_levels(B, p, nmax, delta_field)
        en = np.array([s.energy for s in levels])
        W = SPIN_DEG * deg_per_area(B)                       # m^-2 per level
        # DOS(E) [m^-2 / eV]
        diff = Egrid[:, None] - en[None, :]
        dos_E = (W / np.pi) * (gamma / (diff ** 2 + gamma ** 2)).sum(axis=1)
        # n(E) = integral of DOS, referenced to CNP (E=0)
        nE_cum = np.concatenate([[0.0], np.cumsum(0.5 * (dos_E[1:] + dos_E[:-1])
                                                  * np.diff(Egrid))])
        i0 = int(np.argmin(np.abs(Egrid)))
        n12_E = n12_from_density(nE_cum - nE_cum[i0])
        # resample DOS onto target density (n12_E is monotonic increasing)
        out[i, :] = np.interp(n12_grid, n12_E, dos_E, left=np.nan, right=np.nan)
    return out


def _local_extrema(y):
    """Indices of interior local minima and maxima of 1D array y (NaN-safe)."""
    mn, mx = [], []
    for k in range(1, len(y) - 1):
        a, b, c = y[k - 1], y[k], y[k + 1]
        if not np.isfinite(a + b + c):
            continue
        if b < a and b <= c:
            mn.append(k)
        elif b > a and b >= c:
            mx.append(k)
    return np.array(mn, int), np.array(mx, int)


def bright_dark_loci(dos_nB, n12_grid, B_grid, prominence_frac=0.12):
    """Extract per-B bright (DOS max) and dark (DOS min) loci from a DOS(n,B)
    map, keeping extrema whose prominence exceeds `prominence_frac` of the row
    range. Returns two lists of (n12, B, prominence)."""
    bright, dark = [], []
    for i, B in enumerate(B_grid):
        row = dos_nB[i, :]
        if not np.isfinite(row).any():
            continue
        rng = np.nanmax(row) - np.nanmin(row)
        if rng <= 0:
            continue
        mn, mx = _local_extrema(row)
        # prominence vs local neighbourhood (simple: depth relative to range)
        for k in mx:
            nb = row[max(0, k - 25):k + 25]
            prom = (row[k] - np.nanmin(nb)) / rng
            if prom > prominence_frac:
                bright.append((n12_grid[k], B, prom))
        for k in mn:
            nb = row[max(0, k - 25):k + 25]
            prom = (np.nanmax(nb) - row[k]) / rng
            if prom > prominence_frac:
                dark.append((n12_grid[k], B, prom))
    return bright, dark


# ---------------------------------------------------------------------------
# Spectrum E(B) for Fig 3a validation
# ---------------------------------------------------------------------------

def spectrum_vs_B(p: SWMcC, B_grid, nmax: int = 60, delta_field: float = 0.0,
                  emax: float = 0.18):
    """Return list per B of (energies, ml_weights) for plotting E vs B."""
    res = []
    for B in B_grid:
        levels = all_levels(B, p, nmax, delta_field)
        levels = [s for s in levels if abs(s.energy) < emax]
        en = np.array([s.energy for s in levels])
        ml = np.array([s.ml_weight for s in levels])
        res.append((en, ml))
    return res
