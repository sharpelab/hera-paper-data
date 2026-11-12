import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import read, _base, col, nframe
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
for s, r in (('0823', 6), ('0824', 4)):
    meta, X = read(s, r)
    I, R, B, T, lk = _base(s, r, meta, X)
    nf = len(meta['fast_setpoints'][0]); nr = X.shape[0] // nf
    rs = lambda a: a[:nr * nf].reshape(nr, nf)
    n = nframe(s, rs(col(meta, X, 'k_2400_tg_volt')), rs(col(meta, X, 'k_2400_bg_volt')))
    Rg, Bg = rs(R), rs(B)
    np.savez(f'scratch/fan{s}.npz', n=n, R=Rg, B=Bg)
    fig, ax = plt.subplots(1, 2, figsize=(15, 6))
    ax[0].pcolormesh(n, Bg, np.log10(np.clip(np.abs(Rg), 10, 1e6)), shading='nearest', cmap='viridis')
    # guides: nu lines for scale s_ and n0=0
    for nu in range(-16, 25, 4):
        if nu == 0: continue
        bb = np.linspace(0.5, 8, 50); ax[0].plot(nu * bb / 41.357 / (0.82 if s == '0823' else 0.9), bb, 'r-', lw=0.4)
    ax[0].set_xlim(n.min(), n.max()); ax[0].set_ylim(Bg.min(), Bg.max()); ax[0].set_title(f'{s} r{r} log10 R, nu lines (step 4) at s={0.82 if s=="0823" else 0.9}')
    ax[0].set_xlabel('n_frame'); ax[0].set_ylabel('B')
    # derivative map
    dR = np.gradient(Rg, axis=1) / np.maximum(np.abs(Rg), 20)
    ax[1].pcolormesh(n, Bg, dR, shading='nearest', cmap='RdBu', vmin=-0.2, vmax=0.2); ax[1].set_title('dR/dn / R')
    fig.tight_layout(); fig.savefig(f'scratch/fan{s}.png', dpi=80)
    print(s, r, n.shape, n[0, :3], n[0, -3:], Bg[:3, 0], Bg[-3:, 0])
