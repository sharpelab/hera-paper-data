import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run

NB, NV = 16, 25
Vdc = np.linspace(-5,5,NV); Idc = Vdc/1e8*1e9   # nA

def load(rid):
    r = open_run(f'data/{rid}')
    B = r.col_at(r.col_indices('magnet_field')[0])[:NB*NV].reshape(NB,NV)[:,0]*1e3  # mT per row
    dVdI = ((r.col('sr830_3_X')/100.0)/1e-9)[:NB*NV].reshape(NB,NV)
    T = (r.col('T')*1e3)[:NB*NV].reshape(NB,NV)[:,0]
    return B, dVdI, T

Bn, Rn_, Tn = load(11)   # -6 -> 0
Bp, Rp_, Tp = load(12)   # +6 -> 0
# stitch into ascending B: neg side (-6..0) then pos side (0..+6) reversed
B_all = np.concatenate([Bn, Bp[::-1]])
R_all = np.vstack([Rn_, Rp_[::-1]])
print(f'T over both runs: {min(Tn.min(),Tp.min()):.1f}-{max(Tn.max(),Tp.max()):.1f} mK')

# normal-state dV/dI and Ic(B) via threshold crossing (half of normal)
Rnorm = np.median(R_all[np.abs(B_all)>5])
thr = 0.5*Rnorm
print(f'normal dV/dI {Rnorm:.1f} Ohm; threshold {thr:.1f} Ohm')
def ic_of(trace):
    # symmetric Ic: mean of +/- first crossing above thr from Idc=0 outward
    pos = Idc>=0; neg = Idc<=0
    Ip,Rp = Idc[pos][np.argsort(Idc[pos])], trace[pos][np.argsort(Idc[pos])]
    In,Rn = Idc[neg][np.argsort(-Idc[neg])], trace[neg][np.argsort(-Idc[neg])]
    icp = Ip[np.argmax(Rp>thr)] if (Rp>thr).any() else 0.0
    icn = In[np.argmax(Rn>thr)] if (Rn>thr).any() else 0.0
    zb = trace[np.argmin(np.abs(Idc))]   # zero-bias dV/dI
    return (abs(icp)+abs(icn))/2, zb
Ic = np.array([ic_of(R_all[i])[0] for i in range(len(B_all))])
zb = np.array([ic_of(R_all[i])[1] for i in range(len(B_all))])
imax = np.argmax(Ic)
print(f'effective-zero (Ic max) at B={B_all[imax]:+.2f} mT, Ic={Ic[imax]:.0f} nA')
# B_c_perp: |B| where Ic falls to ~0 (last B with Ic>3nA each side from effZero)
print('Ic(B) (nA):')
for b,ic,z in zip(B_all, Ic, zb):
    print(f'  B={b:+.2f} mT  Ic={ic:4.0f} nA  zero-bias dV/dI={z:6.1f} Ohm')

fig, ax = plt.subplots(1,2,figsize=(13,5))
# 2D Fraunhofer map
im = ax[0].pcolormesh(B_all, Idc, np.clip(R_all,0,60).T, cmap='inferno', shading='nearest')
ax[0].set(xlabel='B_perp (mT)', ylabel='I_dc (nA)', title='dV/dI(I_dc, B) — Fraunhofer map')
fig.colorbar(im, ax=ax[0], label='dV/dI (Ohm)')
# Ic(B)
ax[1].plot(B_all, Ic, 'o-')
ax[1].axvline(B_all[imax], color='r', ls='--', lw=.8, label=f'eff-zero {B_all[imax]:+.1f}mT')
ax[1].set(xlabel='B_perp (mT)', ylabel='I_c (nA)', title='I_c(B) — both polarities'); ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig('hera_scratch/fraunhofer.png', dpi=120); print('saved hera_scratch/fraunhofer.png')
