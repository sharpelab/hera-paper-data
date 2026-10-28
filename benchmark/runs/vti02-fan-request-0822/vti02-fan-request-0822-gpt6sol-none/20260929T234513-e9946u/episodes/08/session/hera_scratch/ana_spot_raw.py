# Runs 6 and 7: raw transport and monitor channels, before spectral interpretation.
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel

fig, ax = plt.subplots(2, 3, figsize=(14, 7), sharex='row')
for row, rid in enumerate((6, 7)):
    r = open_run(Path('data') / str(rid))
    ch = resolve_channels(r.meta)
    ci = current_channel(ch)
    cv = next(c for c in ch if c.cid == 'sr1')
    I = r.col(ci.col) / ci.gain
    R = (r.col(cv.col) / cv.gain) / I
    B = r.col('magnet_field')
    T = r.col('T_sample')
    print(f'run {rid}: {r.rows} rows, B {B[0]:.3f}->{B[-1]:.3f} T, '
          f'T_sample median {np.median(T):.3f} K [{T.min():.3f},{T.max():.3f}], '
          f'I median {np.median(I)*1e9:.3f} nA, R range {R.min():.1f}..{R.max():.1f} Ohm, '
          f'sr1 peak {np.max(np.abs(r.col(cv.col)))/50e-6:.3f} of 50 uV FS')
    ax[row, 0].plot(B, R, lw=.8)
    ax[row, 1].plot(B, I*1e9, lw=.8)
    ax[row, 2].plot(B, r.col('k_2400_tg_curr')*1e12, lw=.7, label='TG')
    ax[row, 2].plot(B, r.col('k_2400_bg_curr')*1e12, lw=.7, label='BG')
    for a in ax[row]: a.set_xlabel('B readback (T)')
    ax[row, 0].set_ylabel('Rxx (Ohm)')
    ax[row, 1].set_ylabel('drain current (nA)')
    ax[row, 2].set_ylabel('gate current (pA)')
    ax[row, 0].set_title(f'run {rid}: raw Rxx = V/I')
ax[0, 2].legend()
fig.tight_layout()
plt.show()
