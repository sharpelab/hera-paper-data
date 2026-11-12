import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

for rid, n in [(6, 3.2), (7, -1.2)]:
    run = open_run(f'data/{rid}')
    b = run.col('magnet_field')
    r = run.col('sr1_X') / 1e-8
    order = np.argsort(b)
    b, r = b[order], r[order]
    print(f'RUN {rid} n={n:+.2f} F_L={float(luttinger_frequency(abs(n))):.2f} T; R range {r.min():.1f}..{r.max():.1f} ohm; T {run.col("T_sample").min():.3f}..{run.col("T_sample").max():.3f} K')
    for lo in [0.3, 1.0, 1.5, 2.0]:
        try:
            on=sdh_onset(r,b,b_lo=lo,r_full_scale=5000)
            print('onset',lo,on.summary())
        except Exception as e:
            print('onset',lo,type(e).__name__,str(e)[:300])
    for cutoff in [1.5,2,2.5,3,4]:
        for deg in [3,5]:
            try:
                f,s=sdh_fft(r[:,None],b,b_range=(cutoff,10),bg_degree=deg,log=False,nfft=4096)
                a=s[0]
                pk,_=find_peaks(a,prominence=np.max(a)*0.06)
                pk=sorted([j for j in pk if 2<f[j]<55],key=lambda j:a[j],reverse=True)[:8]
                print('fft',cutoff,deg,[(round(float(f[j]),2),round(float(a[j]/np.max(a)),3)) for j in pk])
            except Exception as e: print('fft fail',cutoff,deg,type(e).__name__,str(e)[:120])
