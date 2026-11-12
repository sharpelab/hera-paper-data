"""Live-check FFT metrics (fft_q1.analyse + q1_eval definitions) on an arbitrary R map."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from fft_q1 import col_fft, band_peak, SIGV
from load import f_light, f_heavy, f_L

RFIT = (0.0394, 0.1235)   # q1_eval reference light fraction (0825 full window)


def analyse_arr(R, B, n_act, I, sigv, lo_req, hi_req=None, tag='', thr=4.0):
    lo = max(lo_req, B.min()); hi = min(hi_req or B.max(), B.max())
    rows = []
    for j in range(R.shape[1]):
        n = n_act[j]
        if n < 0.3:
            continue
        F, S, m, du, wn = col_fft(R[:, j], B, lo, hi)
        nyq = 0.5 / du; span = 1 / lo - 1 / hi; dF = 1 / span
        fl, fL = f_light(n), f_L(n)
        floor_a = sigv / I * wn * np.sqrt(np.log(2))
        hb = (F > 1.12 * fL) & (F < 0.95 * nyq)
        floor_b = np.median(S[hb]) if hb.sum() > 20 else np.nan
        floor = floor_b if np.isfinite(floor_b) else floor_a
        pl = band_peak(F, S, 0.08 * fL, 0.33 * fL)
        ph = band_peak(F, S, 0.66 * fL, 0.895 * fL)
        pL = band_peak(F, S, 0.925 * fL, 1.08 * fL)
        sep = np.nan
        if np.isfinite(ph[0]) and np.isfinite(pL[0]):
            k = (F > ph[0]) & (F < pL[0]); sep = S[k].min() / min(ph[1], pL[1]) if k.any() else 1.0
        rows.append(dict(win=tag, col=j, n_act=n, F_L=fL, dF=dF, nyq=nyq, floor_noise=floor_a, floor_emp=floor_b,
                         floor=floor, Fpk_light=pl[0], A_light=pl[1], snr_light=pl[1] / floor,
                         Fpk_heavy=ph[0], A_heavy=ph[1], snr_heavy=ph[1] / floor, Fpk_FL=pL[0], A_FL=pL[1],
                         snr_FL=pL[1] / floor, dip=sep, span=span))
    df = pd.DataFrame(rows)
    df['det_light'] = (df.snr_light >= thr) & (df.Fpk_light >= 0.75 * df.dF)
    df['det_heavy'] = df.snr_heavy >= thr
    df['det_FL'] = df.snr_FL >= thr
    df['split_heavy_FL'] = df.det_heavy & df.det_FL & (df.dip < 0.8)
    df['F_light_ref'] = np.polyval(RFIT, df.n_act) * df.F_L
    df['k_light_ref'] = df.F_light_ref * df.span
    tol = np.maximum(0.5 * df.dF, 0.75)
    df['light_true'] = (df.snr_light >= 4) & ((df.Fpk_light - df.F_light_ref).abs() <= tol)
    df['split_true'] = df.split_heavy_FL & ((df.Fpk_FL - df.Fpk_heavy) >= 0.5 * df.dF)
    return df


def spectra(R, B, n_act, lo, hi=None):
    lo = max(lo, B.min()); hi = min(hi or B.max(), B.max())
    out = []
    for j in range(R.shape[1]):
        F, S, m, du, wn = col_fft(R[:, j], B, lo, hi)
        out.append((n_act[j], F, S))
    return out
