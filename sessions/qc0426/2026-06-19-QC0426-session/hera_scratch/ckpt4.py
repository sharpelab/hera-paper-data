import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d="data/4"
cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else c+f".{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']; th=np.arctan2(np.median(Y),np.median(X))
    return (X*np.cos(th)+Y*np.sin(th))/I, (-X*np.sin(th)+Y*np.cos(th))/I
R1,_=proj('sr1'); R2,q2=proj('sr2')
m=B>0.02; o=np.argsort(B[m]); B=B[m][o]; R1=R1[m][o]; R2=R2[m][o]; q2=q2[m][o]
print(f"B {B.min():.2f}-{B.max():.2f}T  n={len(B)}  quad-noise sr2={np.std(np.diff(q2))/np.sqrt(2):.2f} Ohm")
fig,ax=plt.subplots(2,1,figsize=(9,7))
ax[0].plot(B,R2,'.-',ms=3,label='sr2'); ax[0].plot(B,R1,'.-',ms=3,alpha=.7,label='sr1')
ax[0].set_xlabel('B(T)'); ax[0].set_ylabel('Rxx (Ohm)'); ax[0].legend(); ax[0].grid(alpha=.3); ax[0].set_title('data/4 (20nA) Rxx(B) hole n=-10e12')
sel=B>1.8
for nm,R,c in [('sr2',R2,'C0'),('sr1',R1,'C1')]:
    Rs=R[sel]; Bs=B[sel]; p=np.polyfit(Bs,Rs,4); dR=Rs-np.polyval(p,Bs)
    ax[1].plot(1/Bs,dR,'.-',ms=3,label=nm+' dRxx',color=c)
ax[1].set_xlabel('1/B (1/T)'); ax[1].set_ylabel('dRxx (Ohm)'); ax[1].legend(); ax[1].grid(alpha=.3); ax[1].set_title('dRxx vs 1/B [1.8-4T] (look for periodicity)')
plt.tight_layout(); plt.savefig('hera_scratch/ckpt4.png',dpi=110); print("saved")
