import sys, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from load import load
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(2, 4, figsize=(20, 9))
for i, nm in enumerate(['0825-r8', '0822-r8', '0821-r8', '0824-r4']):
    d = load(nm); B = d['B']; R = d['R']; n = d['n']
    o = np.argsort(B); on = np.argsort(n)
    ax = axs[0, i]
    ax.pcolormesh(n[on], B[o], R[o][:, on], shading='nearest', vmin=0, vmax=np.nanpercentile(R, 97))
    ax.set_title(nm); ax.set_xlabel('n'); ax.set_ylabel('B')
    ax = axs[1, i]
    for j in np.linspace(0, len(n) - 1, 6).astype(int):
        ax.plot(B[o], R[o, j], lw=0.7, label=f'n={n[j]:.2f}')
    ax.set_yscale('symlog', linthresh=10); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig('look.png', dpi=70)
