"""Parametric multi-tone Dingle fit per column over u = 1/B in [1/b_hi, 1/b_lo]:
   R(u) = poly3(u) + sum_j exp(s_j (u - u0)) * RT(m_j, Te, u) * (a_j cos 2pi F_j u + b_j sin 2pi F_j u)
tones: light, heavy, F_L (sum), 2*light, heavy-light (diff). Nonlinear: F_j (+-tol), s_j. Linear: a_j, b_j, poly (variable projection).
Free parameters per column: 5 F + 5 s (nonlinear) + 10 amplitudes + 4 poly = 24."""
import numpy as np, warnings
from scipy.optimize import least_squares
from common import ALPHA
def RT(m, Te, u):
    X = ALPHA * m * Te * u; return X / np.sinh(X)
def design(u, F, s, m, Te, u0):
    cols = [u ** k for k in range(4)]
    for Fj, sj, mj in zip(F, s, m):
        env = np.exp(sj * (u - u0)) * RT(mj, Te, u)
        cols += [env * np.cos(2 * np.pi * Fj * u), env * np.sin(2 * np.pi * Fj * u)]
    return np.array(cols).T
def fit(B, R, F0, m, Te=1.2, b_lo=1.0, b_hi=4.0, s0=None, ftol_frac=0.03):
    sel = (B >= b_lo) & (B <= b_hi) & np.isfinite(R)
    u = 1 / B[sel]; y = R[sel]; u0 = u.min()
    nt = len(F0); s0 = s0 if s0 is not None else [-ALPHA * mj * 3.0 for mj in m]
    def resid(p):
        F = p[:nt]; s = p[nt:]
        A = design(u, F, s, m, Te, u0); c, *_ = np.linalg.lstsq(A, y, rcond=None); return y - A @ c
    p0 = np.r_[F0, s0]
    lb = np.r_[[f * (1 - ftol_frac) for f in F0], [-40] * nt]; ub = np.r_[[f * (1 + ftol_frac) for f in F0], [3] * nt]
    r = least_squares(resid, p0, bounds=(lb, ub), x_scale=np.r_[[0.1] * nt, [1] * nt])
    F = r.x[:nt]; s = r.x[nt:]
    A = design(u, F, s, m, Te, u0); c, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ c; dof = max(1, y.size - (2 * nt + A.shape[1])); s2 = (res ** 2).sum() / dof
    J = r.jac
    try: cov = np.linalg.inv(J.T @ J) * s2; se = np.sqrt(np.diag(cov))
    except np.linalg.LinAlgError: se = np.full(2 * nt, np.nan)
    amp0 = [float(np.hypot(c[4 + 2 * k], c[5 + 2 * k])) for k in range(nt)]   # envelope amplitude at u0 (before RT)
    return dict(F=F, s=s, s_se=se[nt:], F_se=se[:nt], amp0=amp0, u0=u0, rms=float(np.sqrt(s2)), npts=int(y.size),
                u=u, y=y, yfit=A @ c, coef=c, cost=r.cost)
