from collections.abc import Sequence
from typing import Any

import numpy as np
import numpy.typing as npt
from sweep import raster

_EPS0 = 8.8541878128e-12  # F/m (CODATA 2018)
_E = 1.602176634e-19  # C (exact)


def stack_capacitance(layers: Sequence[tuple[float, float]]) -> float:
    """Areal capacitance (F/m^2) of a series dielectric stack.

    Args:
        layers: ``(thickness_nm, kappa)`` per layer, in series — e.g.
            ``[(12, 3)]`` for 12 nm of hBN, or ``[(12, 3), (285, 3.9)]``
            for hBN backed by SiO2. Zero-thickness layers contribute
            nothing.

    Returns:
        Capacitance per unit area (F/m^2).
    """
    total = 0.0
    for t_nm, kappa in layers:
        total += (t_nm * 1e-9) / kappa
    return _EPS0 / total


def calc_nD(
    Vtg: Any,
    Vbg: Any,
    c_tg: float,
    c_bg: float,
    n_offset: float = 0.0,
    D_offset: float = 0.0,
) -> tuple[Any, Any]:
    """Convert gate voltages to carrier density and displacement field.

    Canonical (n, D) conversion, parametrized by areal gate capacitances
    (:func:`stack_capacitance`) — the quantity calibration actually
    refines: a fitted CNP-line slope dVtg/dVbg is ``-c_bg/c_tg``, and a
    quantum-Hall lever-arm check sets the absolute scale.

    Args:
        Vtg: Top gate voltage (V).
        Vbg: Back gate voltage (V).
        c_tg: Top gate areal capacitance (F/m^2).
        c_bg: Back gate areal capacitance (F/m^2).
        n_offset: Density offset (10^12 cm^-2).
        D_offset: Displacement field offset (V/nm).

    Returns:
        (n, D): n in 10^12 cm^-2, D in V/nm.
    """
    n = (c_tg * Vtg + c_bg * Vbg) / _E * 1e-16 + n_offset
    D = 0.5 * (c_tg * Vtg - c_bg * Vbg) / _EPS0 * 1e-9 + D_offset
    return n, D


def calc_gate_voltages(
    n: Any,
    D: Any,
    c_tg: float,
    c_bg: float,
    n_offset: float = 0.0,
    D_offset: float = 0.0,
) -> tuple[Any, Any]:
    """Convert (n, D) to gate voltages — inverse of :func:`calc_nD`.

    Args:
        n: Carrier density (10^12 cm^-2).
        D: Displacement field (V/nm).
        c_tg: Top gate areal capacitance (F/m^2).
        c_bg: Back gate areal capacitance (F/m^2).
        n_offset: Density offset (10^12 cm^-2).
        D_offset: Displacement field offset (V/nm).

    Returns:
        (Vtg, Vbg) gate voltages (V). Scalar args return Python floats
        (so ``float(Vtg)`` is unnecessary); array args return arrays.
    """
    n = np.asarray(n, dtype=float)
    D = np.asarray(D, dtype=float)
    n_si = (n - n_offset) * 1e16  # m^-2
    D_si = (D - D_offset) * 1e9  # V/m
    Vtg = (0.5 * _E * n_si + _EPS0 * D_si) / c_tg
    Vbg = (0.5 * _E * n_si - _EPS0 * D_si) / c_bg
    if Vtg.ndim == 0:
        return float(Vtg), float(Vbg)
    return Vtg, Vbg


def calculate_gate_voltages(
    n: Any,
    D: Any,
    dtg: float = 16,
    dbg: float = 25.5,
    ep: float = 3,
) -> tuple[Any, Any]:
    """Convert carrier density and displacement field to gate voltages.

    Single-dielectric special case of :func:`calc_gate_voltages` (both
    gates pure hBN, no offsets), parametrized by thickness. Prefer the
    capacitance form for new work.

    Args:
        n: Carrier density (10^12 cm^-2).
        D: Displacement field (V/nm).
        dtg: Top gate dielectric thickness (nm).
        dbg: Back gate dielectric thickness (nm).
        ep: Dielectric constant of hBN.

    Returns:
        (Vtg, Vbg) gate voltages.
    """
    return calc_gate_voltages(
        n, D, stack_capacitance([(dtg, ep)]), stack_capacitance([(dbg, ep)])
    )


