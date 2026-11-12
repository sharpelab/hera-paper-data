import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all, nframe, read, _base, col, N_SCALE
from common import spec, model, peaks
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
tr = load_all()
fig, axs = plt.subplots(1, 3, figsize=(17, 6))
for ax, (rid, lo, hi) in zip(axs, [('0824-r4', 0.76, 6.0), ('0823-r6', 1.3, 8.0), ('0823-r6', 2.0, 8.0)]):
    T = sorted([t for t in tr if t['id'].startswith(rid + '-')], key=lambda t: t['n_frame'])
    Z = []; ns = []
    for t in T:
        s = spec(t['B'], t['R'], lo, hi, 5, Fmax=25)
        if s is None: continue
        Z.append(s['S'] / s['med_noise']); ns.append(t['n_frame'])
        pk = peaks(s['F'], s['S'] / s['med_noise'], 0.6, min(25, s['nyq']), 4, 6)
        print(t['id'], f"n_fr {t['n_frame']:+.3f} dF {s['dF']:.2f} nyq {s['nyq']:.1f} sig {s['sigma']:.2f}", ' '.join(f'{f:.2f}({z:.0f})' for f, z in pk))
    Z = np.array(Z); F = s['F']; ns = np.array(ns)
    ax.pcolormesh(F, ns, np.log10(np.maximum(Z, 0.5)), shading='nearest', cmap='magma', vmin=0, vmax=2.5)
    nn = np.linspace(-1.45, -0.3, 100)
    for sc, ls in ((N_SCALE[rid[:4]], '-'), (0.80, ':')):
        fl, fh, fL = model(np.abs(nn) * sc)
        ax.plot(fl, nn, 'c' + ls, lw=0.8); ax.plot(fh, nn, 'lime', ls=ls, lw=0.8); ax.plot(fL, nn, 'w' + ls, lw=0.8)
    ax.set_xlim(0, 20); ax.set_ylim(ns.min(), ns.max()); ax.set_title(f'{rid} [{lo},{hi}]'); ax.set_xlabel('F (T)'); ax.set_ylabel('n_frame')
fig.tight_layout(); fig.savefig('scratch/maps.png', dpi=80)
