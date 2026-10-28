# s5_reg_flake_stack.py — register flake map (Scan009, 04 frame) to stack map
# (Scan007, 05 frame) by exhaustive rotation x flip x FFT-translation search on
# graphene-presence masks, then report the best transforms.
import numpy as np
from scipy.signal import fftconvolve
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'
fr = np.load(f'{OUT}/intermediates/flake_regions.npz')
b5 = np.load(f'{OUT}/intermediates/bands_05_007.npz')

# flake graphene-presence mask on its grid (ny,nx), 0.746 um px
fmask = np.isfinite(fr['fwhm'].reshape(57, 101))
fX, fY = fr['X'].T, fr['Y'].T   # (ny,nx), row0 = ymax
# stack mask
smask = b5['d2'] > 8000
sX, sY = b5['X'].T, b5['Y'].T
print('flake px', fmask.sum(), 'stack px', smask.sum())

# resample both to common 0.65um grid in own frames (nearest)
def grid_info(Xi, Yi):
    ny, nx = Xi.shape
    dx = (Xi[0, -1] - Xi[0, 0]) / (nx - 1)
    dy = (Yi[-1, 0] - Yi[0, 0]) / (ny - 1)
    return Xi[0, 0], Yi[0, 0], dx, dy

fx0, fy0, fdx, fdy = grid_info(fX, fY)
sx0, sy0, sdx, sdy = grid_info(sX, sY)
print('flake step', fdx, fdy, 'stack step', sdx, sdy)

# work in physical um: flake mask points (relative to flake mask centroid)
fyi, fxi = np.where(fmask)
fpts = np.column_stack([fX[fyi, fxi], fY[fyi, fxi]])
fc = fpts.mean(axis=0)
rel = fpts - fc

best = []
H = 46  # bins of sdx (~30um shift range)
for flip in [False, True]:
    for thd in np.arange(0, 360, 2.0):
        th = np.radians(thd)
        R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        F = np.diag([1, -1]) if flip else np.eye(2)
        q = rel @ (R @ F).T
        ix = np.round(q[:, 0] / sdx).astype(int) + H
        iy = np.round(q[:, 1] / sdy).astype(int) + H
        good = (ix >= 0) & (ix < 2 * H + 1) & (iy >= 0) & (iy < 2 * H + 1)
        occ = np.zeros((2 * H + 1, 2 * H + 1))
        np.add.at(occ, (iy[good], ix[good]), 1)
        occ = (occ > 0).astype(float)
        # correlate: how well flake-graphene lands on stack-graphene MINUS landing on stack-empty
        sc = smask.astype(float) - 0.6 * (~smask).astype(float)
        corr = fftconvolve(sc, occ[::-1, ::-1], mode='same')
        iyb, ixb = np.unravel_index(corr.argmax(), corr.shape)
        best.append((corr[iyb, ixb], thd, flip, ixb, iyb))
best.sort(reverse=True)
for b in best[:8]:
    score, thd, flip, ixb, iyb = b
    tx = sX[0, 0] + ixb * sdx
    ty = sY[0, 0] + iyb * sdy
    print('score %8.0f  th=%5.1f flip=%s  t=(%6.2f,%6.2f)' % (score, thd, flip, tx, ty))
np.save(f'{OUT}/intermediates/flake_stack_coarse.npy', np.array(best[:20], dtype=object), allow_pickle=True)