def calculate_n_D(
    Vtg: Any,
    Vbg: Any,
    dtg: float = 16,
    dbg: float = 25.5,
    ep: float = 3,
) -> tuple[Any, Any]:
    """Convert gate voltages to carrier density and displacement field.

    Single-dielectric special case of :func:`calc_nD` (both gates pure
    hBN, no offsets), parametrized by thickness. Prefer the capacitance
    form for new work.

    Args:
        Vtg: Top gate voltage (V).
        Vbg: Back gate voltage (V).
        dtg: Top gate dielectric thickness (nm).
        dbg: Back gate dielectric thickness (nm).
        ep: Dielectric constant of hBN.

    Returns:
        (n, D): n in 10^12 cm^-2, D in V/nm.
    """
    return calc_nD(
        Vtg, Vbg, stack_capacitance([(dtg, ep)]), stack_capacitance([(dbg, ep)])
    )


def comment_to_gates(comment: str, delim: str = ":") -> tuple[float, float]:
    """Parse a comment string to extract gate voltages.

    Expects format like ``"label: (Vtg, Vbg)"``.

    Returns:
        (Vtg, Vbg) as floats.
    """
    parts = comment.split(delim)
    values_part = parts[-1].strip()
    values = values_part.strip("()").split(",")
    Vtg = float(values[0].strip())
    Vbg = float(values[1].strip())
    return Vtg, Vbg


