"""Ideal-observer core: forward models (H_B ABAB / H_R ABCA) through vti02_sim's Landau-level physics, expected
acquisition (SR830 step response at the design's timing, clip mask), per-point noise variance from vti_noise
(white, 4.998 Hz comb with random phase, gate-step jitter, 2 f_ref ripple, optional band; quantization as a
Fisher-equivalent variance), the ABCA-explainable span per column, and the profiled KL per column.
Imports vti02_sim / vti_noise / tone_fn read-only."""
import sys, json, warnings
from pathlib import Path
import numpy as np
from scipy.stats import norm
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
TOP = Path('/data/sharpelab/hera-data/vti02-fan-scoring-v2')
sys.path[:0] = [str(TOP / 'synth-calibrate'), str(TOP / 'model-reconcile'), '/data/sharpelab/hera-data/vti-noise/generator']
import vti02_sim as vs
import vti_noise as vn
import tone_fn as TF
HERE = Path(__file__).resolve().parent
P0 = vs.load_params()
FLN = 10.3392
N_LO, N_HI = 0.35, 3.45            # electron columns the simulator + tone tables cover
DN_DVG = 2.6                       # 1e12 cm^-2 per V of the fast gate (vti02_sim_vn)
_AB = np.array(json.load(open(HERE / 'abca_table.json'))['rows'])


# ---------------------------------------------------------------- hypotheses

def abca_mass(n):
    return float(np.interp(n, _AB[:, 0], _AB[:, 2]))


def hyp_fns(hyp, tones='Halder_ABAB'):
    """(tone_fn, mass_fn) for vti02_sim.clean_R. H_B: two g = 4 pockets (light, heavy = F_L - light) with Halder
    masses; tones may be an envelope model (env_lo / env_hi) with Halder masses. H_R: a single g = 4 pocket at
    F_L = (h/4e) n with the ABCA mass (clean_R drops the empty light band; level width = heavy width)."""
    if hyp == 'B':
        def t(n):
            f, h, _ = TF.tone_fn(float(n), 'e', tones, warn=False)
            return (f, h) if f > 0.05 else (0.0, FLN * n)

        def m(n):
            ml, mh = TF.mstar_fn(float(n), 'e', 'Halder_ABAB')
            return max(ml, 1e-3), mh
        return t, m
    return (lambda n: (0.0, FLN * n)), (lambda n: (1e-3, abca_mass(float(n))))


def clean_map(Brc, n, hyp, nu):
    """Noise-free R[row, col] (ohm). Brc: [rows, cols] field of every point (ramps differ per column)."""
    p = dict(P0, T_K=nu.get('T_K', P0['T_K']), g_l=P0['g_l'] * nu.get('wscale', 1.0), g_h=P0['g_h'] * nu.get('wscale', 1.0),
             mass_scale_l=nu.get('mscale', 1.0), mass_scale_h=nu.get('mscale', 1.0))
    p.update(nu.get('p', {}))
    tf, mf = hyp_fns(hyp, nu.get('tones', 'Halder_ABAB'))
    s = nu.get('n_scale', 1.0)
    R = np.empty(Brc.shape)
    same = np.all(Brc == Brc[:, :1])
    if same:
        return vs.clean_R(Brc[:, 0], n, p, tf, mf, s)
    for j in range(Brc.shape[1]):
        R[:, j] = vs.clean_R(Brc[:, j], [n[j]], p, tf, mf, s)[:, 0]
    return R


# ---------------------------------------------------------------- acquisition

def timing(d, rng=None):
    """Reading times [rows, cols] and the field of every point (ramps ride the magnet)."""
    rng = rng or np.random.default_rng(0)
    B = d['B']
    if d.get('ramp'):
        r = d['ramp']
        rows = r['rows']
        t = vn.timestamps(np.zeros(rows), d['nc'], d['fd'], 1.0, 0.0, rng, ramp=True)
        Brc = np.minimum(r['start'] + r['rate_T_per_s'] * t, r['target'])
        return t, Brc
    t = vn.timestamps(B, d['nc'], d['fd'], 1.0, d['slow_delay'], rng)
    return t, np.repeat(B[:, None], d['nc'], 1)


def weights(d):
    return vn.step_weights(d['fd'], vn.point_period(d['fd'], 1.0), d['tau'], 24)


def blur(M, w):
    """SR830 step response along the fast axis (acquisition order = column order); row starts settled."""
    out = np.zeros_like(M)
    nc = M.shape[1]
    for k, wk in enumerate(w):
        out += wk * M[:, np.maximum(np.arange(nc) - k, 0)]
    return out


