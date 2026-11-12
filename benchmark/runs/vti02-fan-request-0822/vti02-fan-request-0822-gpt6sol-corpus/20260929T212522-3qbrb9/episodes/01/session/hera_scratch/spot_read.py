from hera.analysis import open_run, sdh_onset, sdh_fft
import numpy as np

for rid in (6, 7):
    run = open_run(f'data/{rid}')
    b = run.col('magnet_field')
    r = run.col('sr1_X') / (run.col('sr0_X') / -1e6)
    ix = np.argsort(b)
    b, r = b[ix], r[ix]
    print(f'RUN {rid}: B {b[0]:.3f}..{b[-1]:.3f}, R {r.min():.1f}..{r.max():.1f} ohm, median {np.median(r):.1f}')
    for bh in (8.0, 10.0):
        try:
            on = sdh_onset(r, b, b_hi=bh, b_lo=0.3, r_full_scale=5000)
            print('b_hi', bh, on.summary())
            for low in (on.onset_b, max(on.onset_b, 2.0), 2.5, 3.0):
                if low >= bh - 0.1: continue
                f, spec = sdh_fft(r[:,None], b, b_range=(low,bh), nfft=4096, bg_degree=5, log=False)
                yy=spec[0]
                from scipy.signal import find_peaks
                ids,_=find_peaks(yy)
                ids=[i for i in ids if 2<f[i]<55]
                ids=sorted(ids,key=lambda i: yy[i],reverse=True)[:7]
                print(' FFT', low, bh, [(round(f[i],2),round(float(yy[i]),2)) for i in ids])
        except Exception as exc:
            print(type(exc).__name__,str(exc)[:350])
