"""Hole- vs electron-side density frame from the QH Landau-level fan (R minima along n at fixed B).
For each fan row with B in the window, R(n) minima (log R minus a running mean) are collected; per side,
(s, n0) maximise the mean cos(2 pi nu / 4) with nu = s (n_frame - n0) 41.357 / B (4-fold LLs at D = 0).
Bootstrap over rows gives the spread.  Writes ll_frames.csv."""
import sys
import numpy as np, pandas as pd
from scipy.signal import argrelextrema
from scipy.ndimage import uniform_filter1d
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import read, _base, col, nframe

H_E = 41.357   # h/e in T per 1e12 cm^-2


def fan(session, run):
    meta, X = read(session, run)
    I, R, B, T, lk = _base(session, run, meta, X)
    nf = len(meta['fast_setpoints'][0]); nr = X.shape[0] // nf
    rs = lambda a: a[:nr * nf].reshape(nr, nf)
    return nframe(session, rs(col(meta, X, 'k_2400_tg_volt')), rs(col(meta, X, 'k_2400_bg_volt'))), rs(R), rs(B)


def minima(n, R, B, bwin, smooth):
    rows = []
    for i in range(n.shape[0]):
        b = np.median(B[i])
        if not bwin[0] <= b <= bwin[1]:
            continue
        o = np.argsort(n[i]); x = n[i][o]; y = np.log(np.clip(np.abs(R[i][o]), 5, None)); bb = B[i][o]
        yb = y - uniform_filter1d(y, smooth, mode='nearest')
        for j in argrelextrema(yb, np.less, order=2)[0]:
            rows.append((i, x[j], bb[j]))
    return np.array(rows)


def fit(m, S=np.arange(0.70, 1.10, 0.0025), N0=np.arange(-0.30, 0.30, 0.005)):
    nu = S[:, None, None] * (m[None, None, :, 1] - N0[None, :, None]) * H_E / m[None, None, :, 2]
    sc = np.cos(2 * np.pi * nu / 4).mean(axis=2)
    i, j = np.unravel_index(np.argmax(sc), sc.shape)
    return S[i], N0[j], sc[i, j], sc


if __name__ == '__main__':
    rng = np.random.default_rng(0)
    out = []
    for s, r, bwin, sm, cut in (('0823', 6, (1.0, 4.5), 9, 0.25), ('0824', 4, (0.9, 4.5), 5, 0.25)):
        n, R, B = fan(s, r)
        m = minima(n, R, B, bwin, sm)
        for side, sel in (('h', m[:, 1] < -cut), ('e', m[:, 1] > cut)):
            mm = m[sel]
            s0, n00, v, sc = fit(mm)
            rows = np.unique(mm[:, 0]); bs = []
            for _ in range(200):
                pick = rng.choice(rows, rows.size)
                sub = np.concatenate([mm[mm[:, 0] == k] for k in pick])
                bs.append(fit(sub)[:2])
            bs = np.array(bs)
            prof = sc.max(axis=1)
            out.append(dict(session=s, run=r, side=side, B_window=f'{bwin[0]}-{bwin[1]}', n_frame_range=f'{mm[:, 1].min():.2f}..{mm[:, 1].max():.2f}',
                            minima=len(mm), s=round(s0, 4), s_boot_sd=round(bs[:, 0].std(), 4), n0=round(n00, 3), n0_boot_sd=round(bs[:, 1].std(), 3),
                            comb_score=round(v, 3), runner_up_s=round(float(np.arange(0.70, 1.10, 0.0025)[np.argsort(prof)[-8:]].min()), 3)))
            print(out[-1])
    df = pd.DataFrame(out); df.to_csv('ll_frames.csv', index=False)
