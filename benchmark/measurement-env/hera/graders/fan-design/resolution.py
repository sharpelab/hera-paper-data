# Implements Aaron's rulings on the wiki page "Fan-design scorer"
# https://wiki.sharpelab.science/doc/fan-design-scorer-jex5U02n3W  (revision 108, 2026-09-19)
"""Fraction of a Landau fan's area whose field sampling resolves the Luttinger frequency.

The fan is the rectangle [n_lo, n_hi] x [b_cut, B_max], measured in 1/B: the axis the FFT
reads, so a tesla at low field carries the periods it holds.  A point (n, B) is resolved when
the B interval it sits in holds at least m rows per period of F_L(n) = (h / g e)|n|:

    rows_per_period = 1 / (F_L(n) * (1/B_i - 1/B_{i+1}))

b_cut is a per-device low-field cutoff.  Rows below it are ignored, so going lower in field
costs nothing; a fan that starts above it has the gap counted as unresolved, so a high
B_min cannot buy a better fraction.  Density is treated as continuous: the column count is
not scored.

The rectangle's density range and top field are the design's own, so the fraction rises
when either is drawn in.  Read it next to where they sit against the claim (`coverage`,
and the grader's n_max and B_max ratios).

The fraction is a number to report, not a verdict.  The low-density side of any sane fan
resolves, so values crowd toward 1.
"""
from __future__ import annotations

import numpy as np

H_OVER_E_T_M2 = 4.135667696e-15  # h/e in T*m^2
CM2_PER_M2 = 1e4


def luttinger_frequency(n_cm2, g: int = 4):
    """F = (h / g e) * |n|, n in cm^-2, F in T.  g = 4 -> 10.3 T per 1e12 cm^-2."""
    return H_OVER_E_T_M2 / g * np.abs(n_cm2) * CM2_PER_M2


def _fraction_below(n_lo: float, n_hi: float, n_crit: np.ndarray) -> np.ndarray:
    """Share of the density range [n_lo, n_hi] with |n| <= n_crit, per element of n_crit."""
    overlap = np.minimum(n_hi, n_crit) - np.maximum(n_lo, -n_crit)
    return np.clip(overlap, 0.0, None) / (n_hi - n_lo)


def resolved_fraction(B, n_lo: float, n_hi: float, *, b_cut: float, g: int = 4, m: float = 3.0,
                      measure: str = "invB") -> float:
    """Area fraction of [n_lo, n_hi] x [b_cut, B_max] sampled at >= m rows per period.

    B       : field setpoints in tesla, any order.
    n_lo/hi : density range in cm^-2 (signed; a range through zero counts both sides).
    b_cut   : low-field cutoff in tesla.
    measure : 'invB' weights the field axis in 1/B, 'B' in tesla.
    """
    B = np.unique(np.asarray(B, float))
    if B.size < 2 or B[-1] <= b_cut:
        return 0.0
    lo, hi = B[:-1], B[1:]
    with np.errstate(divide="ignore"):
        step_invB = 1.0 / lo - 1.0 / hi
    n_crit = 1.0 / (m * step_invB * luttinger_frequency(1.0, g))
    resolved = _fraction_below(n_lo, n_hi, n_crit)

    lo_w, hi_w = np.maximum(lo, b_cut), np.maximum(hi, b_cut)
    if measure == "invB":
        weight, total = 1.0 / lo_w - 1.0 / hi_w, 1.0 / b_cut - 1.0 / B[-1]
    else:
        weight, total = hi_w - lo_w, B[-1] - b_cut
    return min(1.0, float(np.sum(weight * resolved) / total))


def coverage(n_lo: float, n_hi: float, w_lo: float, w_hi: float) -> dict:
    """The fan's density range against the claim window [w_lo, w_hi], both as shares of the window."""
    width = w_hi - w_lo
    covered = max(0.0, min(n_hi, w_hi) - max(n_lo, w_lo))
    return {"covered_fraction": covered / width, "outside_fraction": ((n_hi - n_lo) - covered) / width}


def worst_column(B, n_lo: float, n_hi: float, *, b_cut: float, g: int = 4, m: float = 3.0) -> dict:
    """The highest-|n| column above the cutoff: its thinnest sampling, and where it resolves.

    resolved_from_T is the field above which every interval holds m rows per period: the
    axis's first row above the cutoff when all do, None when the top interval does not.
    """
    B = np.unique(np.asarray(B, float))
    F = float(luttinger_frequency(max(abs(n_lo), abs(n_hi)), g))
    lo, hi = B[:-1], B[1:]
    inside = hi > b_cut
    if not inside.any():
        return {"F_L_T": F, "rows_per_period_min": None, "resolved_from_T": None}
    with np.errstate(divide="ignore"):
        rpp = 1.0 / (F * (1.0 / lo[inside] - 1.0 / hi[inside]))
    failing = np.flatnonzero(rpp < m)
    if failing.size == 0:
        resolved_from = max(float(B[0]), b_cut)
    elif failing[-1] == rpp.size - 1:
        resolved_from = None
    else:
        resolved_from = float(hi[inside][failing[-1]])
    return {"F_L_T": F, "rows_per_period_min": float(rpp.min()), "resolved_from_T": resolved_from}
