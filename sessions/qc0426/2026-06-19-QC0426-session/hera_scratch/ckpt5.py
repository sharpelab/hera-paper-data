import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d="data/5"
cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else c+f".{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']; th=np.arctan2(np.median(Y),np.median(X))
    return (X*np.cos(th)+Y*np.sin(th))/I, (-X*np.sin(th)+Y*np.cos(th))/I
R2,q2=proj('sr2'); R1,_=proj('sr1')
m=B>0.02; o=np.argsort(B[m]); B=B[m][o]; R2=R2[m][o]; R1=R1[m][o]; q2=q2[m][o]
print(f"B {B.min():.2f}-{B.max():.2f}T  quad-noise sr2={np.std(np.diff(q2))/np.sqrt(2):.2f} Ohm")
# look at highest-field third for oscillations
sel=B>(B.max()-1.2)
Bs=B[sel]; R2s=R2[sel]
p=np.polyfit(Bs,R2s,2); dR=R2s-np.polyval(p,Bs)
print(f"top window [{Bs.min():.2f},{Bs.max():.2f}]T: sr2 dRxx amp={np.std(dR):.2f} Ohm")
fig,ax=plt.subplots(2,1,figsize=(9,6))
ax[0].plot(B,R2,'.-',ms=3,label='sr2'); ax[0].plot(B,R1,'.-',ms=2,alpha=.6,label='sr1')
ax[0].set_xlabel('B(T)'); ax[0].set_ylabel('Rxx'); ax[0].legend(); ax[0].grid(alpha=.3); ax[0].set_title(f'data/5 partial Rxx(B) up to {B.max():.1f}T')
ax[1].plot(Bs,dR,'.-',ms=3); ax[1].set_xlabel('B(T)'); ax[1].set_ylabel('sr2 dRxx (quad bg)'); ax[1].grid(alpha=.3); ax[1].set_title('high-field dRxx')
plt.tight_layout(); plt.savefig('hera_scratch/ckpt5.png',dpi=110); print("saved")
