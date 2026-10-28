from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft

for fid, density, blo in [(6,3.2,1.0),(7,-1.2,0.72)]:
    r=open_run(Path('data')/str(fid))
    fig=plot_raw(r); fig.suptitle(f'Run {fid}: raw signed Rxx and measured current'); fig.tight_layout()
    fig.savefig(f'hera_scratch/spot_{fid}_raw.png'); plt.show()
    chans=resolve_channels(r.meta); cur=current_channel(chans); v=next(c for c in chans if c.cid=='sr1')
    I=r.col(cur.col)/cur.gain; R=(r.col(v.col)/v.gain)/I; B=r.col('magnet_field')
    on=sdh_onset(R,B,b_lo=blo,r_full_scale=5000)
    print(f'Run {fid}, n={density}e12, D=0\n'+on.summary())
    print(f'R={R.min():.2f}..{R.max():.2f} Ohm; I={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; T={r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    fig,axs=plt.subplots(1,2,figsize=(12,4))
    for deg in [3,5,7]:
        f,sp=sdh_fft(R[:,None],B,b_range=(max(blo,on.onset_b),10),bg_degree=deg,log=False)
        axs[0].plot(f,sp[0]/sp[0].max(),label=f'polynomial {deg}')
        pk,_=find_peaks(sp[0]); pk=[p for p in pk if 3<f[p]<50]
        print('degree',deg,'candidate peaks',[(round(float(f[p]),2),round(float(sp[0,p]/sp[0].max()),2)) for p in sorted(pk,key=lambda p:-sp[0,p])[:6]])
    for t in on.tones[:4]: axs[1].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
    axs[0].axvline(abs(density)*10.339169,color='k',ls=':',label='F_L geometry prior')
    axs[0].set(xlim=(0,50),xlabel='F (T)',ylabel='Normalized FFT magnitude',title=f'Run {fid}: stability, signed R (no log)')
    axs[1].axhline(5,color='k',ls=':'); axs[1].set(xlabel='B (T)',ylabel='Matched-filter SNR',title='Per-tone onset tracking')
    for ax in axs: ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(f'hera_scratch/spot_{fid}_fft.png'); plt.show()
print('Interpretation: oscillations are present on both sides, but the low-edge carrying tone is censored on the Nyquist-valid record. Electron range reaches the discriminating high-density regime; hole range does not. No stacking verdict yet. Low-field electron extension is required before committing the fan. Positive-B-only records are not even-in-B; Hall/contact admixture remains a hedge. Harmonic flags alone cannot remove a candidate partition branch; density trajectories will decide.')
