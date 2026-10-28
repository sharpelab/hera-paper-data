from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_onset, sdh_fft
for rid,n in [(6,3.2),(7,-1.2)]:
 r=open_run(Path('data')/str(rid)); ch={c.cid:c for c in resolve_channels(r.meta)}
 plot_raw(r); plt.show()
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain
 R=r.col('sr1_X')/ch['sr1'].gain/I
 print(f'Run {rid}, n={n}e12 cm^-2, D_A=0: complete={r.complete}, interrupted={r.interrupted}; R={R.min():.2f}..{R.max():.2f} ohm; drain={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
 print('Gate current maxima (pA):',*[np.max(np.abs(r.col(c)))*1e12 for c in ['k_2400_tg_curr','k_2400_bg_curr']])
 print('Temperature K:',np.min(r.col('T_sample')),np.max(r.col('T_sample')))
 # Electron <1 T has 50 mT sampling, unsuitable for the high-frequency onset audit.
 on=sdh_onset(R,B,b_lo=1.0 if rid==6 else .3,r_full_scale=50e-6/np.median(I))
 print(on.summary())
 fig,ax=plt.subplots(figsize=(9,4))
 for degree in (3,5,7):
  f,p=sdh_fft(R[:,None],B,b_range=(1.0,10),bg_degree=degree,nfft=4096,log=False)
  ax.plot(f,p[0]/p[0].max(),label=f'B=1..10 T, degree {degree}')
 ax.axvline(abs(n)*10.33916924,color='k',ls='--',label='geometry-prior F_L')
 ax.set(xlim=(0,60),xlabel='Frequency (T)',ylabel='Normalized FFT magnitude',title=f'Run {rid}: provisional spectrum, one polarity only')
 ax.legend(); fig.tight_layout(); plt.show()
print('Interpretation: electron features near 7.3, 14.8, 22.3 and 29.4 T form a possible harmonic comb; frequency-versus-density is required. No stacking classification yet. The electron onset is censored at the adequately sampled 1 T edge; a low-field extension is needed before pricing a full fan. The hole spectrum is stronger but the available D=0 density range ends near -1.27e12, in the model near-degeneracy regime. Region-A calibration is operational; the second CNP ridge means spatial homogeneity cannot be assumed. Single-polarity FFTs retain possible Hall admixture.')
