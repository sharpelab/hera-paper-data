from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft

fig, axs = plt.subplots(2, 2, figsize=(11, 7))
for j, (rid, n) in enumerate(((6, 3.2), (7, -1.2))):
    run = open_run(Path('data') / str(rid))
    B = run.col('magnet_field')
    R = run.col('sr1_X') / 1e-8
    order = np.argsort(B)
    B, R = B[order], R[order]
    print(f'run {rid}: B {B.min():.3f}..{B.max():.3f} T, R {R.min():.1f}..{R.max():.1f} Ohm, max/fullscale {np.max(np.abs(R))/5000:.3f}, T {run.col("T_sample").min():.3f}..{run.col("T_sample").max():.3f} K')
    print(f'currents pA: tg {np.nanmedian(run.col("k_2400_tg_curr"))*1e12:.1f}, maxabs {np.nanmax(np.abs(run.col("k_2400_tg_curr")))*1e12:.1f}; bg {np.nanmedian(run.col("k_2400_bg_curr"))*1e12:.1f}, maxabs {np.nanmax(np.abs(run.col("k_2400_bg_curr")))*1e12:.1f}')
    axs[j,0].plot(B,R,lw=.7)
    axs[j,0].set(title=f'Run {rid}, n={n:+.1f}e12: raw Rxx',xlabel='B (T)',ylabel='Rxx (Ohm)')
    try:
        onset = sdh_onset(R, B, r_full_scale=5000)
        print(onset.summary())
        blo = onset.onset_b
    except Exception as e:
        print('ONSET ERROR:', type(e).__name__, e)
        blo = 2.0
    for cutoff in (max(blo,1.5), max(blo,2.0), max(blo,3.0)):
        try:
            fs, spec = sdh_fft(R[:,None],B,b_range=(cutoff,10),bg_degree=5,log=False)
            y=spec[0]
            peaks,_=find_peaks(y,prominence=np.nanmax(y)*.1)
            peaks=sorted(peaks,key=lambda k:y[k],reverse=True)[:8]
            print(f'run {rid} FFT cutoff {cutoff:.2f}:',[(round(fs[k],2),round(y[k]/max(y),2)) for k in peaks if 2 < fs[k] < 100])
            axs[j,1].plot(fs,y/max(y),label=f'B>{cutoff:.2f}')
        except Exception as e:
            print('FFT ERROR:',type(e).__name__,e)
    axs[j,1].set(xlim=(0,55),title=f'Run {rid}: FFT sensitivity',xlabel='Frequency (T)',ylabel='Norm. amplitude')
    axs[j,1].legend()
fig.tight_layout()
fig.savefig('hera_scratch/spot_analysis.png',dpi=160)
