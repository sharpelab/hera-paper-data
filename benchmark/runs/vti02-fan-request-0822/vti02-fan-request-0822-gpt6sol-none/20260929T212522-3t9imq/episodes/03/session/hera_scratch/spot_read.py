from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError

for rid in (6, 7):
    r = open_run(Path('data') / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    b = r.col('magnet_field')
    i = r.col('sr0_X') / ch['sr0'].gain
    v = r.col('sr1_X') / ch['sr1'].gain
    rr = np.abs(v / i)
    print(f'RUN {rid}: rows={r.rows}, interrupted={r.interrupted}, B={b[0]:.3f}->{b[-1]:.3f}, R={rr.min():.1f}..{rr.max():.1f} ohm, I={i.min()*1e9:.3f}..{i.max()*1e9:.3f} nA, T={r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    for g in ('k_2400_tg_curr', 'k_2400_bg_curr'):
        x = r.col(g)
        print(f'  {g}: median={np.median(x)*1e12:.1f} pA, range={x.min()*1e12:.1f}..{x.max()*1e12:.1f} pA')
    for lo, hi in ((2,10), (3,10), (4,10), (5,10)):
        if b.max()<hi: continue
        try:
            f, spec = sdh_fft(rr[:,None], b, b_range=(lo,hi), bg_degree=3, log=False, nfft=2048)
            y=spec[0]
            p,_=find_peaks(y)
            p=[k for k in p if 2<f[k]<70]
            p=sorted(p,key=lambda k:y[k],reverse=True)[:5]
            print(f'  FFT {lo}-{hi} T:', [(round(f[k],2),round(y[k],2)) for k in p])
        except Exception as e: print(f'  FFT {lo}-{hi} ERROR {e}')
    try:
        onset=sdh_onset(rr,b,b_lo=0.3,b_hi=10,r_full_scale=5000,bg_degree=3)
        print(onset.summary())
    except SdhOnsetError as e: print('  ONSET ERROR',e)
