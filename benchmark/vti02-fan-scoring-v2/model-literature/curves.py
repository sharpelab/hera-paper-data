"""Recommended grader-prior light-tone curves on a fine n grid (electron side, D = 0).
Writes curves_recommended.csv: per model, n, F_light, F_heavy, F_L, frac, masses; plus envelope rows."""
import csv, numpy as np, abab_lib as L
from concurrent.futures import ProcessPoolExecutor
from litsets_defs import SETS
S = dict(SETS); S['corpus_KM'] = L.M.ABAB
S['graphite_DD'] = L.PX(g0=3.16, g1=0.39, g2=-0.020, g3=0.315, g4=0.044, g5=0.038, dp=0.050)
NS = [round(x, 2) for x in np.arange(0.8, 3.51, 0.05)]
MODELS = [('Halder_ABAB', None), ('Shi_ABAB', None), ('Klanurak_ABAB', (5.7, False)),
          ('graphite_DD', (5.7, False)), ('corpus_KM', (4.0, True)), ('corpus_KM', None)]
def one(job):
    name, scr, n = job
    p = S[name]
    U = np.zeros(4) if scr is None else L.hartree_U(p, n, scr[0], include_valence=scr[1])[0]
    try:
        t = L.solve(p, [n], U=U)[0]
    except ValueError:
        return None
    return dict(model=name, screening='bare' if scr is None else f'eps{scr[0]}_val{int(scr[1])}',
                **{k: round(float(x), 5) for k, x in t.items()})
if __name__ == '__main__':
    jobs = [(m, s, n) for m, s in MODELS for n in NS]
    with ProcessPoolExecutor(28) as ex:
        rows = [r for r in ex.map(one, jobs, chunksize=2) if r]
    keys = list(rows[0].keys())
    with open('curves_recommended.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print('n    ' + '  '.join(f'{m[:10]}/{("b" if s is None else s[0])}' for m, s in MODELS))
    for n in (0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5):
        out = []
        for m, s in MODELS:
            sc = 'bare' if s is None else f'eps{s[0]}_val{int(s[1])}'
            r = [x for x in rows if x['model'] == m and x['screening'] == sc and abs(x['n'] - n) < 1e-6]
            out.append(f"{r[0]['frac']:.3f}({r[0]['F_light']:.2f}T)" if r else '   --   ')
        print(f'{n:4.2f} ' + ' '.join(out))
