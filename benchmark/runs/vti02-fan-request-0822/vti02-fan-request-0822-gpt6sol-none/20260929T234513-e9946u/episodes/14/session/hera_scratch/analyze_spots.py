from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency

fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for j, rid in enumerate((6, 7)):
    r = open_run(Path('data') / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = np.abs((r.col('sr1_X') / ch['sr1'].gain) / I)
    it = r.col('k_2400_tg_curr')
    ib = r.col('k_2400_bg_curr')
    print(summarize_run(r))
    print(f'run {rid}: R={R.min():.1f}..{R.max():.1f} Ω, current={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA, TG={it.min()*1e12:.0f}..{it.max()*1e12:.0f} pA, BG={ib.min()*1e12:.0f}..{ib.max()*1e12:.0f} pA, T={r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    ax[0,j].plot(B,R,lw=.8); ax[0,j].set(xlabel='B (T)',ylabel='|Rxx| (Ω)',title=f'run {rid} raw')
    ax[1,j].plot(B,it*1e12,label='TG'); ax[1,j].plot(B,ib*1e12,label='BG'); ax[1,j].legend(); ax[1,j].set(xlabel='B (T)',ylabel='gate current (pA)')
    order=np.argsort(B)
    B,R=B[order],R[order]
    for lo in (1.5,2.0,3.0,4.0):
        try:
            onset=sdh_onset(R,B,b_lo=lo,b_hi=9.8,r_full_scale=5000)
            print(f'run {rid} onset with b_lo {lo}: {onset.summary()}')
            break
        except ValueError as e: print(f'run {rid} onset failed at {lo}: {e}')
    for lo in (2,3,4):
        try:
            f,S=sdh_fft(R[:,None],B,b_range=(lo,9.8),nfft=2048,bg_degree=5)
            spec=S[0]; pk,_=find_peaks(spec,prominence=spec.max()*.07)
            pk=sorted([p for p in pk if 2<f[p]<60],key=lambda p:spec[p],reverse=True)[:8]
            print(f'run {rid} FFT {lo}..9.8: '+', '.join(f'{f[p]:.2f}T({spec[p]/spec.max():.2f})' for p in pk))
        except ValueError as e: print(f'run {rid} FFT failed: {e}')
fig.tight_layout(); fig.savefig('hera_scratch/spots_raw.png',dpi=130)
