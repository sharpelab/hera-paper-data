import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

d = np.load('hera_scratch/map1_reformed.npz')
V_tg, V_bg, R4, R2 = d['V_tg'], d['V_bg'], d['R4'], d['R2']

# clip tiny/negative for log display
R4c = np.clip(R4, 1, None)
R2c = np.clip(R2, 1, None)

fig, ax = plt.subplots(1, 3, figsize=(18, 5.2))

# 1) 4T R_xx, log — shows CNP ridge (rails 2.18k) + low-R landscape
im0 = ax[0].pcolormesh(V_bg, V_tg, R4c, norm=LogNorm(vmin=5, vmax=2200), cmap='inferno', shading='nearest')
ax[0].set_title('4T R_xx (sr3, 30-31)  log  [rails ~2.18k]')
fig.colorbar(im0, ax=ax[0], label='R_xx (Ohm)')

# 2) 4T R_xx, LINEAR low range — resolve the low-R metallic structure / candidate dips
im1 = ax[1].pcolormesh(V_bg, V_tg, np.clip(R4, 0, 60), cmap='viridis', shading='nearest')
ax[1].set_title('4T R_xx, linear 0-60 Ohm  (low-R landscape)')
fig.colorbar(im1, ax=ax[1], label='R_xx (Ohm)')

# 3) 2T, log — CNP gap structure (has headroom to 666k)
im2 = ax[2].pcolormesh(V_bg, V_tg, R2c, norm=LogNorm(vmin=3000, vmax=7e5), cmap='magma', shading='nearest')
ax[2].set_title('2T R (sr2, 5-4)  log')
fig.colorbar(im2, ax=ax[2], label='R_2T (Ohm)')

for a in ax:
    a.set_xlabel('V_bg (V)'); a.set_ylabel('V_tg (V)')

plt.tight_layout()
plt.savefig('hera_scratch/map1_overview.png', dpi=110)
print('saved hera_scratch/map1_overview.png')

# Print min-R location (candidate hint) from 4T
imin = np.unravel_index(np.argmin(R4), R4.shape)
print(f'4T R_xx global min {R4[imin]:.1f} Ohm at V_tg={V_tg[imin[0]]:+.2f}, V_bg={V_bg[imin[1]]:+.2f}')
# where is R4 below 8 ohm?
lo = R4 < 8
if lo.any():
    it, ib = np.where(lo)
    print(f'R4<8 Ohm: {lo.sum()} pts, V_tg [{V_tg[it].min():+.2f},{V_tg[it].max():+.2f}], V_bg [{V_bg[ib].min():+.2f},{V_bg[ib].max():+.2f}]')
