"""Rescore the dev-set fans under each tone model. band.py / roi.py / prereg-stats/common.py / onset-clip/rescore.py
are imported unmodified; the tone model is swapped by rebinding roi.f_light (used by band.cells and
onset-clip cells_percol) and common.f_light (used by common.score, the capped-cells primary).
Episodes: common.inventory() with ending == 'fan' (incl. the 4 hand extractions) + live fans; labels = observed model.
Frame: cases.toml n_scale (the grader's); sensitivity: model-fit's 08-22 F_L frame 0.8625 (n_frame + 0.10) on the
3a4cf818 cut. Clips: own B_min, flat 0.75 T, per-column Dingle ref (onset-clip b_ref_op: 0.524 + 0.0955|n|).
-> rescore.csv, rescore.md"""
import sys, importlib.util, warnings
sys.dont_write_bytecode = True
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
TOP = Path('/data/sharpelab/hera-data/vti02-fan-scoring-v2')
sys.path.insert(0, str(TOP / 'prereg-stats')); sys.path.insert(0, str(Path(__file__).parent))
import common as C          # sets sys.argv around `import roi, band`
import roi, band
import tone_fn as TF
spec = importlib.util.spec_from_file_location('oc_rescore', TOP / 'onset-clip/rescore.py')
OC = importlib.util.module_from_spec(spec); spec.loader.exec_module(OC)
ORIG = roi.f_light
MODELS = ['corpus', 'B', 'Halder_ABAB', 'Shi_ABAB', 'graphite_eps5.7', 'env_lo', 'env_hi']


def make_fl(model):
    def fl(n12):
        if model == 'roi':
            return ORIG(n12)
        try:
            return TF.tone_fn(n12, 'e' if n12 > 0 else 'h', model, warn=False)[0] if n12 != 0 else np.nan
        except ValueError:
            return np.nan
    return fl


def use(model):
    f = make_fl(model); roi.f_light = f
    C.f_light = lambda n, tones='model': np.array([f(x) for x in np.atleast_1d(np.asarray(n, float))])


DING = OC.lin('0825-r8:b_ref_op')
eps = [r for r in C.inventory() if r['ending'] == 'fan'] + [dict(r, model='live', corpus='-', cut='live') for r in C.live_fans() if r['ending'] == 'fan']
rows = []
for r in eps:
    B, n, h, acq = C.design(r)
    frames = [('cases', n)]
    if r.get('cut') == C.CUT_0822:
        frames.append(('mf0822', 0.8625 * (C.g.columns(r['doc']) / 1e12 + 0.10)))
    for fr, nn in frames:
        for m in ['roi'] + MODELS:
            use(m)
            c_own, k_own, _ = band.cells(B, nn, 1e-3)
            c_75, k_75, _ = band.cells(B, nn, 0.75)
            c_d, k_d = OC.cells_percol(B, nn, DING)
            q_own = C.score(B, nn, dict(clip=None))['cells']; q_75 = C.score(B, nn, dict(clip=0.75))['cells']
            rows.append(dict(key=r['key'], model=r['model'], corpus=r['corpus'], cut=r.get('cut'), source=r.get('source', 'grader'),
                             frame=fr, tones=m, B=f'{B.min():.2f}-{B.max():.1f}', n=f'{nn.min():+.2f}..{nn.max():+.2f}x{nn.size}',
                             h=h, cols_own=c_own, cells_own=k_own, cols_075=c_75, cells_075=k_75, cols_ding=c_d, cells_ding=k_d,
                             Q_own=q_own, Q_075=q_75))
roi.f_light = ORIG
R = pd.DataFrame(rows); R.to_csv('rescore.csv', index=False, float_format='%.3f')
chk = R[(R.tones == 'roi') & (R.frame == 'cases')].set_index('key')[['cols_own', 'cols_075']].sub(
    R[(R.tones == 'corpus') & (R.frame == 'cases')].set_index('key')[['cols_own', 'cols_075']])
print('roi(tones.json) vs corpus table: max |d cols| =', int(chk.abs().max().max()))


def lab(k):
    return k.replace('vti02-fan-design-', '').replace('/episodes/', '#')


with open('rescore.md', 'w') as f:
    for fr in ('cases', 'mf0822'):
        D = R[(R.frame == fr) & (R.tones != 'roi')]
        for what, cols in (('cols / cells at own B_min', ('cols_own', 'cells_own')), ('cols / cells at flat 0.75 T clip', ('cols_075', 'cells_075')),
                           ('cols / cells at per-column Dingle clip', ('cols_ding', 'cells_ding')), ('capped-cells Q (own / 0.75 T)', ('Q_own', 'Q_075'))):
            f.write(f'\n### {what} (frame: {fr})\n\n| episode | model | corpus | B | n | ' + ' | '.join(MODELS) + ' |\n|' + '---|' * (5 + len(MODELS)) + '\n')
            for key, g in D.groupby('key', sort=False):
                g = g.set_index('tones'); a = g.iloc[0]
                cell = lambda m: (f"{g.loc[m, cols[0]]:.2f} / {g.loc[m, cols[1]]:.2f}" if what.startswith('capped')
                                  else f"{int(g.loc[m, cols[0]])} / {g.loc[m, cols[1]]:.1f}")
                f.write(f"| {lab(key)}{' (hand)' if a.source == 'hand' else ''} | {a.model} | {a.corpus} | {a.B} | {a.n} | " + ' | '.join(cell(m) for m in MODELS) + ' |\n')
print(open('rescore.md').read())
