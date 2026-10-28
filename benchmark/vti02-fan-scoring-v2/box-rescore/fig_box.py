"""Plot 1: what the box grades, on four real fans."""
import sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
sys.argv = [sys.argv[0], '/data/sharpelab/hera-data/vti02-fan-scoring-v2']
import numpy as np, common as C, importlib.util
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
spec = importlib.util.spec_from_file_location('box', '/home/zack/sharpelab/measurement-env/hera/graders/fan-design/box.py')
box = importlib.util.module_from_spec(spec); spec.loader.exec_module(box)
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, INK2, SURF = '#0b0b0b', '#52514e', '#fcfcfb'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#b5b4ae', 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': SURF,
                     'axes.facecolor': SURF})
want = {'live 0825-r8': '08-25 r8 (reference, live): 1/B 8→1 T × 101',
        'live 0821-r8': '08-21 r8 (live): 1/B 10→2.4 T × 36 — a 2.4 T start',
        'vti02-fan-design-fable-corpus/20260922T192335/00': 'sonnet 192335 #00 (smoke): 1/B 10→0.5 T × 127 — coarse, low start',
        'live 0824-r4': '08-24 r4 (live): 1/B 0.75→6 T × 40'}
eps = {r['key']: r for r in C.inventory() + C.live_fans() if r['key'] in want}
fig = plt.figure(figsize=(15, 11.5))
gs = fig.add_gridspec(4, 2, height_ratios=[3, 1, 3, 1], hspace=0.42, wspace=0.14)
ng = np.linspace(0.35, 3.3, 400)
flg = box.f_light(ng, 'Halder_ABAB')
for i, key in enumerate(want):
    r = eps[key]
    B, n, h = C.design(r); B = np.unique(np.asarray(B)[np.asarray(B) > 0]); n = np.asarray(n)
    L, S = box.window(B, 0.75), box.window(B, 1.0)
    step = L['max_step_per_T']; Wl, Ws = L['W_per_T'], S['W_per_T']
    fl = box.f_light(n, 'Halder_ABAB'); FL = box.FLN * n
    rpp = np.where(n > 0, 1 / (box.FLN * np.where(n > 0, n, 1) * step), 0)
    wm, wk = box.ramp(rpp, box.M), box.ramp(np.nan_to_num(fl * Ws), box.K)
    w = np.where((n > 0) & ~np.isnan(fl), wm * wk, 0)
    s = box.score(B, n * 1e12, r['doc'], b_lo_light=0.75, b_lo_split=1.0, tone_model='Halder_ABAB', signal_lockin='sr1')
    ax = fig.add_subplot(gs[2 * (i // 2), i % 2]); axw = fig.add_subplot(gs[2 * (i // 2) + 1, i % 2], sharex=ax)
    ymax = 40
    hi3, hi2 = 1 / (3 * step), 1 / (2 * step)
    lo3, lo2 = 3 / Ws, 2 / Ws
    ax.axhspan(hi2, ymax, color='#d9d8d2', lw=0)
    ax.axhspan(hi3, hi2, color='#ecebe6', lw=0)
    ax.axhspan(0, lo2, color='#d9d8d2', lw=0)
    ax.axhspan(lo2, lo3, color='#ecebe6', lw=0)
    for y in (hi3, lo3):
        ax.axhline(y, color=INK2, lw=0.8)
    for y in (hi2, lo2):
        ax.axhline(y, color=INK2, lw=0.8, ls=(0, (3, 3)))
    bb = dict(fc=SURF, ec='none', pad=1.5, alpha=0.9)
    if hi2 < ymax:
        ax.text(0.4, hi2 + 0.5, 'F_L above here: < 2 rows/period, weight 0', color=INK2, fontsize=8, bbox=bb)
    if hi3 < ymax:
        ax.text(3.5, hi3 - 0.5, f'high line (F_L): 3 rows/period at {hi3:.1f} T, 2 at {hi2:.1f} T',
                ha='right', va='top', color=INK2, fontsize=8, bbox=bb)
    ax.text(3.5, lo3 + 0.5, f'low line (F_light, window from {S["B_from_T"]:.2f} T): 3 periods at {lo3:.1f} T, 2 at {lo2:.1f} T',
            ha='right', va='bottom', color=INK2, fontsize=8, bbox=bb)
    for y, lab, c in ((box.FLN * ng, 'F_L (ABCA)', BLUE), (box.FLN * ng - flg, 'F_heavy (ABAB)', ORANGE), (flg, 'F_light (ABAB)', AQUA)):
        ax.plot(ng, y, color=c, lw=1, alpha=0.35)
    on = (n > 0) & ~np.isnan(fl)
    for y, c in ((FL, BLUE), (FL - fl, ORANGE), (fl, AQUA)):
        ax.scatter(n[on], y[on], s=10, color=c, edgecolors=SURF, linewidths=0.5, zorder=3)
    for y, lab, c in ((box.FLN * 3.3, 'F_L', BLUE), (box.FLN * 3.3 - box.f_light(np.array([3.3]), 'Halder_ABAB')[0], 'F_heavy', ORANGE), (box.f_light(np.array([3.3]), 'Halder_ABAB')[0], 'F_light', AQUA)):
        if y < ymax:
            ax.text(3.32, y, lab, color=INK, fontsize=8, va='center')
    # light-tone cells over the weighted columns
    if (w > 0).any():
        f0 = fl[w > 0].min(); dF = 1 / Wl
        for k in range(int((fl[w > 0].max() - f0) // dF) + 2):
            ax.axhline(f0 + k * dF, xmin=0.0, xmax=0.012, color=AQUA, lw=2)
    ax.set_xlim(0.35, 3.55); ax.set_ylim(0, ymax); ax.set_ylabel('SdH frequency F (T)')
    ax.set_title(f"{want[key]}\nquality {s['quality']:.2f} = A {s['A']:.2f} × cell weight {s['cell_weight']:.2f} ({s['cells']} cells), {h:.1f} h",
                 fontsize=9.5, color=INK, loc='left')
    # weights strip
    if (w > 0).any():
        c = np.floor((np.nan_to_num(fl) - f0) / dF)
    else:
        c = np.zeros_like(n)
    width = np.median(np.diff(np.sort(n))) * 0.8 if n.size > 1 else 0.05
    cols = np.where(c % 2 == 0, '#6b6a66', '#a9a8a2')
    axw.bar(n[on], w[on], width=width, color=cols[on], lw=0)
    if (w > 0).any():
        for k in np.unique(c[w > 0]):
            sel = (c == k) & (w > 0)
            axw.hlines(w[sel].max(), n[sel].min() - width / 2, n[sel].max() + width / 2, color=INK, lw=1.6)
            axw.axvline(n[sel].min() - width / 2, color=INK2, lw=0.5, ls=(0, (2, 2)))
    axw.plot(n[on], wm[on], color=BLUE, lw=1.2, label='high-line weight (rows/period)')
    axw.plot(n[on], wk[on], color=AQUA, lw=1.2, label='low-line weight (periods)')
    axw.set_ylim(0, 1.08); axw.set_yticks([0, 0.5, 1]); axw.set_ylabel('weight')
    axw.set_xlabel('density n (10¹² cm⁻², actual frame)')
    if i == 1:
        axw.legend(fontsize=7.5, frameon=False, loc='upper left')
fig.suptitle('What the vti-02 fan grader scores: the (n, F) box. Dots = each column\'s model tones (Halder); solid lines = full credit (3), dashed = zero credit (2), shaded between = soft.\n'
             'Bars below = column weight (high × low); dotted verticals and alternating greys = light-tone cells (width 1/W from 0.75 T); black tick = the cell\'s best weight, which is what it scores.',
             fontsize=10, color=INK, x=0.06, ha='left', y=0.995)
fig.savefig('/data/sharpelab/hera-data/vti02-fan-scoring-v2/box-rescore/fig/1_box_on_fans.png', dpi=110, bbox_inches='tight')
