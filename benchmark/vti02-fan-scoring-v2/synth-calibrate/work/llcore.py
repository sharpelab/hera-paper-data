"""Landau-level core: two g=4 bands at fixed total density, Gaussian LLs, thermal average, Drude tensor."""
import numpy as np
from scipy.special import ndtr

HBAR_E_OVER_ME = 0.115767  # meV per T for m* = 1 (hbar e / m_e)
KB = 0.0861733  # meV / K
E_CH = 1.602176634e-19
H_PL = 6.62607015e-34
MU_B = 0.0578838  # meV / T


def _levels(B, F, m, sign, gz, nmax_extra=8):
    """LL energies (meV) of one local-parabolic band, relative to mu0 = 0 at B = 0.
    sign +1 electron band (levels rise), -1 hole band (levels fall). Returns E[nB, L], w (levels x spin)."""
    hw = HBAR_E_OVER_ME * B / m                      # [nB]
    EF = HBAR_E_OVER_ME * F / m                      # band depth at B = 0
    Nmax = int(np.ceil(F / max(B.min(), 1e-3))) + nmax_extra
    N = np.arange(Nmax + 1)
    zs = 0.5 * gz * MU_B * B                          # Zeeman half-splitting
    Eorb = -sign * EF + sign * hw[:, None] * (N[None, :] + 0.5)
    E = np.concatenate([Eorb - zs[:, None], Eorb + zs[:, None]], axis=1)
    return E, hw


def column(B, F_l, F_h, m_l, m_h, sgn_l, T, sig_l, sig_h, gz=2.0, ny=41, iters=48):
    """Normalized DOS-squared thermal averages <D~_b^2> and n_b(B) occupancies for one density column.
    B: 1D array (T), all > 0. sig_b: LL Gaussian std (meV) per point [nB]. Returns dict."""
    kT = KB * T
    bands = []
    for F, m, sg, sig in ((F_l, m_l, sgn_l, sig_l), (F_h, m_h, +1, sig_h)):
        if F <= 1e-6:
            continue
        E, hw = _levels(B, F, m, sg, gz)
        bands.append((F, m, sg, sig, E, hw))
    FL = sum(sg * F for F, m, sg, *_ in bands)
    # occupancy of a Gaussian level convolved with Fermi: normal CDF with combined width
    def occ_total(mu):
        tot = np.zeros_like(B)
        for F, m, sg, sig, E, hw in bands:
            s = np.sqrt(sig**2 + (np.pi * kT) ** 2 / 3.0)
            o = ndtr((mu[:, None] - E) / s[:, None]) * (B[:, None] / 2.0)
            if sg > 0:
                tot += o.sum(1)
            else:  # hole band: carriers are the empty states; the band is filled at mu -> +inf
                tot -= (B[:, None] / 2.0 * (1 - ndtr((mu[:, None] - E) / s[:, None]))).sum(1)
        return tot
    # bisection for mu so that total (signed) carriers = F_L (in T units)
    Emax = max(HBAR_E_OVER_ME * F / m for F, m, *_ in bands) + 50.0
    lo = np.full_like(B, -Emax); hi = np.full_like(B, Emax)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        up = occ_total(mid) > FL
        hi = np.where(up, mid, hi); lo = np.where(up, lo, mid)
    mu = 0.5 * (lo + hi)
    # thermal average of D~^2 on an energy grid around mu, weight -f'(E)
    y = np.linspace(-12, 12, ny)
    wy = 0.25 / np.cosh(y / 2) ** 2; wy /= wy.sum()
    out = {}
    for F, m, sg, sig, E, hw in bands:
        Eg = mu[:, None] + kT * y[None, :]                          # [nB, ny]
        d = (Eg[:, :, None] - E[:, None, :]) / sig[:, None, None]    # [nB, ny, L]
        D = (hw / 2.0)[:, None] * (np.exp(-0.5 * d * d).sum(2) / (np.sqrt(2 * np.pi) * sig[:, None]))
        out[(sg, F)] = dict(D2=(D * D * wy).sum(1), D1=(D * wy).sum(1))
    return mu, out, bands


def rho_tensor(B, n12, F_l, F_h, m_l, m_h, T, g_l, g_h, mob_l, mob_h, gz=2.0, bosc_min=0.02):
    """rho_xx, rho_xy (ohm) for one column. g_b: LL broadening coefficient, sigma_b = g_b * sqrt(B) meV.
    mob_b: transport mobility (m^2/Vs). F_l signed: F_l < 0 means the light pocket is hole-like."""
    B = np.asarray(B, float)
    sgn_l = 1 if F_l >= 0 else -1
    Fl = abs(F_l)
    osc = B > bosc_min
    D2 = {1: np.ones_like(B), 0: np.ones_like(B)}
    if osc.any():
        Bo = B[osc]
        mu, out, bands = column(Bo, Fl, F_h, m_l, m_h, sgn_l, T, g_l * np.sqrt(Bo), g_h * np.sqrt(Bo), gz)
        for (sg, F), v in out.items():
            key = 1 if F == F_h and sg > 0 else 0
            D2[key][osc] = v['D2']
    nb = [(Fl, sgn_l, mob_l, D2[0]), (F_h, 1, mob_h, D2[1])]
    sxx = np.zeros_like(B); sxy = np.zeros_like(B)
    for F, sg, mob, d2 in nb:
        if F <= 0:
            continue
        nden = 4 * E_CH * F / H_PL                     # carriers per m^2
        s0 = nden * E_CH * mob
        mb = mob * B
        sxx += s0 / (1 + mb * mb) * d2
        sxy += sg * s0 * mb / (1 + mb * mb)
    den = sxx ** 2 + sxy ** 2
    return sxx / den, sxy / den
