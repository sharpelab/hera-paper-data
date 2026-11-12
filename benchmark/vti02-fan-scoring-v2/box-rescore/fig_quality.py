"""Figure: how the quality score is built, why, and examples."""
from figlib import *
from matplotlib.patches import FancyBboxPatch
fans = all_fans()
fig = plt.figure(figsize=(15, 17))
gs = fig.add_gridspec(4, 2, height_ratios=[0.95, 1, 1, 1.15], hspace=0.62, wspace=0.26, top=0.925)

# (a) the pipeline
a = fig.add_subplot(gs[0, :]); a.axis('off'); a.set_xlim(0, 100); a.set_ylim(0, 23)
steps = [('The design', 'planned field rows B,\ndensity columns n,\ntime constant τ, current I;\ntones from an ABAB band model'),
         ('Per column', 'the 1/B record that samples\nthe tone: each row interval\ncounted 0 at 2, 1 at 3 rows\nper period; light-tone periods\nin that record'),
         ('Two weights', 'light: tone F_light, window\nfrom 0.75 T (its onset)\nsplit: tone F_L, window from\n1.0 T (lowest field with\nmeasured split evidence)\neach 0 at 1.5 periods, 1 at 3.5'),
         ('Best 7 per part', 'the ≤ 7 columns with the most\nweight whose light tones sit\n≥ ½ FFT bin apart (where model\nerrors decorrelate); 7 cover\n~3 bins of F_light(n)'),
         ('Quality', 'A × (light + split) / 14, 0 to 1\nA: detection probability at the\ndesign\'s current and τ\na sum, not a product: the light\ntone alone is ABAB evidence')]
xw = 17.5
for i, (t, body) in enumerate(steps):
    x = 1 + i * 20
    a.add_patch(FancyBboxPatch((x, 0.5), xw, 18, boxstyle='round,pad=0.4,rounding_size=1.2', fc='#f3f2ee', ec='#b5b4ae'))
    a.text(x + xw / 2, 16.5, t, ha='center', va='center', fontsize=10.5, weight='bold', color=INK)
    a.text(x + xw / 2, 8.2, body, ha='center', va='center', fontsize=8.1, color=INK2, linespacing=1.5)
    if i < len(steps) - 1:
        a.annotate('', xy=(x + xw + 2.2, 10), xytext=(x + xw + 0.4, 10), arrowprops=dict(arrowstyle='-|>', color=INK2, lw=1.2))
a.text(0, 22.5, '(a) The score, step by step, computed from the planned design only (no measured data). Hours are a separate axis, from a rig timing model\n     (magnet ramp, settling, per-point overhead; within 8 % of measured runs): each fan is a point (quality, hours), and a cheaper fan of equal quality is better.',
       fontsize=9.5, color=INK, va='top')

# (b) why the ramps: two tones one light-tone frequency apart
b = fig.add_subplot(gs[1, 0])
F_heavy, F_light = 16.0, 4.0
for k, g in zip((1.5, 2.0, 3.0), ('#9ec5f4', '#3987e5', '#104281')):
    W = k / F_light; x = np.linspace(0, W, 400)
    y = np.cos(2 * np.pi * F_heavy * x) + np.cos(2 * np.pi * (F_heavy + F_light) * x + 0.7)
    y = (y - y.mean()) * np.hanning(x.size)
    Y = np.abs(np.fft.rfft(y, 1 << 16)); f = np.fft.rfftfreq(1 << 16, x[1] - x[0])
    sel = (f > F_heavy - 2 * F_light) & (f < F_heavy + 3 * F_light)
    b.plot((f[sel] - F_heavy) / F_light, Y[sel] / Y[sel].max(), color=g, lw=1.8, label=f'{k:g} periods')
b.axvline(0, color=ORANGE, lw=1); b.axvline(1, color=BLUE, lw=1)
b.text(0, 1.03, 'F_heavy', ha='center', fontsize=8, color=INK); b.text(1, 1.03, 'F_L', ha='center', fontsize=8, color=INK)
b.set_xlim(-1.5, 2.5); b.set_ylim(0, 1.4); b.legend(fontsize=7.5, frameon=False, loc='upper left', ncols=3, handlelength=1.5, columnspacing=1.0)
b.set_xlabel('(F − F_heavy) / F_light'); b.set_ylabel('FFT magnitude (Hann window), normalized')
b.set_title('(b) Why periods matter. Real vti-02 spectra show peaks at both F_heavy and\n'
            'F_L (a tone at F_L also arises in Bernal stacks, via quantum-Hall pinning; see the\n'
            'Fourier maps in the companion figure), so the call rests on resolving that pair.\n'
            'They sit F_light apart: bins apart = light-tone periods. Hann: merged below 2, split by 3.',
            loc='left', fontsize=9.5, color=INK)