def _qfisher_table():
    """Average Fisher information of a uniformly offset, unit-LSB quantized Gaussian, relative to 1/sigma^2."""
    xs = np.geomspace(0.02, 3.0, 60)
    out = []
    for x in xs:
        mus = (np.arange(64) + 0.5) / 64
        edges = np.arange(-40, 41) + 0.5
        fi = []
        for mu in mus:
            a = (edges - mu) / x
            p = np.diff(norm.cdf(a)); dp = -np.diff(norm.pdf(a)) / x
            ok = p > 1e-300
            fi.append(np.sum(dp[ok] ** 2 / p[ok]))
        out.append(np.mean(fi) * x ** 2)
    return xs, np.minimum(np.array(out), 1.0)


_QX, _QR = _qfisher_table()


def quant_ratio(sig_over_lsb):
    x = np.asarray(sig_over_lsb, float)
    r = np.interp(np.log(np.maximum(x, _QX[0])), np.log(_QX), _QR)
    return np.where(x < _QX[0], _QR[0] * x / _QX[0], r)


def noise_var(d, Brc, Rc, n, Q=1.0, band=False, parts=('white', 'comb', 'jitter', 'ripple'), quant=True):
    """Per-point X-channel variance (V^2) at the design's settings; comb/band as incoherent per point
    (random phase per row, independent across rows)."""
    s = dict(tau=d['tau'], slope=24, f_ref=d.get('f_ref', 13.777), I=d['I'], sens=d['sens'], nplc=1, ramp=bool(d.get('ramp')),
             comb_scale=Q, band=band)
    dR = np.gradient(Rc, n, axis=1) if n.size > 2 else np.zeros_like(Rc)
    ps = vn.point_sigma(s, Brc, R=Rc, dRdVg=dR * DN_DVG)
    v = np.zeros(Rc.shape)
    for k in parts + (('band',) if band else ()):
        if k in ps:
            v = v + np.broadcast_to(np.asarray(ps[k]) ** 2, Rc.shape)
    if quant and d['sens']:
        lsb = vs.lsb(d['sens'])
        v = v / quant_ratio(np.sqrt(v) / lsb)
    return v


# ---------------------------------------------------------------- ABCA-explainable span + KL

def _leg(x, deg):
    x = np.asarray(x, float)
    lo, hi = x.min(), x.max()
    z = 2 * (x - lo) / (hi - lo) - 1 if hi > lo else np.zeros_like(x)
    return np.polynomial.legendre.legvander(z, deg)


def span_basis(Bcol_by_k, FL_by_k, w, M=4, Qe=2, pdeg=None, udeg=0):
    """Column basis: Legendre poly in B (live-check degree: 5, or 3 below 30 rows) + for m = 1..M the harmonics
    cos/sin(2 pi m F_L / B) times Legendre(1/B) of degree Qe, each blurred with the step weights over the
    neighbours (shared coefficients). Bcol_by_k[k], FL_by_k[k]: field rows and F_L of the column k steps back."""
    B0 = Bcol_by_k[0]
    nr = B0.size
    pdeg = pdeg if pdeg is not None else (3 if nr < 30 else 5)
    cols = [_leg(B0, pdeg)] + ([_leg(1 / B0, udeg)[:, 1:]] if udeg else [])
    osc = 0
    for k, wk in enumerate(w):
        Bk, Fk = Bcol_by_k[k], FL_by_k[k]
        u = 1 / Bk
        E = _leg(u, Qe)
        parts = []
        for m in range(1, M + 1):
            ph = 2 * np.pi * m * Fk * u
            parts += [E * np.cos(ph)[:, None], E * np.sin(ph)[:, None]]
        osc = osc + wk * np.hstack(parts) if M else osc
    if M:
        cols.append(osc)
    return np.hstack(cols)


def kl_columns(dmu, var, Brc, n_act, w, mask=None, M=4, Qe=2, return_resid=False, J=None):
    """Per-column profiled KL (nats): 0.5 min_beta || (dmu - X beta) / sigma ||^2 over the ABCA span.
    dmu, var: [rows, cols] V and V^2. n_act: actual-frame densities (F_L = 10.3392 n)."""
    nr, nc = dmu.shape
    kl = np.zeros(nc); res = np.zeros_like(dmu); dof = np.zeros(nc, int)
    K = len(w)
    for j in range(nc):
        idx = [max(j - k, 0) for k in range(K)]
        X = span_basis([Brc[:, i] for i in idx], [FLN * n_act[i] for i in idx], w, M, Qe)
        if J is not None:
            X = np.hstack([X] + [Jk[:, j:j + 1] for Jk in J])
        ok = np.ones(nr, bool) if mask is None else mask[:, j]
        if ok.sum() < 3:
            continue
        s = 1 / np.sqrt(var[ok, j])
        Xw = X[ok] * s[:, None]; yw = dmu[ok, j] * s
        beta, *_ = np.linalg.lstsq(Xw, yw, rcond=1e-10)
        r = yw - Xw @ beta
        kl[j] = 0.5 * r @ r
        dof[j] = np.linalg.matrix_rank(Xw, tol=1e-8 * np.abs(Xw).max())
        res[ok, j] = r
    return (kl, res, dof) if return_resid else kl


