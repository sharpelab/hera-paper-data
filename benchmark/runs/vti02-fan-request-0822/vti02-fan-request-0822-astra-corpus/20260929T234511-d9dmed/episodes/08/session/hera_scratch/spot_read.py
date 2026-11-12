from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft, SdhOnsetError, resolve_channels, current_channel
BASE = Path.cwd()
for rid in (6,7):
    r=open_run(BASE/'data'/str(rid))
    plot_raw(r); plt.savefig(BASE/'hera_scratch'/f'spot_{rid}_raw.png'); plt.show()
    ch=resolve_channels(r.meta); cur=current_channel(ch); v=next(c for c in ch if c.cid=='sr1')
    I=r.col(cur.col)/cur.gain; R=(r.col(v.col)/v.gain)/I; B=r.col('magnet_field')
    print('RUN',rid,'complete',r.complete,'seconds',r.meta['end_time']-r.meta['start_time'])
    for name, a in [('R',R),('I_nA',I*1e9),('T',r.col('T_sample')),('TG_pA',r.col('k_2400_tg_curr')*1e12),('BG_pA',r.col('k_2400_bg_curr')*1e12)]:
        print(name, np.percentile(a,[0,50,100]))
    print('time increment quantiles',np.percentile(np.diff(r.col('time')),[10,50,90]))
    try:
        on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
    except SdhOnsetError as e:
        print(type(e).__name__,str(e)); continue
    fig,axs=plt.subplots(1,2,figsize=(12,4))
    for t in on.tones:
        axs[0].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
    axs[0].axhline(5,color='k',ls=':');axs[0].set(xlabel='B (T)',ylabel='matched-filter SNR',yscale='log');axs[0].legend()
    for lo in [on.onset_b, max(1.5,on.onset_b),max(2.,on.onset_b)]:
        for deg in [3,5,7]:
            f,s=sdh_fft(R[:,None],B,b_range=(lo,10),log=False,bg_degree=deg,nfft=2048)
            pk,_=find_peaks(s[0]); pk=[p for p in pk if 3<f[p]<60]; pk=sorted(pk,key=lambda p:-s[0,p])[:5]
            print('FFT',rid,round(lo,3),deg,[(round(f[p],2),round(s[0,p],1)) for p in pk])
            axs[1].plot(f,s[0]/s[0].max(),label=f'{lo:.2f}-10T d{deg}',alpha=.6)
    axs[1].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT');axs[1].legend(fontsize=6)
    fig.suptitle(f'Run {rid}: positive-B only; no even-in-B symmetrization available')
    fig.tight_layout();plt.savefig(BASE/'hera_scratch'/f'spot_{rid}_fft.png');plt.show()
