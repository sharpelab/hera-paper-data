import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft
from scipy.signal import find_peaks
for rid in (6,7):
    run=open_run(f'data/{rid}')
    print('RUN',rid,summarize_run(run))
    print('cols',run.cols)
    B=run.col('magnet_field')
    I=run.col('sr0_X')/-1e6
    R=(run.col('sr1_X'))/I
    R=np.abs(R)
    print('raw', 'B',B.min(),B.max(),'R',np.min(R),np.median(R),np.max(R),'I_nA',np.min(I)*1e9,np.max(I)*1e9,'T',np.min(run.col('T_sample')),np.max(run.col('T_sample')),'Itg_pA',np.min(run.col('k_2400_tg_curr'))*1e12,np.max(run.col('k_2400_tg_curr'))*1e12,'Ibg_pA',np.min(run.col('k_2400_bg_curr'))*1e12,np.max(run.col('k_2400_bg_curr'))*1e12)
    fig,ax=plt.subplots(2,1,figsize=(10,7),sharex=True)
    ax[0].plot(B,R,'.-',ms=1,lw=.5); ax[0].set_ylabel('|Rxx| ohm')
    ax[1].plot(B,run.col('k_2400_tg_curr')*1e12,label='TG'); ax[1].plot(B,run.col('k_2400_bg_curr')*1e12,label='BG');ax[1].legend();ax[1].set_ylabel('gate currents pA');ax[1].set_xlabel('B T')
    fig.tight_layout();fig.savefig(f'hera_scratch/spot_{rid}_raw.png',dpi=130)
    for low in (0.3,1.0,1.5,2.0,2.5,3.0):
      try:
        o=sdh_onset(R,B,b_lo=low,r_full_scale=5000)
        print('onset',low,o.summary())
        break
      except Exception as e: print('onset ERROR',low,str(e)[:350])
    for br in ((1.5,10),(2.0,10),(2.5,10),(3.0,10),(4.0,10),(2.0,7),(3.0,7)):
      f,s=sdh_fft(R[:,None],B,b_range=br,log=False,nfft=4096)
      y=s[0];pk,_=find_peaks(y,prominence=y.max()*.03)
      pk=pk[(f[pk]>2)&(f[pk]<60)]
      pk=sorted(pk,key=lambda p:-y[p])[:7]
      print('fft',br,[(round(float(f[p]),2),round(float(y[p]/y.max()),3)) for p in pk])
