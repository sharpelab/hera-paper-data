from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft
_data = Path(file_path) if 'file_path' in globals() else Path.cwd()/'data'
for rid in (6,7):
    r = open_run(_data/str(rid))
    plot_raw(r); plt.show()
    cs=resolve_channels(r.meta); cur=current_channel(cs); v=next(c for c in cs if c.cid=='sr1')
    B=r.col('magnet_field'); I=r.col(cur.col)/cur.gain; R=(r.col(v.col)/v.gain)/I
    print(f'Run {rid}: complete={r.complete}, interrupted={r.interrupted}, {r.rows} points; R={R.min():.2f}..{R.max():.2f} Ohm; I={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
    print(f'T={r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K; duration={np.ptp(r.col("time"))/60:.1f} min')
    print('Full-record onset (candidate tracks, not independent pocket counts):')
    print(sdh_onset(R,B,r_full_scale=5000).summary())
    if rid==6:
        print('Local 0.3–5 T onset, excluding the large high-field MR rise from background fitting:')
        print(sdh_onset(R,B,b_hi=5,r_full_scale=5000).summary())
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,cut in zip(axes,[1.5,2.0]):
        for degree in (3,5,7):
            f,a=sdh_fft(R[:,None],B,b_range=(cut,10),bg_degree=degree,log=False,nfft=4096)
            ax.plot(f,a[0]/a[0].max(),label=f'B-polynomial degree {degree}')
        ax.set(xlim=(0,60),xlabel='Frequency (T)',ylabel='Normalized FFT magnitude',title=f'Run {rid}: B={cut}–10 T')
        ax.legend(fontsize=8)
    fig.tight_layout();plt.show()
    if rid==6:
        print('READ: peaks near 7, 14–15, 22–23, and 29–30 T form a possible harmonic comb. Do not count four pockets. The slow component is background-sensitive. Full-record censored onsets at 0.3 T do not persist under local MR fits: degree-5 0.3–4 and 0.3–5 T fits give 1.03 and 1.018 T. The ~7 T track varies 1.01–1.04 T in these local fits but is marginal for degree 3 at 4 T. Use 1.018 T as a provisional design edge; no absence claim below it. No stacking verdict yet.')
    else:
        print('READ: hole onset 0.71 T is stable across degrees 3/5/7, but the accessible density is only -1.2e12. Model ABAB tones 5.86/6.54 T differ by 0.68 T, below 2*dF=1.53 T even with 10 T reach. A hole fan cannot cleanly split that pair here. Electron fan chosen for model separation; cross-density frequency trajectories must screen harmonics, adjacent-N, and region-offset alternatives.')
