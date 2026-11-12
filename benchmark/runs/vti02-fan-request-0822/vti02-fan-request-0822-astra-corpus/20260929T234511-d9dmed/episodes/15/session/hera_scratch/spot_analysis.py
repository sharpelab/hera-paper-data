from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft, summarize_run
ROOT = Path.cwd()
results={}
for rid,n in [(6,3.2),(7,-1.2)]:
    r=open_run(ROOT/'data'/str(rid))
    print(summarize_run(r))
    channels=resolve_channels(r.meta); ci=current_channel(channels); cv=next(c for c in channels if c.cid=='sr1')
    I=r.col(ci.col)/ci.gain; R=(r.col(cv.col)/cv.gain)/I; B=r.col('magnet_field')
    ix=np.argsort(B); B=B[ix]; R=R[ix]
    fig=plot_raw(r); plt.savefig(ROOT/f'hera_scratch/spot{rid}_raw.png',dpi=130); plt.close('all')
    print('QUALITY',rid,'R range',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'T',r.col('T_sample').min(),r.col('T_sample').max(),'leak pA',*[np.max(np.abs(r.col(c)))*1e12 for c in ['k_2400_tg_curr','k_2400_bg_curr']])
    on=sdh_onset(R,B,r_full_scale=50e-6/np.median(I))
    print(on.summary())
    print('TIMING',rid,(r.meta['end_time']-r.meta['start_time'])/60, 'median dt',np.median(np.diff(r.col('time'))))
    results[str(rid)]={'onset':float(on.onset_b),'summary':on.summary()}
    fig,axs=plt.subplots(2,2,figsize=(12,8)); axs[0,0].plot(B,R); axs[0,0].set(xlabel='B (T)',ylabel='Rxx (Ohm)',title=f'run {rid}: n={n}e12, D~0; raw')
    axs[0,1].plot(B,R); axs[0,1].set_xlim(0,3); axs[0,1].set_ylim(np.percentile(R[B<3],[1,99])); axs[0,1].axvline(on.onset_b,color='r')
    for cutoff in [on.onset_b,1.0,1.5,2.0]:
        for deg in [3,5]:
            f,sp=sdh_fft(R[:,None],B,b_range=(cutoff,10),bg_degree=deg,nfft=4096,log=False)
            peaks,_=find_peaks(sp[0]); peaks=[p for p in peaks if 2<f[p]<60]; peaks=sorted(peaks,key=lambda p: -sp[0,p])[:5]
            print('FFT',rid,'window',cutoff,10,'deg',deg,[(round(f[p],2),round(sp[0,p],2)) for p in peaks])
            axs[1,0 if deg==3 else 1].plot(f,sp[0],label=f'B>{cutoff:.2f}')
    for ax in axs[1]: ax.set(xlim=(0,60),xlabel='F (T)',ylabel='FFT amplitude'); ax.legend(); ax.axvline(10.33916924*abs(n),color='k',ls=':')
    fig.tight_layout(); fig.savefig(ROOT/f'hera_scratch/spot{rid}_analysis.png',dpi=130); plt.close(fig)
json.dump(results,open(ROOT/'hera_scratch/spot_summary.json','w'),indent=2)
