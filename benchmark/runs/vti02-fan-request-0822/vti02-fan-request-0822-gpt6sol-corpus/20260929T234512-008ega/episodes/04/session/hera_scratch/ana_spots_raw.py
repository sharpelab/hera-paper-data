from hera.analysis import open_run, summarize_run
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for k, rid in enumerate((6, 7)):
    r = open_run(f'data/{rid}')
    print(summarize_run(r))
    B, R = r.col('magnet_field'), r.col('sr1_X') / 1e-8
    order = np.argsort(B)
    ax[k].plot(B[order], R[order], lw=.75)
    ax[k].set(xlabel='B (T)', ylabel='Rxx, B1–B2 (Ω)', title=f'Run {rid}: raw Rxx')
    print(f'run {rid}: R {np.nanmin(R):.1f}…{np.nanmax(R):.1f} Ω; max/full-scale {np.nanmax(np.abs(R))/5000:.3f}; T {np.nanmin(r.col("T_sample")):.3f}…{np.nanmax(r.col("T_sample")):.3f} K')
    for gate in ('k_2400_tg_curr', 'k_2400_bg_curr'):
        print(f'  {gate}: median {np.nanmedian(r.col(gate))*1e12:.1f} pA; max |I| {np.nanmax(np.abs(r.col(gate)))*1e12:.1f} pA')
fig.tight_layout()
plt.show()