def _segments_cross(
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    p4: tuple[float, float],
) -> bool:
    """True if segment p1-p2 strictly crosses segment p3-p4."""

    def _orient(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    d1 = _orient(p3, p4, p1)
    d2 = _orient(p3, p4, p2)
    d3 = _orient(p1, p2, p3)
    d4 = _orient(p1, p2, p4)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and d1 != 0 and d2 != 0 and d3 != 0 and d4 != 0


def _is_simple_polygon(verts: npt.NDArray[np.floating]) -> bool:
    """True if no pair of non-adjacent edges of the closed polygon crosses."""
    n = len(verts)
    pts = [(float(v[0]), float(v[1])) for v in verts]
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if _segments_cross(pts[i], pts[(i + 1) % n], pts[j], pts[(j + 1) % n]):
                return False
    return True


def _nD_vertices_to_gate(
    nD_vertices: npt.NDArray[np.floating],
    dtg: float,
    dbg: float,
    ep: float,
) -> npt.NDArray[np.floating]:
    """Convert (n, D) polygon vertices to a (Vtg, Vbg) vertex array, asserting
    the gate-space polygon is non-self-intersecting (which the ray-casting in
    sweep.raster.* requires)."""
    arr = np.asarray(nD_vertices)
    Vtgs, Vbgs = calculate_gate_voltages(arr[:, 0], arr[:, 1], dtg=dtg, dbg=dbg, ep=ep)
    gate_verts = np.column_stack([Vtgs, Vbgs])
    assert _is_simple_polygon(gate_verts), (
        "gate-space polygon is self-intersecting; check (n, D) vertex order"
    )
    return gate_verts


def pcolorize_nD(
    zs: npt.NDArray[np.floating],
    nD_vertices: npt.NDArray[np.floating],
    nx: int,
    ny: int,
    *,
    fast_axis: int = 0,
    rev_x: bool = False,
    rev_y: bool = False,
    dtg: float = 16,
    dbg: float = 25.5,
    ep: float = 3,
) -> tuple[
    npt.NDArray[np.floating],
    npt.NDArray[np.floating],
    npt.NDArray[np.floating],
]:
    """Reproject a polygon-rasterized gatemap onto a regular (n, D) mesh for ``pcolormesh``.

    The polygon is given in (n, D) space; this helper converts the vertices to
    (Vtg, Vbg) via :func:`calculate_gate_voltages`, calls
    :func:`sweep.raster.pcolorize_data` to bin ``zs`` onto a regular
    gate-voltage mesh, then converts the mesh back to (n, D) via
    :func:`calculate_n_D`. Cells outside the polygon are NaN.

    ``fast_axis=0`` matches the convention used in every observed
    ``multimegasweep`` analysis cell so far; pass ``fast_axis=1`` if your sweep
    inverted the loop order.

    ``rev_y`` defaults to ``False`` (Isaac's convention); Aaron's RPL_19 cells
    pass ``rev_y=True``.

    Args:
        zs: 1D array of measured values, in the order produced by the
            ``multimegasweep`` over the rasterized polygon.
        nD_vertices: ``(N, 2)`` array of polygon vertices in (n, D) space.
        nx: Number of grid points along the (Vtg) fast axis.
        ny: Number of grid points along the (Vbg) slow axis.
        fast_axis: 0 if Vtg is the fast (inner) axis, 1 if Vbg is.
        rev_x: Reverse the gate-space x-axis sweep direction.
        rev_y: Reverse the gate-space y-axis sweep direction.
        dtg: Top gate dielectric thickness (nm).
        dbg: Back gate dielectric thickness (nm).
        ep: hBN dielectric constant.

    Returns:
        ``(n_mat, D_mat, zs_mat)`` each of shape ``(ny, nx)``, ready for
        ``ax.pcolormesh(n_mat, D_mat, zs_mat)``. Exterior cells are NaN.
    """
    gate_verts = _nD_vertices_to_gate(nD_vertices, dtg=dtg, dbg=dbg, ep=ep)
    xs_mat, ys_mat, zs_mat = raster.pcolorize_data(
        zs, gate_verts, nx, ny, fast_axis, rev_x=rev_x, rev_y=rev_y
    )
    n_mat, D_mat = calculate_n_D(xs_mat, ys_mat, dtg=dtg, dbg=dbg, ep=ep)
    return n_mat, D_mat, zs_mat


def triangulate_nD(
    nD_vertices: npt.NDArray[np.floating],
    nx: int,
    ny: int,
    *,
    fast_axis: int = 0,
    rev_x: bool = False,
    rev_y: bool = False,
    dtg: float = 16,
    dbg: float = 25.5,
    ep: float = 3,
) -> tuple[
    npt.NDArray[np.floating],
    npt.NDArray[np.floating],
    npt.NDArray[np.floating],
    npt.NDArray[np.floating],
]:
    """Compute the (n, D) and (Vtg, Vbg) coordinates of a polygon-rasterized scan.

    Use when the underlying sweep was a ``multimegasweep`` over a polygon and
    the analyst wants ``mtri.Triangulation`` + ``tripcolor(shading="gouraud")``
    rather than rectangular ``pcolormesh``. Returns coordinates only — the
    caller pairs them with their own ``zs`` array (which is already shaped per
    the rasterized point order)::

        n_pts, D_pts, _, _ = triangulate_nD(verts, nx, ny)
        tri = mtri.Triangulation(n_pts, D_pts)
        ax.tripcolor(tri, zs, shading="gouraud")

    ``fast_axis=0`` matches the convention used in every observed analysis
    cell so far; pass ``fast_axis=1`` if your sweep inverted the loop order.
    ``rev_y`` defaults to ``False`` (Isaac's convention).

    Args:
        nD_vertices: ``(N, 2)`` array of polygon vertices in (n, D) space.
        nx: Number of grid points along the (Vtg) fast axis.
        ny: Number of grid points along the (Vbg) slow axis.
        fast_axis: 0 if Vtg is the fast (inner) axis, 1 if Vbg is.
        rev_x: Reverse the gate-space x-axis sweep direction.
        rev_y: Reverse the gate-space y-axis sweep direction.
        dtg: Top gate dielectric thickness (nm).
        dbg: Back gate dielectric thickness (nm).
        ep: hBN dielectric constant.

    Returns:
        ``(n, D, Vtg, Vbg)`` each of length ``M`` where ``M`` is the number of
        in-polygon raster points (equal to ``len(zs)``).
    """
    gate_verts = _nD_vertices_to_gate(nD_vertices, dtg=dtg, dbg=dbg, ep=ep)
    xs, ys = raster.rasterize(
        gate_verts, nx, ny, fast_axis, rev_x=rev_x, rev_y=rev_y
    )
    n_pts, D_pts = calculate_n_D(xs, ys, dtg=dtg, dbg=dbg, ep=ep)
    return n_pts, D_pts, xs, ys
