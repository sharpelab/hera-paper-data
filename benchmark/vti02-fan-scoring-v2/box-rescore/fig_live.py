"""Figure: the live vti-02 fans — measured data, its Fourier map, and the grade on the same (n, F) axes."""
from figlib import *
import json, gzip, io
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
LIVE = '/data/sharpelab/hera-data/frontier/calibration/vti02-live/'
fans = all_fans()
order = [('0822-r8', 8, 'live 0822-r8', '08-22 run 8', False, 'fine 1/B grid from 1.0 T: both parts near full',
          'measured (1–10 T): light tone found in 50/61 columns, F_L/F_heavy split in 60/61'),
         ('0825-r8', 8, 'live 0825-r8', '08-25 run 8', True, 'fine 1/B grid from 1.0 T: both parts near full',
          'measured (1–8 T): light tone found in 56/57 columns, split in 54/57'),
         ('0824-r4', 4, 'live 0824-r4', '08-24 run 4', True, 'light part OK; split fails: the 1/B steps give F_L only ~2 rows\nper period, so almost none of the record resolves it',
          'measured (0.75–6 T, electron side): light tone found in 9/26 columns, split in 4/26'),
         ('0821-r8', 8, 'live 0821-r8', '08-21 run 8', False, 'starts at 2.4 T: only the densest columns hold ≥ 1.5 light-tone periods',
          'measured (2.4–10 T): light tone found in 17/41 columns, split in 3/41'),
         ('0823-r6', 6, 'live 0823-r6', '08-23 run 6', True, 'field ramped continuously, rows linear in B: the light tone is\nsampled across the record; F_L only above ~3.5 T, too short for the split',
          'measured: no per-column detection analysis for this run')]
DIV = LinearSegmentedColormap.from_list('div', ['#1c5cab', '#86b6ef', '#f0efec', '#f3a07e', '#b8431a'])
FMIN, FMAX = 0.8, 45
bb = dict(fc=SURF, ec='none', pad=1.0, alpha=0.85)

import pandas as pd
_EV = pd.read_csv('/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check/fft_columns_eval.csv')
_WIN = {'0822-r8': 'full1.0', '0825-r8': 'full1.0', '0824-r4': 'full0.75', '0821-r8': 'o2.0'}
_SC = {'0825-r8': 0.95}

def found_at(fixture, x, field):
    """Whether the live Fourier analysis found the tone in the column nearest density x (None: not analysed)."""
    if fixture not in _WIN:
        return None
    E = _EV[(_EV.fan == fixture) & (_EV.win == _WIN[fixture])]
    k = np.argmin(abs(E.n_act.to_numpy() * _SC.get(fixture, 1.0) - x))
    return bool(E[field].iloc[k])


def load(fixture, run):
    p = f'{LIVE}{fixture}/session/data/{run}/'
    m = json.load(open(p + 'metadata.json')); cols = m['columns']
    X = np.loadtxt(io.StringIO(gzip.decompress(open(p + 'data.tsv.gz', 'rb').read()).decode()), delimiter='\t', ndmin=2)
    nfast = len(m['fast_setpoints'][0]); nrows = X.shape[0] // nfast; X = X[:nrows * nfast]
    col = lambda name, k=-1: X[:, [i for i, c in enumerate(cols) if c == name][k]].reshape(nrows, nfast)
    I = col('sr0_X') / m['measurement_config']['sr0_gain']
    return col('sr1_X') / I, col('magnet_field', 0)   # R (ohm); B: the row setpoint, or per point on a continuous ramp

def detrend(R, B, lo):
    """Oscillatory part per column: minus a degree-5 polynomial in B over B >= lo, scaled by its rms."""
    out = np.full_like(R, np.nan)
    for j in range(R.shape[1]):
        b, y = B[:, j], R[:, j]; ok = np.isfinite(y) & (b >= lo)
        if ok.sum() < 8: continue
        r = y[ok] - np.polyval(np.polyfit(b[ok], y[ok], 5 if ok.sum() >= 30 else 3), b[ok])
        out[ok, j] = r / (r.std() or 1)
    return out

