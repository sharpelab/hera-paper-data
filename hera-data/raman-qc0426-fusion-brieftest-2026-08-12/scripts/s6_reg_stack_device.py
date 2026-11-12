# s6_reg_stack_device.py — register stack(05) -> device(06) stage frames via
# masked edge-map correlation of the video images (persistent features: hBN
# edges, graphite bar, sliver; metal leads + etched core masked out of 06).
import numpy as np
from scipy import ndimage
from scipy.signal import fftconvolve
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'
v5 = np.load(f'{OUT}/intermediates/vid_05_Video_Image000.npz')
v6 = np.load(f'{OUT}/intermediates/vid_06_Video_Image000.npz')

def prep(z, mask_leads=False):
    arr = z['arr'].transpose(1, 0, 2).astype(float)  # (ny,nx,3) row0=ymax
    X, Y = z['X'].T, z['Y'].T
    g = arr.mean(axis=2)
    valid = np.ones(g.shape, bool)
    if mask_leads:
        r, gg, b = arr[..., 0], arr[..., 1], arr[..., 2]
        yellow = (r > 150) & (gg > 120) & (b < 140) & (r + gg - 2 * b > 60)
        yellow = ndimage.binary_dilation(yellow, iterations=12)
        valid &= ~yellow
    return g, valid, X, Y

g5, ok5, X5, Y5 = prep(v5)
g6, ok6, X6, Y6 = prep(v6, mask_leads=True)
# also mask the etched core region of 06 (mesa redefined): radius 14um around (0,-2)
core = (X6 - 0) ** 2 + (Y6 + 2) ** 2 < 14 ** 2
ok6 &= ~core
print('06 valid frac', ok6.mean())

# downsample to ~0.26um/px (factor 4)
def down(a, f=4):
    ny, nx = a.shape
    return a[:ny - ny % f, :nx - nx % f].reshape(ny // f, f, nx // f, f).mean(axis=(1, 3))

g5d, g6d = down(g5), down(g6)
ok6d = down(ok6.astype(float)) > 0.9
X5d, Y5d = down(X5), down(Y5)
X6d, Y6d = down(X6), down(Y6)

def edges(g):
    e = np.hypot(ndimage.sobel(g, 0), ndimage.sobel(g, 1))
    e = e / (np.percentile(e, 99) + 1e-9)
    return np.clip(e, 0, 1)

e5, e6 = edges(g5d), edges(g6d)
e6m = e6 * ok6d
e6m -= e6m[ok6d].mean() * ok6d
px = X5d[0, 1] - X5d[0, 0]
print('px um', px)

best = None
for thd in np.arange(-8, 8.01, 0.5):
    rot = ndimage.rotate(e5, -thd, reshape=False, order=1)  # rotate about image center
    rot = rot - rot.mean()
    corr = fftconvolve(e6m, rot[::-1, ::-1], mode='same')
    iy, ix = np.unravel_index(corr.argmax(), corr.shape)
    if best is None or corr[iy, ix] > best[0]:
        best = (corr[iy, ix], thd, ix, iy)
score, thd, ix, iy = best
ny, nx = e5.shape
# shift in pixels of image centers
dxp = ix - nx // 2
dyp = iy - ny // 2
# in um: x increases with col; y DEcreases with row
c5 = np.array([X5d[ny // 2, nx // 2], Y5d[ny // 2, nx // 2]])
c6 = np.array([X6d[ny // 2 + dyp, nx // 2 + dxp], Y6d[ny // 2 + dyp, nx // 2 + dxp]])
print('best th=%.2f deg, center %s -> %s, score %.1f' % (thd, c5, c6, score))
# transform: dev = R(-thd about c5? careful) -- rotation applied to image about center;
# stage y is flipped vs rows, so image rotation by -thd == stage rotation by +? verify by construction:
# We define: dev_pt = R(theta) @ (stack_pt - c5) + c6, theta = ?
# imagery rotation -thd (rows/cols) with y-flip corresponds to stage-frame rotation of -thd? test empirically below.
for theta_try in [np.radians(thd), np.radians(-thd)]:
    R = np.array([[np.cos(theta_try), -np.sin(theta_try)], [np.sin(theta_try), np.cos(theta_try)]])
    np.savez(f'{OUT}/intermediates/T_stack_to_dev_cand_%+.2f.npz' % np.degrees(theta_try),
             R=R, c5=c5, c6=c6, theta_deg=np.degrees(theta_try), score=score)
print('saved candidates; verify sign with overlay')
