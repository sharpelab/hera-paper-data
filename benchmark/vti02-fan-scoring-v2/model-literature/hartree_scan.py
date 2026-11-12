"""Corpus parameter set + self-consistent Hartree layer potential (symmetric gates), vs eps_z, valence
polarization on/off, and residual D. Writes hartree_scan.csv."""
import csv, numpy as np, abab_lib as L
from concurrent.futures import ProcessPoolExecutor
P = L.M.ABAB
NS = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5]
cases = [('none', None, False, 0.0)]
for eps in (1.0, 2.0, 2.6, 4.0):
    for val in (False, True):
        cases.append((f'eps{eps}_val{int(val)}', eps, val, 0.0))
for D in (0.02, 0.05, 0.1):
    cases.append((f'eps2.6_val0_D{D}', 2.6, False, D))
def run(case):
    name, eps, val, D = case
    rows = []
    for n in NS:
        U = np.zeros(4) if eps is None else L.hartree_U(P, n, eps, D_Vnm=D, include_valence=val)[0]
        t = L.solve(P, [n], U=U)[0]
        rows.append(dict(case=name, eps_z=eps, valence=val, D_Vnm=D, U_meV=';'.join(f'{u*1e3:.2f}' for u in U),
                         **{k: round(float(x), 5) for k, x in t.items()}))
    return rows
with ProcessPoolExecutor(16) as ex:
    allrows = [r for rs in ex.map(run, cases) for r in rs]
with open('hartree_scan.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(allrows[0].keys())); w.writeheader(); w.writerows(allrows)
for c in cases:
    rr = [r for r in allrows if r['case'] == c[0]]
    print(f"{c[0]:22s} " + ' '.join(f"{r['frac']:.3f}" for r in rr) + f"   m@2 {rr[4]['m_light']:.4f}/{rr[4]['m_heavy']:.4f}")
print('n:', NS)
