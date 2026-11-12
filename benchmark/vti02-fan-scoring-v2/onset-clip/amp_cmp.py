"""Tone amplitude (Ohm) at B = 1, 1.5, 2 T from the parametric fits: 0822-r8 (10 nA) vs 0825-r8 (50 nA) at matched actual n; plus sigma_pt."""
import csv, numpy as np
from pfit import RT
P = [r for r in csv.DictReader(open('pfit.csv')) if r['Te'] == '1.2']
E = {(r['rec'], int(r['col']), r['tone']): r for r in csv.DictReader(open('envelopes.csv'))}
f = float
def A(r, t, B):
    u = 1 / B; return f(r[f'A0_{t}']) * np.exp(f(r[f's_{t}']) * (u - f(r['u0']))) * RT(f(r[f'm_{t}']), 1.2, u)
for rec in ('0822-r8', '0825-r8', '0822-r6', '0821-r5'):
    L = [r for r in P if r['rec'] == rec and 2.0 <= f(r['n']) <= 2.95]
    sig = np.median([f(E[(rec, int(r['col']), 'heavy')]['sigma']) for r in L])
    out = []
    for t in ('light', 'heavy', 'FL'):
        for B in (1.0, 1.5, 2.0, 3.0):
            v = [A(r, t, B) for r in L if f(r[f'sse_{t}']) < 0.8]
            out.append(f"{t}@{B}:{np.median(v):.2f}" if v else f"{t}@{B}:-")
    print(rec, f"N={len(L)} I={L[0]['I_nA']} sigma_pt={sig:.2f} Ohm |", ' '.join(out))
