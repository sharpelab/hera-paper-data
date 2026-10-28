import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset

fig, ax = plt.subplots(2, 3, figsize=(14, 7))
for j, rid in enumerate([6, 7]):
    r = open_run(f'data/{rid}')
    ch = resolve_channels(r.meta); ci = current_channel(ch)
    cv = next(c for c in ch if c.cid == 'sr1')
    I = r.col(ci.col) / ci.gain; V = r.col(cv.col) / cv.gain
    R = V / I; B = r.col('magnet_field')
    order = np.argsort(B); B, R = B[order], R[order]
    ax[j, 0].plot(B, R, lw=.7); ax[j, 0].set(xlabel='B (T)', ylabel='signed V/I (ohm)', title=f'Raw run {rid}: B_1 - B_2')
    ax[j, 1].plot(r.col('magnet_field'), I*1e9, label='drain nA')
    ax[j, 1].set(xlabel='B (T)', ylabel='I (nA)', title='Measured drain current')
    print(f'RUN {rid}: {r.rows} points, interrupted={r.interrupted}, wall={(r.meta["end_time"]-r.meta["start_time"])/60:.2f} min, R range {R.min():.2f}..{R.max():.2f} ohm, I range {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
    for name in ['T_sample', 'k_2400_tg_curr', 'k_2400_bg_curr']:
        x=r.col(name); print(name, 'range', x.min(), x.max(), 'median',np.median(x))
    print('columns',r.cols)
    for lo in [1., 1.5, 2.]:
        f, p = sdh_fft(R[:,None], B, b_range=(lo,10), nfft=4096, log=False)
        peaks,_=find_peaks(p[0]); peaks=sorted([k for k in peaks if 3<f[k]<65], key=lambda k:-p[0,k])[:5]
        print('FFT',lo,'..10 T peaks:',[(round(f[k],2),round(p[0,k],1)) for k in peaks], 'Rayleigh',1/(1/lo-.1))
        ax[j,2].plot(f,p[0]/p[0].max(),label=f'{lo}-10 T')
    ax[j,2].set(xlim=(0,65),xlabel='frequency (T)',ylabel='normalized FFT',title='Signed R, degree-5 B background'); ax[j,2].legend()
    try:
        onset=sdh_onset(R,B,r_full_scale=5000)
        print(onset.summary())
    except Exception as e: print('ONSET failed:',e)
fig.tight_layout(); fig.savefig('hera_scratch/spot_review.png',dpi=140)
plt.show()

for rid in [5,6,7]:
    r=open_run(f'data/{rid}'); dt=np.diff(r.col('time'))
    print('TIMING',rid,'wall s',r.meta['end_time']-r.meta['start_time'],'dt percentiles',np.percentile(dt,[10,50,90,99]))
    if rid==5:
        print('delays',r.meta.get('fast_delay'),r.meta.get('slow_delay'),'NPLC',r.meta['instruments']['k_2400_tg']['parameters'].get('nplci', 'not snapshotted; state0=1'))
