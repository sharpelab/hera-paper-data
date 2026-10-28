import numpy as np, warnings
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_fft
h, e = 6.62607015e-34, 1.602176634e-19

def RB(rid):
    r = open_run(f'data/{rid}'); B = r.col('magnet_field'); I = r.col('sr0_X')/(-1e6)
    R = (r.col('sr1_X')/1.0)/I; o = np.argsort(B); return B[o], R[o]

fig, axes = plt.subplots(4, 1, figsize=(13, 13))
for row, (rid, n_nom) in enumerate([(6, 3.2), (7, -1.2)]):
    B, R = RB(rid)
    FT = abs(n_nom)*1e16*h/(4*e)
    m = B >= 1.0
    b, r_ = B[m], R[m]
    bg = np.polyval(np.polyfit(b, r_, 5), b)
    d = r_ - bg
    ax = axes[2*row]
    ax.plot(1/b, d, lw=.9, color='k')
    # minima of raw R above 2 T = QH minima
    mm = b >= 2.0
    pk, _ = find_peaks(-d[mm], prominence=np.std(d[mm])*0.8)
    invb = (1/b[mm])[pk]
    ax.plot(invb, d[mm][pk], 'rv', ms=5)
    ax.set_xlabel('1/B (1/T)'); ax.set_ylabel('dRxx (Ohm)')
    ax.set_title(f'run {rid} n={n_nom:+.1f}e12  detrended vs 1/B; F_total(4-fold)={FT:.1f} T; red = minima (B>2T)')
    # index the minima: spacing in 1/B
    invb = np.sort(invb)
    dd = np.diff(invb)
    print(f'--- run {rid}: {len(invb)} minima above 2 T')
    print('    B of minima :', np.round(1/invb, 3)[::-1])
    print('    nu = 4*FT*(1/B):', np.round(4*FT*invb, 2)[::-1])
    print('    1/B spacings  :', np.round(dd, 4), ' -> F=1/spacing:', np.round(1/dd, 2))
    # fit index vs 1/B
    idx = np.arange(len(invb))
    p = np.polyfit(invb, idx, 1)
    print(f'    index vs 1/B slope (=F) = {p[0]:.2f} T, intercept {p[1]:.2f}; resid rms {np.std(idx-np.polyval(p,invb)):.3f}')
    ax = axes[2*row+1]
    for blo, bhi, c in [(1.0,10.0,'C0'), (3.0,10.0,'C1'), (4.0,10.0,'C2'), (6.0,10.0,'C3')]:
        f, spec = sdh_fft(R[:,None], B, b_range=(blo,bhi), nfft=16384, bg_degree=5, log=False)
        s = spec[0]; k = (f>1)&(f<70)
        ax.plot(f[k], s[k]/s[k].max(), color=c, lw=1, label=f'{blo}-{bhi} T (df {1/(1/blo-1/bhi):.1f})')
    for kk in range(1,7): ax.axvline(kk*7.35, color='gray', ls=':', lw=.7)
    ax.axvline(FT, color='r', ls='--', lw=1); ax.set_xlim(0,70); ax.legend(fontsize=7)
    ax.set_xlabel('F (T)'); ax.set_title('dotted = k x 7.35 T ladder; red dashed = F_total from gate cal')
plt.tight_layout(); plt.savefig('hera_scratch/spot_67_idx.png', dpi=110)
print('saved')
