"""Plot 2: the resolution argument for the low line, the 0.75 / 1.0 T windows, and why a separate light-tone condition adds nothing."""
import sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
sys.argv = [sys.argv[0], '/data/sharpelab/hera-data/vti02-fan-scoring-v2']
import numpy as np, common as C, importlib.util
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
spec = importlib.util.spec_from_file_location('box', '/home/zack/sharpelab/measurement-env/hera/graders/fan-design/box.py')
box = importlib.util.module_from_spec(spec); spec.loader.exec_module(box)
BLUE, ORANGE, AQUA, YEL = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
INK, INK2, SURF = '#0b0b0b', '#52514e', '#fcfcfb'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#b5b4ae', 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': SURF,
                     'axes.facecolor': SURF})
fig, axs = plt.subplots(2, 2, figsize=(15, 10.5)); fig.subplots_adjust(hspace=0.45, wspace=0.26)

# (a) two tones one light-tone frequency apart, Hann FFT over a window holding k light periods
a = axs[0, 0]
F_heavy, F_light = 16.0, 4.0
ks = (1.5, 2.0, 2.5, 3.0, 4.0)
greys = ('#c9c8c2', '#a9a8a2', '#86857f', '#5f5e59', '#0b0b0b')
for k, g in zip(ks, greys):
    W = k / F_light
    x = np.linspace(0, W, 400)
    y = np.cos(2 * np.pi * F_heavy * x) + np.cos(2 * np.pi * (F_heavy + F_light) * x + 0.7)
    y = (y - y.mean()) * np.hanning(x.size)
    Y = np.abs(np.fft.rfft(y, 1 << 16)); f = np.fft.rfftfreq(1 << 16, x[1] - x[0])
    sel = (f > F_heavy - 2 * F_light) & (f < F_heavy + 3 * F_light)
    a.plot((f[sel] - F_heavy) / F_light, Y[sel] / Y[sel].max(), color=g, lw=1.6 if k in (2.0, 3.0) else 1.1,
           label=f'{k:g} periods = {k:g} bins apart')
a.axvline(0, color=ORANGE, lw=1); a.axvline(1, color=BLUE, lw=1)
a.text(0, 1.04, 'F_heavy', color=INK, ha='center', fontsize=8); a.text(1, 1.04, 'F_L', color=INK, ha='center', fontsize=8)
a.set_xlim(-1.5, 2.5); a.set_ylim(0, 1.45)
a.set_xlabel('(F − F_heavy) / F_light      (F_L − F_heavy = F_light by Luttinger)'); a.set_ylabel('|FFT| (Hann), normalized')
a.legend(fontsize=7.5, frameon=False, loc='upper left', ncols=3)
a.set_title('(a) Resolution: light-tone periods = the F_L / F_heavy separation in FFT bins.\n'
            'At 2 the peaks barely part; by 3 the dip is deep: the low line\'s 2 → 3 ramp.', loc='left', fontsize=9.5, color=INK)

# (b) live detection vs periods, with the ramp
b = axs[0, 1]
edges = [0.5, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]
light = {'10 nA': [0.07, 0.35, 0.18, 0.42, 0.68, 0.76, 0.91], '50 nA': [0.10, 0.41, 0.35, 0.64, 0.96, 0.81, 1.00]}
split = {'10 nA': [0.00, 0.09, 0.16, 0.36, 0.45, 0.56, 0.85], '50 nA': [0.08, 0.19, 0.27, 0.51, 0.71, 1.00, 0.97]}
for lab, ls in (('10 nA', '-'), ('50 nA', (0, (4, 2)))):
    b.stairs(light[lab], edges, color=AQUA, lw=1.8, ls=ls, label=f'light tone found, {lab}')
    b.stairs(split[lab], edges, color=BLUE, lw=1.8, ls=ls, label=f'F_L / heavy split found, {lab}')
xx = np.linspace(0.5, 4, 300)
b.plot(xx, np.clip(xx - 2, 0, 1), color=INK, lw=2.2, label='grader low-line weight (0 at 2, 1 at 3)')
b.axvspan(2, 3, color='#ecebe6', lw=0, zorder=0)
b.set_xlim(0.5, 4); b.set_ylim(0, 1.05)
b.set_xlabel('light-tone periods in the analysis window (model tones)'); b.set_ylabel('fraction of columns detected')
b.legend(fontsize=7.5, frameon=False, loc='upper left')
b.set_title('(b) Live vti-02 FFTs (08-21, 08-22, 08-25 r8; windows pooled; live-check/).\n'
            'The split needs more periods than the light tone; the ramp brackets the split\'s 50 % point.',
            loc='left', fontsize=9.5, color=INK)

# (c) windows and onsets, in 1/B (what the FFT sees)
c = axs[1, 0]
Bmax = 10.0
rows = [('light tone present (onset ≈ 0.75 T, Dingle extrapolation)', 0.75, AQUA),
        ('heavy tone present (onset 1.1–1.4 T)', 1.25, ORANGE),
        ('F_L present (onset 1.53–1.86 T)', 1.7, BLUE)]
