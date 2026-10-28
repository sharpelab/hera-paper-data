"""Q5: composite |R|(n_actual, B) on the electron side from the live fans; coverage, max |R| per n column vs B, implied sensitivity."""
import numpy as np, pandas as pd, sys, json, gzip, io
sys.path.insert(0, '.')
from load import load, D
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pts = []
def add(src, n, B, R, V, sens, note=''):
    clip = np.abs(V) >= 0.95 * sens if sens else np.zeros_like(V, bool)
    pts.append(pd.DataFrame(dict(src=src, n=n.ravel(), B=B.ravel(), R=np.abs(R).ravel(), clip=clip.ravel(), note=note)))
for nm in ['0821-r8', '0822-r8', '0825-r8', '0824-r4']:
    d = load(nm)
    n = np.broadcast_to(d['n'], d['R'].shape); B = np.broadcast_to(d['B'][:, None], d['R'].shape)
    if nm == '0824-r4': B = d['g']('magnet_field', 1)
    add(nm, n, B, d['R'], d['V'], d['lk']['sr1']['sensitivity'])
    # also the 0825 run-7 spot columns (5 densities, 1.5-6 T)
d7 = load('0825-r8', run=7)
n7 = np.array([-0.9, 1.8, 2.2, 2.6, 3.0]); add('0825-r7spot', np.broadcast_to(n7, d7['R'].shape), np.broadcast_to(d7['B'][:, None], d7['R'].shape), d7['R'], d7['V'], d7['lk']['sr1']['sensitivity'])
# 0823-r6: continuous ramp, geometry-prior n x 0.90, autoranged sr1 (no fixed sens)
p = D / '0823-r6/session/data/6'; meta = json.load(open(p / 'metadata.json')); cols = meta['columns']
X = np.loadtxt(io.StringIO(gzip.decompress((p / 'data.tsv.gz').read_bytes()).decode()), delimiter='\t')
vbg = X[:, cols.index('k_2400_bg_volt')]; n23 = 0.90 * (-1.55 + (vbg + 0.565) / (1.25 + 0.565) * (3.43 + 1.55))
I23 = X[:, cols.index('sr0_X')] / -1e6; R23 = X[:, cols.index('sr1_X')] / I23
add('0823-r6', n23, X[:, cols.index('magnet_field')], R23, X[:, cols.index('sr1_X')], None, 'geometry-prior n x0.90; autorange')
P = pd.concat(pts, ignore_index=True); P = P[(P.n >= 0.85) & (P.n <= 3.45)]
P.to_csv('composite_points.csv.gz', index=False)
nb = np.round(np.arange(0.9, 3.41, 0.1), 2); Bb = np.arange(0, 10.01, 1.0)
P['nb'] = pd.cut(P.n, np.r_[nb - 0.05, nb[-1] + 0.05], labels=nb); P['Bb'] = pd.cut(P.B, Bb, labels=[f"{a:.0f}-{a+1:.0f}" for a in Bb[:-1]])
ok = P[~P['clip']]
M = ok.pivot_table(index='nb', columns='Bb', values='R', aggfunc='max', observed=False).round(0)
S = ok.pivot_table(index='nb', columns='Bb', values='src', aggfunc=lambda s: '+'.join(sorted(set(x[:4] for x in s))), observed=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print('max |R| (ohm), unclipped points, n actual bin (0.1) x B bin:'); print(M.to_string())
print('\nsources:'); print(S.to_string())
M.to_csv('composite_maxR_nB.csv'); S.to_csv('composite_sources_nB.csv')
print('\nclipped points dropped:', int(P['clip'].sum()), 'by src', P[P['clip']].src.value_counts().to_dict())
# per column: max |R| over B<=10 and implied sens at 10/50 nA, 0.95 headroom (also at +-3% n shift: take max over neighbours)
SENS = np.array([1, 2, 5]) * 10.0 ** np.arange(-9, 1)[:, None]; SENS = np.sort(SENS.ravel())
def pick(v): return SENS[np.searchsorted(SENS, v / 0.95)]
col = ok.groupby('nb', observed=False).agg(Rmax=('R', 'max'), Bmax_cov=('B', 'max'), npts=('R', 'size'))
col['Rmax_nbhd'] = col.Rmax.rolling(3, center=True, min_periods=1).max()
col['V10nA_uV'] = (col.Rmax_nbhd * 1e-8 * 1e6).round(2); col['sens10nA'] = [pick(v * 1e-6) if np.isfinite(v) else np.nan for v in col.V10nA_uV]
col['V50nA_uV'] = (col.Rmax_nbhd * 5e-8 * 1e6).round(2); col['sens50nA'] = [pick(v * 1e-6) if np.isfinite(v) else np.nan for v in col.V50nA_uV]
print('\nper n column:'); print(col.to_string(float_format=lambda v: f'{v:.3g}')); col.to_csv('composite_columns.csv')
# fan-window worst case: n in [1.3,3.4] x B in [2,10] and [1,10]
for lo in (1.0, 2.0):
    w = ok[(ok.n >= 1.3) & (ok.B >= lo)]
    w = w.reset_index(drop=True); i = w.R.idxmax()
    print(w.sort_values('R').tail(5)[['src','n','B','R']].to_string())
    print(f"window n 1.3-3.4, B {lo}-10: max|R| {w.R.max():.0f} ohm at n={w.loc[i,'n']:.2f}, B={w.loc[i,'B']:.1f} ({w.loc[i,'src']}); 99.9th pct {np.percentile(w.R,99.9):.0f}")
fig, ax = plt.subplots(figsize=(7, 5))
for s, a in ok.groupby('src'):
    ax.scatter(a.n, a.B, s=1, label=s)
ax.set_xlabel('n actual (1e12)'); ax.set_ylabel('B (T)'); ax.legend(markerscale=6, fontsize=7); ax.set_title('composite coverage (unclipped, e side)')
fig.tight_layout(); fig.savefig('composite_coverage.png', dpi=110)
fig, ax = plt.subplots(figsize=(7, 5))
pc = ax.pcolormesh(M.columns.astype(str), M.index.astype(float), M.values, shading='nearest', cmap='viridis'); fig.colorbar(pc, label='max |R| (ohm)')
ax.set_xlabel('B bin (T)'); ax.set_ylabel('n actual (1e12)'); ax.set_title('composite max |R| per (n, B) bin'); fig.tight_layout(); fig.savefig('composite_maxR.png', dpi=110)
