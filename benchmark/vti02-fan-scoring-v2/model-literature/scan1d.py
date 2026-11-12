"""One-at-a-time sensitivity of the electron-side light fraction and masses around the corpus set."""
import csv, numpy as np
from dataclasses import replace
import abab_lib as L
P0 = L.M.ABAB
NS = [1.0, 1.5, 2.0, 2.5, 3.0]
scans = {
    'g0': [2.6, 2.8, 3.0, 3.16],
    'g1': [0.36, 0.38, 0.40, 0.42],
    'g2': [-0.032, -0.028, -0.024, -0.020, -0.016, -0.012, -0.008, 0.0],
    'g3': [0.0, 0.1, 0.2, 0.3],
    'g4': [0.0, 0.04, 0.08, 0.14],
    'g5': [0.0, 0.02, 0.04, 0.06],
    'dp': [0.0, 0.02, 0.035, 0.05, 0.065],
}
rows = []
for par, vals in scans.items():
    for v in vals:
        p = replace(P0, **{par: v})
        for t in L.solve(p, NS):
            rows.append(dict(scan=par, value=v, **{k: round(float(x), 5) for k, x in t.items()}))
        r = {t['n']: t for t in rows if t['scan'] == par and t['value'] == v}
        print(f"{par}={v:+.3f}  frac@1.5/2/3 = {r[1.5]['frac']:.3f}/{r[2.0]['frac']:.3f}/{r[3.0]['frac']:.3f}"
              f"  m_l/m_h@2 = {r[2.0]['m_light']:.4f}/{r[2.0]['m_heavy']:.4f}", flush=True)
for ud in [0.0, 0.005, 0.01, 0.02]:
    for t in L.solve(P0, NS, U=L.linear_U(ud)):
        rows.append(dict(scan='ud_linear', value=ud, **{k: round(float(x), 5) for k, x in t.items()}))
    r = {t['n']: t for t in rows if t['scan'] == 'ud_linear' and t['value'] == ud}
    print(f"ud={ud*1e3:.0f}meV/layer  frac@1.5/2/3 = {r[1.5]['frac']:.3f}/{r[2.0]['frac']:.3f}/{r[3.0]['frac']:.3f}  m@2 {r[2.0]['m_light']:.4f}/{r[2.0]['m_heavy']:.4f}", flush=True)
with open('scan1d.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
