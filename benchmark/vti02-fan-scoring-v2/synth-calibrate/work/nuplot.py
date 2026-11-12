import sys, json, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check'); sys.path.insert(0, '..'); sys.path.insert(0, '.')
from load import load
import vti02_sim as vs
from compare import fan_settings
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
p = json.load(open(sys.argv[1])); p = p.get('params', p)
fig, axs = plt.subplots(2, 2, figsize=(16, 9))
for k, (nm, s) in enumerate((('0825-r8', p['s825']), ('0822-r8', p['s822']))):
    d = load(nm); st = fan_settings(d); B = d['B']
    Rc = vs._blur_rows(vs.clean_R(B, d['n'] * s, p, lambda nn: vs.observed_tones(nn, p['r0'], p['r1'])), vs.step_weights(st['delay'], st['tau']))
    nu = 10.3392 * d['n'][None, :] * s / B[:, None] * 1.0
    for ax, R, t in ((axs[k, 0], d['R'], 'live'), (axs[k, 1], Rc, 'model')):
        sc = ax.scatter(nu.ravel(), R.ravel(), c=np.broadcast_to(d['n'], R.shape).ravel(), s=2, cmap='viridis')
        ax.set_xscale('log'); ax.set_yscale('symlog', linthresh=10); ax.set_xlim(1.5, 40); ax.set_ylim(-50, 3000)
        ax.set_title(f'{nm} {t}: R vs filling nu = F_L/B (x4 = nu_total)'); ax.grid(True, which='both', alpha=0.3)
        ax.set_xticks([2, 3, 4, 5, 6, 8, 10, 15, 20, 30]); ax.set_xticklabels([2, 3, 4, 5, 6, 8, 10, 15, 20, 30])
fig.tight_layout(); fig.savefig('nuplot.png', dpi=65)
