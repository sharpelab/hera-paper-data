"""Figures for REPORT.md: fig/spectra.png, fig/hole_nF.png, fig/onsets_detection.png."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import spec, model
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

C1, C2, C3, C4, C5 = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4'
INK, MUTED, GRID = '#222222', '#6b6b6b', '#e6e6e6'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.spines.top': False, 'axes.spines.right': False,
                     'lines.linewidth': 1.6, 'legend.frameon': False})
tr = {t['id']: t for t in load_all()}

# ---- fig 1: spectra of the three dense traces
cases = [('0822-r7', 0.907, 1.063, [(0.6, 2.3, 'low field 0.6-2.3 T'), (1.0, 4.5, '1.0-4.5 T')], '08-22 r7: 10 nA, tau 0.3 s'),
         ('0824-r5-c0', 0.725, 0.720, [(0.51, 2.5, 'low field 0.51-2.5 T'), (0.51, 6.01, 'full 0.51-6 T')], '08-24 r5 (hole density): 10 nA, tau 0.1 s'),
         ('0825-r7-c0', 0.842, 0.855, [(1.5, 3.5, '1.5-3.5 T'), (1.5, 6.0, 'full 1.5-6 T')], '08-25 r7 (hole density): 50 nA, tau 0.1 s')]
fig, axs = plt.subplots(3, 1, figsize=(8, 9.5))
for ax, (k, n, ng, wins, ttl) in zip(axs, cases):
    t = tr[k]
    for (lo, hi, lab), c in zip(wins, (C1, C2)):
        s = spec(t['B'], t['R'], lo, hi, 5, Fmax=30, dFgrid=0.02)
        ax.plot(s['F'], s['amp'], color=c, label=f"{lab} (dF {s['dF']:.2f} T)")
    fl, fh, fL = model(n)
    top = ax.get_ylim()[1]
    for f, nm in ((fl, 'light'), (fh, 'heavy'), (fL, 'F_L'), (2 * fh, '2 heavy')):
        ax.axvline(f, color=INK, lw=0.8, ls='--'); ax.text(f + 0.15, top * 0.93, nm, fontsize=8, color=INK, rotation=90, va='top')
    ax.axvline(model(ng)[2], color=MUTED, lw=0.8, ls=':'); ax.text(model(ng)[2] + 0.15, top * 0.45, 'F_L, grader frame', fontsize=7, color=MUTED, rotation=90, va='top')
    ax.set_xlim(0, 20); ax.set_ylabel('amplitude (ohm)')
    ax.set_title(f'{ttl}; Halder_ABAB tones at |n| {n} (dashed)', fontsize=9, loc='left', color=INK)
    ax.legend(loc='upper right', fontsize=8)
axs[-1].set_xlabel('SdH frequency F (T)')
fig.tight_layout(); fig.savefig('fig/spectra.png', dpi=130); plt.close(fig)

# ---- fig 2: 08-24 r4 hole (n, F) map + consensus tones of every trace
T = pd.read_csv('tones.csv'); T = T[T.F.notna() & (T.frac >= 0.5)]
cols = sorted([t for t in tr.values() if t['id'].startswith('0824-r4-')], key=lambda t: t['n_frame'])
Z, ns = [], []
for t in cols:
    s = spec(t['B'], t['R'], 0.76, 6.1, 5, Fmax=16, dFgrid=0.02)
    band = (s['F'] > 11.5) & (s['F'] < 15.5)
    Z.append(s['S'] / np.median(s['S'][band])); ns.append(abs(t['n_act_e']))
Z, ns = np.array(Z), np.array(ns)
fig, ax = plt.subplots(figsize=(8, 5.5))
pc = ax.pcolormesh(s['F'], ns, np.log10(np.clip(Z, 1, None)), shading='nearest', cmap='Blues', vmin=0, vmax=1.6)
fig.colorbar(pc, ax=ax, label='log10 contrast (|S| / median 11.5-15.5 T), 08-24 r4, 0.76-6 T')
nn = np.linspace(0.3, 1.1, 200); fl, fh, fL = model(nn)
ax.plot(fL, nn, color=INK, lw=1.2, label='F_L = 10.34 |n|'); ax.plot(fh, nn, color=C2, lw=1.4, label='Halder heavy'); ax.plot(fl, nn, color=C3, lw=1.4, label='Halder light')
ax.plot(model(nn, 'h', 'corpus')[0], nn, color=C3, lw=1.0, ls=':', label='corpus light (for scale)')
mk = {'heavy': ('o', C2), 'F_L': ('s', INK), 'light': ('^', C3), '2 heavy': ('D', C5)}
for key, (m, c) in mk.items():
    sub = T[T.tone.astype(str).str.startswith(key + ' (')]
    ax.scatter(sub.F, sub.n_ref, marker=m, s=34, facecolor=c, edgecolor='white', linewidth=1.0, zorder=5, label=f'consensus tone: {key}')
oth = T[~T.tone.astype(str).str.match(r'^(heavy|F_L|light|2 heavy) \(')]
ax.scatter(oth.F, oth.n_ref, marker='x', s=22, color=MUTED, zorder=4, label='other / ambiguous')
ax.set_xlim(0, 16); ax.set_ylim(0.28, 1.08); ax.set_xlabel('SdH frequency F (T)'); ax.set_ylabel('|n| actual (1e12 cm^-2; grader frame / QH / F_L tone)')
ax.set_title('Hole side: 08-24 r4 columns (map) and every trace\'s consensus tones (>= half the extraction choices)', fontsize=9, loc='left')
ax.legend(fontsize=7, loc='lower right', ncol=2); fig.tight_layout(); fig.savefig('fig/hole_nF.png', dpi=130); plt.close(fig)

# ---- fig 3: onsets vs |n| and detection vs periods
O = pd.read_csv('onsets_joint.csv'); S = pd.read_csv('onsets.csv')
nref = {'0822-r7': 0.907, '0824-r5-c0': 0.725, '0825-r7-c0': 0.842}
O['n'] = [nref.get(k, abs(nf) * 0.9) for k, nf in zip(O.trace, O.n_frame)]
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 5.4))
for tone, c, m in (('heavy', C2, 'o'), ('F_L', INK, 's'), ('2 heavy', C5, 'D')):
    d = O[(O.tone == tone) & O.onset_B.notna() & ((O.b_hi > 5) | (O.trace != '0822-r7'))]
    unc = d[~d.censored.astype(bool)]; cen = d[d.censored.astype(bool)]
    a.scatter(unc.n, unc.onset_B, marker=m, s=40, color=c, edgecolor='white', label=f'{tone}: onset', zorder=5)
    a.scatter(cen.n, cen.onset_B, marker='v', s=40, facecolor='none', edgecolor=c, label=f'{tone}: censored (onset below)', zorder=5)
sh = S[(S.method == 'sdh_onset') & S.identity.astype(str).str.startswith('heavy') & S.censored.fillna(False).astype(bool)]
a.scatter([nref.get(k, np.nan) if k in nref else np.nan for k in sh.trace], sh.onset_B, marker='v', s=40, facecolor='none', edgecolor=C2)
d = S[(S.trace == '0824-r5-c0') & (S.method == 'sdh_onset') & (S.identity == 'heavy')]
a.scatter([0.725] * len(d), d.onset_B, marker='v', s=40, facecolor='none', edgecolor=C2)
for y, lab in ((0.75, 'electron light floor 0.75 T'), (1.0, 'electron split floor 1.0 T'), (1.54, 'electron F_L onset 1.54 (50 nA) / 1.93 T (10 nA)')):
    a.axhline(y, color=MUTED, lw=0.8, ls='--'); a.text(0.46, y + 0.03, lab, fontsize=7, color=MUTED)
a.set_xlim(0.45, 1.0); a.set_ylim(0.3, 2.6); a.set_xlabel('|n| (1e12 cm^-2)'); a.set_ylabel('onset B (T)')
a.set_title('Hole tone onsets (joint matched-filter walk, 5 sigma)', fontsize=9, loc='left'); a.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=3)
D = pd.read_csv('detect_columns.csv'); D = D[D.n_ref >= 0.5]
bins = [1.0, 1.5, 2.0, 2.5, 3.5, 8.0]; D['kb'] = pd.cut(D.k_light, bins)
g = D.groupby('kb', observed=False).agg(N=('trace', 'size'), light=('light_true', 'mean'), split=('split_true', 'mean'))
x = np.arange(len(g)); lab = ['1-1.5', '1.5-2', '2-2.5', '2.5-3.5', '>3.5']
e_light = [0.31, 0.50, 0.78, 0.84, 1.00]; e_split = [0.16, 0.41, 0.55, 0.79, 0.90]
b.plot(x, e_light, color=C3, ls='--', marker='o', label='electron light (live fans, model k)')
b.plot(x, e_split, color=C1, ls='--', marker='o', label='electron split')
b.plot(x, g.light.values, color=C3, marker='^', label='hole light')
b.plot(x, g.split.values, color=C1, marker='s', label='hole split')
for xi, nN in zip(x, g.N.values): b.text(xi, -0.08, f'N={nN}', ha='center', fontsize=7, color=MUTED)
b.set_xticks(x, lab); b.set_ylim(-0.12, 1.05); b.set_xlabel('light-tone periods in the window (Halder, reference density)'); b.set_ylabel('fraction of column-windows')
b.set_title('Detection vs periods: hole (|n| >= 0.5) against electron', fontsize=9, loc='left'); b.legend(fontsize=7, loc='upper left')
fig.tight_layout(); fig.savefig('fig/onsets_detection.png', dpi=130); plt.close(fig)
