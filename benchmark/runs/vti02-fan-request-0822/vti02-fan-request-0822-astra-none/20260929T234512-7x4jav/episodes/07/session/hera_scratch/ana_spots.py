from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_onset, sdh_fft
from scipy.signal import find_peaks
root=Path.cwd()
fig,axes=plt.subplots(2,3,figsize=(15,8))
report=[]
for row,rid in enumerate([6,7]):
 r=open_run(root/'data'/str(rid)); ch=resolve_channels(r.meta); ic=current_channel(ch); vc=next(c for c in ch if c.cid=='sr1')
 B=r.col('magnet_field'); I=r.col(ic.col)/ic.gain; V=r.col(vc.col)/vc.gain; R=V/I
 order=np.argsort(B); B=B[order]; R=R[order]
 axes[row,0].plot(r.col('magnet_field'),r.col('sr1_X')*1e6,label='sr1 X (uV)'); axes[row,0].plot(r.col('magnet_field'),I*1e9,label='I (nA)'); axes[row,0].legend(); axes[row,0].set_title(f'run {rid}: raw channels'); axes[row,0].set_xlabel('B (T)')
 axes[row,1].plot(B,R); axes[row,1].set_ylabel('signed Rxx (ohm)'); axes[row,1].set_xlabel('B (T)')
 f,sp=sdh_fft(R[:,None],B,b_range=(1,10),nfft=4096,log=False)
 axes[row,2].plot(f,sp[0]); axes[row,2].set_xlim(0,65); axes[row,2].set_xlabel('F (T), B=1..10 T'); axes[row,2].set_title('Detrended signed-R spectrum')
 peaks,_=find_peaks(sp[0]); peaks=sorted(peaks,key=lambda k:sp[0,k],reverse=True)[:6]
 lines=[f'run {rid}: R range {R.min():.2f}..{R.max():.2f} ohm; I nA {I.min()*1e9:.3f}..{I.max()*1e9:.3f}; max raw voltage {np.max(np.abs(V))*1e6:.2f} uV / 50 uV FS',f'FFT peak candidates {[round(float(f[k]),2) for k in peaks]}']
 for col in ['k_2400_tg_curr','k_2400_bg_curr','T_sample']:
  x=r.col(col); lines.append(f'{col}: {x.min():.5g}..{x.max():.5g}')
 try:
  onset=sdh_onset(np.abs(R),B,r_full_scale=5000); lines.append(onset.summary())
 except ValueError as e: lines.append(f'Onset unresolved: {e}')
 report.extend(lines)
fig.tight_layout(); plt.show()
print('\n'.join(report))
