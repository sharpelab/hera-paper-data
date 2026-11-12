"""Cross-column noise check: KL with the per-column diagonal noise vs the exact row-block covariance (white noise
correlated along the fast axis at the real timestamps, comb coherent within a row with random phase per row,
jitter / ripple diagonal). Rows are independent (row gaps >= 5.5 s >> tau; comb phase random per row).
-> check2d.csv"""
import sys, pickle
import numpy as np, pandas as pd
from scipy.linalg import expm, solve_continuous_lyapunov, cholesky, solve_triangular
import io_core as C
vn = C.vn
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}


def white_acf(tau, slope=24, smax=None, ns=4000):
    n = slope // 6
    A = (-np.eye(n) + np.eye(n, k=-1)) / tau
    b = np.zeros(n); b[0] = 1 / tau
    P = solve_continuous_lyapunov(A, -np.outer(b, b))
    s = np.linspace(0, smax or 60 * tau, ns)
    r = np.array([(expm(A * x) @ P)[-1, -1] for x in s]) / P[-1, -1]
    return s, r


def row_cov(d, t_row, B, Rrow, dRrow, Q=1.0, comb_mode='row'):
    """cols x cols X-channel covariance of one row (V^2)."""
    prm = vn.load_params()
    tau = d['tau']; fr = 13.777
    s, r = white_acf(tau)
    dt = np.abs(t_row[:, None] - t_row[None, :])
    sw2 = vn._e_n(prm, {}) ** 2 * vn.ENBW[24] / tau
    Cw = sw2 * np.interp(dt, s, r, right=0.0)
    st = dict(tau=tau, slope=24, f_ref=fr, I=d['I'], sens=d['sens'], comb_scale=Q)
    amps = vn.comb_amplitudes(st, np.array([B]), prm)
    f0 = prm['comb']['f0_Hz']['H']
    Cc = np.zeros_like(Cw)
    for k, a in amps.items():
        a = float(np.atleast_1d(a)[0])
        for f in (k * f0 - fr, k * f0 + fr):
            Cc += 0.5 * a ** 2 * vn.H2(f, tau, 24) * np.cos(2 * np.pi * f * (t_row[:, None] - t_row[None, :]))
    gj = prm['gate_jitter']
    dj = d['I'] ** 2 * ((gj['eps_R'] * np.abs(Rrow)) ** 2 + (np.abs(dRrow) * C.DN_DVG * gj['dVg_V']) ** 2)
    dr = d['I'] ** 2 * Rrow ** 2 * 0.5 * vn.H2(2 * fr, tau, 24)
    return Cw + Cc + np.diag(dj + dr)


def run(lab, M=3, Qe=1):
    d = dict(D[lab]); n = d['n'][(d['n'] >= C.N_LO) & (d['n'] <= C.N_HI)]; d['nc'] = n.size
    t, Brc = C.timing(d); w = C.weights(d); I = d['I']
    RB = C.clean_map(Brc, n, 'B', {}); RR = C.clean_map(Brc, n, 'R', {})
    muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    var = C.noise_var(d, Brc, RB, n, quant=False)
    tones = C.hb_tones(n, {})
    kl_diag, _, _ = C.tone_kl(muB, muR, var, Brc, n, tones, w, M=M, Qe=Qe, clutter=False)
    nr, nc = muB.shape
    dR = np.gradient(RB, n, axis=1)
    # bases, block per column, stacked into the full (row-major) space
    XR_blocks, XT_blocks = [], []
    for j in range(nc):
        idx = [max(j - k, 0) for k in range(len(w))]
        Bk = [Brc[:, i] for i in idx]
        XR_blocks.append(C.span_basis(Bk, [C.FLN * n[i] for i in idx], w, M, Qe))
        XT_blocks.append(C.tone_basis(Bk, [tones[i] for i in idx], w, Qe) if tones[j] else np.zeros((nr, 0)))
    def full(blocks):
        p = sum(b.shape[1] for b in blocks); X = np.zeros((nr, nc, p)); c = 0
        for j, b in enumerate(blocks):
            X[:, j, c:c + b.shape[1]] = b; c += b.shape[1]
        return X
    XR, XT = full(XR_blocks), full(XT_blocks)
    y = (muB - muR)
    out = {}
    for mode in ('diag', 'rowblock'):
        yw = np.empty_like(y); XRw = np.empty_like(XR); XTw = np.empty_like(XT)
        for i in range(nr):
            if mode == 'diag':
                L = np.diag(np.sqrt(var[i]))
            else:
                Cm = row_cov(d, t[i], Brc[i, 0], RB[i], dR[i])
                L = cholesky(Cm + 1e-30 * np.eye(nc), lower=True)
            yw[i] = solve_triangular(L, y[i], lower=True)
            XRw[i] = solve_triangular(L, XR[i], lower=True)
            XTw[i] = solve_triangular(L, XT[i], lower=True)
        Y = yw.reshape(-1); A = XRw.reshape(nr * nc, -1); T = XTw.reshape(nr * nc, -1)
        beta, *_ = np.linalg.lstsq(np.hstack([A, T]), Y, rcond=1e-10)
        Tf = T @ beta[A.shape[1]:]
        g, *_ = np.linalg.lstsq(A, Tf, rcond=1e-10)
        r = Tf - A @ g
        out[mode] = 0.5 * r @ r
    # white-noise neighbour correlation at the design's timing
    s, rr = white_acf(d['tau'])
    rho1 = float(np.interp(vn.point_period(d['fd'], 1.0), s, rr))
    return dict(label=lab, tau=d['tau'], fd=d['fd'], rho_white_neighbour=rho1, KL_percol_diag=kl_diag.sum(),
                KL_full_diag=out['diag'], KL_full_rowblock=out['rowblock'], ratio_rowblock_over_diag=out['rowblock'] / out['diag'])


if __name__ == '__main__':
    rows = [run(l) for l in (sys.argv[1:] or ['live 0822-r8', 'live 0821-r8', 'live 0824-r4'])]
    df = pd.DataFrame(rows); df.to_csv('check2d.csv', index=False, float_format='%.5g'); print(df.to_string())
