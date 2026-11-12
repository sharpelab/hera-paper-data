# s1_maps.py — flake region masks + per-band amplitude maps for all three stages.
# Run from hera/models/raman_stacking:
#   uv run --no-project --with witio --with numpy --with scipy --with matplotlib python3 \
#     $OUT/scripts/s1_maps.py
import sys, numpy as np
sys.path.insert(0, '/home/zack/sharpelab/measurement-env/hera/models/raman_stacking')
import raman_io, map_tools
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'
SRC = '/data/sharpelab/hera-data/raman-qc0426'

def band_amp(wn, ii, lo, hi, blo, bhi):
    """Peak height in [lo,hi] above a linear baseline from medians of [blo] and [bhi] windows."""
    sel = (wn >= lo) & (wn <= hi)
    b1 = np.median(ii[(wn >= blo[0]) & (wn <= blo[1])], axis=0)
    b2 = np.median(ii[(wn >= bhi[0]) & (wn <= bhi[1])], axis=0)
    base = (b1 + b2) / 2
    return ii[sel].max(axis=0) - base

def grid_for(tag, scan):
    import witio
    prj = witio.read(f'{SRC}/{tag}')
    d = [x for x in prj.data if x.caption == f'{scan}--Spec.Data 1'][0]
    return d.position_grid('um')

# ---- stage 04 flake: region masks ----
ds = raman_io.load_wip(f'{SRC}/04_3LGr.wip')
m = [d for d in ds if d['caption'].startswith('Scan LA--009')][0]
wn, ii, nx, ny = m['wn'], m['ii'], m['nx'], m['ny']
z = np.load(f'{OUT}/intermediates/flake_pm.npz')
f = z['fwhm']
CUT = 56.0  # thickness/p52 mask boundary; reproduces the locked contract's split exactly
body = np.where((f > CUT) & np.isfinite(f), f, np.nan)
labels, centers = map_tools.two_population_split(body)
# label 0 = lower mean (ABA, R1), 1 = higher (ABC, R2)
lab_img = map_tools.to_image(labels.astype(float), nx, ny)
X, Y = grid_for('04_3LGr.wip', 'Scan LA--009')
np.savez(f'{OUT}/intermediates/flake_regions.npz', labels=labels, lab_img=lab_img,
         X=X, Y=Y, fwhm=f, amp=z['amp'], center=z['center'], cut=CUT,
         centers=centers)
print('flake regions: R1(ABA) n=%d mean=%.2f | R2(ABC) n=%d mean=%.2f' % (
    (labels == 0).sum(), body[labels == 0].mean(), (labels == 1).sum(), body[labels == 1].mean()))
print('flake X', X.min(), X.max(), X.shape, 'Y', Y.min(), Y.max())

# 2D amplitude map (graphene footprint, any thickness)
amp_img = map_tools.to_image(z['amp'], nx, ny)
np.savez(f'{OUT}/intermediates/flake_amp.npz', amp_img=amp_img, X=X, Y=Y)

# ---- stages 05/06: band amplitude maps ----
for tag, scans in [('05_3LGr-stack.wip', ['Scan LA--007']),
                   ('06_3LGr-device.wip', ['Scan LA--002', 'Scan LA--004'])]:
    ds = raman_io.load_wip(f'{SRC}/{tag}')
    for scan in scans:
        m = [d for d in ds if d['caption'].startswith(scan)][0]
        wn, ii, nx, ny = m['wn'], m['ii'], m['nx'], m['ny']
        si = band_amp(wn, ii, 500, 540, (430, 470), (560, 600))
        g = band_amp(wn, ii, 1560, 1610, (1450, 1500), (1700, 1750))
        d2 = band_amp(wn, ii, 2620, 2780, (2450, 2550), (2900, 3000))
        hbn = band_amp(wn, ii, 1350, 1385, (1250, 1300), (1450, 1500))
        X, Y = grid_for(tag, scan)
        st = tag[:2]
        np.savez(f'{OUT}/intermediates/bands_{st}_{scan.replace("Scan LA--","")}.npz',
                 si=map_tools.to_image(si, nx, ny), g=map_tools.to_image(g, nx, ny),
                 d2=map_tools.to_image(d2, nx, ny), hbn=map_tools.to_image(hbn, nx, ny),
                 X=X, Y=Y)
        print(tag, scan, 'nx,ny', nx, ny, 'X', round(X.min(), 1), round(X.max(), 1),
              'Y', round(Y.min(), 1), round(Y.max(), 1))
print('done')
