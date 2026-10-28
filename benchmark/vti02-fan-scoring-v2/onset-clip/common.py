"""Shared loaders + per-tone matched-filter envelopes (hera.analysis internals, read-only import)."""
import sys, json, gzip, io, warnings, importlib.util
import numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'live-check'))
from load import load as load_fan, f_L          # live-check loader (read-only reuse)
spec = importlib.util.spec_from_file_location('ha', '/home/zack/sharpelab/measurement-env/src/hera/analysis.py')
ha = importlib.util.module_from_spec(spec); sys.modules['ha'] = ha; spec.loader.exec_module(ha)
M = json.load(open(HERE / 'masses.json'))
_mk = np.array(sorted(float(k) for k in M))
def mass(n, which):  # model ABAB masses (m_e), u_D = 0; which in m_l, m_h
    return float(np.interp(n, _mk, [M[f"{k:.1f}"][which] for k in _mk]))
ALPHA = 14.69           # 2 pi^2 k_B m_e / (hbar e), T/K
HBAR_2PI_KB = 1.2155    # hbar/(2 pi k_B) in ps*K: tau_q[ps] = 1.2155 / T_D[K]
RF = (0.0394, 0.1235)   # observed light fraction F_light/F_L = a n + b (live-check, 0825 [1, 8] T)
def tones_expected(n):
    FL = f_L(n); fl = (RF[0] * n + RF[1]) * FL
    return dict(light=fl, heavy=FL - fl, FL=FL)
S = Path('/home/zack/sharpelab/measurement-env/hera/docs/notes')
def load_run(sess, run):
    p = S / f'2026-08-{sess}-vti-02-session/data/{run}'
    meta = json.load(open(p / 'metadata.json')); cols = meta['columns']
    X = np.loadtxt(io.StringIO(gzip.decompress((p / 'data.tsv.gz').read_bytes()).decode()), delimiter='\t', ndmin=2)
    c = lambda nm: X[:, cols.index(nm)]
    mc = meta['measurement_config']; I = c('sr0_X') / mc['sr0_gain']
    return dict(meta=meta, B=c('magnet_field'), R=c('sr1_X') / I, I=I, tg=c('k_2400_tg_volt') if 'k_2400_tg_volt' in cols else None,
                T=c('T_sample') if 'T_sample' in cols else None,
                tau=meta['instruments']['sr1']['snapshot']['parameters']['time_constant']['value'])

def envelope(B, R, F, *, b_lo=0.3, b_hi=8.0, n_periods=3.0, ppp_min=3.0, snr_thr=5.0):
    """Fixed-frequency Gaussian matched-filter walk (ha._track_tone) for one tone.
    Keeps only rows where the tone is sampled at >= ppp_min points per period (local 1/B step)."""
    o = np.argsort(1 / B); B, R = B[o], R[o]
    u = 1 / B; du = np.gradient(u)
    ok = (B >= b_lo) & (B <= b_hi) & np.isfinite(R) & (1 / (F * np.abs(du)) >= ppp_min)
    # contiguous from high B down: stop at the first under-sampled row
    first_bad = np.where(~ok & (B <= b_hi) & (B >= b_lo))[0]
    keep = ok.copy()
    if first_bad.size: keep[first_bad[0]:] = False
    Bs, Rs = B[keep], R[keep]
    if Bs.size < 12: return None
    bg = ha._bg_subtract_B(Bs, Rs, 5)
    invB = 1 / Bs
    sig = ha._noise_sigma(bg)
    tr, why = ha._track_tone(invB, bg, F, sig, n_periods=n_periods, min_periods=2.0, step_frac=0.25, min_pts=8,
                             snr_threshold=snr_thr, gap_widths=0.5, marginal_mult=2.0)
    if tr is None: return dict(err=why, b_lo_rec=float(Bs.min()), sigma=sig)
    tr['b_lo_rec'] = float(Bs.min()); tr['sigma'] = sig; tr['npts'] = int(Bs.size)
    tr['du_med'] = float(np.median(np.abs(np.diff(invB))))
    return tr

def refine_freq(B, R, F0, tol, b_lo=1.0, b_hi=8.0):
    """FFT peak (Hann, uniform-resampled 1/B, 8x pad) within F0 +- tol over [b_lo, b_hi]."""
    o = np.argsort(1 / B); B, R = B[o], R[o]
    m = (B >= b_lo) & (B <= b_hi) & np.isfinite(R)
    if m.sum() < 16: return F0, 0.0
    bg = ha._bg_subtract_B(B[m], R[m], 5); inv = 1 / B[m]
    out = ha._win_fft(inv, bg, inv[0], inv[-1], 8)
    fr, sp, dF = out
    s = (fr >= F0 - tol) & (fr <= F0 + tol)
    if not s.any(): return F0, 0.0
    i = np.argmax(np.where(s, sp, -1)); return float(fr[i]), float(sp[i] / np.median(sp[fr > 3]))

def dingle_fit(tr, m, Te, b_max=4.0, snr_min=5.0):
    """Weighted LS of ln(A sinh X / X) vs 1/B over windows with SNR >= snr_min and B <= b_max,
    restricted to the connected track above the onset. Returns slope (T), T_D (K), intercept, n windows."""
    Bc, A, snr = tr['b_centers'], tr['amp'], tr['snr']
    sel = (snr >= snr_min) & (Bc <= b_max) & (Bc >= tr['onset_b'] - 1e-9)
    if sel.sum() < 3: return None
    u = 1 / Bc[sel]; X = ALPHA * m * Te * u
    y = np.log(A[sel] * np.sinh(X) / X); w = snr[sel]      # sigma(ln A) ~ 1/SNR
    W = np.diag(w ** 2); Xm = np.c_[np.ones_like(u), u]
    cov = np.linalg.inv(Xm.T @ W @ Xm); beta = cov @ Xm.T @ W @ y
    res = y - Xm @ beta; chi = float((w ** 2 * res ** 2).sum() / max(1, sel.sum() - 2))
    se = np.sqrt(np.diag(cov) * max(chi, 1.0))
    s = beta[1]; TD = -s / (ALPHA * m)
    return dict(c=float(beta[0]), slope=float(s), slope_se=float(se[1]), TD=float(TD), TD_se=float(se[1] / (ALPHA * m)),
                nwin=int(sel.sum()), u_lo=float(u.min()), u_hi=float(u.max()))
