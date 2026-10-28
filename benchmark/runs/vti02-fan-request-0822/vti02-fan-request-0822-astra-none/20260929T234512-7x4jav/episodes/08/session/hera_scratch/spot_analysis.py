from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, summarize_run, sdh_fft, sdh_onset
root = Path.cwd()
fig, axes = plt.subplots(3, 2, figsize=(12, 9), sharex='col')
traces=[]
report=[]
for col, rid in enumerate((6, 7)):
    r=open_run(root/'data'/str(rid)); print(summarize_run(r))
    ch={c.cid:c for c in resolve_channels(r.meta)}
    b=r.col('magnet_field'); current=r.col('sr0_X')/ch['sr0'].gain
    resistance=r.col('sr1_X')/ch['sr1'].gain/current
    axes[0,col].plot(b, r.col('sr1_X')*1e6); axes[0,col].set_ylabel('Raw sr1 X (uV)')
    axes[1,col].plot(b, current*1e9); axes[1,col].set_ylabel('Drain I (nA)')
    for g in ('k_2400_tg_curr','k_2400_bg_curr'): axes[2,col].plot(b,r.col(g)*1e12,label=g)
    axes[2,col].legend(fontsize=7); axes[2,col].set_ylabel('Gate I (pA)'); axes[2,col].set_xlabel('B (T)')
    axes[0,col].set_title(f'Raw run {rid}')
    order=np.argsort(b); b=b[order]; resistance=resistance[order]
    traces.append((rid,b,resistance))
    dt=np.diff(r.col('time')); db=np.abs(np.diff(r.col('magnet_field')))
    print('run',rid,'wall min',(r.meta['end_time']-r.meta['start_time'])/60,'median dt',np.median(dt),'median overhead beyond 0.137T/min',np.median(dt-db*438))
    print('R signed range',resistance.min(),resistance.max(),'I nA',current.min()*1e9,current.max()*1e9,'T',r.col('T_sample').min(),r.col('T_sample').max())
    print('phase sr1 quantiles',np.quantile(r.col('sr1_P'),[0,.1,.5,.9,1]))
fig.tight_layout(); fig.savefig(root/'hera_scratch/spots_raw.png',dpi=130); plt.show()
fig,axes=plt.subplots(2,2,figsize=(12,7))
for col,(rid,b,resistance) in enumerate(traces):
    axes[0,col].plot(b,resistance); axes[0,col].set_xlabel('B (T)'); axes[0,col].set_ylabel('Signed Vxx/I (Ohm)'); axes[0,col].set_title(f'Run {rid}')
    for blo in (1.0,1.5,2.0):
        f,a=sdh_fft(resistance[:,None],b,b_range=(blo,10),log=False,nfft=4096,bg_degree=3)
        a=a[0]; axes[1,col].plot(f,a/a.max(),label=f'{blo}-10 T')
        pk,_=find_peaks(a); pk=sorted((p for p in pk if 3<f[p]<65),key=lambda p:-a[p])[:5]
        print('run',rid,'window',blo,'peaks',[(round(f[p],2),round(a[p]/a.max(),2)) for p in pk])
    axes[1,col].set_xlim(0,65); axes[1,col].legend(); axes[1,col].set_xlabel('F (T)'); axes[1,col].set_ylabel('Normalized FFT, linear signed R')
    try:
        onset=sdh_onset(resistance,b,b_lo=0.7,r_full_scale=5000,bg_degree=3)
        print('run',rid,onset.summary())
    except ValueError as exc: print('onset unresolved',rid,str(exc))
fig.tight_layout(); fig.savefig(root/'hera_scratch/spots_analysis.png',dpi=130); plt.show()
r=open_run(root/'data/5'); dt=np.diff(r.col('time')); within=np.arange(len(dt))%66!=65
print('run5 point dt quantiles',np.quantile(dt[within],[.1,.5,.9]),'turnaround',np.median(dt[~within]),'wall min',(r.meta['end_time']-r.meta['start_time'])/60)
