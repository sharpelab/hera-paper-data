import json
import gzip
import csv
import os
from datetime import datetime, timezone

import numpy as np
import scipy
from scipy.signal import find_peaks, savgol_filter, butter, sosfiltfilt
from itertools import product
from typing import Dict, List, Tuple


# Physical constants
h = 6.626E-34  # Planck constant (J·s)
e = 1.6002E-19  # Elementary charge (C)
phi0 = h / e    # Flux quantum (Wb)
Rq = h/e**2

# Device params
with open(os.path.join(os.path.dirname(__file__), 'rmg19.json'), 'r') as f:
    rmg19 = json.load(f)

dbg = rmg19['default']['dbg']
dtg = rmg19['default']['dtg']

# ==============================================================================
# Gate voltage and carrier density calculations
# ==============================================================================

def calculate_gate_voltages(n, D, dtg=None, dbg=None):
    # Calculate electron density n from nu
    # Use values from config if not provided
    if dtg is None:
        dtg = rmg19['default']['dtg']
    if dbg is None:
        dbg = rmg19['default']['dbg']
    
    ep = 3   
    conversion_factor = 5.52634936
    # Set up system of equations based on original expressions for n and D
    # Rearrange these to solve for Vbg and Vtg
    Vtg = (n / (ep * conversion_factor) + 2* D/ep) * dtg/2
    Vbg = dbg*(n / (ep * conversion_factor) - Vtg/dtg)

    return Vtg, Vbg


def calculate_n_D(Vtg, Vbg, dtg=None, dbg=None):
    # Use values from config if not provided
    if dtg is None:
        dtg = rmg19['default']['dtg']
    if dbg is None:
        dbg = rmg19['default']['dbg']

    ep = 3
    n = (Vbg/dbg + Vtg/dtg)*ep*5.52634936
    D = 0.5*ep*(Vtg/dtg - Vbg/dbg)
    return n, D


def comment_to_gates(comment, delim=':'):
    parts = comment.split(delim)
    values_part = parts[-1].strip()
    values = values_part.strip('()').split(',')
    Vtg = float(values[0].strip())
    Vbg = float(values[1].strip())
    return Vtg, Vbg

# ==============================================================================
# Various Physics Functions
# ==============================================================================

def streda(C, Bs, offset=0):
    return C*Bs/phi0/1E16+offset


# ==============================================================================
# Combinatorics
# ==============================================================================

def linear_combos_close_to_one(
    vals: List[float],
    bound: int,
    window: float,
) -> Dict[Tuple[int, ...], Tuple[float, float]]:
    """
    Returns:
        {
          (c1, c2, ..., cn): (total_sum, abs(total_sum - 1))
        }
        for all |sum - 1| <= window
    """
    n = len(vals)
    r = range(-bound, bound + 1)

    solutions: Dict[Tuple[int, ...], Tuple[float, float]] = {}

    for coeffs in product(r, repeat=n):
        total = sum(c * v for c, v in zip(coeffs, vals))
        err = abs(total - 1.0)

        if err <= window:
            solutions[coeffs] = (total, err)

    return solutions

def linear_combos_close_to_one_restrained(
    vals: List[float],
    bound: int,
    window: float,
) -> Dict[Tuple[int, ...], Tuple[float, float]]:
    """
    Returns:
        {
          (c1, c2, ..., cn): (total_sum, abs(total_sum - 1))
        }
        for all |sum - 1| <= window
    """
    n = len(vals)
    r = range(-bound, bound + 1)

    solutions: Dict[Tuple[int, ...], Tuple[float, float]] = {}

    for coeffs in product(r, repeat=n):
        total = sum(c * v for c, v in zip(coeffs, vals))
        err = abs(total - 1.0)

        if err <= window:
            solutions[coeffs] = (total, err)

    return solutions

def linear_combos_specific_integers(
    vals: List[float],
    allowed_integers: List[int],
    scaling: float = 0.03,
) -> Dict[Tuple[int, ...], Tuple[float, float, float]]:
    """
    Search for linear combinations of vals that equal 1, using only specific
    allowed integers as coefficients, and allowing for scaling of all input values.
    
    Parameters
    ----------
    vals : List[float]
        Input values to combine
    allowed_integers : List[int]
        Specific integers allowed as coefficients (e.g., [-2, -1, 0, 1, 2])
    scaling : float, optional
        Allowed scaling factor for all values (default 0.03 for 3%)
        
    Returns
    -------
    solutions : Dict[Tuple[int, ...], Tuple[float, float, float]]
        {
          (c1, c2, ..., cn): (scaled_sum, scale_factor, error)
        }
        where scale_factor is the scaling applied to all vals
        and error is the absolute difference from 1.0
    """
    n = len(vals)
    solutions: Dict[Tuple[int, ...], Tuple[float, float, float]] = {}
    
    for coeffs in product(allowed_integers, repeat=n):
        # Skip all-zero coefficients
        if all(c == 0 for c in coeffs):
            continue
            
        base_sum = sum(c * v for c, v in zip(coeffs, vals))
        
        if abs(base_sum) < 1e-10:
            continue
            
        # Calculate required scale factor to reach 1.0
        scale_factor = 1.0 / base_sum
        
        # Check if scale factor is within allowed range
        if abs(scale_factor - 1.0) <= scaling:
            scaled_sum = base_sum * scale_factor
            error = abs(scaled_sum - 1.0)
            solutions[coeffs] = (scaled_sum, scale_factor, error)
    
    return solutions



# ==============================================================================
# Data interpolation and FFT analysis
# ==============================================================================

