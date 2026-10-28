from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset

root = Path(__file__).resolve().parent.parent
for rid in (6, 7):
    run = open_run(root / 'data' / str(rid))
    chans = resolve_channels(run.meta)
    ic = current_channel(chans)
    vc = next(c for c in chans if c.cid == 'sr1')
    B = run.col('magnet_field')
    I = run.col(ic.col) / ic.gain
    V = run.col(vc.col) / vc.gain
    R = np.abs(V / I)
    T = run.col('T_sample')
    print(f'RUN {rid}: {run.rows} rows, B {B[0]:.3f} to {B[-1]:.3f} T, T {T.min():.3f}..{T.max():.3f} K')
    print(f'I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, V {V.min()*1e6:.3f}..{V.max()*1e6:.3f} uV, R {R.min():.1f}..{R.max():.1f} ohm')
    print(f'gate currents TG {np.max(np.abs(run.col("k_2400_tg_curr")))*1e12:.1f} pA BG {np.max(np.abs(run.col("k_2400_bg_curr")))*1e12:.1f} pA')
    fig, ax = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
    ax[0].plot(B, V*1e6, lw=.8); ax[0].set_ylabel('sr1 X / gain (uV)')
    ax[1].plot(B, I*1e9, lw=.8); ax[1].set_ylabel('drain current (nA)')
    ax[2].plot(B, R, lw=.8); ax[2].set_ylabel('|Rxx| (ohm)'); ax[2].set_xlabel('B (T)')
    fig.suptitle(f'run {rid}: raw channel values and Rxx'); fig.tight_layout()
    fig.savefig(root/'hera_scratch'/f'spot_{rid}_raw.png', dpi=160)
    plt.close(fig)
    for blo in (1.5, 2.0, 3.0, 4.0):
        sel=(B>=blo)&(B<=10)
        bs=B[sel]; rs=R[sel]
        if len(bs)<20: continue
        freqs,spec=sdh_fft(rs[:,None],bs,nfft=2048,bg_degree=5,log=False)
        y=spec[0]; pk,_=find_peaks(y, prominence=np.max(y)*.08)
        pk=sorted([p for p in pk if 2<freqs[p]<100],key=lambda p:y[p],reverse=True)[:8]
        print('FFT',blo,'resolution',1/(1/blo-0.1),'peaks',[(round(freqs[p],2),round(float(y[p]/y.max()),3)) for p in pk])
        if blo==2:
            fig,ax=plt.subplots(2,1,figsize=(9,7))
            ax[0].plot(B,R,lw=.8);ax[0].set_xlim(blo,10);ax[0].set_ylabel('|Rxx| (ohm)')
            ax[1].plot(freqs,y);ax[1].set_xlim(0,100);ax[1].set_xlabel('frequency (T)');ax[1].set_ylabel('FFT amplitude')
            fig.tight_layout();fig.savefig(root/'hera_scratch'/f'spot_{rid}_fft.png',dpi=160);plt.close(fig)
    try:
        result=sdh_onset(R,B,b_lo=.3,b_hi=10,r_full_scale=5000)
        print('ONSET',result.summary())
    except Exception as exc:
        print('ONSET ERROR',type(exc).__name__,str(exc))
