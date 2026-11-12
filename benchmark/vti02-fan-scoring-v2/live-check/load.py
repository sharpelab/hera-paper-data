"""Load live vti-02 fans into grids (read-only)."""
import sys, json, gzip, io
import numpy as np
from pathlib import Path
D = Path('/data/sharpelab/hera-data/frontier/calibration/vti02-live')
TONES = json.load(open(Path(__file__).resolve().parents[1] / 'tones.json'))
_ks = np.array(sorted(float(k) for k in TONES))
_light = np.array([TONES[f"{k:.1f}"][0][0] for k in _ks]); _heavy = np.array([TONES[f"{k:.1f}"][1][0] for k in _ks])
def f_light(n): return np.interp(n, _ks, _light, left=np.nan, right=np.nan)
def f_heavy(n): return np.interp(n, _ks, _heavy, left=np.nan, right=np.nan)
def f_L(n): return 10.3392 * np.abs(n)   # h/(4e) per 1e12 cm^-2
# fixture, run, design n endpoints (first fast point, last fast point), n_scale
FANS = {
  '0821-r8': dict(run=8, n0=3.40, n1=1.50, scale=0.92, vch='sr1'),
  '0822-r8': dict(run=8, n0=3.25, n1=1.60, scale=0.886, vch='sr1'),
  '0825-r8': dict(run=8, n0=1.20, n1=3.05, scale=1.0, vch='sr1'),
  '0824-r4': dict(run=4, n0=-1.04, n1=2.10, scale=0.90, vch='sr1'),
}
def load(name, run=None):
    c = FANS.get(name, {})
    run = run if run is not None else c['run']
    p = D / name / 'session' / 'data' / str(run)
    meta = json.load(open(p / 'metadata.json'))
    cols = meta['columns']
    X = np.loadtxt(io.StringIO(gzip.decompress((p/'data.tsv.gz').read_bytes()).decode()), delimiter='\t', ndmin=2)
    fs = meta['fast_setpoints']; nfast = len(fs[0]) if isinstance(fs[0], list) else len(fs)
    nrows = X.shape[0] // nfast; X = X[:nrows*nfast]
    g = lambda col, k=0: X[:, [i for i, cc in enumerate(cols) if cc == col][k]].reshape(nrows, nfast)
    ins = meta['instruments']
    lk = {}
    for nm in ('sr0', 'sr1', 'sr2', 'sr3'):
        if nm in ins:
            pp = ins[nm]['snapshot']['parameters']
            lk[nm] = {k: pp[k]['value'] for k in ('sensitivity', 'time_constant', 'filter_slope', 'amplitude') if k in pp}
    mc = meta['measurement_config']
    I = g('sr0_X') / mc['sr0_gain']
    V = g(c.get('vch', 'sr1') + '_X')
    B = g('magnet_field')[:, 0]
    Vtg = g('k_2400_tg_volt')
    # density: linear in Vtg along the co-swept line, endpoints from the design
    v = Vtg[0]; n_design = c['n0'] + (v - v[0]) / (v[-1] - v[0]) * (c['n1'] - c['n0'])
    return dict(name=name, run=run, meta=meta, cols=cols, X=X, g=g, nrows=nrows, nfast=nfast, B=B,
                Vtg=Vtg, n_design=n_design, n=n_design * c['scale'], I=I, V=V, R=V / I, lk=lk,
                t=g('time'), Ibias=lk['sr1']['amplitude'] / mc['bias_resistor'])
if __name__ == '__main__':
    for nm in FANS:
        d = load(nm)
        v = d['Vtg']
        print(nm, 'rows', d['nrows'], 'nfast', d['nfast'], 'B', d['B'][0], '->', d['B'][-1],
              'fast dir row0', v[0, 0], v[0, -1], 'row1', v[1, 0], v[1, -1],
              'n', d['n'][0].round(2), d['n'][-1].round(2), 'I nA', np.median(d['I'])*1e9,
              'R', np.nanpercentile(d['R'], [1, 50, 99]).round(1), 'lk', d['lk'])
        dt = np.diff(d['t'], axis=1); print('   dt fast median', np.median(dt), ' row time', np.median(d['t'][:,-1]-d['t'][:,0]))
        if nm == '0824-r4':
            Bread = d['g']('magnet_field', 1); print('   B readback - setpoint (per row mean, max abs):', np.abs(Bread - d['B'][:, None]).max())
