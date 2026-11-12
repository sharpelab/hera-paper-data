from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import h, e
from hera.analysis import open_run, plot_raw, sdh_fft, sdh_onset
for _id, _n, _hi in [(6,3.2,5),(7,-1.2,4)]:
    r = open_run(f'data/{_id}')
    plot_raw(r); plt.show()
    B = r.col('magnet_field')
    R = r.col('sr1_X') / (r.col('sr0_X') / -1e6)
    print(f'Run {_id}: complete={not r.interrupted}, R={R.min():.2f}..{R.max():.2f} ohm; T={r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    onset = sdh_onset(R,B,b_lo=.3,b_hi=_hi,bg_degree=5,r_full_scale=5000)
    print('Windowed onset:',onset.onset_b,'T; tone table (F,onset,censored,marginal):')
    print([(round(t.freq,3),round(t.onset_b,3),t.censored,t.marginal) for t in onset.tones])
    fig, ax = plt.subplots(figsize=(10,4))
    for lo, hi, degree in [(1,5,3),(1,5,5),(1.5,5,3),(2,7,3)]:
        f,S = sdh_fft(R[:,None],B,b_range=(lo,hi),nfft=4096,bg_degree=degree,log=False)
        ax.plot(f,S[0]/S.max(),label=f'{lo}-{hi} T, polynomial {degree}')
    ax.axvline(h/(4*e)*abs(_n)*1e16,color='k',ls='--',label='geometry-prior F_L')
    ax.set(xlim=(0,150),xlabel='F (T)',ylabel='normalized FFT magnitude',title=f'Run {_id}: extraction stability; no harmonic labels assumed')
    ax.legend(); plt.show()
