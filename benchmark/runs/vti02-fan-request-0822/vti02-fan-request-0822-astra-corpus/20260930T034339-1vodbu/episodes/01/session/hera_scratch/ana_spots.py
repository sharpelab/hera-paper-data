from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, summarize_run
import numpy as np
import matplotlib.pyplot as plt
for fid, nominal_n in [(6,3.2),(7,-1.2)]:
    run = open_run(f'data/{fid}')
    channels = resolve_channels(run.meta)
    ic = current_channel(channels)
    vc = next(c for c in channels if c.cid == 'sr1')
    B = run.col('magnet_field')
    I = run.col(ic.col)/ic.gain
    R = (run.col(vc.col)/vc.gain)/I
    print(summarize_run(run))
    fig, ax = plt.subplots(2,2,figsize=(11,7))
    ax[0,0].plot(B,R); ax[0,0].set(ylabel='Rxx (ohm)',title=f'Run {fid}: B_1 - B_2; n={nominal_n:+g}e12, D~0')
    ax[0,1].plot(B,I*1e9); ax[0,1].set(ylabel='Measured drain current (nA)')
    for key in ['k_2400_tg_curr','k_2400_bg_curr']:
        ax[1,0].plot(B,run.col(key)*1e12,label=key)
    ax[1,0].legend(); ax[1,0].set(ylabel='Gate current (pA)')
    ax[1,1].plot(B,run.col('T_sample')); ax[1,1].set(ylabel='Sample T (K)')
    for a in ax.flat: a.set_xlabel('B (T)')
    fig.tight_layout(); plt.show()
    print('RAW:', 'R range',R.min(),R.max(),'ohm; I range',I.min()*1e9,I.max()*1e9,'nA')
    # Full-window and low-field fits: exposes background sensitivity rather than hiding it.
    for top in ([10,4,5] if fid==6 else [10,3,4]):
        onset=sdh_onset(R,B,b_lo=.3,b_hi=top,r_full_scale=5000)
        print(f'Onset with B_hi={top}:\n{onset.summary()}')
    fig,ax=plt.subplots(figsize=(9,4))
    for degree in (3,5,7):
        for cutoff in (1.2,1.5):
            f,spec=sdh_fft(R[:,None],B,b_range=(cutoff,5),bg_degree=degree,log=False,nfft=4096)
            ax.plot(f,spec[0]/max(spec[0]),label=f'deg {degree}, {cutoff}-5 T')
    ax.axvline(10.33916924*abs(nominal_n),color='k',ls='--',label='nominal F_L (g=4)')
    ax.set(xlim=(0,50),xlabel='Frequency (T)',ylabel='FFT / maximum',title=f'Run {fid}: extraction stability; positive B only')
    ax.legend(fontsize=8); fig.tight_layout(); plt.show()
