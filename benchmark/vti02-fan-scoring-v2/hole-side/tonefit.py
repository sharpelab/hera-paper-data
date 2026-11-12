"""Parametric multi-tone fit of R(1/B): polynomial-in-1/B background (linear) + K damped cosines
A_k exp(-a_k (u - u0)) cos(2 pi F_k u + phi_k) (amplitudes/phases linear; F_k, a_k nonlinear, variable projection).
Rows are weighted by sqrt(du) so a uniform-B record counts like a uniform-1/B one.  Returns F, sigma_F, amplitude at
the window's high-B edge and at its low-B edge, decay a (per 1/T), residual rms, BIC."""
import numpy as np
from scipy.optimize import least_squares


def _design(u, F, a, deg, u0):
    cols = [((u - u0) / (u.max() - u0)) ** p for p in range(deg + 1)]
    for f, al in zip(F, a):
        e = np.exp(-al * (u - u0))
        cols += [e * np.cos(2 * np.pi * f * u), e * np.sin(2 * np.pi * f * u)]
    return np.array(cols).T


def fit(B, R, lo, hi, F0, deg=3, a0=None, fbound=0.35, amax=15.0):
    s = (B >= lo) & (B <= hi) & np.isfinite(R)
    u = 1 / B[s]; y = R[s]; o = np.argsort(u); u, y = u[o], y[o]
    du = np.gradient(u); w = np.sqrt(du / np.median(du))
    u0 = u.min(); K = len(F0)
    a0 = [1.0] * K if a0 is None else a0
    lo_b = [f * (1 - fbound) for f in F0] + [-3.0] * K
    hi_b = [f * (1 + fbound) for f in F0] + [amax] * K

    def res(p):
        X = _design(u, p[:K], p[K:], deg, u0) * w[:, None]
        c, *_ = np.linalg.lstsq(X, y * w, rcond=None)
        return X @ c - y * w

    p0 = np.array(list(F0) + list(a0), float)
    r = least_squares(res, p0, bounds=(lo_b, hi_b), x_scale='jac')
    p = r.x
    X = _design(u, p[:K], p[K:], deg, u0) * w[:, None]
    c, *_ = np.linalg.lstsq(X, y * w, rcond=None)
    N = u.size; npar = 2 * K + (deg + 1) + 2 * K
    rss = float(np.sum(r.fun ** 2)); sig2 = rss / max(N - npar, 1)
    J = r.jac
    try:
        cov = np.linalg.pinv(J.T @ J) * sig2
        se = np.sqrt(np.clip(np.diag(cov), 0, None))
    except Exception:
        se = np.full(p.size, np.nan)
    tones = []
    for k in range(K):
        A = float(np.hypot(c[deg + 1 + 2 * k], c[deg + 2 + 2 * k]))
        tones.append(dict(F=float(p[k]), sF=float(se[k]), a=float(p[K + k]), sa=float(se[K + k]), A_hiB=A,
                          A_loB=A * float(np.exp(-p[K + k] * (u.max() - u0))), at_bound=bool(abs(p[k] - lo_b[k]) < 1e-3 or abs(p[k] - hi_b[k]) < 1e-3)))
    rms = np.sqrt(rss / N)
    bic = N * np.log(rss / N) + npar * np.log(N)
    return dict(tones=tones, rms=float(rms), bic=float(bic), N=int(N), span=float(u.max() - u0), lo=float(1 / u.max()), hi=float(1 / u0))
