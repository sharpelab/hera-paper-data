import numpy as np, sys, pandas as pd
sys.path.insert(0, '.')
from load import load
from noise_q import load_qc, lsb
SIGV = {'0821-r8': 34e-9, '0822-r8': 22e-9, '0825-r8': 25e-9, '0824-r4': 37e-9, 'QC0426-0619-r4': 19e-9}
rows = []
for d in [load(nm) for nm in ['0821-r8', '0822-r8', '0825-r8', '0824-r4']] + [load_qc()]:
    for ch in (['sr1'] if d['name'] != 'QC0426-0619-r4' else ['sr1', 'sr2']):
        X = d['g'](ch + '_X'); s = d['lk'][ch]['sensitivity']; q = lsb(s); B = d['B']
        roi = B >= 2.0
        if d['name'] == '0824-r4': X = X[:, d['n'] > 0.6]
        Xr = X[roi]; clip = np.abs(Xr) >= 0.95 * s
        # flat runs of 3 along B (slow axis) excluding clipped
        flat3 = (np.diff(Xr, axis=0)[:-1] == 0) & (np.diff(Xr, axis=0)[1:] == 0) & ~clip[1:-1]
        zero = (np.diff(Xr, axis=0) == 0) & ~clip[1:] & ~clip[:-1]
        # oscillation rms per column: detrend deg-5 poly in B, rms
        osc = []
        Bs = B[roi]
        for j in range(Xr.shape[1]):
            y = Xr[:, j]; k = ~clip[:, j]
            if k.sum() > 8: osc.append(np.std(y[k] - np.polyval(np.polyfit(Bs[k], y[k], 5), Bs[k])))
        osc = np.array(osc)
        rows.append(dict(fan=d['name'], ch=ch, sens=s, lsb_nV=q * 1e9, sigV_nV=SIGV[d['name']] * 1e9, q_over_sigma=q / SIGV[d['name']],
                         zero_diff_unclipped=zero.mean(), flat3=flat3.mean(), clipped_roi=clip.mean(),
                         osc_rms_over_lsb_med=np.median(osc) / q, osc_rms_over_lsb_min=osc.min() / q, osc_rms_nV_med=np.median(osc) * 1e9))
df = pd.DataFrame(rows); pd.set_option('display.width', 250)
print(df.to_string(float_format=lambda v: f'{v:.3g}')); df.to_csv('quantization.csv', index=False)
