import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_fft
_data_dir = Path('/home/hera/measurements/zack/20260822-vti-02/data')
def run(i):
    return open_run(_data_dir / str(i))

fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
for k, rid in enumerate((6, 7)):
    q = run(rid)
    B = q.col('magnet_field')
    R = q.col('sr1_X') / (q.col('sr0_X') / -1e6)
    order = np.argsort(B)
    ax[k].plot(B[order], R[order], lw=1)
    ax[k].set_ylabel('Rxx (Ohm)')
    ax[k].set_title(f'run {rid}: raw B_1–B_2, ' + ('electron' if rid == 6 else 'hole'))
    print(summarize_run(q))
    print(f'  raw Rxx {np.nanmin(R):.1f}..{np.nanmax(R):.1f} Ohm; T_sample {np.nanmin(q.col("T_sample")):.3f}..{np.nanmax(q.col("T_sample")):.3f} K; '
          f'max |I_tg| {np.nanmax(np.abs(q.col("k_2400_tg_curr")))*1e12:.0f} pA, max |I_bg| {np.nanmax(np.abs(q.col("k_2400_bg_curr")))*1e12:.0f} pA')
ax[-1].set_xlabel('B (T)')
fig.tight_layout(); plt.show()
