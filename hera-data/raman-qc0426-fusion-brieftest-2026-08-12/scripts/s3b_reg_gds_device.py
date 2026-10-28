# s3b_reg_gds_device.py — robust GDS->device fit: theta x flip coarse scan with
# FFT translation search, then Nelder-Mead refine. Overwrites T_gds_to_dev.npz.
import gdstk, numpy as np
from matplotlib.path import Path as MPath
from scipy.signal import fftconvolve
from scipy.optimize import minimize
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'
lib = gdstk.read_gds('/data/sharpelab/hera-data/raman-qc0426/20260428-3LGr.gds')
first = [c for c in lib.cells if c.name == 'FIRST'][0]
comb = [p for p in first.polygons if p.layer == 11][0].points
c0 = comb.mean(axis=0)
path = MPath(comb)

b4 = np.load(f'{OUT}/intermediates/bands_06_004.npz')
X, Y, d2 = b4['X'], b4['Y'], b4['d2']
Xi, Yi = X.T, Y.T
mask = (d2 > 3000).astype(float)
step = 0.39  # scan004 px

# fine raster of comb interior points in GDS frame (relative to c0)
gx, gy = np.meshgrid(np.arange(-14, 14, 0.2), np.arange(-14, 14, 0.2))
gp = np.column_stack([gx.ravel() + c0[0], gy.ravel() + c0[1]])
inside = path.contains_points(gp)
rel = gp[inside] - c0

# device mask grid (regular in index space; treat as uniform grid ignoring ~0.5deg stage shear here,
# refine step recovers it via the exact transform)
ny, nx = mask.shape
x0d, y0d = Xi[0, 0], Yi[0, 0]
dxd = (Xi[0, -1] - Xi[0, 0]) / (nx - 1)
dyd = (Yi[-1, 0] - Yi[0, 0]) / (ny - 1)

def occupancy(theta, flip, s=1.0):
    R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    F = np.diag([1, -1]) if flip else np.eye(2)
    q = s * rel @ (R @ F).T
    # bin into an image the same cell size as scan grid, centered 0
    H = 41  # +/- 8 um
    ix = np.round(q[:, 0] / dxd).astype(int) + H
    iy = np.round(q[:, 1] / dyd).astype(int) + H
    good = (ix >= 0) & (ix < 2 * H + 1) & (iy >= 0) & (iy < 2 * H + 1)
    occ = np.zeros((2 * H + 1, 2 * H + 1))
    np.add.at(occ, (iy[good], ix[good]), 1)
    return (occ > 0).astype(float), H

best = None
for flip in [False, True]:
    for thd in np.arange(0, 360, 2.0):
        occ, H = occupancy(np.radians(thd), flip)
        corr = fftconvolve(mask, occ[::-1, ::-1], mode='same')
        iy, ix = np.unravel_index(corr.argmax(), corr.shape)
        score = corr[iy, ix]
        if best is None or score > best[0]:
            best = (score, thd, flip, ix, iy)
score, thd, flip, ix, iy = best
tx = x0d + ix * dxd
ty = y0d + iy * dyd
print('coarse: th=%.0f flip=%s t=(%.2f,%.2f) score=%.0f' % (thd, flip, tx, ty, score))

pts_dev = np.column_stack([Xi.ravel(), Yi.ravel()])
maskb = mask.astype(bool)

def params_to_A(p, flip):
    th, s, tx, ty = p
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    F = np.diag([1, -1]) if flip else np.eye(2)
    return s * R @ F, np.array([tx, ty])

def iou(p, flip):
    A, t = params_to_A(p, flip)
    g = (pts_dev - t) @ np.linalg.inv(A).T + c0
    ins = path.contains_points(g).reshape(maskb.shape)
    return (ins & maskb).sum() / (ins | maskb).sum()

p0 = [np.radians(thd), 1.0, tx, ty]
print('start IoU %.3f' % iou(p0, flip))
res = minimize(lambda p: -iou(p, flip), p0, method='Nelder-Mead',
               options=dict(xatol=1e-4, fatol=1e-5, maxiter=4000, maxfev=4000))
th, s, tx, ty = res.x
print('refined IoU %.3f: th=%.2f deg scale=%.4f t=(%.2f,%.2f) flip=%s' %
      (-res.fun, np.degrees(th) % 360, s, tx, ty, flip))
A, t = params_to_A(res.x, flip)
np.savez(f'{OUT}/intermediates/T_gds_to_dev.npz', A=A, t=t, c0=c0, iou=-res.fun,
         theta_deg=np.degrees(th) % 360, scale=s, flip=flip)

cp = np.load(f'{OUT}/intermediates/contact_points_gds.npy', allow_pickle=True).item()
fig, ax = plt.subplots(figsize=(11, 10))
ax.imshow(d2, extent=[X.min(), X.max(), Y.min(), Y.max()], origin='upper',
          cmap='gray', aspect='equal')
tc = (comb - c0) @ A.T + t
ax.plot(tc[:, 0], tc[:, 1], 'c-', lw=1)
for lab, (gxx, gyy, _) in cp.items():
    d = (np.array([gxx, gyy]) - c0) @ A.T + t
    ax.plot(*d, 'r.', ms=6)
    ax.annotate(lab, d, color='orange' if lab in ('TG', 'BG') else 'r', fontsize=11)
ax.set_title('GDS comb + contacts -> device frame, IoU %.3f' % -res.fun)
fig.savefig(f'{OUT}/figs/fig_reg_gds_device.png', dpi=110, bbox_inches='tight')
print('done')
