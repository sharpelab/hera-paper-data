from hera.analysis import open_run
import numpy as np
import matplotlib.pyplot as plt

fig, axs = plt.subplots(2, 2, figsize=(11, 6), constrained_layout=True)
for row, fid in enumerate((6, 7)):
    run = open_run(f'data/{fid}')
    b = run.col('magnet_field')
    order = np.argsort(b)
    rxx = run.col('sr1_X') / 1e-8  # sr1 gain 1, drive 1 V / 100 MOhm
    axs[row, 0].plot(b[order], rxx[order], lw=0.7)
    axs[row, 0].set(title=f'Run {fid}: raw B1-B2', xlabel='B (T)', ylabel='Rxx (ohm)')
    for name in ('k_2400_tg_curr', 'k_2400_bg_curr'):
        axs[row, 1].plot(b[order], run.col(name)[order]*1e12, lw=.6, label=name)
    axs[row, 1].set(title=f'Run {fid}: raw gate currents', xlabel='B (T)', ylabel='I (pA)')
    axs[row, 1].legend(fontsize=7)
plt.show()
