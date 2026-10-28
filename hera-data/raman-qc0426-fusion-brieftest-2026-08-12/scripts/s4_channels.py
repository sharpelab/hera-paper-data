# s4_channels.py — extract bar spine + finger junctions from GDS comb; define
# per-channel probed segments (sr1: T3-T4, sr2: B4-B5, sr3: T5/B6 cross) in the
# device stage frame; save polygons/segments for downstream mapping.
import gdstk, numpy as np
from matplotlib.path import Path as MPath
from scipy import ndimage
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'
lib = gdstk.read_gds('/data/sharpelab/hera-data/raman-qc0426/20260428-3LGr.gds')
first = [c for c in lib.cells if c.name == 'FIRST'][0]
comb = [p for p in first.polygons if p.layer == 11][0].points
path = MPath(comb)
T = np.load(f'{OUT}/intermediates/T_gds_to_dev.npz')
A, t, c0 = T['A'], T['t'], T['c0']
cp = np.load(f'{OUT}/intermediates/contact_points_gds.npy', allow_pickle=True).item()

# fine raster in GDS frame
res = 0.1
xs = np.arange(14, 37, res); ys = np.arange(39, 62, res)
GX, GY = np.meshgrid(xs, ys)
pts = np.column_stack([GX.ravel(), GY.ravel()])
ins = path.contains_points(pts).reshape(GX.shape)
# opening with disk r=0.7um kills the ~1.2um fingers, keeps the ~2.5um bar
r = int(0.7 / res)
yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
disk = (xx * xx + yy * yy) <= r * r
bar = ndimage.binary_opening(ins, structure=disk)
# largest connected component
lab, n = ndimage.label(bar)
sizes = ndimage.sum(bar, lab, range(1, n + 1))
bar = lab == (1 + sizes.argmax())
print('bar px:', bar.sum(), 'of mesa', ins.sum())

# spine: fit a line x -> y over bar pixels
bx, by = GX[bar], GY[bar]
cf = np.polyfit(bx, by, 1)
print('bar spine (GDS frame): y = %.4f x + %.2f' % tuple(cf))
u = np.array([1, cf[0]]); u = u / np.linalg.norm(u)   # along-bar unit vector

# junctions: nearest bar pixel to each contact centroid
barpts = np.column_stack([bx, by])
junc = {}
for k, (x, y, _) in cp.items():
    if k in ('TG', 'BG'):
        continue
    d = np.hypot(barpts[:, 0] - x, barpts[:, 1] - y)
    junc[k] = barpts[d.argmin()]
# along-bar coordinate s (µm along spine, origin = bar centroid)
bc = barpts.mean(axis=0)
def s_of(p):
    return float((p - bc) @ u)
for k in ['T1','T2','T3','T4','T5','T6','T7','B1','B2','B3','B4','B5','B6','B7','B8']:
    j = junc[k]
    print('%s junction gds=(%.2f,%.2f) s=%.2f' % (k, j[0], j[1], s_of(j)))

# channel definitions (bar segments between junctions, full bar width)
def segment_mask(s1, s2):
    ss = (barpts - bc) @ u
    m = (ss >= min(s1, s2)) & (ss <= max(s1, s2))
    return barpts[m]

chan = {
    'sr1_T3T4': segment_mask(s_of(junc['T3']), s_of(junc['T4'])),
    'sr2_B4B5': segment_mask(s_of(junc['B4']), s_of(junc['B5'])),
    'sr3_T5B6': segment_mask((s_of(junc['T5']) + s_of(junc['B6'])) / 2 - 0.5,
                             (s_of(junc['T5']) + s_of(junc['B6'])) / 2 + 0.5),
    'bar_full': barpts,
    'sd_T2B7': segment_mask(s_of(junc['T2']), s_of(junc['B7'])),
}
# transform all to device frame
out = {}
for k, p in chan.items():
    out[k] = (p - c0) @ A.T + t
out['junctions_dev'] = {k: tuple((np.array(v) - c0) @ A.T + t) for k, v in junc.items()}
out['mesa_pts_dev'] = (pts[ins.ravel()] - c0) @ A.T + t
np.save(f'{OUT}/intermediates/channels_dev.npy', out, allow_pickle=True)
for k in ['sr1_T3T4', 'sr2_B4B5', 'sr3_T5B6', 'sd_T2B7']:
    q = out[k]
    print(k, 'dev-frame extent x %.2f..%.2f y %.2f..%.2f (%d pts)' %
          (q[:, 0].min(), q[:, 0].max(), q[:, 1].min(), q[:, 1].max(), len(q)))
print('done')
