from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_fft, sdh_onset
for rid in (6,7):
    r=open_run(Path('data')/str(rid))
    plot_raw(r); plt.show()
    ch={c.cid:c for c in resolve_channels(r.meta)}
    I=r.col('sr0_X')/ch['sr0'].gain
    R=r.col('sr1_X')/ch['sr1'].gain/I; B=r.col('magnet_field')
    print(f'Run {rid}: complete={r.complete}, interrupted={r.interrupted}, elapsed={(r.meta["end_time"]-r.meta["start_time"])/60:.1f} min')
    print('I_drain nA min/median/max:',np.percentile(I*1e9,[0,50,100]),'Rxx range Ohm:',R.min(),R.max())
    print('T range K:',r.col('T_sample').min(),r.col('T_sample').max())
    for key in ('k_2400_tg_curr','k_2400_bg_curr'):
        print(key,'pA min/median/max:',np.percentile(r.col(key)*1e12,[0,50,100]))
    print(sdh_onset(R,B,r_full_scale=5000).summary())
    fig,axs=plt.subplots(1,2,figsize=(11,4))
    axs[0].plot(B,R); axs[0].set(xlim=(0,2),xlabel='B (T)',ylabel='Signed Rxx (Ohm)',title='Raw low-field detail')
    for degree in (3,5):
        for lo in (1.0,1.5,2.0):
            f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),nfft=4096,bg_degree=degree,log=False)
            p,_=find_peaks(sp[0]); p=sorted([j for j in p if 3<f[j]<60],key=lambda j:sp[0,j],reverse=True)[:4]
            print('FFT',rid,'Blo',lo,'degree',degree,'peaks T:',np.round(f[p],2))
            axs[1].plot(f,sp[0]/sp[0].max(),label=f'{lo:g} T, deg {degree}')
    axs[1].set(xlim=(0,60),xlabel='Frequency (T)',ylabel='Normalized FFT',title='Window/background stability')
    axs[1].legend(fontsize=7); fig.tight_layout(); plt.show()
print('Design read: electron run 6 has a stable ~7.3 T comb (~14.7,22.2,29.5 T). These may include harmonics; no pocket count yet. Run 7 has window-dependent nearby low tones and limited accessible hole density. The default electron onset is censored and sub-1 T sampling undersamples F_L: establish onset with a short finely sampled check before pricing the fan. No stacking verdict from these traces alone.')
