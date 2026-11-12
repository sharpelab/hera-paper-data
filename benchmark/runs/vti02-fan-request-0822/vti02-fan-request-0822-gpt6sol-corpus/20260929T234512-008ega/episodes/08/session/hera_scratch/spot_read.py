import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft

for fid, n in [(6, 3.2), (7, -1.2)]:
    r = open_run(f'data/{fid}')
    b = r.col('magnet_field')
    v = r.col('sr1_X')
    rr = v / 1e-8
    print('\nrun', fid, 'n', n, 'B', b.min(), b.max(), 'R', np.min(rr), np.max(rr), 'T', (np.min(r.col('T_sample')), np.max(r.col('T_sample'))))
    print('leak med/max pA', *[(np.median(np.abs(r.col(c)))*1e12, np.max(np.abs(r.col(c)))*1e12) for c in ('k_2400_tg_curr','k_2400_bg_curr')])
    try:
        o=sdh_onset(rr,b,r_full_scale=5000,b_lo=1.0)
        print('onset',o.summary())
    except Exception as e:
        print('onset ERROR', type(e).__name__, str(e))
    for lo in [1.5,2.0,2.5,3.0,3.5,4.0]:
        try:
            f,s=sdh_fft(rr[:,None],b,b_range=(lo,10),log=False)
            y=s[0]
            ps,_=find_peaks(y,prominence=np.max(y)*.04)
            top=sorted(ps,key=lambda i:y[i],reverse=True)[:8]
            print('FFT',lo,[(round(f[i],2),round(y[i]/np.max(y),3)) for i in top])
        except Exception as e: print('fft err',lo,str(e))
