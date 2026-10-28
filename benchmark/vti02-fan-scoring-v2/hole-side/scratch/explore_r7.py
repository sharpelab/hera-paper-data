import numpy as np, sys
sys.path.insert(0, '..'); sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
t = [x for x in load_all(include_ramp=False) if x['id'] == '0822-r7'][0]
B, R = t['B'], t['R']
def fft(B, R, lo, hi, deg=5, nfft=8192):
    s = (B >= lo) & (B <= hi); b, y = B[s], R[s]
    y = y - np.polyval(np.polyfit(b, y, deg), b)
    u = 1 / b; o = np.argsort(u); u, y = u[o], y[o]
    uu = np.linspace(u[0], u[-1], len(u)); yy = np.interp(uu, u, y)
    w = np.hanning(len(uu)); F = np.fft.rfftfreq(nfft, uu[1] - uu[0]); S = np.abs(np.fft.rfft((yy - yy.mean()) * w, nfft))
    return F, S, 1 / (u[-1] - u[0]), len(uu)
fig, ax = plt.subplots(3, 1, figsize=(9, 11))
ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel('B'); ax[0].set_ylabel('R')
ax[1].plot(1 / B[B > 0.8], R[B > 0.8], lw=0.7); ax[1].set_xlabel('1/B')
for lo, hi in [(0.5, 5), (1, 5), (1, 4), (0.75, 3), (1.5, 5), (2, 10), (1, 10), (4.5, 10)]:
    F, S, dF, m = fft(B, R, lo, hi)
    k = (F > 0.5) & (F < 40)
    ax[2].plot(F[k], S[k] / np.median(S[k]), lw=0.8, label=f'[{lo},{hi}] dF {dF:.2f}')
    # peaks
    s = S / np.median(S[k]); pk = [i for i in range(1, len(F) - 1) if k[i] and s[i] > s[i - 1] and s[i] >= s[i + 1] and s[i] > 4]
    pk = sorted(pk, key=lambda i: -s[i])[:8]
    print(f'[{lo},{hi}] dF {dF:.2f} rows {m}:', ', '.join(f'{F[i]:.2f}({s[i]:.0f})' for i in sorted(pk)))
ax[2].legend(fontsize=7); ax[2].set_xlim(0, 40); ax[2].set_yscale('log')
for x in (1.72, 4.72, 6.59, 9.38, 14.83): ax[2].axvline(x, color='k', lw=0.3)
fig.savefig('scratch/r7_explore.png', dpi=90)
