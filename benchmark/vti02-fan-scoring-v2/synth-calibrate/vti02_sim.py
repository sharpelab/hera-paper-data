"""Synthetic vti-02 electron-side Landau fans: R(n, B) as the live sr1_X / I_meas would read it.

Physics: two g = 4 ABAB pockets (light, heavy) as local parabolic bands with the tone
frequencies F(n) and cyclotron masses m*(n) of the corpus model (tetralayer_fs_count), held at
fixed total density. Gaussian Landau levels (sigma = g_b * sqrt(B)), Zeeman g = 2, the chemical
potential solved at every field (plus a smooth reservoir DOS, res_dos x the band DOS,
that softens chemical-potential pinning), <D^2> thermally averaged per band, a two-band Drude tensor
weighted by it, inverted to rho. This is the non-perturbative form of LK x Dingle: harmonics,
the F_L = F_light + F_heavy tone (chemical-potential pinning in the QH regime) and the
difference tone come out of the level structure; none is added by hand.
Measured R = G (n/2)^p rho_xx h(nu) + c_xy rho_xy + dR0(n) / (1 + (B/B_w)^2), averaged over a
Gaussian density spread delta_n. h(nu) = 1 + a / (1 + exp((nu - nu_c)/w)), nu = F_L/B, is an
empirical lowest-Landau-level enhancement (live R at nu_total < 12 runs ~4x the LL model).

Acquisition: in-row SR830 24 dB filter response along the fast (density) axis when a settle
time is given, input noise sqrt(e_n^2 + e_excess^2) * sqrt(ENBW) independent per point (e_n = 40 nV/rtHz
white; e_excess is the session-dependent excess seen along B in the signal-free quadrature channel),
clipping at 1.092 * sens, quantization LSB = 2^(ceil(log2 sens) - 15). Row gain jitter and row
field jitter are knobs held at 0: the live fans show neither (see REPORT).

    import numpy as np, vti02_sim as vs
    R = vs.simulate(B_grid, n_cols, I_A=10e-9, tau_s=0.3, sens_V=100e-6, rng=np.random.default_rng(0))

B_grid is the slow-axis field of each row (any order, 0 T allowed); n_cols the density of each
fast column in acquisition order, in 1e12 cm^-2 on the F_L = 10.3392 n frame (see n_scale).
"""
import json
from pathlib import Path

import numpy as np
from scipy.special import ndtr

_HERE = Path(__file__).resolve().parent
PARAMS_PATH = _HERE / 'vti02_sim_params.json'
TABLE_PATH = _HERE / 'corpus_abab_table.json'

HBAR_E_OVER_ME = 0.115767   # meV/T at m* = 1
KB = 0.0861733              # meV/K
MU_B = 0.0578838            # meV/T
E_CH = 1.602176634e-19
H_PL = 6.62607015e-34
H_OVER_4E = 10.3392         # T per 1e12 cm^-2 (g = 4)

_tab = json.load(open(TABLE_PATH))
_T = np.array(_tab['rows'], float)            # n, F_light(signed), F_heavy, m_light, m_heavy


def _tab_interp(n, col):
    n = np.asarray(n, float)
    if np.any(n < _T[0, 0]) or np.any(n > _T[-1, 0]):
        raise ValueError(f'n outside the corpus table [{_T[0, 0]}, {_T[-1, 0]}] e12 cm^-2')
    return np.interp(n, _T[:, 0], _T[:, col])


def corpus_tones(n):
    """Corpus ABAB model: (F_light, F_heavy) in T. F_light < 0 marks a hole-like light pocket
    (near-CNP semimetal regime, where F_heavy - |F_light| = F_L)."""
    n = np.asarray(n, float)
    Fl, Fh = _tab_interp(n, 1), _tab_interp(n, 2)
    hole = np.abs(Fh - Fl - H_OVER_4E * n) < np.abs(Fh + Fl - H_OVER_4E * n)
    return np.where(hole, -Fl, Fl), Fh


