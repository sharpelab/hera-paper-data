"""sr0 (drain current) phase as a proxy for two-terminal / contact impedance; vs B and T, and vs the quadrature noise."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
inv = json.load(open('inventory_raw.json'))
bd = json.load(open('bdep.json')); Be = bd['edges']
for r in inv:
    key = f"{r['day']}-r{r['run']}"
    if (r.get('npts') or 0) < 60: continue
    d = loadrun(r['day'], r['run'])
    x0, y0 = d['sr0X'], d['sr0Y']
    if y0 is None: continue
    ph = np.rad2deg(np.arctan2(y0, x0)); ph = (ph + 360) % 360 - 180   # sr0_gain negative: phase near 180
    ph = np.where(ph > 90, ph - 180, np.where(ph < -90, ph + 180, ph))
    mag = np.hypot(x0, y0) / 1e6
    B = d['B'] if d['B'] is not None else np.zeros_like(x0)
    s = f"{key:7s} tau {d['tau']:.1f} T {np.nanmedian(d['T']) if d['T'] is not None else np.nan:5.1f}: sr0 phase(deg)/|I|nA by B: "
    for lo, hi in zip(Be[:-1], Be[1:]):
        m = (B >= lo) & (B < hi)
        if m.sum() >= 10: s += f"[{lo},{hi}) {np.median(ph[m]):+.2f}/{np.median(mag[m])*1e9:.2f} "
    if key in bd['runs']: s += ' | Ynoise ' + ' '.join('-' if x is None else f'{x:.0f}' for x in bd['runs'][key]['res'])
    print(s)