def interp_rxx(B, Rxx, nx=400, type="cubic"):
    """
    Interpolate Rxx onto evenly-spaced 1/B grid.
    
    Parameters
    ----------
    B : array
        Magnetic field values (T)
    Rxx : array
        Resistance values (Ω)
    nx : int
        Number of interpolation points
    
    Returns
    -------
    invBvec : array
        Evenly-spaced 1/B values (1/T)
    Rxx_interp : array
        Interpolated resistance values
    """
    invB = 1.0 / B
    order = np.argsort(invB)
    invB_sorted = invB[order]
    Rxx_sorted = Rxx[order, ...]
    
    invBvec = np.linspace(invB_sorted[0], invB_sorted[-1], nx)
    if type == "cubic":
        cs = scipy.interpolate.CubicSpline(invB_sorted, Rxx_sorted, axis=0)
        Rxx_interp = cs(invBvec)
    elif type == "linear":
        Rxx_interp = np.interp(invBvec, invB_sorted, Rxx_sorted)
    return invBvec, Rxx_interp


def interp_rxx_B(B, Rxx, nx=400, type="cubic"):
    """
    Interpolate Rxx onto an evenly-spaced B grid (NOT 1/B).

    Use this when checking for oscillations periodic in B itself rather than
    in 1/B (e.g. Aharonov–Bohm-like or apparent B-periodic artifacts).
    """
    order = np.argsort(B)
    B_sorted = B[order]
    Rxx_sorted = Rxx[order, ...]

    Bvec = np.linspace(B_sorted[0], B_sorted[-1], nx)
    if type == "cubic":
        cs = scipy.interpolate.CubicSpline(B_sorted, Rxx_sorted, axis=0)
        Rxx_interp = cs(Bvec)
    elif type == "linear":
        Rxx_interp = np.interp(Bvec, B_sorted, Rxx_sorted)
    return Bvec, Rxx_interp


def make_vec_fft(invB, Rxx, n, padding=0, normalize=True, return_fft=False):
    """
    Compute FFT of Rxx in 1/B space.
    
    Parameters
    ----------
    invB : array
        Evenly-spaced 1/B values (1/T)
    Rxx : array
        Resistance values (Ω)
    n : float
        Carrier density in units of 10^12 cm^-2
    padding : int
        Zero-padding factor for FFT
    
    Returns
    -------
    psd : array
        Normalized power spectral density
    freq : array
        Frequency in units of f/(hn/e)
    """
    bstep = invB[1] - invB[0]
    sy, = Rxx.shape

    hanning_window = scipy.signal.windows.hann(sy)
    windowed_data = np.pad(np.multiply(Rxx, hanning_window), (sy*padding, sy*padding))
    window_fft = scipy.fft.fft(windowed_data)
    
    freq_T = scipy.fft.fftfreq(windowed_data.size, d=bstep)
    f_expected = (phi0 * n * 1E16) / 4
    
    freq = freq_T / (4 * f_expected)

    psd = np.abs(window_fft)**2
    if normalize:
        psd = psd / np.amax(psd)

    if return_fft:
    	return psd, freq, window_fft
    else:
    	return psd, freq



def make_vec_fft_B(B, Rxx, padding=0, normalize=True):
    """
    Compute FFT of Rxx on a uniformly-sampled B grid (NOT 1/B).

    Returns
    -------
    psd : array
        Squared FFT magnitude.
    freq : array
        Frequency in cycles per Tesla (1/T). A sharp peak at f_B implies
        a B-periodic component with period 1/f_B Tesla.
    """
    bstep = B[1] - B[0]
    sy, = Rxx.shape

    hanning_window = scipy.signal.windows.hann(sy)
    windowed_data = np.pad(np.multiply(Rxx, hanning_window), (sy * padding, sy * padding))
    window_fft = abs(scipy.fft.fft(windowed_data))

    freq = scipy.fft.fftfreq(windowed_data.size, d=bstep)  # cycles per T

    psd = window_fft**2
    if normalize:
        psd = psd / np.amax(psd)

    return psd, freq