# (c) the ramp against live detection, from the per-column records
import pandas as pd
Acsv = pd.read_csv('/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check/fft_columns_eval.csv')
Acsv = Acsv[Acsv.fan.isin(['0821-r8', '0822-r8', '0825-r8'])].copy()
nfix = np.where(Acsv.fan == '0825-r8', 0.95, 1.0) * Acsv.n_act
Acsv['k'] = box.f_light(nfix.to_numpy(), 'Halder_ABAB') / Acsv.dF
c = fig.add_subplot(gs[1, 1])
edges = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.5, 8.0])
Acsv['bin'] = pd.cut(Acsv.k, edges)
G = Acsv.groupby('bin', observed=False).agg(N=('k', 'size'), light=('light_true', 'mean'), split=('split_true', 'mean'))
mid = (edges[:-1] + edges[1:]) / 2; mid[-1] = 5.0
def wilson(p, N, z=1.0):
    p, N = np.asarray(p, float), np.asarray(N, float)
    d = 1 + z**2 / N; cen = (p + z**2 / (2 * N)) / d; hw = z * np.sqrt(p * (1 - p) / N + z**2 / (4 * N**2)) / d
    return cen - hw, cen + hw
for col, lab, cc in (('light', 'light tone found', AQUA), ('split', 'F_L / F_heavy split found', BLUE)):
    p_, N_ = G[col].to_numpy(), G.N.to_numpy()
    lo_, hi_ = wilson(p_, N_)
    c.errorbar(mid, p_, yerr=[p_ - lo_, hi_ - p_], color=cc, marker='o', ms=5, lw=1.4, capsize=2, label=lab)
xx = np.linspace(0.5, 6, 300); c.plot(xx, np.clip((xx - 1.5) / 2, 0, 1), color=INK, lw=2.4, label='weight used in the score')
for x_, N_ in zip(mid, G.N):
    c.text(x_, 1.035, f'{N_}', ha='center', fontsize=7, color=INK2)
c.text(0.55, 1.035, 'N:', fontsize=7, color=INK2)
c.set_xlim(0.5, 6); c.set_ylim(0, 1.1); c.legend(fontsize=7.5, frameon=False, loc='center right')
c.set_xlabel('light-tone periods in the analysis window (band model)'); c.set_ylabel('fraction of columns / weight')
c.set_title(f'(c) Real data behind the ramp: {len(Acsv)} column-windows from three measured vti-02 fans\n'
            '(windows from 1.0, 1.53 and 2.0 T). "Found": peak ≥ 4× noise floor at the observed\n'
            'tone position; split: both peaks with a dip between. Bars: ±1σ. The weight runs from\n'
            '0 at 1.5 periods to 1 at 3.5; its midpoint, 2.5, is where the split is found half the time.',
            loc='left', fontsize=9.5, color=INK)

# (d) the spacing rule on one fan
d = fig.add_subplot(gs[2, 0])
key = 'vti02-fan-design-fable-corpus/20260922T232408/00'
cc = columns(fans[key]); s = cc['s']; e = cc['e']
f, ws = cc['fl'], cc['ws']
dF = s['split']['min_spacing_T']
lo = np.nanmin(f[e]); hi = np.nanmax(f[e])
d.vlines(f[e], 0, ws[e], color='#a9a8a2', lw=2)
ch = np.array(s['split']['chosen_n_actual_1e12'])
fch = box.f_light(ch, 'Halder_ABAB'); wch = np.array(s['split']['chosen_weights'])
d.vlines(fch, 0, wch, color=BLUE, lw=3)
d.scatter(fch, wch, color=BLUE, s=40, zorder=3)
for x0, x1 in zip(fch[:-1], fch[1:]):
    d.annotate('', xy=(x1, 1.1), xytext=(x0, 1.1), arrowprops=dict(arrowstyle='<->', color=INK2, lw=0.8))
    d.text((x0 + x1) / 2, 1.13, f'{x1 - x0:.2f} T', ha='center', fontsize=7.5, color=INK2)