# ---------------------------------------------------------------- the systematic (mimic) cap

def capped_kl(res, kl, sigma_a=1.0):
    """Evidence with a per-column mimic systematic: the discriminating pattern r_j (whitened residual) carries an
    amplitude error a ~ N(0, sigma_a^2 K), K_jj' = normalized overlap <r_j, r_j'> of the columns' patterns
    (a systematic that mimics one column mimics another in proportion to how alike their patterns are).
    d'^2 = z^T (I + sigma_a^2 Z K Z)^-1 z with z_j = sqrt(2 KL_j), Z = diag(z); KL = d'^2 / 2.
    High-SNR limit: 0.5 * 1^T K^-1 1 / sigma_a^2 (half a nat per independent pattern at sigma_a = 1)."""
    z = np.sqrt(2 * np.maximum(kl, 0))
    ok = z > 1e-6
    if ok.sum() == 0:
        return 0.0, 0.0
    r = res[:, ok] / z[ok][None, :]
    Kmat = r.T @ r
    zz = z[ok]
    A = np.eye(zz.size) + sigma_a ** 2 * (zz[:, None] * Kmat * zz[None, :])
    d2 = zz @ np.linalg.solve(A, zz)
    ev, _ = np.linalg.eigh(Kmat)
    n_eff = (ev.sum() ** 2) / (ev ** 2).sum()           # participation ratio of the pattern Gram matrix
    return 0.5 * d2, n_eff


# ---------------------------------------------------------------- tone-level observer (clutter as noise)

def tone_basis(Bcol_by_k, F_by_k, w, Qe=2):
    """Blurred tone basis: for each (F, m) the cos/sin(2 pi m F / B) x Legendre(1/B) degree Qe, shared
    coefficients over the step-response neighbours. F_by_k[k]: list of (F, m) of the column k steps back."""
    out = 0
    for k, wk in enumerate(w):
        u = 1 / Bcol_by_k[k]
        E = _leg(u, Qe)
        parts = []
        for F, m in F_by_k[k]:
            ph = 2 * np.pi * m * F * u
            parts += [E * np.cos(ph)[:, None], E * np.sin(ph)[:, None]]
        if parts and (k == 0 or np.ndim(out) == 2 and np.hstack(parts).shape == out.shape):
            out = out + wk * np.hstack(parts)
    return out


def _smooth(x, h=3):
    k = np.ones(2 * h + 1)
    num = np.convolve(x, k, 'same'); den = np.convolve(np.ones_like(x), k, 'same')
    return num / den


def tone_kl(muB, muR, var, Brc, n_act, FL_tones, w, mask=None, M=4, Qe=2, clutter=True, h=3, udeg=0):
    """Per column: X_R = poly(B) + F_L harmonics m <= M (the ABCA-explainable span); X_T = the H_B tones
    (FL_tones[j] = [(F, m), ...]: light m = 1, 2 and heavy m = 1). Fit muB - muR on [X_R, X_T]; the clutter C is
    what neither explains (QH non-linearity, combination tones, the two models' different F_L-tone shapes), and
    enters as extra per-point variance (locally smoothed C^2) - the analyst has no trustworthy model of it.
    KL_j = 0.5 || T_perp ||^2 in the metric (noise + clutter), T = X_T beta_T, T_perp = T minus its projection on
    X_R. Returns kl[cols], whitened T_perp[rows, cols], clutter/noise variance ratio (median per column)."""
    nr, nc = muB.shape
    kl = np.zeros(nc); pat = np.zeros((nr, nc)); cr = np.zeros(nc)
    K = len(w)
    y_all = muB - muR
    for j in range(nc):
        idx = [max(j - k, 0) for k in range(K)]
        if not FL_tones[j]:
            continue
        Bk = [Brc[:, i] for i in idx]
        XR = span_basis(Bk, [FLN * n_act[i] for i in idx], w, M, Qe, udeg=udeg)
        XT = tone_basis(Bk, [FL_tones[i] for i in idx], w, Qe)
        ok = np.ones(nr, bool) if mask is None else mask[:, j].copy()
        if ok.sum() < 4 or np.ndim(XT) < 2:
            continue
        v = var[:, j].copy()
        X = np.hstack([XR, XT]); y = y_all[:, j]
        for it in range(2 if clutter else 1):
            s = 1 / np.sqrt(v[ok])
            beta, *_ = np.linalg.lstsq(X[ok] * s[:, None], y[ok] * s, rcond=1e-10)
            if clutter and it == 0:
                C = np.zeros(nr); C[ok] = y[ok] - X[ok] @ beta
                vc = _smooth(C ** 2, h)
                cr[j] = np.median(vc[ok] / var[ok, j])
                v = var[:, j] + vc
        T = XT @ beta[XR.shape[1]:]
        s = 1 / np.sqrt(v[ok])
        XRw = XR[ok] * s[:, None]; Tw = T[ok] * s
        g, *_ = np.linalg.lstsq(XRw, Tw, rcond=1e-10)
        r = Tw - XRw @ g
        kl[j] = 0.5 * r @ r
        pat[ok, j] = r
    return kl, pat, cr


