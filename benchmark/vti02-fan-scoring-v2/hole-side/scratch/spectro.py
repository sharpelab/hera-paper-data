import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import spec, peaks
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
tr = {t['id']: t for t in load_all(include_ramp=False)}
fig, axs = plt.subplots(1, 3, figsize=(18, 6))
for ax, (k, L) in zip(axs, [('0822-r7', 0.6), ('0824-r5-c0', 0.6), ('0825-r7-c0', 0.3)]):
    t = tr[k]; B, R = t['B'], t['R']
    u0s = np.arange(1 / B.max() + L / 2, 1 / B.min() - L / 2, 0.02)
    Z = []
    for uc in u0s:
        lo, hi = 1 / (uc + L / 2), 1 / (uc - L / 2)
        s = spec(B, R, lo, hi, 3, Fmax=25, dFgrid=0.05)
        if s is None or s['rows'] < 12: Z.append(np.full(501, np.nan)); continue
        Z.append(s['amp'])
    Z = np.array(Z)
    Z = np.nan_to_num(Z); Fg = np.arange(0, 25.0001, 0.05)
    ax.pcolormesh(Fg, 1 / u0s, Z, shading='nearest', cmap='magma', vmax=np.percentile(Z, 99.5))
    ax.set_yscale('log'); ax.set_xlabel('F (T)'); ax.set_ylabel('window centre B (T)'); ax.set_title(f'{k}: sliding {L}/T window amplitude (ohm)')
    for i in range(0, len(u0s), 3):
        pk = peaks(Fg, Z[i] / np.median(Z[i]), 1.5, 20, 3, 4)
        print(k, f'Bc {1 / u0s[i]:.2f}', ' '.join(f'{f:.2f}({z:.0f})' for f, z in pk))
fig.tight_layout(); fig.savefig('scratch/spectro.png', dpi=80)
