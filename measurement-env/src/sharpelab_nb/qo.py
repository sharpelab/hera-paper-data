"""Quantum-oscillation analysis pipeline: background subtraction, 1/B
interpolation, and FFT vs Landau-fan filling fraction.

Lifted from cell 125 of ``aaron/RPL_19/20260112_ana.ipynb`` with cleanups:
- Bare ``except:`` dispatch in the polynomial-removal path is replaced with
  explicit ``ndim`` dispatch.
- Polynomial degree is now a kwarg (``degree=5`` default) instead of being
  baked into the function name (Isaac uses ``degree=4``).
- ``find_1d_peaks`` returns a list, not a single-use ``zip`` iterator.
- ``h``, ``e`` come from :mod:`scipy.constants` rather than inline literals.
- ``find_dR_div_R``'s parameters are now keyword-only.

**Units convention:** carrier density ``n`` is given in units of
``10^12 cm^-2`` throughout (parameter name ``n_per_cm2_e12``). The ``1E16``
factor in the FFT-frequency normalization converts to SI: ``1 cm^-2 =
1E4 m^-2``, so ``n_per_cm2_e12 * 1E16`` is the density in ``m^-2``.
"""

import numpy as np
import numpy.typing as npt
import scipy.fft
from scipy.constants import e, h
from scipy.interpolate import CubicSpline
from scipy.signal import find_peaks
from scipy.signal.windows import hann

_PHI_0 = h / e


def remove_polynomial_background(
    B: npt.NDArray[np.floating],
    Rxx: npt.NDArray[np.floating],
    *,
    degree: int = 5,
) -> npt.NDArray[np.floating]:
    """Subtract a degree-N polynomial background from Rxx(B) at each carrier
    density column.

    Aaron's RPL_19 notebooks use ``degree=5``; Isaac's b1c2 fan blocks use
    ``degree=4``. Choose per analyst preference.

    Behavior change vs the inline form (cell 125, ``20260112_ana.ipynb``):
    the inline ``except:`` branch on the 1D path subtracted ``np.nanmean``
    from the result, while the 2D branch did not — looked like an oversight,
    so this lift applies the mean subtraction to **both** branches.

    Args:
        B: Magnetic field, shape ``(N,)``.
        Rxx: Longitudinal resistance. Either ``(N,)`` (1D) or ``(N, M)``
            (2D, M density columns).
        degree: Polynomial degree. Default 5 (Aaron's convention).

    Returns:
        Background-subtracted Rxx, same shape as input. NaN-aware fit (skips
        non-finite samples in B or Rxx).
    """
    if Rxx.ndim == 2:
        new_Rxx = np.zeros(Rxx.shape)
        for i in range(Rxx.shape[1]):
            col = Rxx[:, i]
            idx = np.isfinite(col) & np.isfinite(B)
            coeff = np.polyfit(B[idx], col[idx], degree)
            fit = np.polyval(coeff, B)
            cleaned = col - fit
            cleaned -= np.nanmean(cleaned)
            new_Rxx[:, i] = cleaned
        return new_Rxx
    idx = np.isfinite(Rxx) & np.isfinite(B)
    coeff = np.polyfit(B[idx], Rxx[idx], degree)
    fit = np.polyval(coeff, B)
    cleaned = Rxx - fit
    cleaned -= np.nanmean(cleaned)
    return cleaned


def interp_inv_b(
    B: npt.NDArray[np.floating],
    Rxx: npt.NDArray[np.floating],
    nx: int = 400,
) -> tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]:
    """Cubic-spline interpolate Rxx onto a uniform 1/B grid.

    Required preprocessing for the FFT — ``scipy.fft.fft`` assumes evenly
    spaced samples, which Rxx(B) sweeps don't naturally produce in 1/B.

    Args:
        B: Magnetic field, shape ``(N,)``. Must be monotonic and non-zero
            (positive or negative; 1/B is what gets resampled).
        Rxx: Either ``(N,)`` or ``(N, M)``. Resampled along axis 0.
        nx: Number of points on the uniform 1/B grid. Default 400.

    Returns:
        ``(inv_b, Rxx_interp)`` where ``inv_b`` is shape ``(nx,)`` with
        constant spacing, and ``Rxx_interp`` is shape ``(nx,)`` or
        ``(nx, M)`` to match the input's leading axis.
    """
    inv_b = 1.0 / B
    order = np.argsort(inv_b)
    inv_b_sorted = inv_b[order]
    Rxx_sorted = Rxx[order, ...]

    inv_b_grid = np.linspace(inv_b_sorted[0], inv_b_sorted[-1], nx)
    cs = CubicSpline(inv_b_sorted, Rxx_sorted, axis=0)
    return inv_b_grid, cs(inv_b_grid)


