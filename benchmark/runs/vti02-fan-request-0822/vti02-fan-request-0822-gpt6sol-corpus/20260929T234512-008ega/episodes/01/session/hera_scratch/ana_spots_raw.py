import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

fig, axs = plt.subplots(2, 4, figsize=(15, 6))
for row, rid in enumerate((6, 7)):
    run = open_run(f'data/{rid}')
    print(summarize_run(run))
    assert run.complete and not run.interrupted
    b = run.col('magnet_field')
    ib = run.meta['instruments']['sr1']['snapshot']['parameters']['amplitude']['value'] / run.meta['measurement_config']['bias_resistor']
    r = run.col('sr1_X') / ib
    axs[row, 0].plot(b, r, lw=.7); axs[row, 0].set_ylabel(f'run {rid} Rxx (Ω)')
    axs[row, 1].plot(b, run.col('sr0_X'), lw=.7); axs[row, 1].set_ylabel('drain X (V)')
    axs[row, 2].plot(b, run.col('k_2400_tg_curr')*1e12, lw=.7, label='TG')
    axs[row, 2].plot(b, run.col('k_2400_bg_curr')*1e12, lw=.7, label='BG')
    axs[row, 2].set_ylabel('gate current (pA)'); axs[row, 2].legend(fontsize=7)
    axs[row, 3].plot(b, run.col('T_sample'), lw=.7); axs[row, 3].set_ylabel('T sample (K)')
    for ax in axs[row]: ax.set_xlabel('B (T)')
    print(f'run {rid}: Rxx {r.min():.1f}..{r.max():.1f} Ω; max |R|/full scale {np.max(abs(r))*ib/50e-6:.3f}; '
          f'max |I_TG| {max(abs(run.col("k_2400_tg_curr")))*1e12:.0f} pA, max |I_BG| {max(abs(run.col("k_2400_bg_curr")))*1e12:.0f} pA; '
          f'T {run.col("T_sample").min():.3f}..{run.col("T_sample").max():.3f} K')
fig.tight_layout(); plt.show()
