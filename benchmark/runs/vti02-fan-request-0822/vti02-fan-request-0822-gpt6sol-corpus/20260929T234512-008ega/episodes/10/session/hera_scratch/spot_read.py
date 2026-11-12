from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, summarize_run

fig, ax = plt.subplots(2, 2, figsize=(12, 8))
for j, rid in enumerate((6, 7)):
    r = open_run(f'data/{rid}')
    print(summarize_run(r))
    B = r.col('magnet_field')
    I = r.col('sr0_X') / -1e6
    R = r.col('sr1_X') / I
    ix = np.argsort(B); B, R = B[ix], R[ix]
    print('T', np.nanmin(r.col('T_sample')), np.nanmax(r.col('T_sample')), 'I', np.nanmin(I), np.nanmax(I), 'R', np.nanmin(R), np.nanmax(R))
    ax[j, 0].plot(B, R, lw=.8); ax[j, 0].set(xlabel='B (T)', ylabel='Rxx (ohm)', title=f'run {rid} raw')
    try:
        on = sdh_onset(R, B, r_full_scale=5000)
        print(on.summary())
        cutoff = max(on.onset_b, 1.0)
    except Exception as e:
        print('ONSET ERROR', repr(e)); cutoff=1.5
    for lo in sorted(set([round(cutoff, 2), 2.0, 2.5, 3.0])):
        if lo >= 8: continue
        f, spec = sdh_fft(R[:,None], B, b_range=(lo, 10), log=False, nfft=4096)
        y=spec[0]; pk,_=find_peaks(y, prominence=np.max(y)*.04)
        pk=sorted((p for p in pk if 2<f[p]<50),key=lambda p:y[p],reverse=True)[:8]
        print('FFT cutoff',lo,'peaks',[(round(f[p],2),round(y[p],2)) for p in pk])
        ax[j,1].plot(f,y/y.max(),label=f'B>{lo}')
    ax[j,1].set(xlim=(0,45),xlabel='F (T)',ylabel='normalized FFT',title=f'run {rid}'); ax[j,1].legend(fontsize=7)
fig.tight_layout(); fig.savefig('hera_scratch/spot_runs6_7.png', dpi=150)
