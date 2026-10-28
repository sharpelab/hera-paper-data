import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft
from scipy.signal import find_peaks
for fid, density in ((6,3.2),(7,-1.2)):
    r=open_run(f'data/{fid}')
    fig=plot_raw(r); plt.show()
    cs=resolve_channels(r.meta); cur=current_channel(cs); v=next(c for c in cs if c.cid=='sr1')
    B=r.col('magnet_field'); I=r.col(cur.col)/cur.gain; R=(r.col(v.col)/v.gain)/I
    print(f'Run {fid}, n={density:+g}e12, D=0: complete={r.complete}, interrupted={r.interrupted}; R={R.min():.2f}..{R.max():.2f} Ohm; I={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
    print('T range',np.min(r.col('T_sample')),np.max(r.col('T_sample')),'K; gate max |I| pA',*[np.max(np.abs(r.col(c)))*1e12 for c in ('k_2400_tg_curr','k_2400_bg_curr')])
    print('Full-record onset (diagnostic, check background sensitivity):')
    print(sdh_onset(R,B,r_full_scale=5000).summary())
    print('Low-field onset, limited to 4 T to exclude the large high-field MR rise:')
    for degree in (3,5):
        print('background degree',degree)
        print(sdh_onset(R,B,b_hi=4,bg_degree=degree,r_full_scale=5000).summary())
    fig,axs=plt.subplots(1,2,figsize=(12,4))
    axs[0].plot(B,R,'.-',ms=2); axs[0].set(xlim=(0,4),xlabel='B (T)',ylabel='Signed Rxx (Ohm)')
    for lo,hi in ((1,4),(1.2,6),(1.5,10)):
        for degree in (3,5):
            f,a=sdh_fft(R[:,None],B,b_range=(lo,hi),bg_degree=degree,log=False,nfft=4096)
            axs[1].plot(f,a[0]/max(a[0]),label=f'{lo}-{hi} T, degree {degree}')
    axs[1].set(xlim=(0,45),xlabel='Frequency (T)',ylabel='Normalized amplitude'); axs[1].legend(fontsize=7)
    fig.suptitle(f'Run {fid}: B_1-B_2, n={density:+g}e12 cm^-2, D=0'); fig.tight_layout(); plt.show()
