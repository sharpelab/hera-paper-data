from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_onset, sdh_fft
_bases=[Path.cwd(), Path('/home/hera/measurements/zack/20260822-vti-02')]
file_path=next(str(b/'data') for b in _bases if (b/'data/6/metadata.json').exists())
for rid,nden in ((6,3.2),(7,-1.2)):
    r=open_run(Path(file_path)/str(rid))
    plot_raw(r); plt.show()
    ch={c.cid:c for c in resolve_channels(r.meta)}
    B=r.col('magnet_field'); Id=r.col('sr0_X')/ch['sr0'].gain
    R=(r.col('sr1_X')/ch['sr1'].gain)/Id
    print(f'Run {rid}: n={nden}e12, D=0 (run-5 calibration); interrupted={r.interrupted}; R={R.min():.2f}..{R.max():.2f} ohm; I={Id.min()*1e9:.3f}..{Id.max()*1e9:.3f} nA')
    print('T range',r.col('T_sample').min(),r.col('T_sample').max(),'K; peak abs gate currents pA',*[np.max(np.abs(r.col(k)))*1e12 for k in ('k_2400_tg_curr','k_2400_bg_curr')])
    # Run 6 below 1 T is too coarsely sampled for its fastest expected tone.
    on=sdh_onset(R,B,b_lo=1.0 if rid==6 else .3,r_full_scale=5000)
    print(on.summary())
    fig,ax=plt.subplots(1,2,figsize=(12,4))
    ax[0].plot(B,R,'.-',ms=2); ax[0].set(xlabel='B (T)',ylabel='signed Rxx (ohm)',title=f'Run {rid}: drain-normalized raw')
    for degree in (3,5):
        for lo in (1.,1.5,2.):
            f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=degree,nfft=4096,log=False)
            ax[1].plot(f,sp[0]/sp.max(),label=f'{lo}-10 T, degree {degree}')
    ax[1].set(xlim=(0,45),xlabel='Frequency (T)',ylabel='normalized amplitude',title='Hann FFT; detrend in B; no log transform')
    ax[1].axvline(abs(nden)*10.33916924,color='k',ls=':',label='nominal F_L')
    ax[1].legend(fontsize=7); fig.tight_layout(); plt.show()
    print('Interpretation:', 'Electron comb near 7.4,14.8,22.2,29.6 T; harmonic/orbit origin unresolved. Censored onset and near-residual flags prevent a clean onset claim. No stacking verdict.' if rid==6 else 'Hole trace has clear low-field oscillations; onset 0.71388 T, candidate 4.7 and 6.6 T components plus 12.3 T near F_L=12.41 T. Window-dependent low-frequency peaks and harmonic flags: no unique pocket count. Fan tests density trajectories; neither an ABAB nor an ABCA verdict follows yet.')
