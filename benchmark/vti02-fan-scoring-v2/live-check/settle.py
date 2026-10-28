"""Q4: settling. (a) retrace test: first point of each row vs extrapolation from points 1-3, regressed on the step
from the previous row's last reading; (b) same statistic at interior points, regressed on the local step (lag signature)."""
import numpy as np, sys, json
sys.path.insert(0, '.')
from load import load
from noise_q import load_qc
def unsettled(x):  # 4-pole step response remainder at t = x tau
    return np.exp(-x) * (1 + x + x**2 / 2 + x**3 / 6)
out = []
for d in [load(nm) for nm in ['0821-r8', '0822-r8', '0825-r8', '0824-r4']] + [load_qc()]:
    ch = 'sr1'; X = d['g'](ch + '_X'); t = d['t']; tau = d['lk'][ch]['time_constant']
    meta_fd = {'0821-r8': 0.7, '0822-r8': 1.2, '0825-r8': 2.1, '0824-r4': 0.7, 'QC0426-0619-r4': 1.0}[d['name']]
    dt = np.median(np.diff(t, axis=1))
    gap = np.median(t[1:, 0] - t[:-1, -1])
    # (a) retrace: e0 = x0 - (3x1 - 3x2 + x3); step = x_prev_last - x0_extrap
    ext = 3 * X[1:, 1] - 3 * X[1:, 2] + X[1:, 3]
    e0 = X[1:, 0] - ext; step = X[:-1, -1] - X[1:, 5:8].mean(1)
    A = np.c_[step, np.ones_like(step)]
    coef, *_ = np.linalg.lstsq(A, e0, rcond=None)
    # control: same extrapolation residual at an interior point j=10 regressed on (x[j-1]-extrap) -> should be ~0 if interior settled
    j = X.shape[1] // 2
    extj = 3 * X[:, j + 1] - 3 * X[:, j + 2] + X[:, j + 3]
    ej = X[:, j] - extj; sj = X[:, j - 5] - X[:, j + 5]
    cj, *_ = np.linalg.lstsq(np.c_[sj, np.ones_like(sj)], ej, rcond=None)
    # (b) interior lag: regress e_j on (x[j-1]-x[j]) over all interior j using symmetric curvature-free predictor
    print(f"{d['name']:15s} tau {tau} fast_delay {meta_fd} (={meta_fd/tau:.1f} tau) point spacing {dt:.2f}s  row gap {gap:.0f}s | "
          f"retrace: median |step| {np.median(np.abs(step))*1e9:.0f} nV, fitted unsettled fraction {coef[0]:+.3f} (corr {np.corrcoef(step, e0)[0,1]:+.2f}); "
          f"4-pole prediction at fast_delay {unsettled(meta_fd/tau):.3f}, at slow_delay+fd n/a | interior control slope {cj[0]:+.3f} (corr {np.corrcoef(sj, ej)[0,1]:+.2f})")
    out.append(dict(fan=d['name'], tau=tau, fd=meta_fd, fd_over_tau=meta_fd / tau, pred_unsettled=unsettled(meta_fd / tau), retrace_slope=coef[0], retrace_corr=np.corrcoef(step, e0)[0, 1], interior_slope=cj[0]))
json.dump(out, open('settle.json', 'w'), indent=1, default=float)
for x in (2, 3, 4, 5, 7, 10): print(f"4-pole unsettled fraction at {x} tau: {unsettled(x):.3f}")
