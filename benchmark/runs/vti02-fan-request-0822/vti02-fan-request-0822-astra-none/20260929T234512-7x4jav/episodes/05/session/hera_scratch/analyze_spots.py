from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
from scipy.signal import find_peaks
root = Path(globals().get('file_path', 'data'))
fig, ax = plt.subplots(2, 3, figsize=(14, 7))
for j, rid in enumerate((6,7)):
    r = open_run(root/str(rid)); channels = resolve_channels(r.meta)
    cur = current_channel(channels); volt = next(c for c in channels if not c.is_current)
    I = r.col(cur.col)/cur.gain; V = r.col(volt.col)/volt.gain
    B = r.col('magnet_field'); order = np.argsort(B); B = B[order]; R = (V/I)[order]
    ax[j,0].plot(B, V[order]*1e6, lw=.8, label='voltage (uV)')
    ax[j,0].plot(B, I[order]*1e9, lw=.8, label='drain (nA)'); ax[j,0].legend(fontsize=8)
    ax[j,0].set_title(f'data/{rid}: raw gain-divided channels'); ax[j,0].set_xlabel('B (T)')
    ax[j,1].plot(B,R,lw=.8); ax[j,1].set(xlabel='B (T)',ylabel='signed V/I (ohm)',title='Measured-current resistance')
    print(f'run {rid}: complete={not r.interrupted}; N={r.rows}; R={R.min():.2f}..{R.max():.2f} ohm; I={I.min()*1e9:.4f}..{I.max()*1e9:.4f} nA; elapsed={(r.data[-1,0]-r.data[0,0])/60:.2f} min')
    for lo in (1.5,2.,2.5):
        f,a = sdh_fft(R[:,None],B,b_range=(lo,10),nfft=4096,bg_degree=3,log=False)
        a=a[0]; use=(f>=3)&(f<=55); ax[j,2].plot(f[use],a[use]/a[use].max(),label=f'{lo}–10 T')
        p,_=find_peaks(a); p=[k for k in p if 3<=f[k]<=55]; p=sorted(p,key=lambda k:-a[k])[:5]
        print(f'  linear-R FFT {lo}..10 T: peaks {[round(float(f[k]),2) for k in p]}, resolution {1/(1/lo-0.1):.2f} T')
    ax[j,2].set(xlabel='F (T)',ylabel='normalized FFT',title='Window robustness (cubic B background)');ax[j,2].legend(fontsize=8)
fig.tight_layout(); fig.savefig(root.parent/'hera_scratch'/'spots_6_7.png',dpi=150); plt.show()
# Median point times separate the scan floor from gate-map latency.
r=open_run(root/'5'); t=r.col('time'); dt=np.diff(t); within=np.arange(1,r.rows)%66 != 0
print('run 5: within-row median',np.median(dt[within]),'s; row-boundary median',np.median(dt[~within]),'s; dwell 1.0 s')
for rid in (6,7):
 r=open_run(root/str(rid)); dt=np.diff(r.col('time')); db=np.abs(np.diff(r.col('magnet_field')))
 print('run',rid,'median excess over bare ramp',np.median(dt-db*7.3*60),'s/point')
