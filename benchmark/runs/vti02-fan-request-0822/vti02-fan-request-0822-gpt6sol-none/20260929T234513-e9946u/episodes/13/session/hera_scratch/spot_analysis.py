from pathlib import Path
import numpy as np
from hera.analysis import open_run, summarize_run, resolve_channels, current_channel, sdh_fft, sdh_onset

for rid in (6, 7):
    r = open_run(Path('data') / str(rid))
    print('\nRUN', rid, summarize_run(r))
    c = resolve_channels(r.meta)
    print('channels', [(x.cid, x.gain, x.is_current) for x in c])
    cur = current_channel(c)
    b = r.col('magnet_field')
    i = r.col(cur.col) / cur.gain
    v = r.col('sr1_X')
    rr = np.abs(v/i)
    print('B', b[0], b[-1], 'rows', len(b), 'I nA', np.quantile(i*1e9,[0,.5,1]), 'R Ohm',np.quantile(rr,[0,.1,.5,.9,1]), 'V uV',np.quantile(np.abs(v)*1e6,[0,.5,.99,1]))
    k = np.argsort(b)
    b,rr = b[k],rr[k]
    try:
        o=sdh_onset(rr,b,b_hi=9.8,b_lo=.5,r_full_scale=5000)
        print(o.summary())
    except Exception as e: print('onset error',repr(e))
    for lo in (2,3,4):
        try:
            f,s=sdh_fft(rr[:,None],b,b_range=(lo,9.8),log=False)
            inds=np.argsort(s[0][(f>2)&(f<60)])[-5:]
            print('FFT',lo,sorted(zip(f[(f>2)&(f<60)][inds],s[0][(f>2)&(f<60)][inds]),key=lambda z:z[1],reverse=True))
        except Exception as e: print('FFT error',repr(e))
