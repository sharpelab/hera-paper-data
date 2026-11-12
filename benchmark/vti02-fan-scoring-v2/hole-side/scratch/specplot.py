import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import spec, model
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
tr = {t['id']: t for t in load_all(include_ramp=False)}
cases = [('0822-r7', 1.012, [(0.6, 2.0), (0.75, 3.0), (1.0, 4.5), (0.75, 4.5), (4.5, 10)]), ('0824-r5-c0', 0.725, [(0.51, 2.0), (0.51, 3.0), (0.75, 6.1), (0.51, 6.1), (2, 6.1)]),
         ('0825-r7-c0', 0.846, [(1.5, 3.0), (1.5, 4.5), (1.5, 6.0), (2.5, 6.0)])]
fig, axs = plt.subplots(3, 1, figsize=(10, 12))
for ax, (k, n, wins) in zip(axs, cases):
    t = tr[k]; fl, fh, fL = model(n)
    for lo, hi in wins:
        s = spec(t['B'], t['R'], lo, hi, 3, Fmax=45, dFgrid=0.02)
        ax.plot(s['F'], s['amp'], lw=0.9, label=f"[{s['lo']:.2f},{s['hi']:.1f}] dF {s['dF']:.2f}")
    for f, c, nm in ((fl, 'c', 'light'), (fh, 'g', 'heavy'), (fL, 'k', 'F_L'), (2 * fh, 'g', '2h'), (fh - fl, 'm', 'h-l'), (fL + fh, 'y', 'F_L+h'), (2 * fL, 'k', '2F_L')):
        ax.axvline(f, color=c, ls='--', lw=0.7); ax.text(f, ax.get_ylim()[1] * 0.9, nm, fontsize=7, rotation=90)
    ax.set_xlim(0, 30); ax.legend(fontsize=7); ax.set_title(f'{k} |n| {n} (QH/F_L frame); Halder model lines'); ax.set_ylabel('amp (ohm)')
fig.tight_layout(); fig.savefig('scratch/specplot.png', dpi=80)
