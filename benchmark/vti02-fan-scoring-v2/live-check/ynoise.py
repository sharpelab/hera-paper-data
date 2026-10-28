import numpy as np, sys
sys.path.insert(0, '.')
from load import load, FANS
from noise_q import sigma_d2, acf4, load_qc, lsb
out = []
for d in [load(nm) for nm in FANS] + [load_qc()]:
    cols = d.get('cols') or []
    for ch in (['sr1'] if d['name'] != 'QC0426-0619-r4' else ['sr1', 'sr2']):
        X = d['g'](ch + '_X')
        try: Y = d['g'](ch + '_Y')
        except Exception: Y = X * np.tan(np.deg2rad(d['g'](ch + '_P')))
        tau = d['lk'][ch]['time_constant']; dt = np.median(np.diff(d['t'], axis=1))
        rho, rho2 = acf4(dt / tau), acf4(2 * dt / tau); corr = np.sqrt(6 / (6 - 8 * rho + 2 * rho2))
        sel = slice(None)
        if d['name'] == '0824-r4': sel = d['n'] > 0.6   # e-side, away from CNP
        sy = sigma_d2(Y[:, sel]) * corr; sx = sigma_d2(X[:, sel]) * corr
        B = d['B']; o = np.argsort(B)
        I = np.median(np.abs(d['I']))
        q = [0, len(B)//4, len(B)//2, 3*len(B)//4, len(B)-1]
        print(d['name'], ch, 'I=%.1fnA tau=%.1f' % (I*1e9, tau), 'sigma_Y nV (B asc):', ' '.join(f"{B[o[i]]:.1f}T:{sy[o[i]]*1e9:.0f}" for i in q),
              '| med sigY %.1f nV = %.2f ohm' % (np.median(sy)*1e9, np.median(sy)/I), '| sigX lowB %.1f nV' % (np.median(sx[o[:max(4,len(B)//10)]])*1e9),
              '| Y/X median %.3f' % np.median(np.abs(Y)/np.maximum(np.abs(X),1e-12)))
        out.append((d['name'], ch, I, tau, np.median(sy)))
np.save('ynoise.npy', np.array(out, dtype=object), allow_pickle=True)
