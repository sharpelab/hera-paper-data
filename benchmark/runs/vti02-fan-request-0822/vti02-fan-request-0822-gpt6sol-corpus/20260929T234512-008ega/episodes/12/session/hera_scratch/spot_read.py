from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft

for rid in (6, 7):
    run = open_run(Path('data') / str(rid))
    channels = {c.cid: c for c in resolve_channels(run.meta)}
    B = run.col('magnet_field')
    I = run.col('sr0_X') / channels['sr0'].gain
    R = (run.col('sr1_X') / channels['sr1'].gain) / I
    Itg, Ibg = run.col('k_2400_tg_curr'), run.col('k_2400_bg_curr')
    print(f'RUN {rid} N={len(B)} duration={(run.meta["end_time"]-run.meta["start_time"])/60:.1f} min B={B.min():.2f}..{B.max():.2f} T')
    print(f'  R={np.percentile(R,[0,10,50,90,100])} Ω, I={np.percentile(I*1e9,[0,10,50,90,100])} nA')
    print(f'  TG={np.percentile(Itg*1e12,[0,50,100])} pA BG={np.percentile(Ibg*1e12,[0,50,100])} pA T={np.percentile(run.col("T_sample"),[0,50,100])} K')
    try:
        on = sdh_onset(np.abs(R), B, r_full_scale=5000)
        print(on.summary())
    except Exception as exc:
        print('ONSET ERROR:', type(exc).__name__, exc)
    for b_lo in (0.5, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0):
        if b_lo >= B.max(): continue
        f, a = sdh_fft(np.abs(R)[:,None],B,b_range=(b_lo,B.max()),nfft=4096,log=False)
        y=a[0]
        peaks,_=find_peaks(y)
        peaks=[p for p in peaks if 3<=f[p]<=60]
        peaks=sorted(peaks,key=lambda p:y[p],reverse=True)[:8]
        print(f'  FFT {b_lo:.1f}-{B.max():.0f} T δF={1/(1/b_lo-1/B.max()):.2f} T: '+', '.join(f'{f[p]:.2f}T/{y[p]:.1f}' for p in peaks))
