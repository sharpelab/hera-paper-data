from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

fig, axes = plt.subplots(2, 2, figsize=(12, 7))
for j, (fid, n) in enumerate(((6, 3.2), (7, -1.2))):
    run = open_run(Path('data') / str(fid))
    B = run.col('magnet_field')
    I = run.col('sr0_X') / -1e6
    R = run.col('sr1_X') / I
    T = run.col('T_sample')
    tg = run.col('k_2400_tg_curr')
    bg = run.col('k_2400_bg_curr')
    print(f'run {fid}: B {B[0]:.3f}->{B[-1]:.3f}, T {T.min():.3f}-{T.max():.3f} K, I {np.nanmedian(I)*1e9:.2f} nA, R {np.nanmin(R):.1f}..{np.nanmax(R):.1f} ohm; |gate I| max {np.nanmax(abs(tg))*1e12:.0f}/{np.nanmax(abs(bg))*1e12:.0f} pA')
    ax = axes[j,0]
    ax.plot(B, R, lw=0.6)
    ax.set(xlabel='B (T)', ylabel='Rxx (ohm)', title=f'Run {fid}: raw Rxx, n={n:+.1f}e12')
    try:
        on = sdh_onset(R, B, r_full_scale=5000)
        print(on.summary())
        low = on.onset_b
    except Exception as ex:
        print('ONSET ERROR', type(ex).__name__, ex)
        low = 2.0
    ax = axes[j,1]
    for cut in (max(low, 1.0), max(low+0.5, 2.0), max(low+1.0, 2.5)):
        try:
            f,s = sdh_fft(R[:,None], B, b_range=(cut,10), log=False, nfft=4096)
            y=s[0]
            inds=np.argsort(y[(f>3)&(f<70)])[-8:]
            ff=f[(f>3)&(f<70)][inds]; yy=y[(f>3)&(f<70)][inds]
            print('FFT cut',cut,'top',sorted(zip(np.round(ff,2),np.round(yy,4)), key=lambda x:x[0]))
            ax.plot(f,y/y.max(),label=f'{cut:.2f}T')
        except Exception as ex:
            print('FFT ERROR',ex)
    ax.axvline(10.339*n.__abs__(),color='k',ls=':',label='F_L')
    ax.set(xlim=(0,70),xlabel='F (T)',ylabel='relative FFT',title=f'Run {fid}: FFT (degree 5)')
    ax.legend()
fig.tight_layout()
fig.savefig('hera_scratch/spot_read.png',dpi=170)
