from hera.analysis import open_run, summarize_run
import matplotlib.pyplot as plt
import numpy as np

r7 = open_run('data/7')
print(summarize_run(r7))
b7 = r7.col('magnet_field')
ix7 = r7.col('sr0_X') / -1e6
rxx7 = r7.col('sr1_X') / ix7
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(b7, rxx7, lw=0.9)
ax.set(xlabel='B (T)', ylabel='Rxx (Ω)', title='Run 7: raw Rxx, n = −1.2×10¹² cm⁻², D = 0')
ax.grid(alpha=0.2)
plt.tight_layout()
plt.show()
print(f'Rxx: {np.nanmin(rxx7):.1f} to {np.nanmax(rxx7):.1f} Ω; '
      f'T_sample: {r7.col("T_sample").min():.3f} to {r7.col("T_sample").max():.3f} K; '
      f'|I_tg|max {np.abs(r7.col("k_2400_tg_curr")).max()*1e12:.0f} pA, '
      f'|I_bg|max {np.abs(r7.col("k_2400_bg_curr")).max()*1e12:.0f} pA')
