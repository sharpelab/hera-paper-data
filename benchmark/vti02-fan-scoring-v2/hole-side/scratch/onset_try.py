import numpy as np, sys, warnings
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from hera.analysis import sdh_onset
tr = {t['id']: t for t in load_all(include_ramp=False)}
for k, bhis in [('0822-r7', (10, 5, 4, 3)), ('0824-r5-c0', (6.01, 4)), ('0825-r7-c0', (6.0, 5))]:
    t = tr[k]
    for bhi in bhis:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            try:
                o = sdh_onset(t['R'], t['B'], b_hi=bhi, b_lo=0.3, f_min=1.0, r_full_scale=t['sens_V'] / (t['I_nA'] * 1e-9))
            except Exception as e:
                print(k, bhi, 'ERR', str(e)[:300]); continue
        print(f"{k} b_hi {bhi}: onset {o.onset_b:.2f} T from {o.onset_freq:.2f} T; record lo {o.b_lo_record:.2f}; sigma {o.noise_sigma:.2f}")
        for tt in o.tones:
            print(f"    F {tt.freq:6.2f} contrast {tt.contrast:6.1f} onset {tt.onset_b:5.2f} cens {tt.censored} marg {tt.marginal} nearres {tt.near_residual} revived {tt.revived} harm_of {tt.harmonic_of} nper {tt.n_periods:.1f}")
        for f, r in o.untracked: print('    untracked', round(f, 2), r[:100])
        for ww in w: print('    W:', str(ww.message)[:160])
