from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset

root = Path.cwd()
fig, axs = plt.subplots(2, 3, figsize=(14, 7))
for row, rid in enumerate((6, 7)):
    r = open_run(root / 'data' / str(rid))
    ch = resolve_channels(r.meta); ci = current_channel(ch)
    cv = next(c for c in ch if c.cid == 'sr1')
    I = r.col(ci.col) / ci.gain
    R = (r.col(cv.col) / cv.gain) / I
    B = r.col('magnet_field')
    order = np.argsort(B); B, R = B[order], R[order]
    print('RUN', rid, 'rows', r.rows, 'interrupted', r.interrupted,
          'minutes', (r.data[-1,0]-r.data[0,0])/60,
          'I nA', np.percentile(I*1e9,[0,50,100]),
          'signed R Ohm', np.percentile(R,[0,50,100]))
    print('columns', r.cols)
    print('T', np.percentile(r.col('T_sample'), [0,50,100]))
    for gate in ('k_2400_tg_curr','k_2400_bg_curr'):
        print(gate, 'pA', np.percentile(r.col(gate)*1e12,[0,50,100]))
    axs[row,0].plot(B, r.col(cv.col)[order]*1e6, lw=.8)
    axs[row,0].set(xlabel='B (T)', ylabel='raw sr1 X (uV)', title=f'run {rid}: raw voltage')
    axs[row,1].plot(B,R,lw=.8)
    axs[row,1].set(xlabel='B (T)', ylabel='signed V/I (Ohm)', title='Measured-current normalization')
    for blo in (1., 2., 3.):
        f, spec = sdh_fft(R[:,None], B, b_range=(blo,10), log=False, nfft=2048, bg_degree=3)
        a = spec[0]; axs[row,2].plot(f, a/max(a), label=f'{blo:g}-10 T')
    axs[row,2].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized amplitude',title='Window robustness (signed R)')
    axs[row,2].legend()
    try:
        onset = sdh_onset(R,B,b_lo=.5,r_full_scale=5000,bg_degree=3)
        print(onset.summary())
    except ValueError as e:
        print('ONSET NOT RESOLVED:', e)
fig.tight_layout()
fig.savefig(root/'hera_scratch'/'spot_review.png',dpi=150)
plt.show()
