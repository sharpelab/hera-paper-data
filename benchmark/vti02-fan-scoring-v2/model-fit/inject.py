"""Injection test of the extractor: synthetic tones on each fan's real B grid + that column's smooth background
+ white noise at the measured sigma_R; F_light = p_true * F_L. Measures extraction bias in the partition.
Assumptions: envelopes exp(-B_t/B) with B_t = 1.5 (light), 4 (heavy), 8 T (sum, breakdown-like); amplitudes set
so the median SNRs match the data's medians; light 2nd harmonic at 0.3x."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '.')
from runs import load_run
import extract as X

rng = np.random.default_rng(1)
SIGR = {'0821': 3.4, '0822': 2.2, '0825': 0.5}
FRAME = {'0821': (0.927, 0.0), '0822': (0.8625, -0.100), '0825': (0.9496, 0.0)}
raw = pd.read_csv('columns_raw.csv', dtype={'session': str})
rows = []
for sess, run in (('0825', 8), ('0822', 8), ('0821', 8)):
    cols = load_run(sess, run, 'fan')
    s, n0 = FRAME[sess]
    med = raw[(raw.session == sess) & (raw.run == run)]
    for rep in range(3):
        syn = []
        for c in cols:
            B = c['B']; FL = X.FLN * s * (c['n_frame'] - n0); n_act = FL / X.FLN
            p = 0.0394 * n_act + 0.1235
            Fl, Fh = p * FL, (1 - p) * FL
            bg = np.polyval(np.polyfit(B, c['R'], 3), B)
            ph = rng.uniform(0, 2 * np.pi, 4)
            sig = SIGR[sess]
            amp = {'0825': (6, 8, 10), '0822': (5, 6, 8), '0821': (8, 10, 14)}[sess]
            y = (amp[0] * np.exp(-1.5 / B) * (np.cos(2 * np.pi * Fl / B + ph[0]) + 0.3 * np.cos(4 * np.pi * Fl / B + ph[3]))
                 + amp[1] * np.exp(-4 / B) * np.cos(2 * np.pi * Fh / B + ph[1])
                 + amp[2] * np.exp(-8 / B) * np.cos(2 * np.pi * FL / B + ph[2]) + bg + rng.normal(0, sig, B.size))
            cc = dict(c); cc['R'] = y; cc['p_true'] = p; cc['FL_true'] = FL
            syn.append(cc)
        specs = X.spectra(syn)
        m = X.measure(specs, s, n0)
        m['p_true'] = np.repeat([c['p_true'] for c in syn], [sum(1 for x in specs if x[0] is c) for c in syn])
        m['rep'] = rep
        rows.append(m)
R = pd.concat(rows)
R['det_light'] = (R.snr_light >= 4) & (R.F_light >= 0.75 * R.dF)
g = R[R.det_light].groupby(['session', 'rep', 'col']).agg(n=('n_frame', 'first'), Fl=('F_light', 'median'), FLp=('FL_pred', 'first'),
                                                          p_true=('p_true', 'first'), Fh=('F_heavy', 'median'),
                                                          snr=('snr_light', 'median')).reset_index()
g['dp_light'] = g.Fl / g.FLp - g.p_true
g['dp_heavy'] = (1 - g.Fh / g.FLp) - g.p_true
g['FL_bin'] = pd.cut(g.FLp, [0, 14, 18, 22, 26, 40])
print(g.groupby(['session', 'FL_bin'], observed=True).agg(n=('dp_light', 'size'), dp_light=('dp_light', 'mean'), sd_light=('dp_light', 'std'),
                                                           dp_heavy=('dp_heavy', 'mean'), sd_heavy=('dp_heavy', 'std'), snr=('snr', 'median')).round(4).to_string())
g.to_csv('inject_bias.csv', index=False)
