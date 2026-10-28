import sys, time, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check'); sys.path.insert(0, '.')
from load import load
from llcore import rho_tensor
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = load('0825-r8'); B = d['B']; o = np.argsort(B)
fig, axs = plt.subplots(3, 1, figsize=(14, 11))
for ax, nl in zip(axs, (1.5, 2.1, 2.9)):
    j = np.argmin(abs(d['n'] - nl)); n = d['n'][j] * 0.95; FL = 10.3392 * n
    r = 0.0394 * d['n'][j] + 0.1235; Fl = r * FL; Fh = FL - Fl
    Bf = np.linspace(0.8, 8, 2000)
    t = time.time()
    rx, ry = rho_tensor(Bf, n, Fl, Fh, 0.025, 0.058, 8.0, 0.25, 0.25, 10.0, 10.0)
    print('time', time.time() - t)
    ax.plot(B[o], d['R'][o, j], 'k.-', lw=0.6, ms=3, label=f'0825 n_load={d["n"][j]:.2f}')
    ax.plot(Bf, rx, 'r-', lw=0.7, label='LL model rho_xx (G=1)')
    ax.legend(); ax.set_ylim(-20, 700)
fig.tight_layout(); fig.savefig('t1.png', dpi=70)
