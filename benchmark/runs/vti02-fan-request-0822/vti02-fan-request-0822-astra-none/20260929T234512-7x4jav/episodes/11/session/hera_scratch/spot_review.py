from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset

fig, ax = plt.subplots(2, 3, figsize=(14, 7))
records = []
for row, rid in enumerate((6, 7)):
    r = open_run(Path('data') / str(rid))
    ch = {c.cid:c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field'); I = r.col('sr0_X')/ch['sr0'].gain
    R = (r.col('sr1_X')/ch['sr1'].gain)/I
    records.append((rid, B, R))
    ax[row,0].plot(B, r.col('sr1_X')*1e6, lw=.7)
    ax[row,0].set(xlabel='B (T)', ylabel='raw sr1 X (uV)', title=f'Run {rid}, B_1-B_2')
    ax[row,1].plot(B,I*1e9,label='drain'); ax[row,1].set(xlabel='B (T)',ylabel='drain current (nA)')
    ax[row,2].plot(B,r.col('k_2400_tg_curr')*1e12,label='TG',lw=.6)
    ax[row,2].plot(B,r.col('k_2400_bg_curr')*1e12,label='BG',lw=.6)
    ax[row,2].set(xlabel='B (T)',ylabel='gate current (pA)'); ax[row,2].legend()
    print(f'Run {rid}: {r.rows} points, interrupted={r.interrupted}, R signed {R.min():.1f}..{R.max():.1f} Ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; T {np.min(r.col("T_sample")):.3f}..{np.max(r.col("T_sample")):.3f} K')
fig.tight_layout(); fig.savefig('hera_scratch/spot_raw.png',dpi=140); plt.show()
fig,ax=plt.subplots(2,2,figsize=(12,8))
for row,(rid,B,R) in enumerate(records):
    ax[row,0].plot(B,R,lw=.7); ax[row,0].set(xlabel='B (T)',ylabel='signed V/I (Ohm)',title=f'Run {rid}: no absolute-value rectification')
    for lo in (1.5,2.,3.):
        f,p=sdh_fft(R[:,None],B,b_range=(lo,10),log=False,nfft=2048,bg_degree=3)
        spec=p[0]; sel=(f>3)&(f<60)
        pk,_=find_peaks(spec)
        pk=sorted([k for k in pk if 3<f[k]<60],key=lambda k:-spec[k])[:5]
        print(f'Run {rid} signed FFT B={lo}..10 T: nominal resolution {1/(1/lo-.1):.2f} T; peak frequencies '+str([(round(f[k],2),round(spec[k],1)) for k in pk]))
        ax[row,1].plot(f[sel],spec[sel]/max(spec[sel]),label=f'{lo}..10 T')
    try:
        onset=sdh_onset(R,B,b_lo=1.,r_full_scale=5000,bg_degree=3)
        print(f'Run {rid}: '+onset.summary())
    except ValueError as exc: print(f'Run {rid}: onset inconclusive: {exc}')
    ax[row,1].set(xlabel='F (T)',ylabel='normalized FFT amplitude',title='Window dependence; peaks are not band assignments'); ax[row,1].legend()
fig.tight_layout(); fig.savefig('hera_scratch/spot_analysis.png',dpi=140); plt.show()
