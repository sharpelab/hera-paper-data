"""Electron-side ABAB tones under literature parameter sets (bare and Hartree-screened).
Sets defined in SETS; provenance in the report. Writes litsets_curves.csv."""
import csv, sys, numpy as np, abab_lib as L
from concurrent.futures import ProcessPoolExecutor
P = L.Params
SETS = {
 # name: (Params, note)
 'corpus_KM':        P(g0=3.0,  g1=0.40,  g2=-0.020, g3=0.0,   g4=0.040, g5=0.040, dp=0.050),
 'corpus_KM_g3':     P(g0=3.0,  g1=0.40,  g2=-0.020, g3=0.30,  g4=0.040, g5=0.040, dp=0.050),
 'graphite_DD':      P(g0=3.16, g1=0.39,  g2=-0.020, g3=0.315, g4=0.044, g5=0.038, dp=0.050),
}
NS = [round(x, 2) for x in np.arange(1.0, 3.51, 0.25)]
SCREEN = [None, (2.0, True), (4.0, True), (5.7, False)]
def run(job):
    name, scr = job
    p = SETS[name]
    rows = []
    for n in NS:
        U = np.zeros(4) if scr is None else L.hartree_U(p, n, scr[0], include_valence=scr[1])[0]
        try:
            t = L.solve(p, [n], U=U)[0]
        except ValueError as e:
            print(name, scr, n, e, file=sys.stderr); continue
        rows.append(dict(set=name, screening='bare' if scr is None else f'eps{scr[0]}_val{int(scr[1])}',
                         U_meV=';'.join(f'{u*1e3:.2f}' for u in U), **{k: round(float(x), 5) for k, x in t.items()}))
    return rows
if __name__ == '__main__':
    if len(sys.argv) > 1:
        import importlib; SETS.update(importlib.import_module(sys.argv[1]).SETS)
    jobs = [(s, c) for s in SETS for c in SCREEN]
    with ProcessPoolExecutor(24) as ex:
        allrows = [r for rs in ex.map(run, jobs) for r in rs]
    with open('litsets_curves.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0].keys())); w.writeheader(); w.writerows(allrows)
    obs_n = np.array([1.56, 1.85, 2.15, 2.45, 2.75]); obs_f = np.array([0.178, 0.192, 0.213, 0.224, 0.238])
    print(f"{'set':18s} {'screen':12s}  frac@1.5  2.0  2.5  3.0 | m_l m_h @2 | rms vs obs  mean resid")
    for s, c in jobs:
        rr = [r for r in allrows if r['set'] == s and r['screening'] == ('bare' if c is None else f'eps{c[0]}_val{int(c[1])}')]
        d = {r['n']: r for r in rr}
        mf = np.interp(obs_n, [r['n'] for r in rr], [r['frac'] for r in rr])
        print(f"{s:18s} {rr[0]['screening']:12s}  {d[1.5]['frac']:.3f} {d[2.0]['frac']:.3f} {d[2.5]['frac']:.3f} {d[3.0]['frac']:.3f} |"
              f" {d[2.0]['m_light']:.4f} {d[2.0]['m_heavy']:.4f} | {np.sqrt(np.mean((mf-obs_f)**2)):.3f}  {np.mean(mf-obs_f):+.3f}")
