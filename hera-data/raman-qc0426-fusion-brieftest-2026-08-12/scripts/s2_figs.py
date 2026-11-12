# s2_figs.py — stage figures: flake regions, stack bands, device bands.
# Map/video grids: axis0=x ascending, axis1=y descending; images are (ny,nx),
# row 0 = y max -> imshow(origin='upper', extent=[xmin,xmax,ymin,ymax]).
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'
SPOTS_04 = {'spot1': (13.3, 0.9), 'spot2': (-23.1, 5.1)}
SPOT_06 = (11.2, -4.3)

def ext(z):
    return [z['X'].min(), z['X'].max(), z['Y'].min(), z['Y'].max()]

def vid(ax, tag, name='Video_Image000'):
    z = np.load(f'{OUT}/intermediates/vid_{tag}_{name}.npz')
    ax.imshow(z['arr'].transpose(1, 0, 2), extent=ext(z), origin='upper', aspect='equal')

# ---- flake ----
fr = np.load(f'{OUT}/intermediates/flake_regions.npz')
fa = np.load(f'{OUT}/intermediates/flake_amp.npz')
fw_img = fr['fwhm'].reshape(57, 101)
lab = fr['lab_img']
cls = np.full(lab.shape, np.nan)
cls[np.isfinite(fw_img) & (fw_img < 40)] = 0          # 1L
cls[np.isfinite(fw_img) & (fw_img >= 40) & (fw_img <= 56)] = 1  # p52/thickness-ambig
cls[lab == 0] = 2   # R1 ABA
cls[lab == 1] = 3   # R2 ABC
fig, axs = plt.subplots(1, 2, figsize=(20, 7))
vid(axs[0], '04')
axs[0].add_patch(plt.Rectangle((fr['X'].min(), fr['Y'].min()),
                 fr['X'].max() - fr['X'].min(), fr['Y'].max() - fr['Y'].min(),
                 fill=False, ec='r', lw=1.5))
axs[0].set_title('04 flake video + map footprint')
cmap = ListedColormap(['#bbbbbb', '#666666', '#3b6fd4', '#d43b3b'])
axs[1].imshow(cls, extent=ext(fr), origin='upper', cmap=cmap, vmin=-0.5, vmax=3.5,
              interpolation='nearest', aspect='equal')
axs[1].set_title('flake classes: gray=1L/p52, blue=R1 (ABA 58.8), red=R2 (ABC 64.0)')
for ax in axs:
    for k, (x, y) in SPOTS_04.items():
        ax.plot(x, y, 'k*', ms=14, mec='w')
        ax.annotate(k, (x, y), color='k', fontsize=11, xytext=(x + 1, y + 1))
    ax.set_xlabel('x µm'); ax.set_ylabel('y µm'); ax.grid(alpha=.3)
fig.savefig(f'{OUT}/figs/fig_flake_regions.png', dpi=110, bbox_inches='tight'); plt.close()

# ---- stack ----
b5 = np.load(f'{OUT}/intermediates/bands_05_007.npz')
fig, axs = plt.subplots(2, 2, figsize=(17, 13))
vid(axs[0, 0], '05'); axs[0, 0].set_title('05 stack video')
axs[0, 0].add_patch(plt.Rectangle((b5['X'].min(), b5['Y'].min()),
                    b5['X'].max() - b5['X'].min(), b5['Y'].max() - b5['Y'].min(),
                    fill=False, ec='r', lw=1.5))
for ax, key, t in [(axs[0, 1], 'si', 'Si 520 amp'), (axs[1, 0], 'd2', '2D amp'),
                   (axs[1, 1], 'hbn', 'hBN E2g amp')]:
    im = ax.imshow(b5[key], extent=ext(b5), origin='upper', aspect='equal', cmap='viridis')
    plt.colorbar(im, ax=ax, shrink=.8); ax.set_title('05 Scan007 ' + t)
for ax in axs.ravel():
    ax.set_xlabel('x µm'); ax.grid(alpha=.3, color='w', lw=.3)
fig.savefig(f'{OUT}/figs/fig_stack_bands.png', dpi=110, bbox_inches='tight'); plt.close()

# ---- device ----
b4 = np.load(f'{OUT}/intermediates/bands_06_004.npz')
b2 = np.load(f'{OUT}/intermediates/bands_06_002.npz')
fig, axs = plt.subplots(2, 2, figsize=(17, 13))
vid(axs[0, 0], '06'); axs[0, 0].set_title('06 device video (Image000)')
for z, c in [(b4, 'r'), (b2, 'orange')]:
    axs[0, 0].add_patch(plt.Rectangle((z['X'].min(), z['Y'].min()),
                        z['X'].max() - z['X'].min(), z['Y'].max() - z['Y'].min(),
                        fill=False, ec=c, lw=1.5))
axs[0, 0].plot(*SPOT_06, 'k*', ms=14, mec='w')
axs[0, 0].set_xlim(-30, 30); axs[0, 0].set_ylim(-25, 20)
for ax, z, key, t in [(axs[0, 1], b4, 'si', 'Scan004 Si 520'),
                      (axs[1, 0], b4, 'd2', 'Scan004 2D amp'),
                      (axs[1, 1], b2, 'd2', 'Scan002 2D amp')]:
    im = ax.imshow(z[key], extent=ext(z), origin='upper', aspect='equal', cmap='viridis')
    plt.colorbar(im, ax=ax, shrink=.8); ax.set_title('06 ' + t)
for ax in axs.ravel():
    ax.set_xlabel('x µm'); ax.grid(alpha=.3, color='w', lw=.3)
fig.savefig(f'{OUT}/figs/fig_device_bands.png', dpi=110, bbox_inches='tight'); plt.close()
print('figs written')
