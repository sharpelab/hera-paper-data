"""Empirical partition p(F_L) on the training points (electron, 08-25 + 08-22): weighted polynomial in x = F_L / 20 T.
Degree chosen by leave-one-session-out CV. CI: parametric covariance scaled to chi2/dof = 1 and inflated by
sqrt(N / N_eff) (same N_eff as fit.py). Outputs empirical.json."""
import json
import numpy as np, pandas as pd
P = pd.read_csv('partition_points.csv', dtype={'session': str})
TR = P[P.split == 'train']
cells = 0.0
for (s, t), g in TR.groupby(['session', 'tone']):
    F = g.y * g.F_L_ref if t == 'light' else (1 - g.y) * g.F_L_ref
    cells += max(1.0, (F.max() - F.min()) / g.dF.median())
infl = len(TR) / cells


def wfit(D, deg):
    x = D.F_L_ref.values / 20.0; w = 1 / D.sy.values
    A = np.vander(x, deg + 1)
    c, *_ = np.linalg.lstsq(A * w[:, None], D.y.values * w, rcond=None)
    r = (D.y.values - A @ c) * w
    chi = float(r @ r); dof = len(x) - deg - 1
    cov = np.linalg.inv((A * w[:, None]).T @ (A * w[:, None])) * max(chi / dof, 1.0) * infl
    return c, cov, chi, dof


def pred(c, cov, FL):
    A = np.vander(np.atleast_1d(FL) / 20.0, len(c))
    return A @ c, np.sqrt(np.einsum('ij,jk,ik->i', A, cov, A))


out = {}
for deg in (1, 2, 3):
    cv = []
    for s in ('0825', '0822'):
        c, cov, *_ = wfit(TR[TR.session != s], deg)
        T = TR[TR.session == s]
        cv.append(np.sqrt(np.mean((T.y - pred(c, cov, T.F_L_ref)[0]) ** 2)))
    c, cov, chi, dof = wfit(TR, deg)
    out[deg] = dict(coef=c.tolist(), cov=cov.tolist(), chi2=chi, dof=dof, loso_rmse=[float(v) for v in cv])
    print(f'deg {deg}: chi2 {chi:.1f}/{dof}, LOSO rmse 0825-out {cv[0]:.4f}, 0822-out {cv[1]:.4f}, coef {np.round(c, 4)}')
best = min(out, key=lambda d: np.mean(out[d]['loso_rmse']) + 0.002 * d)   # prefer the simpler on near-ties
out['best'] = best
json.dump(out, open('empirical.json', 'w'), indent=1)
print('chosen degree', best)
