import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import spec, model, peaks
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
tr = [t for t in load_all(include_ramp=False, n_max=9) if t['id'].startswith('0824-r4-')]
tr = sorted(tr, key=lambda t: t['n_frame'])
fig, axs = plt.subplots(1, 2, figsize=(14, 7))
for ax, (lo, hi) in zip(axs, [(0.76, 6.0), (1.2, 6.0)]):
    Z = []; ns = []
    for t in tr:
        s = spec(t['B'], t['R'], lo, hi, 5, Fmax=25)
        fl = np.median(s['S'][(s['F'] > 12) & (s['F'] < 16)])
        Z.append(s['S'] / fl); ns.append(t['n_frame'])
        if lo == 0.76:
            pk = peaks(s['F'], s['S'] / fl, 0.8, 16, 3, 6)
            print(t['id'], f"n_fr {t['n_frame']:+.3f}", ' '.join(f'{f:.2f}({z:.0f})' for f, z in pk))
    Z = np.array(Z); F = s['F']; ns = np.array(ns)
    ax.pcolormesh(F, ns, np.log10(np.maximum(Z, 0.5)), shading='nearest', cmap='magma', vmin=0, vmax=2.0)
    for side, nn in (('h', np.linspace(-1.1, -0.3, 60)), ('e', np.linspace(0.3, 2.1, 60))):
        fl, fh, fL = model(np.abs(nn) * 0.9, side)
        ax.plot(fl, nn, 'c-', lw=0.8); ax.plot(fh, nn, color='lime', lw=0.8); ax.plot(fL, nn, 'w-', lw=0.8)
    ax.set_xlim(0, 20); ax.set_title(f'0824 r4 [{lo},{hi}] model s=0.9'); ax.set_xlabel('F'); ax.set_ylabel('n_frame')
fig.tight_layout(); fig.savefig('scratch/map0824.png', dpi=80)