def fft_map(dR, B, lo, F):
    S = np.full((F.size, dR.shape[1]), np.nan)
    for j in range(dR.shape[1]):
        ok = np.isfinite(dR[:, j]) & (B[:, j] >= lo)
        if ok.sum() < 8: continue
        u = 1 / B[ok, j]; y = dR[ok, j]; o = np.argsort(u); u, y = u[o], y[o]
        uu = np.linspace(u[0], u[-1], max(len(u), 64)); yy = np.interp(uu, u, y); yy = (yy - yy.mean()) * np.hanning(uu.size)
        f = np.fft.rfftfreq(8192, uu[1] - uu[0]); A = np.abs(np.fft.rfft(yy, 8192))
        a = np.interp(F, f, A); band = (F >= 2.0) & (F <= 40)
        S[:, j] = np.minimum(a / np.nanmax(a[band]), 1.0)
    return S

def edges(x):
    x = np.asarray(x); m = (x[1:] + x[:-1]) / 2
    return np.r_[x[0] - (m[0] - x[0]), m, x[-1] + (x[-1] - m[-1])]

fig = plt.figure(figsize=(16, 30))
outer = fig.add_gridspec(len(order) + 1, 1, height_ratios=[0.62] + [1] * len(order), hspace=0.48, top=0.935, bottom=0.02)
ng = np.linspace(0.3, 3.4, 400); flg = box.f_light(ng, 'Halder_ABAB')
F = np.geomspace(FMIN, FMAX, 500)
for i, (fixture, run, key, name, ascending, verdict, measured) in enumerate(order):
    c = columns(fans[key]); s = c['s']
    R, B = load(fixture, run)
    ncol = R.shape[1]
    n = np.sort(c['n']); assert n.size == ncol, (key, n.size, ncol)
    n = n if ascending else n[::-1]
    o = np.argsort(n); n, R, B = n[o], R[:, o], B[:, o]
    if B.shape == R.shape and np.ptp(B[0]) < 1e-6:
        pass
    lo_fft = max(0.75, np.nanmin(B[B > 0]))
    dR = detrend(R, B, max(0.3, np.nanmin(B[B > 0])))
    row = outer[i + 1].subgridspec(2, 2, width_ratios=[1, 1.25], height_ratios=[3, 1], hspace=0.08, wspace=0.22)
    af = fig.add_subplot(row[:, 0]); ax = fig.add_subplot(row[0, 1]); axw = fig.add_subplot(row[1, 1], sharex=ax)
    # measured fan
    Bm = np.nanmedian(B, axis=1) if np.ptp(B[0]) < 1e-3 else None
    if Bm is not None:
        mfan = af.pcolormesh(edges(n), edges(Bm), dR, cmap=DIV, vmin=-2.5, vmax=2.5, shading='flat', rasterized=True)
    else:
        for j in range(ncol):
            mfan = af.scatter(np.full(B.shape[0], n[j]), B[:, j], c=dR[:, j], cmap=DIV, vmin=-2.5, vmax=2.5, s=14, marker='s', lw=0)
    af.set_xlabel('carrier density n (10¹² cm⁻²)'); af.set_ylabel('magnetic field B (T)')
    af.set_title(f'{name}: measured fan (four-probe resistance minus a smooth\nbackground per column, in units of its rms)', loc='left', fontsize=9.2, color=INK)
    fig.colorbar(mfan, ax=af, fraction=0.04, pad=0.02, label='ΔR / rms')
    # Fourier map with the grade on top
    S = fft_map(dR, B, lo_fft, F)
    mfft = ax.pcolormesh(edges(n), edges(F), S, cmap='Greys', vmin=0, vmax=1, shading='flat', rasterized=True, zorder=0.2)
    e = (n > 0) & ~np.isnan(box.f_light(n, 'Halder_ABAB'))
    labels = []
    def rline(y, text, color, ls, va='bottom'):
        if FMIN < y < FMAX:
            ax.axhline(y, color=color, lw=1.1, ls=ls, alpha=0.9)
            labels.append([y, text, color])
    ax.set_xlim(n.min() - 0.02 * np.ptp(n), n.max() + 0.02 * np.ptp(n))
    du = c['du_l']
    if du.size:
        frac = box.w_eff(F, du, box.M) / du.sum()
        ax.imshow((1 - frac)[:, None] * np.ones((1, 2)), extent=(n.min() - 1, n.max() + 1, FMIN, FMAX), origin='lower',
                  aspect='auto', cmap=LinearSegmentedColormap.from_list('shade', [(1, 1, 1, 0), (0.82, 0.81, 0.78, 0.8)]),
                  vmin=0, vmax=1, zorder=0.5, interpolation='nearest')
        F_full, F_none = 1 / (3 * du.max()), 1 / (2 * du.min())
        rline(F_none, 'no interval samples tones above', INK2, (0, (3, 3)))
        rline(F_full, 'whole record samples tones below', INK2, '-')
    if abs(c['WS'] - c['WL']) < 1e-9:
        rline(3.5 / c['WS'], '3.5 periods ↑ full weight', VIOLET, '-')
        rline(1.5 / c['WS'], '1.5 periods ↓ weight 0', VIOLET, (0, (3, 3)))
    else:
        rline(3.5 / c['WS'], 'split (from 1.0 T): 3.5 periods', VIOLET, '-')
        rline(1.5 / c['WS'], 'split: 1.5 periods', VIOLET, (0, (3, 3)))
        rline(3.5 / c['WL'], 'light (from 0.75 T): 3.5 periods', '#8f84d8', '-')
        rline(1.5 / c['WL'], 'light: 1.5 periods', '#8f84d8', (0, (3, 3)))
    labels.sort(key=lambda t: t[0]); ys = [t[0] for t in labels]
    for j in range(1, len(ys)):
        ys[j] = max(ys[j], ys[j - 1] * 1.16)
    for (y0, text, color), y in zip(labels, ys):
        ax.annotate(text, xy=(1.0, y0), xycoords=ax.get_yaxis_transform(), xytext=(1.02, y), textcoords=ax.get_yaxis_transform(),
                    fontsize=7.5, color=color, va='center', ha='left', annotation_clip=False,
                    arrowprops=dict(arrowstyle='-', color=color, lw=0.5) if abs(np.log(y / y0)) > 0.02 else None)
    gm = (ng >= max(n.min(), 0.3)) & (ng <= n.max())
    for y, col in ((box.FLN * ng, BLUE), (box.FLN * ng - flg, ORANGE), (flg, AQUA)):
        ax.plot(ng[gm], y[gm], color=col, lw=1.6, alpha=0.9)
    pl = np.array([x for x, w in zip(s['light']['chosen_n_actual_1e12'], s['light']['chosen_weights']) if w >= 0.05])
    ps = np.array([x for x, w in zip(s['split']['chosen_n_actual_1e12'], s['split']['chosen_weights']) if w >= 0.05])
    for pts, yfun, col, fld in ((pl, lambda x: box.f_light(x, 'Halder_ABAB'), AQUA, 'light_true'), (ps, lambda x: box.FLN * x, BLUE, 'split_true')):
        for x in pts:
            found = found_at(fixture, x, fld)
            ax.scatter([x], [yfun(np.array([x]))[0] if np.ndim(yfun(np.array([x]))) else yfun(x)], s=85,
                       facecolors=col if found else SURF, edgecolors=INK if found is None else col, linewidths=1.8, zorder=5)
    ax.set_yscale('log'); ax.set_ylim(FMIN, FMAX)
    ax.set_yticks([1, 2, 3, 5, 10, 20, 40]); ax.set_yticklabels(['1', '2', '3', '5', '10', '20', '40'])
    ax.set_ylabel('frequency F (T, log)'); plt.setp(ax.get_xticklabels(), visible=False)
    acq = s['acquisition']; best = acq
    ax.set_title(f"its Fourier map in 1/B from {lo_fft:.2f} T (each column scaled to its peak above 2 T; dark = strong) with the grade on top\n"
                 f"design: {c['B'].min():.2f}–{c['B'].max():.1f} T, {c['B'].size} rows × {ncol} columns, {c['h']:.1f} h · {verdict}\n"
                 f"{measured}\n"
                 f"light {s['light']['score']:.2f}/7 · split {s['split']['score']:.2f}/7 · A {s['A']:.2f} ({acq['I_A'] * 1e9:.0f} nA, τ {best['tau_s']:g} s)"
                 f"  →  quality {s['quality']:.2f} (P(call) {s['p_call']:.2f})", loc='left', fontsize=9.2, color=INK)
    wl, ws = np.zeros(n.size), np.zeros(n.size)
    cn = c['n']
    for j, x in enumerate(n):
        k = np.argmin(abs(cn - x)); wl[j], ws[j] = c['wl'][k], c['ws'][k]
    if np.allclose(wl, ws):
        axw.plot(n, ws, color=INK, lw=1.6, label='light = split weight')
    else:
        axw.plot(n, wl, color=AQUA, lw=1.6, label='light-part weight')
        axw.plot(n, ws, color=BLUE, lw=1.6, ls=(0, (4, 2)), label='split-part weight')
    axw.legend(fontsize=7.5, frameon=False, loc='upper left')
    axw.set_ylim(-0.05, 1.15); axw.set_yticks([0, 0.5, 1]); axw.set_ylabel('column\nweight')
    axw.set_xlabel('carrier density n (10¹² cm⁻²)')