def fft_vs_filling_2d(
    inv_b: npt.NDArray[np.floating],
    Rxx: npt.NDArray[np.floating],
    n_per_cm2_e12: npt.NDArray[np.floating],
    *,
    padding: int = 0,
    degeneracy: int = 4,
) -> tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]:
    """FFT of Rxx(1/B) per carrier-density column, normalized to filling
    fraction.

    For each column of ``Rxx``, applies a Hann window, optional zero-pads,
    runs ``scipy.fft.fft``, and rescales the frequency axis to filling
    fraction ``f / (phi_0 * n * degeneracy)``.

    **Units:** ``n_per_cm2_e12`` is the carrier density in units of
    ``10^12 cm^-2``. The body multiplies by ``1E16`` to convert to SI
    (``m^-2``).

    Args:
        inv_b: Uniformly spaced 1/B grid, shape ``(N,)``. Use
            :func:`interp_inv_b`.
        Rxx: Background-subtracted Rxx, shape ``(N, M)``.
        n_per_cm2_e12: Carrier density per column, shape ``(M,)``,
            in ``10^12 cm^-2``.
        padding: Zero-padding multiplier on each side of the FFT input.
            ``0`` means no padding; ``k`` adds ``k * N`` zeros on each side.
        degeneracy: Spin x valley filling factor (default 4 for graphene).

    Returns:
        ``(psd, freq)`` both shape ``((2 * N * padding) + N, M)``.
        ``psd`` is normalized so its global max is 1. ``freq`` is in units
        of filling fraction.
    """
    bstep = inv_b[1] - inv_b[0]
    sy, sx = Rxx.shape
    window = hann(sy)

    fft_out = np.zeros(((2 * sy * padding) + sy, sx))
    freq_out = np.zeros(((2 * sy * padding) + sy, sx))
    for ni in range(sx):
        col = Rxx[:, ni]
        windowed = np.pad(col * window, (sy * padding, sy * padding))
        col_fft = np.abs(scipy.fft.fft(windowed))
        freq = scipy.fft.fftfreq(windowed.size, d=bstep)
        fft_out[:, ni] = col_fft
        freq_out[:, ni] = freq / (_PHI_0 * n_per_cm2_e12[ni] * 1e16 * degeneracy)

    psd = fft_out**2
    psd = psd / np.amax(psd)
    return psd, freq_out


def fft_vs_filling_1d(
    inv_b: npt.NDArray[np.floating],
    Rxx: npt.NDArray[np.floating],
    n_per_cm2_e12: float,
    *,
    padding: int = 0,
    degeneracy: int = 4,
) -> tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]:
    """1D variant of :func:`fft_vs_filling_2d`.

    **Note on the frequency axis:** the inline cell-125 ``make_vec_fft`` and
    ``make_mat_fft`` use *reciprocal* frequency-axis conventions: the 1D form
    is ``(1 / freq_T) * phi_0 * n / degeneracy`` (so the standard SdH peak at
    ``B_F = phi_0 * n / degeneracy`` lands at exactly 1), while the 2D form
    is ``freq_T / (phi_0 * n * degeneracy)``. This lift preserves both
    behaviors as-is to avoid silently shifting downstream interpretation;
    callers should not expect the two to share an axis.

    Returns ``inf`` at the freq=0 bin (preserved from the original).

    Args:
        inv_b: Uniformly spaced 1/B grid, shape ``(N,)``.
        Rxx: Background-subtracted Rxx, shape ``(N,)``.
        n_per_cm2_e12: Carrier density (scalar), in ``10^12 cm^-2``.
        padding: Zero-padding multiplier.
        degeneracy: Spin x valley filling factor (default 4).

    Returns:
        ``(psd, freq)`` both shape ``((2 * N * padding) + N,)``. ``psd``
        normalized to its max. ``freq`` axis: SdH peak at ``B_F = phi_0 * n
        / degeneracy`` lands at 1.
    """
    bstep = inv_b[1] - inv_b[0]
    (sy,) = Rxx.shape
    window = hann(sy)

    windowed = np.pad(Rxx * window, (sy * padding, sy * padding))
    col_fft = np.abs(scipy.fft.fft(windowed))
    freq_T = scipy.fft.fftfreq(windowed.size, d=bstep)

    inv_f0_expected = degeneracy / (_PHI_0 * n_per_cm2_e12 * 1e16)
    with np.errstate(divide="ignore"):
        freq_filling = (1.0 / freq_T) / inv_f0_expected
    psd = col_fft**2
    psd = psd / np.amax(psd)
    return psd, freq_filling


def find_1d_peaks(
    fv: npt.NDArray[np.floating],
    fft: npt.NDArray[np.floating],
    *,
    distance: int = 10,
    prominence: float | None = None,
) -> list[tuple[float, float]]:
    """Find peaks in a 1D FFT spectrum.

    Thin wrapper around :func:`scipy.signal.find_peaks`. Returns a
    materialized list (the inline form returned a single-use ``zip``
    iterator, easy to trip over).

    Args:
        fv: Frequency-axis values, shape ``(N,)``.
        fft: Spectrum values, shape ``(N,)``.
        distance: Minimum sample separation between peaks.
        prominence: Minimum peak prominence.

    Returns:
        List of ``(freq, amplitude)`` tuples for each detected peak.
    """
    peak_ind, _ = find_peaks(fft, distance=distance, prominence=prominence)
    return [(float(fv[i]), float(fft[i])) for i in peak_ind]


def delta_R_over_R(
    B: npt.NDArray[np.floating],
    Rxx: npt.NDArray[np.floating],
    *,
    norm_b: float = 1.0,
    tol: float = 0.001,
) -> tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]:
    """Normalize Rxx(B) to ``(Rxx(B) - Rxx(norm_b)) / Rxx(norm_b)``.

    A common low-field SdH normalization: subtracts and divides by the
    Rxx slice at a fixed reference field.

    Args:
        B: Magnetic field, shape ``(N,)``. In Tesla.
        Rxx: Shape ``(N, M)``.
        norm_b: Reference field, in Tesla. Default 1.0 T.
        tol: Tolerance (in T) for matching ``norm_b`` to a sample in ``B``.

    Returns:
        ``(dRxx, inv_b)`` where ``dRxx`` has shape ``(N, M)`` and ``inv_b``
        has shape ``(N,)``.
    """
    norm_idx = np.where(np.abs(B - norm_b) < tol)[0][0]
    norm_R = Rxx[norm_idx, :]
    dRxx = (Rxx - norm_R) / norm_R
    inv_b = 1.0 / B
    return dRxx, inv_b