def corpus_masses(n):
    """Corpus ABAB model cyclotron masses (m_light, m_heavy) in m_e."""
    return _tab_interp(n, 3), _tab_interp(n, 4)


def observed_tones(n, r0=None, r1=None):
    """Tones fitted on the calibration fans: F_light = r(n) F_L with r linear in n, F_heavy = F_L - F_light.
    Coefficients from the parameter file unless given."""
    if r0 is None:
        p = load_params(); r0, r1 = p['r0'], p['r1']
    n = np.asarray(n, float)
    FL = H_OVER_4E * n
    Fl = (r0 + r1 * (n - 2.0)) * FL
    return Fl, FL - Fl


def load_params(path=PARAMS_PATH):
    return json.load(open(path))


# ---------------------------------------------------------------- Landau-level core

def _band_levels(B, F, m, sign, gz):
    hw = HBAR_E_OVER_ME * B / m
    depth = HBAR_E_OVER_ME * F / m
    Nmax = int(np.ceil(F / B.min())) + 8
    N = np.arange(Nmax + 1)
    zs = 0.5 * gz * MU_B * B
    Eorb = -sign * depth + sign * hw[:, None] * (N[None, :] + 0.5)
    return np.concatenate([Eorb - zs[:, None], Eorb + zs[:, None]], axis=1), hw


def _dos2(B, bands, T, res_dos=0.0, ny=41, iters=46):
    """Solve mu at fixed total density; return <D~^2>_T per band (same order as bands)."""
    kT = KB * T
    lv = [(_band_levels(B, F, m, sg, gz), F, sg, sig) for F, m, sg, sig, gz in bands]
    target = sum(sg * F for F, m, sg, sig, gz in bands)
    d0 = res_dos * sum(m / HBAR_E_OVER_ME for F, m, sg, sig, gz in bands)   # reservoir DOS, T per meV
    swid = [np.sqrt(sig ** 2 + (np.pi * kT) ** 2 / 3.0)[:, None] for *_, sig, gz in bands]

    def carriers(mu):
        tot = d0 * mu
        for ((E, hw), F, sg, sig), s in zip(lv, swid):
            o = ndtr((mu[:, None] - E) / s)
            tot += sg * (B / 2.0) * (o.sum(1) if sg > 0 else (1.0 - o).sum(1))
        return tot
    top = max(HBAR_E_OVER_ME * F / m for F, m, *_ in bands) + 60.0
    lo = np.full_like(B, -top); hi = np.full_like(B, top)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        up = carriers(mid) > target
        hi = np.where(up, mid, hi); lo = np.where(up, lo, mid)
    mu = 0.5 * (lo + hi)
    y = np.linspace(-12.0, 12.0, ny)
    wy = 0.25 / np.cosh(y / 2) ** 2; wy /= wy.sum()
    out = []
    for (E, hw), F, sg, sig in lv:
        Eg = mu[:, None] + kT * y[None, :]
        d = (Eg[:, :, None] - E[:, None, :]) / sig[:, None, None]
        D = (hw / 2.0)[:, None] * np.exp(-0.5 * d * d).sum(2) / (np.sqrt(2 * np.pi) * sig[:, None])
        out.append((D * D * wy).sum(1))
    return out


def _lk_amp(B, m, T, g):
    """Leading-harmonic LK x Gaussian-Dingle amplitude of one band, to skip fields where it is negligible."""
    X = 14.6947 * m * T / B
    rt = np.where(X < 1e-6, 1.0, X / np.sinh(np.minimum(X, 700)))
    hw = HBAR_E_OVER_ME * B / m
    return rt * np.exp(-2 * np.pi ** 2 * (g * np.sqrt(B)) ** 2 / hw ** 2)


