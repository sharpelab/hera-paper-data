import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run

r = open_run('data/10')
B = r.col_at(r.col_indices('magnet_field')[0]) * 1e3   # mT
dVdI = (r.col('sr830_3_X')/100.0)/1e-9                  # Ohm
T = r.col('T')*1e3                                      # mK
print(f'rows {len(B)}  B [{B.min():.1f},{B.max():.1f}] mT')
print(f'T during sweep: {T.min():.1f}-{T.max():.1f} mK  (base ~34) -> settle {"OK" if T.max()<60 else "MARGINAL/heating"}')

Rn = np.median(dVdI[np.abs(B) > 40])     # normal-ish dV/dI at high |B|
Rmin = dVdI.min(); Bmin = B[np.argmin(dVdI)]
print(f'normal-ish dV/dI (|B|>40mT): {Rn:.1f} Ohm ; min dV/dI {Rmin:.2f} Ohm at B={Bmin:+.2f} mT (effective-zero)')
# B_c_perp = |B| where dV/dI crosses half-way between min and normal
half = (Rmin+Rn)/2
# from B=0 outward to negative
order = np.argsort(-B)   # from +0 down to -50
Bo, Ro = B[order], dVdI[order]
ix = np.argmax(Ro > half)
Bc = Bo[ix] if (Ro>half).any() else np.nan
print(f'half-level {half:.1f} Ohm crossed at B={Bc:+.1f} mT -> |B_c_perp| ~ {abs(Bc):.0f} mT (order-of-mag)')

fig, ax = plt.subplots(1,2,figsize=(12,4.6))
ax[0].plot(B, dVdI, '.-')
ax[0].axhline(half,color='gray',ls=':',lw=.8,label=f'half {half:.0f}Ω')
ax[0].axvline(Bc,color='r',ls='--',lw=.8,label=f'B_c⊥~{abs(Bc):.0f}mT')
ax[0].set(xlabel='B_perp (mT)', ylabel='zero-bias dV/dI (Ohm)', title='Run 10 field-kill: dV/dI(B), SC optimum'); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].plot(B, T, '.-'); ax[1].axhline(34,color='gray',ls=':',label='base 34mK')
ax[1].set(xlabel='B_perp (mT)', ylabel='T (mK)', title='T during field sweep (settle check)'); ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig('hera_scratch/field.png', dpi=120); print('saved hera_scratch/field.png')
