# s7_compose.py — compose device->stack->flake transforms; map channel probe
# footprints onto the flake R1/R2 mask; compute per-channel domain shares with
# a registration stress scan (transform variants). Writes the registration
# artifact figure + shares table.
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/data/sharpelab/hera-data/raman-qc0426-fusion-brieftest-2026-08-12'

# stack->dev central
c5 = np.array([-0.156, -0.488]); c6 = np.array([6.960, -4.945])
TH_SD = 1.0  # deg
Tfs = np.load(f'{OUT}/intermediates/T_flake_to_stack.npz')   # flake->stack
A_fs, t_fs, fc = Tfs['A'], Tfs['t'], Tfs['fc']
ch = np.load(f'{OUT}/intermediates/channels_dev.npy', allow_pickle=True).item()
fr = np.load(f'{OUT}/intermediates/flake_regions.npz')
fX, fY = fr['X'].T, fr['Y'].T
lab_img = fr['lab_img']; fw_img = fr['fwhm'].reshape(57, 101)
nyf, nxf = lab_img.shape
fx0, fdx = fX[0, 0], (fX[0, -1] - fX[0, 0]) / (nxf - 1)
fy0, fdy = fY[0, 0], (fY[-1, 0] - fY[0, 0]) / (nyf - 1)

def R(deg):
    th = np.radians(deg)
    return np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])

def dev_to_flake(pts, th_sd=TH_SD, dt_sd=(0, 0), th_fs=None, dt_fs=(0, 0)):
    # dev -> stack
    q = (pts - (c6 + np.asarray(dt_sd))) @ np.linalg.inv(R(th_sd)).T + c5
    # stack -> flake: stack = A_fs@(flake-fc)+t_fs  (with optional perturbation)
    A = A_fs if th_fs is None else R(th_fs)
    t = t_fs + np.asarray(dt_fs)
    return (q - t) @ np.linalg.inv(A).T + fc

def classify(pts_flake):
    """Return share of px on R1 (lab 0), R2 (lab 1), other-graphene, off-map/no-data."""
    ix = np.round((pts_flake[:, 0] - fx0) / fdx).astype(int)
    iy = np.round((pts_flake[:, 1] - fy0) / fdy).astype(int)
    ok = (ix >= 0) & (ix < nxf) & (iy >= 0) & (iy < nyf)
    n = len(pts_flake)
    lab = np.full(n, -2.0)  # off-map
    l = lab_img[iy[ok], ix[ok]]
    f = fw_img[iy[ok], ix[ok]]
    v = np.where(np.isnan(l), np.where(np.isfinite(f), -1.0, -2.0), l)  # -1: graphene, not R1/R2
    lab[ok] = v
    return {k: float((lab == c).mean()) for k, c in
            [('R1_ABA', 0), ('R2_ABC', 1), ('other_gr', -1), ('nodata', -2)]}

theta_fs_c = float(Tfs['theta_deg'])
variants = [dict(th_sd=TH_SD, th_fs=theta_fs_c)]
for dth_sd in (-0.5, 0.5):
    variants.append(dict(th_sd=TH_SD + dth_sd, th_fs=theta_fs_c))
for dth_fs in (-0.3, 0.3):
    variants.append(dict(th_sd=TH_SD, th_fs=theta_fs_c + dth_fs))
for dt in [(-0.75, 0), (0.75, 0), (0, -0.75), (0, 0.75)]:
    variants.append(dict(th_sd=TH_SD, th_fs=theta_fs_c, dt_fs=dt))
# upper-anchor outlier variant (th -0.68, t +(0.54,-0.53) vs central)
variants.append(dict(th_sd=TH_SD, th_fs=-0.68, dt_fs=(0.47, -0.53)))

names = ['sr1_T3T4', 'sr2_B4B5', 'sr3_T5B6', 'sd_T2B7', 'bar_full']
table = {}
for name in names:
    rows = []
    for v in variants:
        pf = dev_to_flake(ch[name], th_sd=v.get('th_sd', TH_SD), th_fs=v.get('th_fs'),
                          dt_fs=v.get('dt_fs', (0, 0)))
        rows.append(classify(pf))
    table[name] = rows
    c = rows[0]
    r1 = [r['R1_ABA'] for r in rows]; r2 = [r['R2_ABC'] for r in rows]
    print('%-9s central R1 %.2f R2 %.2f other %.2f nodata %.2f | stress R1 %.2f-%.2f R2 %.2f-%.2f'
          % (name, c['R1_ABA'], c['R2_ABC'], c['other_gr'], c['nodata'],
             min(r1), max(r1), min(r2), max(r2)))
np.save(f'{OUT}/intermediates/channel_shares.npy', table, allow_pickle=True)

# ---- registration artifact figure ----
from matplotlib.colors import ListedColormap
cls = np.full(lab_img.shape, np.nan)
cls[np.isfinite(fw_img) & (fw_img < 40)] = 0
cls[np.isfinite(fw_img) & (fw_img >= 40) & (fw_img <= 56)] = 1
cls[lab_img == 0] = 2
cls[lab_img == 1] = 3
fig, ax = plt.subplots(figsize=(16, 9))
cmap = ListedColormap(['#cccccc', '#8a8a8a', '#7ba3e8', '#e87b7b'])
ax.imshow(cls, extent=[fX.min(), fX.max(), fY.min(), fY.max()], origin='upper',
          cmap=cmap, vmin=-.5, vmax=3.5, interpolation='nearest', aspect='equal')
style = {'sr1_T3T4': ('blue', 'sr1 (T3-T4)'), 'sr2_B4B5': ('darkgreen', 'sr2 (B4-B5)'),
         'sr3_T5B6': ('purple', 'sr3 (T5/B6 Hall)'), 'sd_T2B7': ('k', None), 'bar_full': (None, None)}
mesa = dev_to_flake(ch['mesa_pts_dev'][::7])
ax.plot(mesa[:, 0], mesa[:, 1], '.', color='0.25', ms=1, alpha=.35, label='mesa (etched device)')
for name in ['sd_T2B7', 'sr1_T3T4', 'sr2_B4B5', 'sr3_T5B6']:
    col, lab = style[name]
    pf = dev_to_flake(ch[name])
    ax.plot(pf[:, 0], pf[:, 1], '.', color=col, ms=2.5, alpha=.9,
            label=lab or 'S-D span (T2-B7)')
for k, (x, y) in {'spot1': (13.3, 0.9), 'spot2': (-23.1, 5.1)}.items():
    ax.plot(x, y, 'k*', ms=15, mec='w'); ax.annotate(k, (x, y), fontsize=11)
ax.legend(loc='lower right', fontsize=10)
ax.set_xlabel('x µm (flake stage frame, 2026-04-28)')
ax.set_ylabel('y µm')
ax.set_title('QC0426 registration artifact: device channels -> flake-stage R1/R2 mask\n'
             'lt-gray=1L, dk-gray=p52/thickness-ambig, blue=R1(ABA), red=R2(ABC); '
             'chain: GDS->Scan004 (IoU .76) -> video NCC (th=+1.0) -> ribbon-mask fit (th=-2.09)')
fig.savefig(f'{OUT}/figs/fig_registration_artifact.png', dpi=120, bbox_inches='tight')
print('artifact written')
