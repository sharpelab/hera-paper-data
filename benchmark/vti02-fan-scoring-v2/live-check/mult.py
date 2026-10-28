import numpy as np, sys
sys.path.insert(0, '.')
from load import load
for nm in ['0822-r8', '0825-r8', '0821-r8']:
    d = load(nm); B = d['B']; o = np.argsort(B)[:12]
    for lab, Z in (('V', d['g']('sr1_X')), ('R=V/Imeas', d['R'] * np.median(d['I']))):
        Zs = Z[o]  # rows ascending B
        dd = np.diff(Zs, axis=0)  # row to row
        dd = dd - np.median(dd, axis=1, keepdims=True)
        s = 1.4826 * np.median(np.abs(dd), axis=0) / np.sqrt(2)
        m = np.abs(Zs).mean(0)
        c = np.corrcoef(m, s)[0, 1]; k = np.polyfit(m, s, 1)
        print(f"{nm} {lab:10s} B {B[o].min():.2f}-{B[o].max():.2f}: col sigma med {np.median(s)*1e9:.1f} nV; corr(sigma, |V|) {c:+.2f}; fit sigma = {k[1]*1e9:.1f} nV + {k[0]*100:.2f}% x |V| ; |V| range {m.min()*1e9:.0f}-{m.max()*1e9:.0f} nV")
    # current fluctuations
    I = d['I'][o]; di = np.diff(I, axis=0); print('   sr0 current row-to-row rel sigma %.2e' % (1.4826*np.median(np.abs(di - np.median(di)))/np.sqrt(2)/np.median(I)))
