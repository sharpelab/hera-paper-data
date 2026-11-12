from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError, summarize_run
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

for rid, n, b_floor in [(6, 3.2, 0.3), (7, -1.2, 0.3)]:
    run = open_run(Path('data') / str(rid))
    print('\n', summarize_run(run))
    print('columns', run.cols)
    ch = resolve_channels(run.meta)
    print('channels', [(c.cid,c.gain,c.label,c.is_current) for c in ch])
    B = run.col('magnet_field')
    I = run.col('sr0_X') / run.meta['measurement_config']['sr0_gain']
    R = np.abs(run.col('sr1_X') / I)
    print('B',B.min(),B.max(),'R min max',np.min(R),np.max(R),'I min max',I.min(),I.max(), 'T range',run.col('T_sample').min(),run.col('T_sample').max())
    print('gate current max',[(name,np.nanmax(np.abs(run.col(name)))) for name in ['k_2400_tg_curr','k_2400_bg_curr']])
    fig,ax=plt.subplots(2,2,figsize=(11,7))
    ax[0,0].plot(B,R,'.-',ms=1);ax[0,0].set(xlabel='B (T)',ylabel='|Rxx| (Ohm)',title=f'run {rid} raw')
    ax[0,1].plot(B,I*1e9,'.-',ms=1);ax[0,1].set(xlabel='B (T)',ylabel='I drain (nA)')
    for blo,color in [(1.5,'C0'),(2.5,'C1'),(3.5,'C2')]:
        sel=(B>=blo)&(B<=10)
        ax[1,0].plot(1/B[sel],R[sel],'.-',ms=1,label=f'B≥{blo}')
        f,sp=sdh_fft(R[:,None],B,b_range=(blo,10),nfft=4096,bg_degree=5,log=False)
        y=sp[0]; ax[1,1].plot(f,y/y.max(),label=f'B≥{blo}',color=color)
    ax[1,0].set(xlabel='1/B (1/T)',ylabel='|Rxx| (Ohm)');ax[1,0].legend()
    ax[1,1].set(xlabel='F (T)',ylabel='FFT / max',xlim=(0,45));ax[1,1].legend()
    fig.tight_layout();fig.savefig(f'hera_scratch/spot_{rid}_raw_fft.png',dpi=150);plt.close(fig)
    for floor in [0.3,1.0,1.5]:
        try:
            onset=sdh_onset(R,B,b_lo=floor,r_full_scale=5000)
            print('floor',floor,onset.summary())
        except SdhOnsetError as e:
            print('ONSET ERROR',floor,e)
    for blo in [1.5,2,2.5,3,4]:
        f,sp=sdh_fft(R[:,None],B,b_range=(blo,10),nfft=4096,bg_degree=5,log=False)
        y=sp[0]
        peaks,_=find_peaks(y,prominence=np.max(y)*0.04)
        peaks=[p for p in peaks if 3<f[p]<60]
        peaks=sorted(peaks,key=lambda p:y[p],reverse=True)[:8]
        print('FFT',blo,[(round(f[p],2),round(y[p]/np.max(y),3)) for p in peaks])
