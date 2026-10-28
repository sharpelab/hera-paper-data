from hera.analysis import open_run, summarize_run
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 1, figsize=(9, 7), constrained_layout=True)
for i, (file_id, n) in enumerate(((6, +3.2), (7, -1.2))):
    r = open_run(f'data/{file_id}')
    print(summarize_run(r))
    B = r.col('magnet_field')
    R = r.col('sr1_X') / 1e-8  # sr1 unity gain, live 1 V / 100 MΩ = 10 nA
    T = r.col('T_sample')
    print(f'run {file_id}: Rxx [{R.min():.1f}, {R.max():.1f}] Ω; '
          f'T_sample [{T.min():.3f}, {T.max():.3f}] K; '
          f'TG/BG median currents {np.median(r.col("k_2400_tg_curr"))*1e12:.1f}/'
          f'{np.median(r.col("k_2400_bg_curr"))*1e12:.1f} pA')
    ax[i].plot(B, R, lw=1)
    ax[i].set(title=f'Run {file_id}: n = {n:+.1f}×10¹² cm⁻², D ≈ 0',
              xlabel='B (T)', ylabel='raw Rxx (Ω)')
    ax[i].grid(alpha=.25)
plt.show()
