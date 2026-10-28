from pathlib import Path
import sys, json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft
root=Path.cwd(); scratch=root/'hera_scratch'
for rid in (6,7):
    r=open_run(root/'data'/str(rid))
    fig=plot_raw(r,channels=['sr0','sr1']); fig.savefig(scratch/f'run{rid}_raw_review.png'); plt.show()
    chans=resolve_channels(r.meta); cur=current_channel(chans); v=next(c for c in chans if c.cid=='sr1')
    I=r.col(cur.col)/cur.gain; R=(r.col(v.col)/v.gain)/I; B=r.col('magnet_field')
    print(f'RUN {rid}: complete={r.complete}, interrupted={r.interrupted}, Rxx {R.min():.2f}..{R.max():.2f} ohm; drain {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
    for name in ['T_sample','k_2400_tg_curr','k_2400_bg_curr']:
        print(name, np.min(r.col(name)),np.max(r.col(name)))
    on=sdh_onset(R,B,r_full_scale=5000)
    print('Full-record diagnostic (censored/near-residual tracks are NOT established pockets):\n'+on.summary())
    if rid==6:
        on_low=sdh_onset(R,B,b_lo=.3,b_hi=4,r_full_scale=5000)
        print('Low-field-only diagnostic, excluding broad high-field MR:\n'+on_low.summary())
        print('Onset stability, b_hi=4, b_lo=.3/.5:')
        for low in [.3,.5]:
            for deg in [3,5,7]:
                oo=sdh_onset(R,B,b_lo=low,b_hi=4,r_full_scale=5000,bg_degree=deg)
                print(low,deg,oo.onset_b)
    fig,ax=plt.subplots(figsize=(10,4))
    for low,high,deg in [(1,4,3),(1,6,5),(1.5,8,5),(2,10,3),(2,10,7)]:
        f,S=sdh_fft(R[:,None],B,b_range=(low,high),bg_degree=deg,nfft=4096,log=False)
        ax.plot(f,S[0]/np.max(S[0]),label=f'{low}-{high} T, degree {deg}')
        peaks,_=find_peaks(S[0],prominence=.05*np.max(S[0]))
        print('FFT',rid,(low,high,deg),np.round(f[peaks[(f[peaks]>3)&(f[peaks]<65)]],2))
    ax.set(xlim=(0,65),xlabel='Frequency (T)',ylabel='Normalized FFT amplitude',title=f'Run {rid}: extraction stability, signed Rxx, no log')
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(scratch/f'run{rid}_fft_review.png'); plt.show()