def hb_tones(n, nu, light2=False):
    """[(F, m)] H_B tone list at actual-frame n under nuisance nu (light m = 1, 2; heavy m = 1); [] if single pocket."""
    tf, _ = hyp_fns('B', nu.get('tones', 'Halder_ABAB'))
    s = nu.get('n_scale', 1.0)
    out = []
    for x in n:
        fl, fh = tf(x * s)
        out.append([(fl, 1), (fh, 1)] + ([(fl, 2)] if light2 else []) if fl > 0 else [])
    return out


# ---------------------------------------------------------------- resolution-kernel evidence (the cap)

def w_eff(pat, Brc):
    """Effective aperture in 1/B of each column's discriminating pattern: sqrt(12) x the energy-weighted sd of u
    (= the window W for a flat-envelope tone). This is the Fourier resolution the data actually have."""
    u = 1 / Brc
    e = pat ** 2
    tot = e.sum(0)
    m = (e * u).sum(0) / np.where(tot > 0, tot, 1)
    v = (e * (u - m) ** 2).sum(0) / np.where(tot > 0, tot, 1)
    return np.sqrt(12 * v)


def evidence(kl, fl, weff, sigma_a=1.0, zmin=1e-3):
    """Nats of evidence with a mimic systematic of relative amplitude sigma_a whose column-to-column correlation is
    exp(-|x_i - x_j| / l), x = cumulative F_light x W_eff along the columns sorted by F_light, l = 1/2: two columns
    are the same 'cell' when their light tones sit within one Fourier resolution 1/W_eff. The exponential (OU) kernel
    counts cells: 1^T K^-1 1 -> 1 + span(F_light W_eff) as columns densify. d'^2 = z^T (I + sigma_a^2 Z K Z)^-1 z,
    z_j = sqrt(2 KL_j); returns (nats = d'^2 / 2, cells = 1^T K^-1 1 over active columns, active columns)."""
    z = np.sqrt(2 * np.maximum(kl, 0))
    ok = (z > zmin) & (fl > 0) & np.isfinite(weff)
    if ok.sum() == 0:
        return 0.0, 0.0, 0
    o = np.argsort(fl[ok])
    f, W, zz = fl[ok][o], weff[ok][o], z[ok][o]
    x = np.r_[0.0, np.cumsum(np.diff(f) * 0.5 * (W[1:] + W[:-1]))]
    Kmat = np.exp(-2.0 * np.abs(x[:, None] - x[None, :]))
    A = np.eye(zz.size) + sigma_a ** 2 * zz[:, None] * Kmat * zz[None, :]
    d2 = zz @ np.linalg.solve(A, zz)
    cells = np.ones(zz.size) @ np.linalg.solve(Kmat + 1e-9 * np.eye(zz.size), np.ones(zz.size))
    return 0.5 * d2, cells, int(ok.sum())


def nyquist_mask(Brc, n_act, rows_per_period=2.0):
    """Points where F_L is sampled at >= rows_per_period rows per period locally in 1/B (per column, both
    neighbouring steps). Used for the analyst-exploitable variant: aliased tones need exact-frequency fits."""
    m = np.zeros(Brc.shape, bool)
    for j in range(Brc.shape[1]):
        u = 1 / Brc[:, j]; o = np.argsort(u); us = u[o]
        du = np.diff(us)
        loc = np.maximum(np.r_[du[:1], du], np.r_[du, du[-1:]]) if us.size > 1 else np.array([np.inf])
        ok = FLN * n_act[j] * loc <= 1.0 / rows_per_period
        m[o, j] = ok
    return m
