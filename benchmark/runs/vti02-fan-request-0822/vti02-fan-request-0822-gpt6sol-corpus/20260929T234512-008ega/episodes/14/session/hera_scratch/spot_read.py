from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, summarize_run

for rid in (6, 7):
    r = open_run(Path('data') / str(rid))
    c = {x.cid:x for x in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / c['sr0'].gain
    R = (r.col('sr1_X') / c['sr1'].gain) / I
    print('\nRUN',rid, summarize_run(r))
    print('B', B[0], B[-1], 'R',np.nanmin(R),np.nanmax(R),'I_nA',np.nanmin(I)*1e9,np.nanmax(I)*1e9)
    print('T',np.nanmin(r.col('T_sample')),np.nanmax(r.col('T_sample')))
    print('Igate_pA',[(k,np.nanmin(r.col(k))*1e12,np.nanmax(r.col(k))*1e12) for k in ('k_2400_tg_curr','k_2400_bg_curr')])
    try:
        on=sdh_onset(R,B,r_full_scale=5000.)
        print(on.summary())
        lo=on.onset_b
    except Exception as e:
        print('ONSET ERROR',repr(e));lo=2.0
    for cutoff in (max(lo,1.5),max(lo,2.0),max(lo,3.0)):
        try:
            f,s=sdh_fft(R[:,None],B,b_range=(cutoff,10),bg_degree=5)
            y=s[0]; floor=np.median(y[f>3]); inds,_=find_peaks(y,prominence=floor*2)
            inds=sorted((i for i in inds if f[i]>3),key=lambda i:-y[i])[:8]
            print('FFT',cutoff,'dF',f[1]-f[0],[(round(f[i],2),round(y[i]/floor,1)) for i in inds])
        except Exception as e:print('FFT ERROR',repr(e))