for i, (lab, bon, col) in enumerate(rows):
    y = 5 - i
    c.barh(y, 1 / bon - 1 / Bmax, left=1 / Bmax, height=0.55, color=col, alpha=0.85)
    c.text(1 / Bmax + 0.02, y + 0.42, lab, fontsize=8, color=INK)
c.barh(1.6, 1 / 0.75 - 1 / Bmax, left=1 / Bmax, height=0.45, color='#a9a8a2')
c.text(1 / Bmax + 0.02, 1.95, 'light window: from max(B_min, 0.75 T) — sets the cell width 1/W and the high line', fontsize=8, color=INK)
c.barh(0.6, 1 / 1.0 - 1 / Bmax, left=1 / Bmax, height=0.45, color='#5f5e59')
c.text(1 / Bmax + 0.02, 0.95, 'split window: from max(B_min, 1.0 T) — the low line counts periods here', fontsize=8, color=INK)
c.axvspan(1 / 1.0, 1 / 0.3, color='#ecebe6', lw=0, zorder=0)
c.text(1.75, 3.0, 'no live fan below 1.0 T:\nno split evidence here', fontsize=8.5, color=INK2)
for Bs, got, dy in ((1.0, '60/61', 0.0), (1.53, '43/61', -0.5), (2.0, '15/61', -1.0)):
    c.plot([1 / Bs], [-0.1], marker='v', color=INK, ms=7)
    c.plot([1 / Bs, 1 / Bs], [-0.1, -0.35 + dy], color=INK2, lw=0.6)
    c.text(1 / Bs + 0.03, -0.45 + dy, f'from {Bs:g} T: split {got}', ha='left', fontsize=7.5, color=INK)
c.set_ylim(-1.8, 6); c.set_yticks([])
c.set_xlim(0, 1 / 0.3); c.set_xlabel('1/B (1/T)   — top axis in B')
sec = c.secondary_xaxis('top', functions=(lambda u: 1 / np.maximum(u, 1e-3), lambda v: 1 / np.maximum(v, 1e-3)))
sec.set_xticks([10, 2, 1.0, 0.75, 0.5, 0.4, 0.3]); sec.set_xlabel('B (T)', color=INK2)
c.set_title('(c) The two windows against the tone onsets (08-22 r8 split counts below the axis).\n'
            'F_L switches on at ~1.5 T, yet a record from 1.0 T still sharpens the split (60/61 vs 43/61).',
            loc='left', fontsize=9.5, color=INK)

# (d) every dev-set column: light-window periods vs split-window periods
d = axs[1, 1]
P = []
for r in C.inventory() + C.live_fans():
    if r.get('ending') != 'fan':
        continue
    B, n, h = C.design(r); B = np.unique(np.asarray(B)[np.asarray(B) > 0]); n = np.asarray(n)
    L, S = box.window(B, 0.75), box.window(B, 1.0)
    fl = box.f_light(n, 'Halder_ABAB'); ok = (n > 0) & ~np.isnan(fl)
    P.append(np.c_[fl[ok] * L['W_per_T'], fl[ok] * S['W_per_T'], np.full(ok.sum(), B[0] < 1.0)])
P = np.vstack(P)
d.axhspan(2, 3, color='#ecebe6', lw=0, zorder=0)
d.scatter(P[P[:, 2] == 0, 0], P[P[:, 2] == 0, 1], s=9, color=BLUE, alpha=0.5, edgecolors='none', label='fans starting at or above 1.0 T (windows coincide)')
d.scatter(P[P[:, 2] == 1, 0], P[P[:, 2] == 1, 1], s=9, color=YEL, alpha=0.7, edgecolors='none', label='fans starting below 1.0 T')
m = max(P[:, 0].max(), 1) * 1.02
d.plot([0, m], [0, m], color=INK2, lw=0.8, ls=(0, (3, 3)))
d.text(m * 0.62, m * 0.66, 'split = light', rotation=38, color=INK2, fontsize=8)
d.axvline(1.7, color=AQUA, lw=1.2); d.text(1.8, m * 0.55, 'light tone 50 % found\n(~1.7 periods, observed)', color=INK, fontsize=8)
d.axhline(2.2, color=BLUE, lw=1.2); d.text(m * 0.98, 2.3, 'split 50 % found (~2.2, observed)', color=INK, fontsize=8, ha='right')
d.text(m * 0.98, 2.55, 'low-line soft band 2–3', color=INK2, fontsize=8, ha='right')
d.set_xlim(0, m); d.set_ylim(0, m)
d.set_xlabel('light-tone periods in the light window (from 0.75 T)'); d.set_ylabel('light-tone periods in the split window (from 1.0 T)')
d.legend(fontsize=7.5, frameon=False, loc='upper left')
d.set_title(f'(d) All {len(P)} dev-set electron columns. Split periods never exceed light periods, and the split needs more of them:\n'
            'any column that clears the low line has already cleared the light tone. A separate light-tone condition never binds.',
            loc='left', fontsize=9.5, color=INK)
fig.savefig('/data/sharpelab/hera-data/vti02-fan-scoring-v2/box-rescore/fig/2_resolution_windows.png', dpi=110, bbox_inches='tight')
