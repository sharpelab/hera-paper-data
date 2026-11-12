import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run
from scipy.signal import savgol_filter

fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for i, rid in enumerate((6, 7)):
    r = open_run(f'data/{rid}')
    B = r.col('magnet_field')
    R = r.col('sr1_X') / (r.col('sr0_X') / -1e6)
    ix = np.argsort(B); B = B[ix]; R = R[ix]
    axs[i, 0].plot(B, R, '.', ms=1.4)
    axs[i, 0].set(xlabel='B (T)', ylabel='Rxx signed (ohm)', title=f'Run {rid} raw Rxx')
    for lo, hi, color in [(1, 10, 'C0'), (1.5, 6, 'C1'), (2, 10, 'C2')]:
        m = (B >= lo) & (B <= hi)
        bs, rs = B[m], R[m]
        n = min(101, len(rs)//2*2-1)
        bg = savgol_filter(rs, n, 3)
        axs[i, 1].plot(1/bs, rs-bg, '-', lw=.8, color=color, label=f'{lo}-{hi} T')
    axs[i, 1].set(xlabel='1/B (1/T)', ylabel='Rxx - smooth (ohm)', title=f'Run {rid} residual')
    axs[i, 1].legend()
fig.tight_layout()
fig.savefig('hera_scratch/spot_raw.png', dpi=180)