d.set_ylim(0, 1.25); d.set_xlim(lo - 0.3, hi + 0.3)
d.set_xlabel('light-tone frequency F_light of each column (T)'); d.set_ylabel('split weight')
d.annotate('', xy=(lo - 0.2 + 2 * dF, 0.55), xytext=(lo - 0.2, 0.55), arrowprops=dict(arrowstyle='|-|', color=INK, lw=1))
d.text(lo - 0.2, 0.6, f'one FFT bin = {2 * dF:.2f} T\n(1/B window 0.9–10 T);\npicks ≥ ½ bin = {dF:.2f} T apart', ha='left', fontsize=7.5, color=INK)
d.set_title(f'(d) Counting independent columns, on one design ({cc["n"].size} columns, 0.9–10 T).\n'
            f'Columns closer than half an FFT bin repeat the same point (measured: model\n'
            f'errors decorrelate by ½ bin), so each part scores the ≤ 7 highest-weight columns\n'
            f'at least ½ bin apart (blue): here {s["split"]["score"]:.2f} of 7. Denser columns add nothing.',
            loc='left', fontsize=9.5, color=INK)

# (e) acquisition factor: the detection probability
e_ = fig.add_subplot(gs[2, 1])
x = np.logspace(np.log10(0.3), np.log10(40), 300)
e_.plot(x, [box.detection(v) for v in x], color=INK, lw=2.2, label='A: detection probability (fitted)')
nm = [(1.0, 0.04), (1.7, 0.2), (3.2, 0.9), (5.5, 1.0)]
e_.scatter([p[0] for p in nm], [p[1] for p in nm], marker='s', s=34, facecolors=SURF, edgecolors=INK2, lw=1.2, zorder=3,
           label='rig noise model (simulated), for comparison')
e_.scatter([50 * 0.3 ** 0.5, 10 * 0.3 ** 0.5], [1.0, 0.82], marker='D', s=60, color=ORANGE, edgecolors=SURF, zorder=4,
           label='measured fans used for the fit')
e_.annotate('08-25 run 8: 50 nA, τ 0.3 s\nsplit found 96–100 %', (27.4, 1.0), textcoords='offset points', xytext=(0, -92), ha='center', fontsize=7.5, color=INK, arrowprops=dict(arrowstyle='-', color=INK2, lw=0.6))
e_.annotate('08-22 run 8: 10 nA, τ 0.3 s\nsplit plateau 82 %', (5.48, 0.82), textcoords='offset points', xytext=(12, -38), ha='left', fontsize=7.5, color=INK, arrowprops=dict(arrowstyle='-', color=INK2, lw=0.6))
for I, tau, off in ((10, 0.01, (8, 4)), (10, 0.03, (8, -4)), (10, 0.1, (8, -6))):
    xx = I * np.sqrt(tau); yy = box.detection(xx)
    e_.annotate(f'{I} nA, τ {tau * 1e3:g} ms', (xx, yy), textcoords='offset points', xytext=off, fontsize=7.5, color=INK2)
e_.set_xscale('log'); e_.set_ylim(-0.03, 1.12); e_.set_xlim(0.3, 45)
e_.set_xticks([0.3, 1, 3, 10, 30], ['0.3', '1', '3', '10', '30']); e_.minorticks_off()
e_.set_xlabel('I·√τ  (current in nA × √(lock-in time constant in s))'); e_.set_ylabel('acquisition factor A')
e_.legend(fontsize=7.5, frameon=False, loc='upper left')
e_.text(9.0, 0.40, 'Also: A = 0 for τ ≤ 3 ms (lock-in 2f ripple);\nA × 0.75 if the settle delay is under 3τ.\nSample heating is not modelled: 50 nA was\nchecked heating-safe on this device.',
        fontsize=7.5, color=INK2, va='top')
e_.set_title('(e) Acquisition factor A: the chance that a tone\'s Fourier peak clears the detection threshold,\n'
             'relative to 50 nA at τ 0.3 s. Median peak SNR ∝ (I·√τ)^0.63, lognormal across columns; fitted on\n'
             'two measured fans. It also matches the rig noise model at short τ, where that model is reliable.',
             loc='left', fontsize=9.5, color=INK)

