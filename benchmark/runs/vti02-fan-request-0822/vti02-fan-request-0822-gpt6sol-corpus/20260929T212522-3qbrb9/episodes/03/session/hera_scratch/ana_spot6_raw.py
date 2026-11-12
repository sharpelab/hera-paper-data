from hera.analysis import open_run, summarize_run
import matplotlib.pyplot as plt
import numpy as np

r6 = open_run('data/6')
print(summarize_run(r6))
b6 = r6.col('magnet_field')
ix6 = r6.col('sr0_X') / -1e6
rxx6 = r6.col('sr1_X') / ix6
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(b6, rxx6, lw=0.9)
ax.set(xlabel='B (T)', ylabel='Rxx (Ω)', title='Run 6: raw Rxx, n = +3.2×10¹² cm⁻², D = 0')
ax.grid(alpha=0.2)
plt.tight_layout()
plt.show()
print(f'Rxx: {np.nanmin(rxx6):.1f} to {np.nanmax(rxx6):.1f} Ω; '
      f'T_sample: {r6.col("T_sample").min():.3f} to {r6.col("T_sample").max():.3f} K; '
      f'|I_tg|max {np.abs(r6.col("k_2400_tg_curr")).max()*1e12:.0f} pA, '
      f'|I_bg|max {np.abs(r6.col("k_2400_bg_curr")).max()*1e12:.0f} pA')
