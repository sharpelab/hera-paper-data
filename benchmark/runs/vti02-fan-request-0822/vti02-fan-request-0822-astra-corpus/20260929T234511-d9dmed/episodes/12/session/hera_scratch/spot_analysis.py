from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft
out={}
for rid,n in [(6,3.2),(7,-1.2)]:
    run=open_run(Path('data')/str(rid))
    fig=plot_raw(run); plt.savefig(f'hera_scratch/spot_{rid}_raw.png'); plt.show()
    ch=resolve_channels(run.meta); cur=current_channel(ch); v=next(c for c in ch if c.cid=='sr1')
    I=run.col(cur.col)/cur.gain; R=(run.col(v.col)/v.gain)/I; B=run.col('magnet_field')
    order=np.argsort(B); B,R=B[order],R[order]
    on=sdh_onset(R,B,r_full_scale=5000)
    print(f'RUN {rid} n={n}:',on.summary())
    print('R range',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'T',run.col('T_sample').min(),run.col('T_sample').max())
    print('gate max pA',*[np.max(np.abs(run.col(c)))*1e12 for c in ['k_2400_tg_curr','k_2400_bg_curr']])
    fig,ax=plt.subplots(1,2,figsize=(12,4)); ax[0].plot(B,R); ax[0].axvline(on.onset_b,color='r'); ax[0].set(xlabel='B (T)',ylabel='Rxx (Ohm)',title=f'Run {rid}: raw signed Rxx')
    peaks={}
    for lo in [on.onset_b,1.,1.5,2.]:
        if lo>=9: continue
        for deg in [3,5]:
            f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,log=False,nfft=4096)
            pk,_=find_peaks(sp[0]); pk=[p for p in pk if 2<f[p]<60]; pk=sorted(pk,key=lambda p:-sp[0,p])[:6]
            peaks[f'{lo:.3f}/{deg}']=[round(float(f[p]),2) for p in pk]
            ax[1].plot(f,sp[0]/sp[0].max(),label=f'B>{lo:.2f}, deg {deg}')
    ax[1].axvline(10.33916924*abs(n),color='k',ls='--',label='F_L scale 1'); ax[1].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT'); ax[1].legend(fontsize=6)
    fig.tight_layout(); fig.savefig(f'hera_scratch/spot_{rid}_fft.png'); plt.show()
    print('FFT peak candidates:',peaks)
    out[str(rid)]={'onset':on.onset_b,'summary':on.summary(),'peaks':peaks}
json.dump(out,open('hera_scratch/spot_results.json','w'),indent=2)
g=open_run('data/5'); t=g.col('time'); dt=np.diff(t); idx=np.arange(len(dt)); intra=dt[(idx+1)%66!=0]; turns=dt[(idx+1)%66==0]
print('run5 timing intra median/mean',np.median(intra),np.mean(intra),'row-turn median',np.median(turns),'total',g.meta['end_time']-g.meta['start_time'])