def rho_column(B, F_l, F_h, m_l, m_h, T, g_l, g_h, mob_l, mob_h, gz=2.0, res_dos=0.0, amp_min=1e-5, chunk=48):
    """rho_xx, rho_xy (ohm) of one density column on field array B (T, >= 0, any order).
    F_l < 0: hole-like light pocket. Fields where every band's LK amplitude is below amp_min get <D^2> = 1."""
    B = np.asarray(B, float)
    sgn_l = 1 if F_l >= 0 else -1
    Fl = abs(float(F_l))
    parts = [(Fl, m_l, sgn_l, mob_l, g_l), (float(F_h), m_h, 1, mob_h, g_h)]
    parts = [q for q in parts if q[0] > 1e-3]
    d2 = [np.ones_like(B) for _ in parts]
    Bs = np.maximum(B, 1e-6)
    osc = np.zeros(B.shape, bool)
    for F, m, sg, mob, g in parts:
        osc |= _lk_amp(Bs, m, T, g) > amp_min
    idx = np.where(osc)[0]
    idx = idx[np.argsort(B[idx])]
    for c0 in range(0, idx.size, chunk):
        ii = idx[c0:c0 + chunk]
        Bo = B[ii]
        res = _dos2(Bo, [(F, m, sg, g * np.sqrt(Bo), gz) for F, m, sg, mob, g in parts], T, res_dos)
        for k, r in enumerate(res):
            d2[k][ii] = r
    sxx = np.zeros_like(B); sxy = np.zeros_like(B)
    for (F, m, sg, mob, g), dd in zip(parts, d2):
        s0 = 4 * E_CH * F / H_PL * E_CH * mob
        mb = mob * B
        sxx += s0 / (1 + mb * mb) * dd
        sxy += sg * s0 * mb / (1 + mb * mb)
    den = sxx ** 2 + sxy ** 2
    return sxx / den, sxy / den


_GH_X, _GH_W = np.polynomial.hermite_e.hermegauss(5)
_GH_W = _GH_W / _GH_W.sum()


def clean_R(B_grid, n_cols, p, tone_fn=None, mass_fn=None, n_scale=1.0):
    """Noise-free R[row, col] (ohm) on the design grid, before acquisition."""
    tone_fn = tone_fn or corpus_tones
    mass_fn = mass_fn or corpus_masses
    B = np.abs(np.asarray(B_grid, float))
    n_cols = np.asarray(n_cols, float) * n_scale
    R = np.zeros((B.size, n_cols.size))
    for j, n in enumerate(n_cols):
        if n <= 0:
            raise ValueError('vti02_sim covers the electron side only (n > 0)')
        acc = np.zeros_like(B)
        for x, w in zip(_GH_X, _GH_W):
            nn = n * (1 + p['delta_n'] * x)
            Fl, Fh = (float(v) for v in tone_fn(nn))
            ml, mh = (float(v) for v in mass_fn(nn))
            ml *= p['mass_scale_l']; mh *= p['mass_scale_h']
            gl = p['g_l'] * (nn / 2.0) ** p['g_l_pow']
            gh = p['g_h'] * (nn / 2.0) ** p['g_h_pow']
            rx, ry = rho_column(B, Fl, Fh, ml, mh, p['T_K'], gl, gh,
                                p['mob_h'] * p['mob_ratio_lh'], p['mob_h'], res_dos=p.get('res_dos', 0.0))
            nu = H_OVER_4E * nn / np.maximum(B, 1e-6)
            hq = 1 + p.get('hq_a', 0.0) / (1 + np.exp((nu - p.get('hq_nu', 3.0)) / p.get('hq_w', 0.2)))
            acc += w * (p['G'] * (nn / 2.0) ** p['G_pow'] * rx * hq + p['c_xy'] * ry)
        dR0 = max(0.0, np.interp(n, p['R0_n'], p['R0_ohm']) - _drude_R0(n, p, tone_fn))
        R[:, j] = acc + dR0 / (1 + (B / p['B_w']) ** 2)
    return R


def _drude_R0(n, p, tone_fn):
    Fl, Fh = (abs(float(v)) for v in tone_fn(n))
    s = 4 * E_CH / H_PL * E_CH * (Fl * p['mob_h'] * p['mob_ratio_lh'] + Fh * p['mob_h'])
    return p['G'] * (n / 2.0) ** p['G_pow'] / s


