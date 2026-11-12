from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, plot_raw, sdh_onset, sdh_fft
out=Path('hera_scratch')
for rid,n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{rid}')
 fig=plot_raw(r); fig.savefig(out/f'spot_{rid}_raw.png',dpi=140); plt.show()
 ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/I
 print(f'Run {rid}: n={n}, signed R {R.min():.2f}..{R.max():.2f} Ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
 on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
 fig,axs=plt.subplots(2,2,figsize=(12,8))
 for deg in (3,5,7):
  sel=B>=0.3
  bg=np.polynomial.Polynomial.fit(B[sel],R[sel],deg)(B[sel])
  axs[0,0].plot(B[sel],R[sel]-bg,label=f'degree {deg}')
  for ax,lo in zip((axs[0,1],axs[1,0]),(1,2)):
   f,a=sdh_fft(R[:,None],B,b_range=(lo,8),bg_degree=deg,nfft=4096,log=False)
   ax.plot(f,a[0]/a[0].max(),label=f'deg {deg} B={lo}..8')
   p,_=find_peaks(a[0]); p=p[(f[p]>3)&(f[p]<50)]; p=p[np.argsort(a[0,p])[-6:]][::-1]
   print('FFT',rid,lo,deg,list(np.round(f[p],2)))
   ax.set_xlim(0,50); ax.axvline(abs(n)*10.33916924,color='k',ls='--'); ax.set_xlabel('F (T)'); ax.legend()
 for t in on.tones: axs[1,1].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
 axs[1,1].set_yscale('log');axs[1,1].axhline(5,color='k'); axs[1,1].legend(fontsize=7);axs[1,1].set_xlabel('B (T)');axs[1,1].set_ylabel('matched filter SNR')
 axs[0,0].set_xlabel('B (T)');axs[0,0].set_ylabel('signed residual R (Ohm)');axs[0,0].legend()
 fig.suptitle(f'Run {rid}, sr1 B_1-B_2; positive field only, no B symmetrization available');fig.tight_layout();fig.savefig(out/f'spot_{rid}_fft.png',dpi=140);plt.show()
r=open_run('data/6');ch={c.cid:c for c in resolve_channels(r.meta)}
B=r.col('magnet_field');R=r.col('sr1_X')/ch['sr1'].gain/(r.col('sr0_X')/ch['sr0'].gain)
print('Local onset audit: restrict the background fit below the large high-field MR feature')
for hi,deg in [(4,5),(5,3),(5,5),(6,5)]:
 on=sdh_onset(R,B,b_hi=hi,bg_degree=deg,r_full_scale=5000)
 print(f'B_hi={hi}, degree={deg}: '+on.summary())
