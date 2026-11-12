from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
base = Path.cwd()
results = {}
fig, axs = plt.subplots(2,3,figsize=(15,8))
for row, (rid,n) in enumerate([(6,3.2),(7,-1.2)]):
    r=open_run(base/'data'/str(rid))
    ch={c.cid:c for c in resolve_channels(r.meta)}
    I=r.col('sr0_X')/ch['sr0'].gain
    R=(r.col('sr1_X')/ch['sr1'].gain)/I
    B=r.col('magnet_field'); t=r.col('time')
    print(f'RUN {rid}: complete={r.complete}, interrupted={r.interrupted}, points={r.rows}, duration={np.ptp(t)/60:.2f} min, R={R.min():.2f}..{R.max():.2f} ohm, I={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA, T={r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    print('timing median', np.median(np.diff(t)), 'nonramp median',np.median(np.diff(t)-abs(np.diff(B))*7.3*60))
    for g in ['k_2400_tg_curr','k_2400_bg_curr']:
        print(g, np.quantile(r.col(g),[0,.5,1])*1e12,'pA')
    axs[row,0].plot(B,R,lw=.7); axs[row,0].set(xlabel='B (T)',ylabel='signed Rxx (ohm)',title=f'Run {rid}, n={n:+.1f}e12, raw TSV')
    try:
        on=sdh_onset(R,B,r_full_scale=5000)
        print(on.summary()); results[str(rid)]={'onset':on.onset_b,'onset_freq':on.onset_freq,'summary':on.summary()}
        for tone in on.tones:
            axs[row,1].plot(tone.b_centers,tone.snr,label=f'{tone.freq:.1f} T')
        axs[row,1].axhline(5,color='k',ls=':'); axs[row,1].legend(fontsize=7)
        axs[row,1].set(xlabel='B (T)',ylabel='matched-filter SNR',yscale='log',title='Computed per-tone onset')
        for cut,deg in [(on.onset_b,3),(on.onset_b,5),(max(on.onset_b,1.5),3),(max(on.onset_b,1.5),5)]:
            f,sp=sdh_fft(R[:,None],B,b_range=(cut,10),bg_degree=deg,log=False,nfft=2048)
            pk,_=find_peaks(sp[0]); pk=[i for i in pk if 3<f[i]<70]; pk=sorted(pk,key=lambda i:-sp[0,i])[:6]
            print('FFT',cut,deg,[(round(f[i],2),round(sp[0,i]/sp.max(),3)) for i in pk])
            axs[row,2].plot(f,sp[0]/sp.max(),label=f'B>{cut:.2f}, deg {deg}')
        axs[row,2].axvline(10.339*n if n>0 else -10.339*n,color='k',ls=':',label='nominal F_L')
        axs[row,2].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT',title='Detrend in B, signed R, Hann'); axs[row,2].legend(fontsize=7)
    except SdhOnsetError as e:
        print('SdhOnsetError:',e); results[str(rid)]={'error':str(e)}
fig.tight_layout(); fig.savefig(base/'hera_scratch/spot_checks.png',dpi=150); plt.show()
(base/'hera_scratch/spot_onsets.json').write_text(json.dumps(results,indent=2))
