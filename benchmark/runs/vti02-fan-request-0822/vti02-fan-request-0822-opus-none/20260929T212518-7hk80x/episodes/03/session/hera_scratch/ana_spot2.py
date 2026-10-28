import numpy as np, warnings
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, sdh_onset, SdhOnsetError
h, e = 6.62607015e-34, 1.602176634e-19

def RB(rid):
    r = open_run(f'data/{rid}')
    B = r.col('magnet_field'); I = r.col('sr0_X')/(-1e6)
    R = (r.col('sr1_X')/1.0)/I
    o = np.argsort(B); return B[o], R[o]

def peaks(f, s, fmax):
    k = (f > 1.0) & (f < fmax)
    f, s = f[k], s[k]
    idx = [i for i in range(1, len(f)-1) if s[i] > s[i-1] and s[i] >= s[i+1]]
    idx = sorted(idx, key=lambda i: -s[i])[:8]
    out = []
    for i in idx:   # parabolic interpolation
        y0, y1, y2 = s[i-1], s[i], s[i+1]
        d = 0.5*(y0-y2)/(y0-2*y1+y2) if (y0-2*y1+y2) != 0 else 0
        out.append((f[i] + d*(f[1]-f[0]), s[i]/s[idx[0]]))
    return sorted(out)

for rid, n_nom in [(6, 3.2), (7, -1.2)]:
    B, R = RB(rid)
    FL = abs(n_nom)*1e16*h/(4*e)
    print(f'\n######## run {rid}  n_cal={n_nom:+.2f}e12  F_L(4-fold)={FL:.1f} T')
    # Nyquist-safe windows only (B>=1 T where step is 10/20 mT)
    for blo, bhi in [(1.0,10.0), (1.5,10.0), (2.0,10.0), (2.0,6.0), (5.0,10.0)]:
        f, spec = sdh_fft(R[:,None], B, b_range=(blo,bhi), nfft=8192, bg_degree=5, log=False)
        df = 1/(1/blo - 1/bhi)
        p = peaks(f, spec[0], 2.2*FL)
        print(f'  win {blo:4.1f}-{bhi:4.1f} T (df={df:5.2f} T): ' +
              '  '.join(f'{fp:6.2f}T({a:.2f})' for fp, a in p if a > 0.12))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        o = sdh_onset(R, B, b_lo=1.0, r_full_scale=50e-6/10e-9)
    print('  --- sdh_onset (b_lo=1.0 T, Nyquist-safe) ---')
    for ln in o.summary().splitlines(): print('   ', ln)
