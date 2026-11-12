import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

d = np.load('hera_scratch/map1_nD.npz')
V_tg, V_bg, R4 = d['V_tg'], d['V_bg'], d['R4']
n, D, m, b = d['n'], d['D'], float(d['m']), float(d['b'])   # n in 1e12 cm^-2, D in V/nm
NT, NB = R4.shape

# candidate band: n in [-0.6,-0.4] (1e12 cm^-2 = -4..-6 e11), |D|>=0.5
n11 = n*10.0   # -> 1e11 cm^-2
cand = (n11<=-4)&(n11>=-6)&(np.abs(D)>=0.5)
print('candidate cells:', cand.sum())
if cand.any():
    it,ib=np.where(cand)
    for sgn,lab in ((-1,'D<0'),(1,'D>0')):
        s=cand&(np.sign(D)==sgn)
        if s.any():
            jt,jb=np.where(s)
            print(f"  {lab}: {s.sum()} cells  V_tg[{V_tg[jt].min():+.2f},{V_tg[jt].max():+.2f}] "
                  f"V_bg[{V_bg[jb].min():+.2f},{V_bg[jb].max():+.2f}]  |D|<= {np.abs(D[s]).max():.2f}  "
                  f"4T R min {R4[s].min():.1f} med {np.median(R4[s]):.1f}")

fig, ax = plt.subplots(1, 2, figsize=(14, 5.6))

# (1) gate-space 4T with CNP fit overlay (verify the extraction tracks the ridge)
im0=ax[0].pcolormesh(V_bg, V_tg, np.clip(R4,1,None), norm=LogNorm(vmin=5,vmax=2200),
                     cmap='inferno', shading='nearest')
ax[0].plot(m*V_tg+b, V_tg, 'c--', lw=1.5, label=f'CNP fit (c_bg/c_tg={d["ratio"]:.3f})')
ax[0].set_xlabel('V_bg (V)'); ax[0].set_ylabel('V_tg (V)'); ax[0].legend(loc='upper right')
ax[0].set_title('4T R_xx + CNP fit'); fig.colorbar(im0,ax=ax[0],label='R_xx (Ohm)')

# (2) (n,D)-projected 4T via tripcolor (sheared grid)
nf, Df, Rf = n11.ravel(), D.ravel(), np.clip(R4,1,None).ravel()
tp=ax[1].tripcolor(nf, Df, Rf, norm=LogNorm(vmin=5,vmax=2200), cmap='inferno', shading='gouraud')
ax[1].set_xlabel('n (1e11 cm^-2)'); ax[1].set_ylabel('D (V/nm)')
ax[1].set_title('4T R_xx in (n, D)'); fig.colorbar(tp,ax=ax[1],label='R_xx (Ohm)')
# mark candidate band
for sgn in (-1,1):
    s=cand&(np.sign(D)==sgn)
    if s.any(): ax[1].scatter(n11[s], D[s], s=18, facecolors='none', edgecolors='cyan', lw=0.8)
ax[1].axvspan(-6,-4, color='cyan', alpha=0.08)
ax[1].axhline(0.5,color='w',ls=':',lw=0.6); ax[1].axhline(-0.5,color='w',ls=':',lw=0.6)

plt.tight_layout(); plt.savefig('hera_scratch/map1_nD.png', dpi=115)
print('saved hera_scratch/map1_nD.png')