# ---------------------------------------------------------------- acquisition

ENBW = {6: 1 / 4, 12: 1 / 8, 18: 3 / 32, 24: 5 / 64}


def lsb(sens):
    return 2.0 ** (np.ceil(np.log2(sens)) - 15)


def step_weights(delay_s, tau_s, slope_db=24, kmax=12):
    """Weights of the current and previous fast points in a reading taken delay_s after the step."""
    order = slope_db // 6
    t = delay_s * np.arange(kmax + 2)
    S = np.array([_step(tt, tau_s, order) for tt in t])
    w = np.diff(S)                       # w[k]: weight of the value k steps back
    w[-1] += 1 - S[-1]
    return w


def _fact(k):
    out = 1
    for i in range(2, k + 1):
        out *= i
    return out


def _step(t, tau, order):
    x = t / tau
    return 1 - np.exp(-x) * sum(x ** k / _fact(k) for k in range(order))


def _blur_rows(V, w):
    """Filter along the fast axis; each row starts settled on its first point."""
    out = np.zeros_like(V)
    nf = V.shape[1]
    for k, wk in enumerate(w):
        idx = np.maximum(np.arange(nf) - k, 0)
        out += wk * V[:, idx]
    return out


def acquire(Rclean, B_grid, I_A, tau_s, sens_V, rng, p, slope_db=24, delay_s=None,
            e_n=None, gain_jitter=None, field_jitter=None, dRdB=None):
    """Turn a clean R map into what sr1_X / I_meas reads."""
    e_n = np.hypot(p['e_n_V_rtHz'], p.get('e_excess_V_rtHz', 0.0)) if e_n is None else e_n
    gj = p['gain_jitter'] if gain_jitter is None else gain_jitter
    fj = p['field_jitter_T'] if field_jitter is None else field_jitter
    V = Rclean * I_A
    nrow, ncol = V.shape
    if fj and dRdB is not None:
        V = V + dRdB * I_A * (fj * rng.standard_normal(nrow))[:, None]
    if gj:
        V = V * (1 + gj * rng.standard_normal((nrow, 1)))
    if delay_s is not None:
        V = _blur_rows(V, step_weights(delay_s, tau_s, slope_db))
    V = V + e_n * np.sqrt(ENBW[int(slope_db)] / tau_s) * rng.standard_normal(V.shape)
    q = lsb(sens_V)
    V = np.clip(V, -1.092 * sens_V, 1.092 * sens_V)
    V = np.round(V / q) * q
    return V / I_A


def simulate(B_grid, n_cols, I_A, tau_s, sens_V, rng, tone_fn=None, *, mass_fn=None, params=None,
             slope_db=24, delay_s=None, n_scale=1.0, return_clean=False):
    """Synthetic R[row, col] (ohm) for a fan: rows follow B_grid, columns follow n_cols.

    tone_fn(n) -> (F_light, F_heavy) in T, scalar n; default the corpus model (corpus_tones).
    Contract: F_light + F_heavy = 10.3392 n; a negative F_light marks a hole-like light pocket
    (F_heavy - |F_light| = 10.3392 n). observed_tones is the calibration-fitted alternative.
    mass_fn(n) -> (m_light, m_heavy) in m_e; default corpus_masses. delay_s: fast-axis settle time
    (None = fully settled). n_scale multiplies n_cols (true density / design density)."""
    p = params or load_params()
    B = np.asarray(B_grid, float)
    Rc = clean_R(B, n_cols, p, tone_fn, mass_fn, n_scale)
    dRdB = None
    if p.get('field_jitter_T'):
        o = np.argsort(B)
        dRdB = np.empty_like(Rc)
        dRdB[o] = np.gradient(Rc[o], B[o], axis=0) if B.size > 1 else 0.0
    R = acquire(Rc, B, I_A, tau_s, sens_V, rng, p, slope_db, delay_s, dRdB=dRdB)
    return (R, Rc) if return_clean else R