# (f) examples: quality vs hours
g = fig.add_subplot(gs[3, :])
pts = []
for kk, r in fans.items():
    cc = columns(r); pts.append((kk, cc['s']['quality'], cc['h'], kk.startswith('live')))
P = np.array([(q, h) for _, q, h, _ in pts])
live = np.array([l for *_, l in pts])
g.scatter(P[~live, 1], P[~live, 0], s=36, color=BLUE, alpha=0.75, edgecolors=SURF, linewidths=0.8, label='fans designed offline by AI agents (not measured)')
g.scatter(P[live, 1], P[live, 0], s=70, color=ORANGE, marker='D', edgecolors=SURF, linewidths=0.8, label='fans designed and measured in the lab')
o = np.argsort(P[:, 1]); best = -1; front = []
for i in o:
    if P[i, 0] > best + 1e-9:
        front.append(i); best = P[i, 0]
fx, fy = P[front, 1], P[front, 0]
g.step(np.r_[fx, 20], np.r_[fy, fy[-1]], where='post', color=INK2, lw=1, ls=(0, (3, 3)), label='best of these designs by a given time')
labels = {'live 0822-r8': ('08-22 run 8', (-14, -22)), 'live 0825-r8': ('08-25 run 8', (14, -18)),
          'live 0824-r4': ('08-24 run 4', (-6, 40)), 'live 0821-r8': ('08-21 run 8 (starts at 2.4 T)', (10, 52)),
          'live 0823-r6': ('08-23 run 6 (linear in B)', (6, 60)), 'live 0825-r5': ('08-25 run 5 (12-row calibration fan)', (40, -2)),
          'vti02-fan-design-fable-corpus/20260922T232408/00': ('design of panel (d), 2.7 h', (-10, 8)),
          'vti02-fan-design-fable-corpus/20260923T011400-r3w0gf/00': ('0.3–10 T, 647 rows', (8, -12)),
          'vti02-fan-design-fable-corpus/20260923T010641-3xn8hn/00': ('651 rows × 81 columns from 1.5 T: short window,\nfew columns hold 3 light-tone periods', (-8, 8)),
          'vti02-fan-design-sol-none/20260923T013751-ls25bv/00': ('linear-in-B grid: F_L undersampled', (30, 40))}
for kk, q, h, l in pts:
    if kk in labels:
        t, off = labels[kk]
        g.annotate(t, (h, q), textcoords='offset points', xytext=off, fontsize=8, color=INK, ha='right' if off[0] < 0 else 'left',
                   arrowprops=dict(arrowstyle='-', color=INK2, lw=0.6, shrinkA=0, shrinkB=3))
g.set_xscale('log'); g.set_xlim(0.8, 22); g.set_ylim(-0.04, 1.08)
g.set_xticks([1, 2, 3, 5, 8, 12, 20]); g.set_xticklabels(['1', '2', '3', '5', '8', '12', '20'])
g.set_xlabel('estimated measurement time (hours, log scale)'); g.set_ylabel('quality')
g.legend(fontsize=8, frameon=False, loc='lower right')
g.set_title(f'(f) Every vti-02 fan design graded so far ({len(pts)}: 29 by AI agents, 6 measured in the lab): quality against time. The best is the measured\n'
            '08-25 run 8 (50 nA); agent designs, all at 10 nA, top out near 0.8. Fans that start too high in field, undersample F_L, or have too few rows score low.',
            loc='left', fontsize=9.5, color=INK)
fig.text(0.06, 0.985, 'How a Landau fan design is scored for telling ABAB from ABCA stacking', fontsize=14, color=INK, va='top', weight='bold')
fig.text(0.06, 0.972,
         'vti-02 is a tetralayer graphene device. A Landau fan (resistance over field rows B × density columns n) must tell Bernal (ABAB) from rhombohedral (ABCA) stacking.\n'
         'In the Fourier transform of resistance vs 1/B, ABAB shows a slow light tone F_light and a heavy tone F_heavy; ABCA shows one tone F_L = F_light + F_heavy.\n'
         'The score asks, from the planned design alone, whether the fan would resolve the light tone and whether it would separate F_L from F_heavy.',
         fontsize=9, color=INK2, va='top', linespacing=1.45)
fig.savefig(OUT + '4_quality_score.png', dpi=110, bbox_inches='tight')
