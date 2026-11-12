from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft
from scipy.signal import find_peaks
for fid, n in [(6,3.2),(7,-1.2)]:
    r=open_run(Path('data')/str(fid))
    plot_raw(r, channels=['sr0','sr1'])
    plt.show()
    B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
    print(f'Run {fid}, n={n:+.1f}e12: R [{R.min():.2f},{R.max():.2f}] ohm; T [{r.col("T_sample").min():.3f},{r.col("T_sample").max():.3f}] K; interrupted={r.interrupted}')
    for hi in ([4,10] if fid==6 else [10]):
        on=sdh_onset(R,B,b_hi=hi,r_full_scale=5000)
        print(f'Onset background-fit upper edge {hi} T:\n{on.summary()}')
    fig, axs=plt.subplots(1,2,figsize=(12,4))
    axs[0].plot(B,R); axs[0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'Run {fid}: B_1 - B_2')
    for low,hi in [(1.04,4),(1.04,7),(1.5,10)]:
        f,a=sdh_fft(R[:,None],B,b_range=(low,hi),nfft=4096,log=False)
        use=(f>3)&(f<45)
        axs[1].plot(f,a[0]/a[0,use].max(),label=f'{low}-{hi} T')
        pp,_=find_peaks(a[0]); pp=sorted([p for p in pp if 3<f[p]<45],key=lambda p:a[0,p],reverse=True)[:5]
        print(f'Window {low}-{hi} T; delta_F={1/(1/low-1/hi):.2f} T; peaks',np.round(f[pp],2))
    axs[1].set(xlim=(3,45),ylim=(0,1.2),xlabel='F (T)',ylabel='FFT / largest peak above 3 T');axs[1].legend();fig.tight_layout();plt.show()
