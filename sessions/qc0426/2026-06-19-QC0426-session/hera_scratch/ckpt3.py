import numpy as np, os, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import json
d="data/3"
cols=json.load(open(os.path.join(d,"metadata.json"))).get("columns")
print("cols:", cols)
raw=np.genfromtxt(os.path.join(d,"data.tsv"), delimiter="\t")
print("rows:", raw.shape)
C={c:raw[:,i] for i,c in enumerate(cols)}
# field axis: the swept magnet_mag column (first match)
B = C[[c for c in cols if 'mag' in c][0]]
I = C['sr0_X']/(-1e6)
# magnitude Rxx
R1=C['sr1_R']/np.abs(I); R2=C['sr2_R']/np.abs(I); R3=C['sr3_R']/np.abs(I)
# keep ascending part B>0 (after ramp down), sort by B
m = B>0.02
B=B[m]; R1=R1[m]; R2=R2[m]; R3=R3[m]
o=np.argsort(B); B=B[o]; R1=R1[o]; R2=R2[o]; R3=R3[o]
print(f"B range {B.min():.3f}..{B.max():.3f} T, n={len(B)}")
print(f"sr2 |R|: {R2.min():.1f}..{R2.max():.1f} Ohm  median {np.median(R2):.1f}")
# background subtract (poly) and look for oscillation
fig,ax=plt.subplots(3,1,figsize=(9,9))
ax[0].plot(B,R2,'.-',ms=3,label='sr2 |R|'); ax[0].plot(B,R1,'.-',ms=2,alpha=.6,label='sr1 |R|')
ax[0].set_ylabel('Rxx |R| (Ohm)'); ax[0].legend(); ax[0].set_xlabel('B (T)'); ax[0].grid(alpha=.3)
ax[0].set_title('QC0426 data/3 partial — hole n=-10e12 Rxx(B)')
# dRxx after poly bg (5th order) over B>0.4
for nm,R,c in [('sr2',R2,'C0'),('sr1',R1,'C1')]:
    sel=B>0.3
    if sel.sum()>20:
        p=np.polyfit(B[sel],R[sel],5); dR=R[sel]-np.polyval(p,B[sel])
        ax[1].plot(B[sel],dR,'.-',ms=3,label=nm+' dRxx',color=c)
ax[1].set_ylabel('dRxx (Ohm)'); ax[1].set_xlabel('B (T)'); ax[1].legend(); ax[1].grid(alpha=.3)
ax[2].plot(B,R3,'.-',ms=3,color='C2',label='sr3 |R| Hall'); ax[2].set_ylabel('|R| Hall (Ohm)'); ax[2].set_xlabel('B (T)'); ax[2].legend(); ax[2].grid(alpha=.3)
plt.tight_layout(); plt.savefig('hera_scratch/ckpt3.png',dpi=110)
print("saved ckpt3.png")