k = fig.add_subplot(outer[0]); k.axis('off')
items = [(Line2D([], [], color=BLUE, lw=2), 'F_L = (h/4e)·n: the single tone of rhombohedral (ABCA) stacking'),
         (Line2D([], [], color=ORANGE, lw=2), 'F_heavy: Bernal (ABAB) heavy tone (band model)'),
         (Line2D([], [], color=AQUA, lw=2), 'F_light: Bernal (ABAB) light tone (band model); F_L − F_heavy = F_light'),
         (Line2D([], [], color='none', marker='o', mfc=AQUA, mec=AQUA, mew=1.8, ms=10), 'column counted by the light part (≤ 7, ≥ ½ bin apart); filled = the data found the light tone there'),
         (Line2D([], [], color='none', marker='o', mfc=SURF, mec=BLUE, mew=1.8, ms=10), 'column counted by the split part; open = the data did not find the split there'),
         (plt.Rectangle((0, 0), 1, 1, fc='#d1cfc7'), 'grey shading: the share of the 1/B record too coarse for a tone at that F (< 2–3 rows per period)'),
         (Line2D([], [], color=VIOLET, lw=1.2), 'violet: light-tone periods in the full record; solid 3.5 (full weight), dashed 1.5 (weight 0)')]
k.legend([h for h, _ in items], [t for _, t in items], loc='upper left', fontsize=9, frameon=False, ncols=2, handlelength=2.5, labelspacing=0.9,
         title='Key (right-hand panels: the grade drawn on each fan\'s measured Fourier map)', title_fontsize=10, alignment='left', bbox_to_anchor=(0, 1))
