import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run

r = open_run('data/9')
Vdc = r.col_at(r.col_indices('dc205_1_voltage')[0])  # swept setpoint
Idc = Vdc/1e8 * 1e9                     # nA
dVdI = (r.col('sr830_3_X')/100.0)/1e-9  # Ohm (AC 1 nA)
N = len(Idc); half = N//2
fwd = slice(0, half+1); bwd = slice(half, N)   # -15->+15 then +15->-15

# normal-state dV/dI (mean of |Idc|>120 nA) and threshold = 50% of it
Rn = np.median(dVdI[np.abs(Idc) > 120])
thr = 0.5*Rn
print(f'normal-state dV/dI ~ {Rn:.1f} Ohm; threshold {thr:.1f} Ohm')
print(f'zero-bias dV/dI (|Idc|<3nA): {np.median(dVdI[np.abs(Idc)<3]):.2f} Ohm')

def ic_cross(I, R):
    # from I=0 outward, first crossing above threshold each side
    pos = I >= 0; neg = I <= 0
    Ip = I[pos][np.argsort(I[pos])]; Rp = R[pos][np.argsort(I[pos])]
    In = I[neg][np.argsort(-I[neg])]; Rn_ = R[neg][np.argsort(-I[neg])]
    icp = Ip[np.argmax(Rp>thr)] if (Rp>thr).any() else np.nan
    icn = In[np.argmax(Rn_>thr)] if (Rn_>thr).any() else np.nan
    return icn, icp

icn_f, icp_f = ic_cross(Idc[fwd], dVdI[fwd])
icn_b, icp_b = ic_cross(Idc[bwd], dVdI[bwd])
print(f'forward : Ic- {icn_f:+.1f} nA  Ic+ {icp_f:+.1f} nA')
print(f'backward: Ic- {icn_b:+.1f} nA  Ic+ {icp_b:+.1f} nA')
print(f'mean |Ic|: {np.nanmean(np.abs([icn_f,icp_f,icn_b,icp_b])):.1f} nA ; '
      f'asym Ic+/-Ic-: fwd {abs(icp_f)-abs(icn_f):+.1f} nA')

fig, ax = plt.subplots(figsize=(7.5,5))
ax.plot(Idc[fwd], dVdI[fwd], '.-', ms=3, label='forward -15→+15')
ax.plot(Idc[bwd], dVdI[bwd], '.-', ms=3, alpha=0.7, label='backward +15→-15')
ax.axhline(thr, color='gray', ls=':', lw=0.8, label=f'thr {thr:.0f}Ω')
for x in (icn_f, icp_f):
    if np.isfinite(x): ax.axvline(x, color='r', ls='--', lw=0.8)
ax.set(xlabel='I_dc (nA)', ylabel='dV/dI (Ohm)', title='Run 9 — bias spectroscopy at SC optimum (n=-5.2e11, D=-0.645, B=0)')
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('hera_scratch/bias.png', dpi=120)
print('saved hera_scratch/bias.png')
