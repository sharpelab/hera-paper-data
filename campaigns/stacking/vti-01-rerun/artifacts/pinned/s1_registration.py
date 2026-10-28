#!/usr/bin/env python
# Step 2 (fusion recipe) — spatial registration artifact for vti-01.
# Frame bridges actually available: (a) the three stage-registered video
# images inside vti-01.wip, (b) the device card's topological contact map
# (T_SD -- L1..L4 down one side -- B_SD; R1/R2 dead), (c) the Raman
# contract's regions.npz raster with its inferred device rectangle.
# There is NO GDS and NO post-fab optical image: the flake->finished-device
# link is the piece-identity inference (the 11.5 x 13 um rectangle is the
# only Hall-bar-shaped remnant). Contact positions inside the rectangle are
# unconstrained -> handled as placement variants + jitter, not as one guess.
#
# Run from the run dir:
#   uv run --no-project --with numpy --with matplotlib --with witio \
#       python s1_registration.py
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import ListedColormap, BoundaryNorm
import witio

RUN = '/data/sharpelab/hera-data/raman-vti-01-20260818-fusion-b'
WIP = f'{RUN}/inputs/vti-01.wip'
NPZ = f'{RUN}/inputs/regions.npz'

proj = witio.read(WIP)
imgs = {}
for cap in ['73474_--Video Image--002', '73474_--Video Image--004',
            '73474_--Video Image--007']:
    d = [x for x in proj.data if (getattr(x, 'caption', '') or '') == cap][0]
    a = d.array()
    gx, gy = d.position_grid()
    imgs[cap[-3:]] = (a, gx, gy)

z = np.load(NPZ)
labels_S0 = z['labels_S0']
labels_S1 = z['labels_S1']
xe, ye = z['x_edges'], z['y_edges']
xc, yc = z['x_centres'], z['y_centres']
rect = json.loads(str(z['device_rect']))
cuts = json.loads(str(z['cut_footprints']))
mapfp = json.loads(str(z['map_footprints']))
RX, RY = rect['x'], rect['y']

# ---- channel placement variants -------------------------------------------
# Hall bar: T_SD -- L1 L2 L3 L4 (probes in order down one side) -- B_SD.
# Channels: sr1 = B_SD-L4, sr2 = L4-L1, sr3 = L3-L2.
# Contacts modeled evenly spaced along the bar axis at fractions 0 (T_SD),
# 1/5..4/5 (L1..L4), 1 (B_SD). Variants: bar axis along y or x, both
# orientations; jitter: rect shifted on a +/-2 um grid (in-frame
# registration budget). Composition counted over classified graphene pixels
# (labels 10/11/12) inside each channel's segment band, full transverse width.
FR = {'sr1': (4/5, 1.0), 'sr2': (1/5, 4/5), 'sr3': (2/5, 3/5)}


def seg_counts(lab, x0, x1, y0, y1, axis, flip, f0, f1):
    if flip:
        f0, f1 = 1 - f1, 1 - f0
    if axis == 'y':
        sy0, sy1 = y0 + f0 * (y1 - y0), y0 + f1 * (y1 - y0)
        sx0, sx1 = x0, x1
    else:
        sx0, sx1 = x0 + f0 * (x1 - x0), x0 + f1 * (x1 - x0)
        sy0, sy1 = y0, y1
    m = ((xc[None, :] >= sx0) & (xc[None, :] <= sx1) &
         (yc[:, None] >= sy0) & (yc[:, None] <= sy1))
    vals = lab[m]
    out = {int(k): int((vals == k).sum()) for k in np.unique(vals)}
    cl = sum(out.get(k, 0) for k in (10, 11, 12))
    return out, cl, out.get(11, 0), out.get(10, 0), out.get(12, 0)


