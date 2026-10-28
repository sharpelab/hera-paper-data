"""Out-of-sample test on QC0426 (VTI rig, June; f_ref = 13.000 Hz): the 14.9935 Hz interference should sit at +1.99 Hz offset.
Coherent one-sided line fit on each lock-in's complex output (X + iY, Y from P if needed) and LS on gate currents."""
import json, glob, gzip, io, os, sys, numpy as np
from scipy.signal import lombscargle
from scipy.ndimage import median_filter
H = lambda f, tau: (1 + (2 * np.pi * f * tau) ** 2) ** -2
res = []
for p in sorted(glob.glob('/home/zack/sharpelab/measurement-env/hera/docs/notes/2026-06-*-QC0426-session*/data/*/metadata.json')):
    try: d = json.load(open(p))
    except Exception: continue
    cols = d.get('columns'); f = os.path.join(os.path.dirname(p), 'data.tsv.gz')
    if not cols or not os.path.exists(f) or 'time' not in cols: continue
    X = np.loadtxt(io.StringIO(gzip.decompress(open(f, 'rb').read()).decode()), delimiter='\t', ndmin=2)
    if X.shape[0] < 80: continue
    t = X[:, cols.index('time')]; o = np.argsort(t); X = X[o]; t = t[o] - t[o][0]
    ins = d.get('instruments', {}); mc = d.get('measurement_config', {}) or {}
    tag = p.split('/')[-4][5:10] + p.split('/')[-4][26:] + ' r' + p.split('/')[-2]
    s = f"{tag:14s} n={X.shape[0]} dt={np.median(np.diff(t)):.2f}: "
    for nm in ('sr0', 'sr1', 'sr2', 'sr3'):
        if nm + '_X' not in cols: continue
        x = X[:, cols.index(nm + '_X')]
        if nm + '_Y' in cols: y = X[:, cols.index(nm + '_Y')]
        elif nm + '_P' in cols: y = x * np.tan(np.deg2rad(X[:, cols.index(nm + '_P')]))
        else: continue
        pp = ins.get(nm, {}).get('snapshot', {}).get('parameters', {})
        tau = pp.get('time_constant', {}).get('value'); fr = pp.get('frequency', {}).get('value') or 13.0
        z = x + 1j * y
        w = max(5, int(20 / max(np.median(np.diff(t)), 1e-3)) | 1)
        z = z - (median_filter(z.real, w, mode='nearest') + 1j * median_filter(z.imag, w, mode='nearest'))
        ff = np.arange(-3, 3, 0.0005)
        P = np.abs(np.exp(-2j * np.pi * ff[:, None] * t[None, :]) @ z) / z.size
        fexp = 14.9935 - 13.0
        k = np.argmax(np.where(np.abs(ff - fexp) < 0.02, P, 0)); km = np.argmax(np.where(np.abs(ff + fexp) < 0.02, P, 0))
        med = np.median(P)
        kk = np.argmax(P)
        s += f"| {nm} tau {tau}: @{ff[k]:+.4f} {P[k]:.2e} (x{P[k]/med:.0f}; mirror x{P[km]/med:.0f}) top {ff[kk]:+.3f} x{P[kk]/med:.0f}"
        if nm == 'sr0' and tau:
            gain = abs(mc.get('sr0_gain', 1e6) or 1e6)
            s += f" -> i_n = {P[k]/gain/H(fexp, tau)*1e12:.0f} pA"
        res.append(dict(run=tag, ch=nm, tau=tau, f=float(ff[k]), amp=float(P[k]), snr=float(P[k] / med), mirror=float(P[km] / med), top=float(ff[kk]), top_snr=float(P[kk] / med)))
    for gc in [c for c in cols if c.endswith('_curr')]:
        y = X[:, cols.index(gc)]; y = y - median_filter(y, 15, mode='nearest')
        fg = np.arange(14.9, 15.1, 0.0005)
        A = np.sqrt(4 * lombscargle(t, y - y.mean(), 2 * np.pi * fg, normalize=False) / y.size)
        fb = np.arange(0.05, 20, 0.002); Ab = np.sqrt(4 * lombscargle(t, y - y.mean(), 2 * np.pi * fb, normalize=False) / y.size)
        s += f" | {gc} 15Hz: {fg[np.argmax(A)]:.4f} {A.max()*1e12:.1f} pA (x{A.max()/np.median(Ab):.0f})"
    print(s, flush=True)
json.dump(res, open('qcline.json', 'w'), indent=1)
