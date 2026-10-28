# s5b_refine_flake_stack.py — refine flake->stack similarity (theta,s,tx,ty) by
# IoU on graphene masks; render overlay + landed R1/R2 regions in stack frame.
import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import RegularGridInterpolator
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'
fr = np.load(f'{OUT}/intermediates/flake_regions.npz')
b5 = np.load(f'{OUT}/intermediates/bands_05_007.npz')
fmask = np.isfinite(fr['fwhm'].reshape(57, 101))
fX, fY = fr['X'].T, fr['Y'].T
sX, sY = b5['X'].T, b5['Y'].T
smask = b5['d2'] > 8000

fyi, fxi = np.where(fmask)
fpts = np.column_stack([fX[fyi, fxi], fY[fyi, fxi]])
fc = fpts.mean(axis=0)

# stack mask sampler on approx-regular grid (use stage um via nearest index)
ny, nx = smask.shape
sx0, sdx = sX[0, 0], (sX[0, -1] - sX[0, 0]) / (nx - 1)
sy0, sdy = sY[0, 0], (sY[-1, 0] - sY[0, 0]) / (ny - 1)

def sample(mask, pts):
    ix = np.round((pts[:, 0] - sx0) / sdx).astype(int)
    iy = np.round((pts[:, 1] - sy0) / sdy).astype(int)
    ok = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    v = np.zeros(len(pts), bool)
    v[ok] = mask[iy[ok], ix[ok]]
    return v, ok

def T(p):
    th, s, tx, ty = p
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return s * R, np.array([tx, ty])

def score(p):
    A, t = T(p)
    q = (fpts - fc) @ A.T + t
    v, ok = sample(smask, q)
    if ok.sum() < 500:
        return 0.0
    return v.sum() / ok.sum()   # fraction of in-FOV flake px landing on stack graphene

p0 = [np.radians(-2.0), 1.0, 4.51, -1.39]
res = minimize(lambda p: -score(p), p0, method='Nelder-Mead',
               options=dict(xatol=1e-4, fatol=1e-5, maxiter=3000))
th, s, tx, ty = res.x
print('refined: hit-frac %.3f th=%.2f deg scale=%.4f t=(%.2f,%.2f)' %
      (-res.fun, np.degrees(th), s, tx, ty))
A, t = T(res.x)
np.savez(f'{OUT}/intermediates/T_flake_to_stack.npz', A=A, t=t, fc=fc,
         theta_deg=np.degrees(th), scale=s, hitfrac=-res.fun)

# overlay figure
lab_img = fr['lab_img']
fig, axs = plt.subplots(1, 2, figsize=(21, 8))
ax = axs[0]
ax.imshow(smask, extent=[sX.min(), sX.max(), sY.min(), sY.max()], origin='upper',
          cmap='gray', aspect='equal', alpha=.7)
q = (fpts - fc) @ A.T + t
ax.plot(q[:, 0], q[:, 1], 'r.', ms=1, alpha=.25)
ax.set_title('flake graphene px -> stack frame (bg = stack 2D mask)')
ax = axs[1]
ax.imshow(b5['d2'], extent=[sX.min(), sX.max(), sY.min(), sY.max()], origin='upper',
          cmap='gray', aspect='equal')
for lv, c in [(0, 'dodgerblue'), (1, 'red')]:
    m = lab_img == lv
    pyi, pxi = np.where(m)
    pp = np.column_stack([fX[pyi, pxi], fY[pyi, pxi]])
    qq = (pp - fc) @ A.T + t
    ax.plot(qq[:, 0], qq[:, 1], '.', color=c, ms=2, alpha=.5)
ax.set_title('R1 (blue, ABA) / R2 (red, ABC) landed in stack frame')
for a in axs:
    a.set_xlabel('x µm (stack frame)'); a.grid(alpha=.3)
fig.savefig(f'{OUT}/figs/fig_reg_flake_stack.png', dpi=110, bbox_inches='tight')
print('done')