def run_grid(jit):
    variants = []
    for axis in ('y', 'x'):
        for flip in (False, True):
            for dx in jit:
                for dy in jit:
                    row = {'axis': axis, 'flip': flip, 'dx': dx, 'dy': dy}
                    for ch, (f0, f1) in FR.items():
                        out, cl, b, a, mx = seg_counts(
                            labels_S1, RX[0] + dx, RX[1] + dx,
                            RY[0] + dy, RY[1] + dy, axis, flip, f0, f1)
                        row[ch] = {'counts': out, 'classified': cl,
                                   'B_abc': b, 'A_aba': a, 'mixed': mx,
                                   'abc_frac': (b / cl if cl else None)}
                    variants.append(row)
    summary = {}
    for ch in FR:
        fr = [v[ch]['abc_frac'] for v in variants
              if v[ch]['abc_frac'] is not None]
        ncl = [v[ch]['classified'] for v in variants]
        summary[ch] = {'n_variants': len(variants),
                       'n_no_coverage': sum(1 for v in variants
                                            if v[ch]['classified'] == 0),
                       'abc_frac_min': float(min(fr)),
                       'abc_frac_max': float(max(fr)),
                       'classified_px_min': int(min(ncl)),
                       'classified_px_max': int(max(ncl))}
    return variants, summary


variants, summary = run_grid((-1, 0, 1))           # stated ±1 µm budget
variants2, summary2 = run_grid((-2, 0, 2))         # stress margin

# whole-rectangle composition (S0 and S1), no jitter
whole = {}
for tag, lab in (('S0', labels_S0), ('S1', labels_S1)):
    out, cl, b, a, mx = seg_counts(lab, RX[0], RX[1], RY[0], RY[1], 'y', False, 0, 1)
    whole[tag] = {'counts': out, 'classified': cl, 'B_abc': b, 'A_aba': a,
                  'mixed': mx, 'abc_frac': b / cl if cl else None}

with open(f'{RUN}/intermediates/registration_coverage.json', 'w') as f:
    json.dump({'device_rect': rect, 'cut_footprints': cuts,
               'contact_fractions': FR, 'whole_rect': whole,
               'variant_summary_pm1um': summary,
               'variant_summary_pm2um_stress': summary2,
               'variants_pm1um': variants,
               'variants_pm2um_stress': variants2}, f, indent=1)

# ---- figure ---------------------------------------------------------------
lab_colors = {0: (1, 1, 1, 0), 1: (.92, .92, .92, .6), 2: (.35, .35, .35, .8),
              3: (.75, .75, .95, .8), 5: (.85, .85, .6, .7),
              10: (.10, .45, .85, .75), 11: (.90, .35, .10, .75),
              12: (.55, .10, .60, .8)}
keys = sorted(lab_colors)                      # [0,1,2,3,5,10,11,12]
cmap = ListedColormap([lab_colors[k] for k in keys])
norm = BoundaryNorm([-.5, .5, 1.5, 2.5, 4, 7.5, 10.5, 11.5, 12.5], len(keys))


def show_img(ax, key, ds=4):
    a, gx, gy = imgs[key]
    ax.pcolormesh(gx[::ds, ::ds], gy[::ds, ::ds],
                  a[::ds, ::ds].mean(axis=2)[:-1, :-1] if False else
                  a[::ds, ::ds, :].mean(axis=2), cmap='gray', shading='auto',
                  rasterized=True)


def show_labels(ax, lab, alpha=1.0):
    ax.pcolormesh(xe, ye, lab, cmap=cmap, norm=norm, shading='flat',
                  alpha=alpha, rasterized=True)


def draw_rect(ax, x, y, **kw):
    ax.add_patch(Rectangle((x[0], y[0]), x[1] - x[0], y[1] - y[0],
                           fill=False, **kw))


fig, axs = plt.subplots(2, 2, figsize=(15, 11))
for ax in axs.flat:
    ax.set_aspect('equal')
    ax.set_xlabel('stage x (µm)')
    ax.set_ylabel('stage y (µm)')

