import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks
d="data/6"
cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else c+f".{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']; th=np.arctan2(np.median(Y),np.median(X))
    return (X*np.cos(th)+Y*np.sin(th))/I, (-X*np.sin(th)+Y*np.cos(th))/I
R2,q2=proj('sr2'); R1,q1=proj('sr1')
m=B>0.02; o=np.argsort(B[m]); B=B[m][o]; R2=R2[m][o]; R1=R1[m][o]; q2=q2[m][o]
FL=cst.h*5e16/(4*cst.e); noise=np.std(np.diff(q2))/np.sqrt(2)
print(f"n=-5e12 F_L={FL:.0f}T  B {B.min():.2f}-{B.max():.2f}T  quad-noise={noise:.2f} Ohm")
sel=(B>=5.5)&(B<=8); Bw=B[sel]
for nm,R in [('sr2',R2),('sr1',R1)]:
    Rw=R[sel]; p=np.polyfit(Bw,Rw,3); dR=Rw-np.polyval(p,Bw)
    print(f"  {nm} [{Bw.min():.1f}-{Bw.max():.1f}T]: dRxx amp={np.std(dR):.1f} Ohm  SNR={np.std(dR)/noise:.1f}")
fig,ax=plt.subplots(2,1,figsize=(9,6))
ax[0].plot(B,R2,'.-',ms=3,label='sr2'); ax[0].plot(B,R1,'.-',ms=3,alpha=.6,label='sr1')
ax[0].set_xlabel('B(T)'); ax[0].set_ylabel('Rxx'); ax[0].legend(); ax[0].grid(alpha=.3); ax[0].set_title(f'data/6 n=-5e12 Rxx(B) down to {B.min():.1f}T')
p=np.polyfit(Bw,R2[sel],3); dR=R2[sel]-np.polyval(p,Bw)
ax[1].plot(1/Bw,dR,'.-',ms=4); ax[1].set_xlabel('1/B'); ax[1].set_ylabel('sr2 dRxx'); ax[1].grid(alpha=.3); ax[1].set_title('dRxx vs 1/B [5.5-8T] -- periodic?')
plt.tight_layout(); plt.savefig('hera_scratch/ckpt6.png',dpi=110); print("saved")