def make_mat_fft(B, Rxx, ns, nx=400, win=401, padding=5, poly=3, max_win_frac=0.4, normalize=True, return_fft=False):
    """
    Compute FFT of Rxx in 1/B space for multiple densities.
    
    Parameters
    ----------
    B : array
        Magnetic field values (T)
    Rxx : array (2D)
        Resistance values (Ω), shape (len(B), len(ns))
    ns : array
        Carrier densities in units of 10^12 cm^-2
    nx : int
        Number of interpolation points for 1/B
    win : int
        Savitzky-Golay filter window size
    padding : int
        Zero-padding factor for FFT
    poly : int
        Polynomial order for Savitzky-Golay filter
    max_win_frac : float
        Maximum window fraction for detrending
    
    Returns
    -------
    psds : array
        Power spectral density (positive frequencies only), shape (fft_length//2, len(ns))
    freqs : array
        Frequency in units of f/(hn/e) (positive only), shape (fft_length//2, len(ns))
    """
    psds = []
    freqs = []
    ffts = []
    
    for i, cut in enumerate(Rxx.T):
        ne = ns[i]
        interp_invB, interp_cut = interp_rxx(B, cut, nx=nx)
        cut_detrended, bg, _ = detrend_savgol(interp_invB, interp_cut, win=win, poly=poly, max_win_frac=max_win_frac)
        psd, freq, fft = make_vec_fft(interp_invB, cut_detrended, ne, padding=padding, normalize=normalize, return_fft=True)
        psds.append(psd[:len(freq)//2])
        freqs.append(freq[:len(freq)//2])
    
    psds = np.array(psds).T  # Transpose to shape (freq, density)
    freqs = np.array(freqs).T
    ffts = np.array(ffts).T

    if return_fft:
    	return psds, freqs, ffts
    else:
    	return psds, freqs

def make_mat_fft_bw(B, Rxx, ns, nx=400, cutoff=5, order=2, normalize=True, padding=5):
    """
    Compute FFT of Rxx in 1/B space for multiple densities.

    Parameters
    ----------
    B : array
        Magnetic field values (T)
    Rxx : array (2D)
        Resistance values (Ω), shape (len(B), len(ns))
    ns : array
        Carrier densities in units of 10^12 cm^-2
    nx : int
        Number of interpolation points for 1/B
    cutoff : float or array
        Butterworth high-pass cutoff in cycles per (T^-1). A scalar applies the
        same cutoff to every column; a 1D array of length len(ns) applies a
        per-density cutoff (e.g. ns/0.125 for a density-scaled rule).
    order : int
        Butterworth filter order
    normalize : bool
        Whether to normalize the power spectral density

    Returns
    -------
    psds : array
        Power spectral density (positive frequencies only), shape (fft_length//2, len(ns))
    freqs : array
        Frequency in units of f/(hn/e) (positive only), shape (fft_length//2, len(ns))
    """
    cutoffs = np.broadcast_to(np.asarray(cutoff, dtype=float), (len(ns),))

    psds = []
    freqs = []

    for i, cut in enumerate(Rxx.T):
        ne = ns[i]
        interp_invB, interp_cut = interp_rxx(B, cut, nx=nx)
        cut_detrended, bg = detrend_butterworth(interp_invB, interp_cut,
                                                cutoff=cutoffs[i], order=order, mode="highpass")
        psd, freq = make_vec_fft(interp_invB, cut_detrended, ne, padding=padding, normalize=normalize)
        psds.append(psd[:len(freq)//2])
        freqs.append(freq[:len(freq)//2])

    psds = np.array(psds).T  # Transpose to shape (freq, density)
    freqs = np.array(freqs).T

    return psds, freqs


def fft_single_bw(file_path, file, n, contacts=(1, 2, 3), current_contact=4,
                  blo=0.9, bhi=8.0, cutoff=5.0, order=2,
                  nx=1000, padding=5, normalize=False,
                  prominence_frac=0.02, height_frac=0.05):
    """
    Load a single B-field sweep and compute per-contact FFTs in 1/B with
    Butterworth detrending.

    Parameters
    ----------
    file_path : str
        Path to the sweep data directory.
    file : int
        Sweep file number.
    n : float
        Carrier density (10^12 cm^-2) used to normalize the FFT frequency axis.
    contacts : iterable of int
        Voltage contacts (sr830_{i}_X) to compute FFTs for.
    current_contact : int
        Reference current channel (sr830_{i}_X) used to form Rxx = V/I.
    blo, bhi : float
        Magnetic-field window (T).
    cutoff : float
        Butterworth high-pass cutoff in cycles per (T^-1).
    order : int
        Butterworth filter order.
    nx : int
        Number of interpolation points for 1/B.
    padding : int
        Zero-padding factor for the FFT.
    normalize : bool
        Whether to normalize the FFT magnitude.
    prominence_frac, height_frac : float
        Peak detection thresholds as fractions of nanmax(fft).

    Returns
    -------
    freq_b : array, shape (nfreq,)
        Frequency axis in units of f/(hn/e).
    ffts : list of arrays
        FFT magnitude per contact (same order as `contacts`).
    peaks_list : list of arrays
        Peak indices into freq_b/ffts[i] per contact.
    """
    from sweep import sweep_load as sl

    data = sl.pload(file_path, file)
    xs = data['xs']
    flip = xs[0] > xs[-1]
    if flip:
        xs = xs[::-1]

    indlo = np.abs(xs - blo).argmin()
    indhi = np.abs(xs - bhi).argmin()

    I = data[f'sr830_{current_contact}_X']
    if flip:
        I = I[::-1]

    freq_b = None
    ffts = []
    peaks_list = []
    for ind in contacts:
        Vxx = data[f'sr830_{ind}_X']
        if flip:
            Vxx = Vxx[::-1]
        zs = Vxx / I

        invB, R_interp = interp_rxx(xs[indlo:indhi], zs[indlo:indhi], nx=nx)
        R_detrended, _ = detrend_butterworth(invB, R_interp, cutoff=cutoff, order=order)
        fft_full, freq_full = make_vec_fft(invB, R_detrended, n, padding=padding, normalize=normalize)

        # Real input -> |FFT|^2 is even-symmetric; restrict to positive half
        # so find_peaks doesn't return mirror peaks at negative frequencies.
        npos = len(freq_full) // 2
        fft = fft_full[:npos]
        freq_b = freq_full[:npos]

        peaks, _ = find_peaks(
            fft,
            prominence=prominence_frac * np.nanmax(fft),
            height=height_frac * np.nanmax(fft),
        )
        ffts.append(fft)
        peaks_list.append(peaks)

    return freq_b, ffts, peaks_list


def plot_linecut_fft(file_path, file, n, contacts=(1, 2, 3), current_contact=4,
                     blo=0.9, bhi=8.0, cutoff=5.0, order=2,
                     nx=1000, padding=5, normalize=True,
                     prominence_frac=0.02, height_frac=0.05,
                     fft_xlim=(0, 4.1), fft_ylim=(0, 1.2),
                     figsize=None):
    """
    Diagnostic 4-row plot for a single B-field sweep, one column per contact.
    Rows: raw R(B); R(1/B) with smooth background; detrended R(1/B);
    FFT vs f/(nh/e) with peaks labeled.

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : ndarray of shape (4, len(contacts))
        Row index 0..3 = (raw, invB, detrended, fft); column index = contact.
        E.g. ``axes[3, 0].set_xlim(0, 2)`` resizes the FFT panel of the first contact.
    results : list of dicts (one per contact, in `contacts` order) with keys
        'invB', 'R_interp', 'bg', 'R_detrended', 'freq_b', 'fft', 'peaks'.
    """
    import matplotlib.pyplot as plt
    from sweep import sweep_load as sl

    contacts = list(contacts)
    n_c = len(contacts)
    if figsize is None:
        figsize = (3 * 1.618 * n_c, 12)

    data = sl.pload(file_path, file)
    md = data.get('measurement_config', {})

    xs = data['xs']
    flip = xs[0] > xs[-1]
    if flip:
        xs = xs[::-1]

    indlo = np.abs(xs - blo).argmin()
    indhi = np.abs(xs - bhi).argmin()

    I = data[f'sr830_{current_contact}_X']
    if flip:
        I = I[::-1]

    fig, axes = plt.subplots(4, n_c, figsize=figsize, squeeze=False)
    results = []

    for j, ind in enumerate(contacts):
        Vxx = data[f'sr830_{ind}_X']
        if flip:
            Vxx = Vxx[::-1]
        zs = Vxx / I

        invB, R_interp = interp_rxx(xs[indlo:indhi], zs[indlo:indhi], nx=nx)
        R_detrended, bg = detrend_butterworth(invB, R_interp, cutoff=cutoff, order=order)
        fft_full, freq_full = make_vec_fft(invB, R_detrended, n, padding=padding, normalize=normalize)

        # positive-frequency half only (|FFT|^2 is mirror-symmetric)
        npos = len(freq_full) // 2
        fft = fft_full[:npos]
        freq_b = freq_full[:npos]

        peaks, _ = find_peaks(
            fft,
            prominence=prominence_frac * np.nanmax(fft),
            height=height_frac * np.nanmax(fft),
        )

        ax_raw  = axes[0, j]
        ax_invB = axes[1, j]
        ax_det  = axes[2, j]
        ax_fft  = axes[3, j]

        ax_raw.plot(xs, zs)
        ax_raw.set_xlabel(r'$B$ (T)')
        ax_raw.set_ylabel(r'$R_{xx}$ ($\Omega$)')
        ax_raw.axvline(blo, color='k', linestyle='--', linewidth=1)
        if bhi < np.nanmax(xs):
            ax_raw.axvline(bhi, color='k', linestyle='--', linewidth=1)

        ax_invB.plot(1 / xs[indlo:indhi], zs[indlo:indhi])
        ax_invB.plot(invB, bg, color='r', linewidth=1.5, label='Background')
        ax_invB.set_xlabel(r'$1/B$ (1/T)')
        ax_invB.set_ylabel(r'$R_{xx}$ ($\Omega$)')

        ax_det.plot(invB, R_detrended)
        ax_det.set_xlabel(r'$1/B$ (1/T)')
        ax_det.set_ylabel(r'$R_{xx}$ detrended ($\Omega$)')

        ax_fft.plot(freq_b, fft, linewidth=1)
        x_lo, x_hi = fft_xlim
        x_thresh = x_lo + 0.7 * (x_hi - x_lo)
        for p in peaks:
            f0 = freq_b[p]
            y0 = fft[p]
            ax_fft.plot(f0, y0, marker='o', markersize=3)
            if f0 > x_thresh:
                xytext, ha = (-6, 6), 'right'
            else:
                xytext, ha = (6, 6), 'left'
            ax_fft.annotate(f'{f0:.3f}', xy=(f0, y0),
                            xytext=xytext, textcoords='offset points',
                            ha=ha, va='bottom', fontsize=6)
        ax_fft.set_xlabel(r'$f/(hn/e)$')
        ax_fft.set_ylabel('FFT (a.u.)')
        ax_fft.set_xlim(*fft_xlim)
        ax_fft.set_ylim(*fft_ylim)

        ax_raw.set_title(md.get(f'sr830_{ind}', f'sr830_{ind}'))

        results.append({
            'invB': invB, 'R_interp': R_interp, 'bg': bg,
            'R_detrended': R_detrended,
            'freq_b': freq_b, 'fft': fft, 'peaks': peaks,
        })

    fig.suptitle(
        f'file {file}  $n$={n:.3f}  '
        f'$B\\in$[{blo:.2f}, {bhi:.2f}] T  '
        f'cutoff={cutoff:.3g}  order={order}'
    )
    fig.tight_layout()

    return fig, axes, results


def plot_linecut_fft_B(file_path, file, contacts=(1, 2, 3), current_contact=4,
                       blo=0.9, bhi=8.0, cutoff=2.0, order=2,
                       nx=1000, padding=5, normalize=True,
                       prominence_frac=0.02, height_frac=0.05,
                       fft_xlim=None, fft_ylim=(0, 1.2),
                       figsize=None):
    """
    Diagnostic 4-row plot for a single B-field sweep, FFT taken in B (not 1/B),
    one column per contact.

    Use this alongside `plot_linecut_fft` to check whether an oscillation is
    actually periodic in B rather than in 1/B. A sharp peak here that is
    absent in the 1/B FFT indicates a B-periodic component; the converse
    indicates a standard SdH-like 1/B-periodic component.

    Rows: raw R(B); R(B) with smooth background; detrended R(B);
    B-space FFT in cycles/T with peaks labeled.

    `cutoff` is in cycles per T (1/T) — different units from the 1/B-space cutoff.

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : ndarray of shape (4, len(contacts))
        Row index 0..3 = (raw, B, detrended, fft); column index = contact.
    results : list of dicts (one per contact) with keys
        'B', 'R_interp', 'bg', 'R_detrended', 'freq_B', 'fft', 'peaks'.
    """
    import matplotlib.pyplot as plt
    from sweep import sweep_load as sl

    contacts = list(contacts)
    n_c = len(contacts)
    if figsize is None:
        figsize = (3 * 1.618 * n_c, 12)

    data = sl.pload(file_path, file)
    md = data.get('measurement_config', {})

    xs = data['xs']
    flip = xs[0] > xs[-1]
    if flip:
        xs = xs[::-1]

    indlo = np.abs(xs - blo).argmin()
    indhi = np.abs(xs - bhi).argmin()

    I = data[f'sr830_{current_contact}_X']
    if flip:
        I = I[::-1]

    fig, axes = plt.subplots(4, n_c, figsize=figsize, squeeze=False)
    results = []

    for j, ind in enumerate(contacts):
        Vxx = data[f'sr830_{ind}_X']
        if flip:
            Vxx = Vxx[::-1]
        zs = Vxx / I

        Bvec, R_interp = interp_rxx_B(xs[indlo:indhi], zs[indlo:indhi], nx=nx)
        R_detrended, bg = detrend_butterworth(Bvec, R_interp, cutoff=cutoff, order=order)
        fft, freq_B = make_vec_fft_B(Bvec, R_detrended, padding=padding, normalize=normalize)
        peaks, _ = find_peaks(
            fft,
            prominence=prominence_frac * np.nanmax(fft),
            height=height_frac * np.nanmax(fft),
        )

        ax_raw = axes[0, j]
        ax_B   = axes[1, j]
        ax_det = axes[2, j]
        ax_fft = axes[3, j]

        ax_raw.plot(xs, zs)
        ax_raw.set_xlabel(r'$B$ (T)')
        ax_raw.set_ylabel(r'$R_{xx}$ ($\Omega$)')
        ax_raw.axvline(blo, color='k', linestyle='--', linewidth=1)
        if bhi < np.nanmax(xs):
            ax_raw.axvline(bhi, color='k', linestyle='--', linewidth=1)

        ax_B.plot(Bvec, R_interp)
        ax_B.plot(Bvec, bg, color='r', linewidth=1.5, label='Background')
        ax_B.set_xlabel(r'$B$ (T)')
        ax_B.set_ylabel(r'$R_{xx}$ ($\Omega$)')

        ax_det.plot(Bvec, R_detrended)
        ax_det.set_xlabel(r'$B$ (T)')
        ax_det.set_ylabel(r'$R_{xx}$ detrended ($\Omega$)')

        # positive frequencies only for the spectrum panel
        npos = len(freq_B) // 2
        ax_fft.plot(freq_B[:npos], fft[:npos], linewidth=1)
        if fft_xlim is None:
            x_lo, x_hi = 0, freq_B[npos - 1]
        else:
            x_lo, x_hi = fft_xlim
        x_thresh = x_lo + 0.7 * (x_hi - x_lo)
        for p in peaks:
            if p >= npos:
                continue
            f0 = freq_B[p]
            y0 = fft[p]
            ax_fft.plot(f0, y0, marker='o', markersize=3)
            if f0 > x_thresh:
                xytext, ha = (-6, 6), 'right'
            else:
                xytext, ha = (6, 6), 'left'
            ax_fft.annotate(f'{f0:.3f}', xy=(f0, y0),
                            xytext=xytext, textcoords='offset points',
                            ha=ha, va='bottom', fontsize=6)
        ax_fft.set_xlabel(r'$f_B$ (1/T)  [period $=1/f_B$ T]')
        ax_fft.set_ylabel('FFT (a.u.)')
        ax_fft.set_xlim(x_lo, x_hi)
        ax_fft.set_ylim(*fft_ylim)

        ax_raw.set_title(md.get(f'sr830_{ind}', f'sr830_{ind}'))

        results.append({
            'B': Bvec, 'R_interp': R_interp, 'bg': bg,
            'R_detrended': R_detrended,
            'freq_B': freq_B, 'fft': fft, 'peaks': peaks,
        })

    fig.suptitle(
        f'B-periodic check — file {file}  '
        f'$B\\in$[{blo:.2f}, {bhi:.2f}] T  '
        f'cutoff={cutoff:.3g} (1/T)  order={order}'
    )
    fig.tight_layout()

    return fig, axes, results


def fft_stability_sweep(file_path, file, n, contact, *,
                        param, values, fixed,
                        current_contact=4, domain='invB',
                        freq_grid=None, freq_units='normalized',
                        normalize=True):
    """
    Sweep one FFT parameter for a single contact and return a 2D matrix of
    FFT magnitudes for stability inspection.

    Parameters
    ----------
    file_path, file : sweep file location.
    n : float
        Carrier density (10^12 cm^-2). Used by the 1/B FFT to normalize the
        frequency axis to f/(nh/e). Ignored when domain='B'.
    contact : int
        Voltage contact (sr830_{contact}_X).
    param : {'cutoff', 'order', 'blo', 'bhi'}
        Which FFT parameter to vary.
    values : 1D array
        Values of the swept parameter.
    fixed : dict
        The remaining FFT parameters. Must include the three of
        {cutoff, order, blo, bhi} not equal to `param`. May also include
        `nx` and `padding`.
    current_contact : int
        Reference current channel.
    domain : {'invB', 'B'}
        Which FFT domain. Cutoff units differ between domains.
    freq_grid : 1D array or None
        Common frequency axis on which all spectra are resampled before
        stacking. Defaults depend on `freq_units`:
            domain='invB', freq_units='normalized' -> linspace(0, 5, 1024) in f/(nh/e)
            domain='invB', freq_units='tesla'      -> linspace(0, 50, 2048) in cycles/T^-1 (T)
            domain='B'                             -> linspace(0, 30, 1024) in 1/T
    freq_units : {'normalized', 'tesla'}
        Only meaningful for domain='invB'. 'normalized' returns f/(nh/e);
        'tesla' returns cycles per T^-1 (numerically T). Ignored for domain='B'
        (which is always cycles per T = 1/T).
    normalize : bool
        Whether each spectrum is normalized to its own max before stacking.

    Returns
    -------
    values : array
        Echo of the input.
    freq_grid : array
        Common frequency axis used for stacking.
    fft_mat : array, shape (len(values), len(freq_grid))
        FFT magnitudes. Rows for which the B-window is too narrow contain NaN.
    """
    from sweep import sweep_load as sl

    if param not in ('cutoff', 'order', 'blo', 'bhi'):
        raise ValueError(f"param must be one of cutoff/order/blo/bhi, got {param!r}")
    if domain not in ('invB', 'B'):
        raise ValueError(f"domain must be 'invB' or 'B', got {domain!r}")

    required = {'cutoff', 'order', 'blo', 'bhi'} - {param}
    missing = required - set(fixed)
    if missing:
        raise ValueError(f"fixed is missing keys: {sorted(missing)}")

    if freq_units not in ('normalized', 'tesla'):
        raise ValueError(f"freq_units must be 'normalized' or 'tesla', got {freq_units!r}")

    if freq_grid is None:
        if domain == 'invB' and freq_units == 'tesla':
            freq_grid = np.linspace(0, 50, 2048)   # cycles per T^-1 (= T)
        elif domain == 'invB':
            freq_grid = np.linspace(0, 5, 1024)    # f/(nh/e)
        else:
            freq_grid = np.linspace(0, 30, 1024)   # cycles per T (= 1/T)

    data = sl.pload(file_path, file)
    xs = data['xs']
    flip = xs[0] > xs[-1]
    if flip:
        xs = xs[::-1]

    I = data[f'sr830_{current_contact}_X']
    if flip:
        I = I[::-1]
    Vxx = data[f'sr830_{contact}_X']
    if flip:
        Vxx = Vxx[::-1]
    zs = Vxx / I

    fft_mat = np.full((len(values), len(freq_grid)), np.nan)

    for k, v in enumerate(values):
        p = dict(fixed)
        p[param] = v
        blo_v = p['blo']
        bhi_v = p['bhi']
        cutoff_v = p['cutoff']
        order_v = int(p['order'])
        nx_v = int(p.get('nx', 1000))
        padding_v = int(p.get('padding', 5))

        indlo = np.abs(xs - blo_v).argmin()
        indhi = np.abs(xs - bhi_v).argmin()
        if indhi - indlo < max(8, padding_v):
            continue

        xs_w = xs[indlo:indhi]
        zs_w = zs[indlo:indhi]

        if domain == 'invB':
            invB, R = interp_rxx(xs_w, zs_w, nx=nx_v)
            R_det, _ = detrend_butterworth(invB, R, cutoff=cutoff_v, order=order_v)
            psd, freq = make_vec_fft(invB, R_det, n, padding=padding_v, normalize=normalize)
            if freq_units == 'tesla':
                # make_vec_fft returns freq normalized by phi0*n*1E16; undo it.
                freq = freq * (phi0 * n * 1E16)
        else:
            Bvec, R = interp_rxx_B(xs_w, zs_w, nx=nx_v)
            R_det, _ = detrend_butterworth(Bvec, R, cutoff=cutoff_v, order=order_v)
            psd, freq = make_vec_fft_B(Bvec, R_det, padding=padding_v, normalize=normalize)

        npos = len(freq) // 2
        freq_pos = freq[:npos]
        psd_pos = psd[:npos]

        # freq is fftfreq output: monotonically increasing on the positive half.
        fft_mat[k, :] = np.interp(freq_grid, freq_pos, psd_pos, left=0.0, right=0.0)

    return values, freq_grid, fft_mat


def plot_fft_stability(values, freq_grid, fft_mat, ax=None, *,
                       param_name='', freq_label='',
                       marker_value=None,
                       cmap='viridis', norm=None,
                       vmin=None, vmax=None,
                       log_x=False, style='pcolormesh',
                       contour_levels=20):
    """
    Render a stability sweep as a 2D heatmap with the swept parameter on x
    and frequency on y.

    Parameters
    ----------
    values, freq_grid, fft_mat : output of `fft_stability_sweep`.
    ax : matplotlib Axes or None
        Where to draw. A new figure is created if None.
    param_name, freq_label : str
        Axis labels.
    marker_value : float or None
        If given, draws a red dashed vertical line at the user's chosen
        parameter value (e.g. the value being used in the main analysis).
    cmap : matplotlib colormap.
    norm : matplotlib Normalize-like, optional.
        If None, builds LogNorm from (vmin, vmax). Override to control color
        scaling completely.
    vmin, vmax : float, optional.
        Color limits for the default LogNorm. If unset, vmax=nanmax(fft_mat)
        and vmin = vmax * 1e-4 (4 decades). Ignored when `norm` is supplied.
    log_x : bool
        Useful for cutoff sweeps that span ~one decade.
    style : {'pcolormesh', 'contourf'}
        pcolormesh is faster and shows fine structure; contourf gives smoother
        bands at the cost of a little blurring.
    contour_levels : int
        Levels for contourf.

    Returns
    -------
    fig, ax, im
        `im` is the QuadMesh / ContourSet — pass to `fig.colorbar(im, ...)`.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    if norm is None:
        if vmax is None:
            vmax = np.nanmax(fft_mat)
            if not np.isfinite(vmax) or vmax <= 0:
                vmax = 1.0
        if vmin is None:
            vmin = vmax * 1e-4
        norm = LogNorm(vmin=vmin, vmax=vmax)

    Z = fft_mat.T  # rows=freq, cols=param
    if style == 'pcolormesh':
        im = ax.pcolormesh(values, freq_grid, Z, cmap=cmap, norm=norm,
                           rasterized=True, lw=0)
    elif style == 'contourf':
        im = ax.contourf(values, freq_grid, Z, levels=contour_levels,
                         cmap=cmap, norm=norm)
    else:
        raise ValueError(f"style must be 'pcolormesh' or 'contourf', got {style!r}")

    if marker_value is not None:
        ax.axvline(marker_value, color='r', linestyle='--', linewidth=1)

    if log_x:
        ax.set_xscale('log')

    if param_name:
        ax.set_xlabel(param_name)
    if freq_label:
        ax.set_ylabel(freq_label)

    return fig, ax, im


def find_1d_peaks(fv, fft, dist=10, prom=None):
    """
    Find peaks in 1D FFT spectrum.
    
    Parameters
    ----------
    fv : array
        Frequency values
    fft : array
        FFT magnitude values
    dist : int
        Minimum distance between peaks (in samples)
    prom : float, optional
        Minimum prominence for peak detection
    
    Returns
    -------
    peaks : zip iterator
        Iterator of (frequency, magnitude) tuples for each peak
    """
    peak_ind = scipy.signal.find_peaks(fft, distance=dist, prominence=prom)[0]
    peak_xval = fv[peak_ind]
    peak_yval = fft[peak_ind]

    return zip(peak_xval, peak_yval)


def find_dR_div_R(B, Rxx, normB=1, tol=0.001):
    """
    Calculate normalized resistance change ΔR/R.
    
    Takes in a Rxx of shape (M, N) and a B field vector of shape (M,). Returns
    deltaRxx / Rxx(B=normB). Delta is found by subtracting Rxx(B) - Rxx(B=normB).
    
    Parameters
    ----------
    B : array
        Magnetic field values (T), shape (M,)
    Rxx : array
        Resistance values (Ω), shape (M, N)
    normB : float
        Normalization field value (T)
    tol : float
        Tolerance for finding normB in the B array
    
    Returns
    -------
    dRxx : array
        Normalized resistance change ΔR/R, shape (M, N)
    invB : array
        1/B values (1/T)
    """
    normBind = np.where(abs(B - normB) < tol)[0][0]
    normR = Rxx[normBind, :]

    dRxx = np.zeros(Rxx.shape)
    for i in range(len(Rxx)):
        dRxx[i] = (Rxx[i, :] - normR) / normR

    invB = 1 / B

    return dRxx, invB


# ==============================================================================
# Background subtraction methods
# ==============================================================================

def detrend_savgol(invB, y, win='auto', poly=3, max_win_frac=0.2):
    """
    Subtract a smooth baseline using Savitzky-Golay filter.

    Parameters
    ----------
    invB : array
        1/B values (used for estimating oscillation period when win='auto')
    y : array
        Rxx values to detrend
    win : int or 'auto'
        Window length (odd integer). Should be longer than oscillation period in 1/B.
        If 'auto', adaptively sets window to max_win_frac of data length,
        capped at 401 points.
    poly : int
        Polynomial order for local fits.
    max_win_frac : float
        Maximum window size as fraction of data length (used when win='auto').
        Default 0.2 means window is at most 20% of the data.

    Returns
    -------
    out : array
        Detrended signal with zero mean.
    bg : array
        Extracted background.
    win_used : int
        Actual window size used (useful when win='auto').
    """
    y = np.asarray(y, float)
    n = len(y)

    # Adaptive window sizing
    if win == 'auto':
        win = min(401, int(n * max_win_frac))
    else:
        win = int(win)

    # Ensure odd
    if win % 2 == 0:
        win += 1

    # Ensure valid for data length
    max_allowed = n - (1 - n % 2)  # largest odd <= n-1
    win = min(win, max_allowed)

    # Ensure valid for polynomial order
    if win < poly + 2:
        out = y - np.nanmean(y)
        return out, np.full_like(y, np.nanmean(y)), win

    bg = savgol_filter(y, window_length=win, polyorder=poly, mode="interp")
    out = y - bg
    out -= np.nanmean(out)
    return out, bg, win


def detrend_divide(invB, y, win='auto', poly=3, max_win_frac=0.4):
    """
    Normalize by a smooth baseline (divide instead of subtract).
    
    This preserves relative oscillation amplitude better than subtraction,
    and is less likely to remove real structure when you have few periods.

    Parameters
    ----------
    invB : array
        1/B values
    y : array
        Rxx values to detrend
    win : int or 'auto'
        Window length for Savitzky-Golay smoothing.
    poly : int
        Polynomial order for local fits.
    max_win_frac : float
        Maximum window size as fraction of data length.
        Default 0.4 (larger than subtract method to be gentler).

    Returns
    -------
    out : array
        Normalized signal: (R - R_smooth) / R_smooth = R/R_smooth - 1
    bg : array
        Extracted background (smoothed R).
    win_used : int
        Actual window size used.
    """
    y = np.asarray(y, float)
    n = len(y)

    # Adaptive window sizing
    if win == 'auto':
        win = min(201, int(n * max_win_frac))
    else:
        win = int(win)

    # Ensure odd
    if win % 2 == 0:
        win += 1

    # Ensure valid for data length
    max_allowed = n - (1 - n % 2)
    win = min(win, max_allowed)

    # Ensure valid for polynomial order
    if win < poly + 2:
        bg = np.full_like(y, np.nanmean(y))
        out = y / bg - 1
        return out, bg, win

    bg = savgol_filter(y, window_length=win, polyorder=poly, mode="interp")
    
    # Avoid division by zero
    bg_safe = np.where(np.abs(bg) < 1e-10, 1e-10, bg)
    out = y / bg_safe - 1  # fractional deviation from background
    
    return out, bg, win


def detrend_linear(invB, y, degree=1):
    """
    Remove only a linear (or quadratic) trend - the gentlest option.
    
    Use this when you have very few oscillation periods and don't want
    to remove any curvature that might be real signal.

    Parameters
    ----------
    invB : array
        1/B values
    y : array
        Rxx values to detrend
    degree : int
        1 = linear (just slope), 2 = quadratic. Default 1.

    Returns
    -------
    out : array
        Detrended signal.
    bg : array
        Linear/quadratic background.
    """
    y = np.asarray(y, float)
    invB = np.asarray(invB, float)
    
    idx = np.isfinite(y) & np.isfinite(invB)
    coeff = np.polyfit(invB[idx], y[idx], degree)
    bg = np.polyval(coeff, invB)
    out = y - bg
    out -= np.nanmean(out)
    
    return out, bg


def detrend_endpoints(invB, y):
    """
    Subtract a line connecting the first and last points.
    
    The absolute gentlest option - only removes the overall tilt,
    preserves all curvature.

    Parameters
    ----------
    invB : array
        1/B values
    y : array
        Rxx values

    Returns
    -------
    out : array
        Detrended signal.
    bg : array
        Linear background.
    """
    y = np.asarray(y, float)
    invB = np.asarray(invB, float)
    
    # Line from first to last point
    slope = (y[-1] - y[0]) / (invB[-1] - invB[0])
    bg = y[0] + slope * (invB - invB[0])
    
    out = y - bg
    out -= np.nanmean(out)
    
    return out, bg


def detrend_butterworth(invB, y, cutoff=None, order=2, mode="highpass",
                        nan_policy="interpolate", uniform_tol=1e-3):
    """
    Butterworth detrending in uniformly sampled invB = 1/B space.

    Parameters
    ----------
    invB : array
        1/B values. Should be evenly spaced (uniform grid).
    y : array
        Signal (e.g., Rxx) to detrend.
    cutoff : float
        Cutoff frequency in the SAME UNITS as an FFT frequency axis for y(invB):
        cycles per (1/B) i.e. cycles per (T^-1), numerically "Tesla".
        Example: SdH peak at f=20 -> you might choose cutoff ~ 2-5.
    order : int
        Butterworth order (2-4 typical).
    mode : {"highpass","lowpass"}
        "highpass" returns oscillatory component as `out`.
        "lowpass" returns background component as `out`.
    nan_policy : {"interpolate","raise"}
        How to handle NaNs in y.
    uniform_tol : float
        Relative tolerance for uniform spacing check.

    Returns
    -------
    out : array
        Requested component (high-pass oscillations or low-pass background).
    other : array
        Complementary component (bg or oscillations), computed as y - out.
    """
    invB = np.asarray(invB, float)
    y = np.asarray(y, float)

    # Check uniform spacing
    d = np.diff(invB)
    d_med = np.median(d)
    if not np.allclose(d, d_med, rtol=uniform_tol, atol=0):
        raise ValueError("invB must be uniformly spaced (resample onto a uniform 1/B grid first).")

    # NaN handling
    if np.isnan(y).any():
        if nan_policy == "raise":
            raise ValueError("y contains NaNs; filter requires finite values.")
        elif nan_policy == "interpolate":
            x = np.arange(y.size)
            m = np.isfinite(y)
            y = np.interp(x, x[m], y[m])
        else:
            raise ValueError("nan_policy must be 'interpolate' or 'raise'.")

    # Sampling frequency and Nyquist
    fs = 1.0 / abs(d_med)       # samples per (T^-1)
    nyq = 0.5 * fs

    if cutoff is None:
        raise ValueError("Provide cutoff explicitly (recommended) to avoid removing real low-f SdH content.")

    Wn = np.clip(cutoff / nyq, 1e-6, 0.999)

    btype = "highpass" if mode == "highpass" else "lowpass"
    sos = butter(order, Wn, btype=btype, output="sos")

    out = sosfiltfilt(sos, y)
    other = y - out

    # Optional: center oscillatory component
    if mode == "highpass":
        out -= np.mean(out)

    return out, other


def detrend_poly(B, y, degree=5):
    """
    Subtract a polynomial baseline (original method).

    Parameters
    ----------
    B : array
        Magnetic field values.
    y : array
        Rxx values.
    degree : int
        Polynomial degree.

    Returns
    -------
    out : array
        Detrended signal.
    bg : array
        Polynomial background.
    """
    y = np.asarray(y, float)
    idx = np.isfinite(y) & np.isfinite(B)
    coeff = np.polyfit(B[idx], y[idx], degree)
    bg = np.polyval(coeff, B)
    out = y - bg
    out -= np.nanmean(out)
    return out, bg


# ==============================================================================
# InfluxDB data retrieval
# ==============================================================================

def _get_file_time_range(file_number, data_path="./data"):
    """Read first and last unix timestamps from a data file."""
    path = os.path.join(data_path, str(file_number), "data.tsv.gz")
    first_t = last_t = None
    with gzip.open(path, "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if first_t is None:
                first_t = float(row[0])
            last_t = float(row[0])
    return first_t, last_t


def _load_influxdb_token():
    """Load InfluxDB token from .env file next to this script."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("INFLUXDB_TOKEN="):
                return line.split("=", 1)[1]
    raise ValueError("INFLUXDB_TOKEN not found in .env")


def fetch_influxdb(file_number, measurement, metric, unit=None,
                   bucket="023_toploader", data_path="./data"):
    """Fetch a variable from InfluxDB for the time range of a data file.

    Reads the start/end timestamps from the file's data.tsv.gz and queries
    InfluxDB for the requested measurement/metric pair.

    Parameters
    ----------
    file_number : int
        Numbered data directory to look up.
    measurement : str
        InfluxDB measurement name (e.g. "avs_bridge").
    metric : str
        Metric tag to filter on (e.g. "mixing_ch_low").
    unit : str, optional
        Unit tag to filter on. Only applied if provided.
    bucket : str
        Bucket to query. Default "023_toploader".
    data_path : str
        Path to the data directory. Default "./data".

    Returns
    -------
    times : np.ndarray
        Unix epoch timestamps.
    values : np.ndarray
        Field values.
    """
    from influxdb_client import InfluxDBClient

    t_start, t_stop = _get_file_time_range(file_number, data_path)
    token = _load_influxdb_token()

    url = "https://metrics.aaronsharpe.science"
    org = "dgg"

    start_dt = datetime.fromtimestamp(t_start, tz=timezone.utc)
    stop_dt = datetime.fromtimestamp(t_stop, tz=timezone.utc)

    start_rfc = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    stop_rfc = stop_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    query = (
        f'from(bucket: "{bucket}")'
        f'  |> range(start: {start_rfc}, stop: {stop_rfc})'
        f'  |> filter(fn: (r) => r["_measurement"] == "{measurement}")'
        f'  |> filter(fn: (r) => r["metric"] == "{metric}")'
        f'  |> filter(fn: (r) => r["_field"] == "value")'
    )
    if unit is not None:
        query += f'  |> filter(fn: (r) => r["unit"] == "{unit}")'

    with InfluxDBClient(url=url, token=token, org=org) as client:
        tables = client.query_api().query(query, org=org)

    times, values = [], []
    for table in tables:
        for record in table.records:
            times.append(record.get_time().timestamp())
            values.append(record.get_value())

    return np.array(times), np.array(values)