ax = axs[0, 0]
show_img(ax, '002')
show_labels(ax, labels_S0, alpha=.5)
draw_rect(ax, RX, RY, ec='lime', lw=2)
draw_rect(ax, mapfp['22'][:2], mapfp['22'][2:], ec='w', lw=1, ls='--')
ax.set_xlim(-12085, -12020); ax.set_ylim(1260, 1308)
ax.set_title('S0 12:55–12:57 — video 002 + map-22 labels\n'
             'orange=B/ABC, blue=A/ABA, purple=wall; green=inferred device rect')

ax = axs[0, 1]
show_img(ax, '004')
show_labels(ax, labels_S1, alpha=.5)
draw_rect(ax, RX, RY, ec='lime', lw=2)
draw_rect(ax, mapfp['27'][:2], mapfp['27'][2:], ec='w', lw=1, ls='--')
for k, c in cuts.items():
    draw_rect(ax, c['x'], c['y'], ec='red', lw=1.5, ls=':')
ax.set_xlim(-12060, -12020); ax.set_ylim(1260, 1305)
ax.set_title('S1 13:19–13:20 — video 004 + map-27 labels\n'
             'red dotted = later 1064 nm cut passes (13:27 / 13:30)')

ax = axs[1, 0]
show_img(ax, '007')
draw_rect(ax, RX, RY, ec='lime', lw=2)
for k, c in cuts.items():
    draw_rect(ax, c['x'], c['y'], ec='red', lw=1.5, ls=':')
# channel schematic, axis=y variant, T_SD at top (y1) — TOPOLOGICAL ONLY
x_bar = (RX[0] + RX[1]) / 2
names = ['B_SD', 'L4', 'L3', 'L2', 'L1', 'T_SD']
for i, nm in enumerate(names):
    yy = RY[0] + i / 5 * (RY[1] - RY[0])
    ax.plot([RX[0], RX[1]], [yy, yy], color='cyan', lw=.8, ls='--')
    ax.text(RX[1] + .4, yy, nm, color='cyan', fontsize=8, va='center')
for ch, (f0, f1), off in [('sr1', FR['sr1'], -3.2), ('sr2', FR['sr2'], -4.4),
                          ('sr3', FR['sr3'], -5.6)]:
    y0 = RY[0] + (1 - f1) * (RY[1] - RY[0])
    y1 = RY[0] + (1 - f0) * (RY[1] - RY[0])
    ax.plot([RX[0] + off + 1.2] * 2, [y0, y1], lw=3)
    ax.text(RX[0] + off + 1.2, y1 + .4, ch, fontsize=9, va='bottom',
            ha='center', color='k')
ax.set_xlim(-12060, -12020); ax.set_ylim(1260, 1300)
ax.set_title('post-cut video 007 (13:29) + one placement variant\n'
             'contact positions NOT registered — evenly-spaced model, all variants stress-tested')

ax = axs[1, 1]
show_labels(ax, labels_S1, alpha=1)
draw_rect(ax, RX, RY, ec='lime', lw=2)
for k, c in cuts.items():
    draw_rect(ax, c['x'], c['y'], ec='red', lw=1.5, ls=':')
txt = [f"whole rect S1: {whole['S1']['B_abc']}/{whole['S1']['classified']} "
       f"classified px ABC ({100*whole['S1']['abc_frac']:.0f}%)"]
for ch in ('sr1', 'sr2', 'sr3'):
    s = summary[ch]
    txt.append(f"{ch}: ABC share {100*s['abc_frac_min']:.0f}–"
               f"{100*s['abc_frac_max']:.0f}% over {s['n_variants']} variants")
ax.text(.02, .02, '\n'.join(txt), transform=ax.transAxes, fontsize=9,
        bbox=dict(fc='w', alpha=.85))
ax.set_xlim(-12052, -12028); ax.set_ylim(1262, 1300)
ax.set_title('S1 labels, device-rect zoom — coverage stress result')

fig.suptitle('vti-01 fusion Step 2 — registration: Raman stage frame ↔ transport channels', y=.995)
fig.tight_layout()
fig.savefig(f'{RUN}/figures/f_registration.png', dpi=160)
print(json.dumps({'whole_rect': whole, 'variant_summary': summary}, indent=1))
