import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset

for rid in (6, 7):
    r = open_run(f'data/{rid}')
    channels = resolve_channels(r.meta)
    ci = current_channel(channels)
    cv = next(c for c in channels if c.cid == 'sr1')
    I = r.col(ci.col) / ci.gain
    R = r.col(cv.col) / cv.gain / I
    B = r.col('magnet_field')
    order = np.argsort(B); B, R = B[order], R[order]
    print(f'RUN {rid}: {r.rows} points; interrupted={r.interrupted}; wall={(r.meta["end_time"]-r.meta["start_time"])/60:.2f} min')
    print(f'R signed {R.min():.2f}..{R.max():.2f} Ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    print('max |gate currents| pA:', [np.max(np.abs(r.col(c)))*1e12 for c in ('k_2400_tg_curr','k_2400_bg_curr')])
    fig, ax = plt.subplots(3, 2, figsize=(12, 9))
    ax[0,0].plot(r.col('magnet_field'), r.col(cv.col)*1e6); ax[0,0].set_ylabel('Raw sr1 X (uV)')
    ax[0,1].plot(r.col('magnet_field'), r.col(ci.col)*1e3); ax[0,1].set_ylabel('Raw sr0 X (mV)')
    ax[1,0].plot(B, R); ax[1,0].set_ylabel('Signed V / measured I (Ohm)')
    for c in ('k_2400_tg_curr','k_2400_bg_curr'):
        ax[1,1].plot(r.col('magnet_field'),r.col(c)*1e12,label=c)
    ax[1,1].legend(fontsize=7); ax[1,1].set_ylabel('Gate current (pA)')
    for lo in (1.5, 2.0, 3.0):
        f, spec = sdh_fft(R[:,None], B, b_range=(lo,10), nfft=2048, log=False)
        sp=spec[0]; mask=(f>=3)&(f<=65)
        pk,_=find_peaks(sp)
        pk=[p for p in pk if 3<=f[p]<=65]
        top=sorted(pk,key=lambda p:sp[p],reverse=True)[:5]
        print(f'  FFT {lo}..10 T: resolution {1/(1/lo-1/10):.2f} T; peaks', [(round(f[p],2),round(sp[p]/sp[mask].max(),3)) for p in top])
        ax[2,0].plot(f[mask],sp[mask]/sp[mask].max(),label=f'{lo}..10 T')
    ax[2,0].legend(); ax[2,0].set_xlabel('F (T)'); ax[2,0].set_ylabel('Normalized linear-R FFT')
    try:
        onset=sdh_onset(R,B,r_full_scale=5000)
        print(onset.summary())
        for tone in onset.tones:
            ax[2,1].plot(tone.b_centers,tone.snr,label=f'{tone.freq:.1f} T')
        ax[2,1].axhline(5,color='k',ls=':'); ax[2,1].legend(fontsize=7)
    except ValueError as exc:
        print('Onset unresolved:',exc)
    ax[2,1].set_ylabel('Tone SNR'); ax[2,1].set_xlabel('B (T)')
    for a in ax[:2].flat: a.set_xlabel('B (T)')
    fig.suptitle(f'Run {rid}: raw first, then signed transport and exploratory SdH analysis')
    fig.tight_layout(); fig.savefig(f'hera_scratch/spot_{rid}.png',dpi=120)
    plt.show()

r=open_run('data/5'); dt=np.diff(r.col('time')).reshape(-1)
print('RUN 5 timing: point dt 10/50/90 percentiles',np.quantile(dt,[.1,.5,.9]),'wall min',(r.meta['end_time']-r.meta['start_time'])/60)
