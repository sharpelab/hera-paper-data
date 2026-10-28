# s3_reg_gds_device.py — fit GDS(mesa comb) -> device stage frame (Scan LA--004)
# similarity transform (flip, rotation, scale, translation) by maximizing IoU
# between the rasterized comb polygon and the Scan004 graphene (2D-amp) mask.
import gdstk, numpy as np
from matplotlib.path import Path as MPath
from scipy.optimize import minimize
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'
lib = gdstk.read_gds('/data/sharpelab/hera-data/raman-qc0426/20260428-3LGr.gds')
first = [c for c in lib.cells if c.name == 'FIRST'][0]
comb = [p for p in first.polygons if p.layer == 11][0].points
c0 = np.array([25.6, 50.2])  # comb bbox center in GDS frame
path = MPath(comb)

b4 = np.load(f'{OUT}/intermediates/bands_06_004.npz')
X, Y, d2 = b4['X'], b4['Y'], b4['d2']            # X,Y (nx,ny); d2 (ny,nx)
Xi, Yi = X.T, Y.T                                 # (ny,nx) to match d2
mask = d2 > 3000

pts_dev = np.column_stack([Xi.ravel(), Yi.ravel()])

def params_to_T(p, flip):
    th, s, tx, ty = p
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    F = np.diag([1, -1]) if flip else np.eye(2)
    A = s * R @ F
    return A, np.array([tx, ty])

def iou(p, flip):
    A, t = params_to_T(p, flip)
    # inverse: gds = F^-1 R^-1 (dev - t)/s + c0
    inv = np.linalg.inv(A)
    g = (pts_dev - t) @ inv.T + c0
    inside = path.contains_points(g).reshape(mask.shape)
    inter = (inside & mask).sum(); union = (inside | mask).sum()
    return inter / union

best = None
for flip in [False, True]:
    for th0 in np.radians(np.arange(0, 360, 10)):
        v = iou([th0, 1.0, 0.0, -1.0], flip)
        if best is None or v > best[0]:
            best = (v, th0, flip)
print('coarse best IoU %.3f th=%.0fdeg flip=%s' % (best[0], np.degrees(best[1]), best[2]))
flip = best[2]
res = minimize(lambda p: -iou(p, flip), [best[1], 1.0, 0.0, -1.0],
               method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-5, maxiter=2000))
th, s, tx, ty = res.x
print('refined IoU %.3f: th=%.2f deg scale=%.4f t=(%.2f,%.2f) flip=%s' %
      (-res.fun, np.degrees(th), s, tx, ty, flip))
A, t = params_to_T(res.x, flip)
np.savez(f'{OUT}/intermediates/T_gds_to_dev.npz', A=A, t=t, c0=c0, iou=-res.fun,
         theta_deg=np.degrees(th), scale=s, flip=flip)

# overlay figure: transformed comb + contacts on Scan004 2D map
cp = np.load(f'{OUT}/intermediates/contact_points_gds.npy', allow_pickle=True).item()
fig, ax = plt.subplots(figsize=(11, 10))
ax.imshow(d2, extent=[X.min(), X.max(), Y.min(), Y.max()], origin='upper',
          cmap='gray', aspect='equal')
tc = (comb - c0) @ A.T + t
ax.plot(tc[:, 0], tc[:, 1], 'c-', lw=1)
for lab, (gx, gy, _) in cp.items():
    d = (np.array([gx, gy]) - c0) @ A.T + t
    ax.plot(*d, 'r.', ms=6)
    ax.annotate(lab, d, color='orange' if lab in ('TG', 'BG') else 'r', fontsize=11)
ax.set_title('GDS comb + labeled contacts -> device frame (Scan004 2D amp), IoU %.3f' % -res.fun)
ax.set_xlabel('x µm (device stage frame)')
fig.savefig(f'{OUT}/figs/fig_reg_gds_device.png', dpi=110, bbox_inches='tight')
print('done')
