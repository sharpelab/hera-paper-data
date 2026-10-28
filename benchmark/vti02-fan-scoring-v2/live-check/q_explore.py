import numpy as np, sys
sys.path.insert(0, '.')
from load import load
for nm in ['0821-r8','0822-r8','0825-r8','0824-r4']:
    d = load(nm)
    for ch in ['sr1', 'sr0']:
        x = d['g'](ch+'_X').ravel(); s = d['lk'][ch]['sensitivity']
        u = np.unique(x); du = np.diff(u)
        q = du[du > 0].min()
        # candidate LSB = sens/ K
        print(nm, ch, 'sens', s, 'max|x|/s %.3f' % (np.abs(x).max()/s), 'nuniq', u.size, 'of', x.size,
              'min step %.4g' % q, 'sens/minstep %.1f' % (s/q), 'p5 step %.4g' % np.percentile(du, 5))
        r = x / (s/30000); print('   residual from sens/30000 grid:', np.abs(r - np.round(r)).max().round(3), ' from sens/16777.216:', np.abs(x/(s/16777.216) - np.round(x/(s/16777.216))).max().round(3), ' sample', x[:6])