k.text(0.0, 0.15,
       'Each part counts light-tone periods over the part of the 1/B record that samples its tone (each row interval weighted 0 at 2, 1 at 3 rows per period).\n'
       'Light part: tone F_light, window from 0.75 T (its onset).   Split part: tone F_L, window from 1.0 T (periods = F_L/F_heavy separation in FFT bins).\n'
       'Column weight: 0 at 1.5 effective periods, 1 at 3.5.   '
       'Each part counts its best ≤ 7 columns at least half an FFT bin apart.   Quality = A × (light + split) / 14;\n'
       'A: the probability a tone\'s peak clears the detection threshold at the design\'s current and τ, relative to 50 nA at 0.3 s (10 nA at 0.3 s: 0.82).   '
       'Only electron-doped columns are scored (the band model and tone onsets are validated there).\n'
       '"Found" (titles, filled circles): a peak ≥ 4× the noise floor (median spectrum above 1.12 F_L) within tolerance of the observed tone; split: F_L and F_heavy both found with a dip below 0.8 between.',
       fontsize=9, color=INK2, va='top', linespacing=1.6, transform=k.transAxes)
fig.text(0.04, 0.995, 'How a Landau fan design is graded for telling ABAB from ABCA stacking: five fans measured on vti-02, with their data', fontsize=15, color=INK, va='top', weight='bold')
fig.text(0.04, 0.985,
         'vti-02 is a tetralayer graphene device. A Landau fan measures resistance on a grid of field rows B × density columns n (left panels). Its Fourier transform in 1/B, column by column,\n'
         'shows the quantum-oscillation frequencies F (right panels, dark = strong). The fan must tell Bernal (ABAB: a light tone F_light and a heavy tone F_heavy) from rhombohedral\n'
         '(ABCA: one tone F_L = F_light + F_heavy). The grader never uses the measured data: it reads only the planned rows and columns, places the tones from a published ABAB band model\n'
         '(Halder et al., arXiv:2607.25757; displacement field D = 0, T ≈ 1.3 K), and asks whether each tone is sampled finely enough and the 1/B window is long enough. The data are shown so the grade can be checked against what the fan saw;\n'
         '"measured" lines count the columns where a Fourier analysis of the data found each tone (peak ≥ 4× the noise floor, at the observed tone position).',
         fontsize=9.5, color=INK2, va='top', linespacing=1.5)
fig.savefig(OUT + '3_live_fans.png', dpi=100, bbox_inches='tight')
