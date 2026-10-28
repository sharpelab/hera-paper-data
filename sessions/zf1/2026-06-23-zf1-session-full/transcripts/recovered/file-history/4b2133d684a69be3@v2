import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run

n11 = np.linspace(-8, -1, 71)   # 1e11 cm^-2
cuts = {5:-0.4, 6:-0.5, 7:-0.6}
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for rid, D0 in cuts.items():
    r = open_run(f'data/{rid}')
    itg=np.abs(r.col('k_tg_curr')).max(); ibg=np.abs(r.col('k_bg_curr')).max()
    R4=(r.col('sr830_3_X')/100)/1e-9
    ax[0].plot(n11, R4, '.-', label=f'D={D0:+.2f}  (leak tg{itg*1e12:.0f}/bg{ibg*1e12:.0f}pA)')
    ax[1].semilogy(n11, np.clip(R4,0.5,None), '.-', label=f'D={D0:+.2f}')
    # local-min search in the candidate band n in [-6.5,-2] (away from doped-end & CNP rail)
    band=(n11<=-2)&(n11>=-6.5)
    nb=n11[band]; rb=R4[band]
    jmin=np.argmin(rb)
    # is it a genuine local dip (lower than both shoulders) vs monotone?
    print(f"D={D0:+.2f}: R4 band[-6.5,-2] min {rb.min():.1f} Ohm at n={nb[jmin]:+.2f}e11 ; "
          f"R at n=-8 (doped end)={R4[0]:.1f}; full-cut min {R4.min():.2f} at n={n11[np.argmin(R4)]:+.2f}")
ax[0].set(xlabel='n (1e11 cm^-2)', ylabel='4T R_xx (Ohm)', title='constant-D n-linecuts (linear)', ylim=(0,120))
ax[1].set(xlabel='n (1e11 cm^-2)', ylabel='4T R_xx (Ohm)', title='log')
ax[0].legend(); ax[1].legend(); ax[0].grid(alpha=0.3); ax[1].grid(alpha=0.3)
plt.tight_layout(); plt.savefig('hera_scratch/linecuts.png', dpi=120)
print('saved hera_scratch/linecuts.png')
