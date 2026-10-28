import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import sdh_fft, sdh_onset, SdhOnsetError, GateCalibration, luttinger_frequency

fig, axes = plt.subplots(2,3, figsize=(16,8))
for k,(rid,tag,nspot) in enumerate(((6,'electron n=+3.2e12',3.2),(7,'hole n=-1.2e12',-1.2))):
    B,R,T = np.load(f'hera_scratch/spot{rid}_BR.npy')
    o = np.argsort(B); B,R = B[o],R[o]
    ax=axes[k,0]; ax.plot(B,R,lw=.7); ax.set_xlabel('B (T)'); ax.set_ylabel('R (Ohm)'); ax.set_title(f'run {rid} raw — {tag}')
    # onset
    try:
        res = sdh_onset(R, B, r_full_scale=5050.)
        print('='*70); print(f'run {rid} onset:'); print(res.summary())
    except SdhOnsetError as e:
        print(f'run {rid} sdh_onset FAILED: {e}')
    # FFT over several windows
    ax=axes[k,1]
    for blo,bhi in ((1.0,10.0),(2.0,10.0),(4.0,10.0),(1.0,5.0)):
        if B.max()<bhi-0.01: continue
        f,s = sdh_fft(R[:,None], B, b_range=(blo,bhi), nfft=2048, bg_degree=5, log=False)
        s=s[0]; s=s/s.max()
        ax.plot(f,s,lw=.9,label=f'{blo}-{bhi} T')
    ax.set_xlim(0,60); ax.legend(fontsize=7); ax.set_xlabel('F (T)'); ax.set_title(f'run {rid} FFT (lin R)')
    F_L = luttinger_frequency(abs(nspot)*1e16)
    for frac,lab in ((1,'F_L'),(0.5,'F_L/2'),(0.25,'F_L/4')):
        ax.axvline(F_L*frac, color='r' if frac==1 else 'gray', ls='--', lw=.8)
    print(f'run {rid}: F_L(full deg-4) = {F_L:.2f} T ; F/2={F_L/2:.2f} F/4={F_L/4:.2f}')
    # dR after background subtract vs 1/B
    ax=axes[k,2]
    m=(B>=1.0)
    p=np.polyfit(B[m],R[m],5); dR=R[m]-np.polyval(p,B[m])
    ax.plot(1/B[m],dR,lw=.8); ax.set_xlabel('1/B (1/T)'); ax.set_ylabel('dR (Ohm)'); ax.set_title(f'run {rid} detrended')
    print(f'run {rid}: dR rms (B>1T) = {dR.std():.2f} Ohm; peak-peak {dR.max()-dR.min():.1f}')
    m2=(B>=5.0); p2=np.polyfit(B[m2],R[m2],3); dR2=R[m2]-np.polyval(p2,B[m2])
    print(f'run {rid}: dR rms (B>5T) = {dR2.std():.2f} Ohm')
plt.tight_layout(); plt.savefig('hera_scratch/spot_sdh.png',dpi=110)
print('saved hera_scratch/spot_sdh.png')
