import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import scipy.constants as cst
d="data/3"
cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={};  # handle duplicate magnet_mag: take first
seen={}
for i,c in enumerate(cols):
    key=c if c not in seen else c+f"_{seen[c]}"
    seen[c]=seen.get(c,0)+1
    C[key]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
R1=C['sr1_R']/I; R2=C['sr2_R']/I
m=B>0.02; o=np.argsort(B[m]); B=B[m][o]; R1=R1[m][o]; R2=R2[m][o]
n=cst.h*10e16/(4*cst.e); FL=cst.h*10e16/(4*cst.e)  # n=10e12 cm^-2 =10e16 m^-2
print(f"F_L (n=10e12) = {FL:.0f} T")
Bfloor=1.76  # Nyquist floor for dB=10mT @ F=103

def analyze(B,R,name,Blo):
    sel=(B>=Blo)&(B<=4.0)
    Bs=B[sel]; Rs=R[sel]
    # MR background: 5th order poly in B
    p=np.polyfit(Bs,Rs,5); dR=Rs-np.polyval(p,Bs)
    # resample uniform in 1/B
    invB=1/Bs; 
    order=np.argsort(invB); invB=invB[order]; dRo=dR[order]
    ub=np.linspace(invB.min(),invB.max(),2048)
    dRi=np.interp(ub,invB,dRo)
    win=np.hanning(len(dRi)); 
    F=np.fft.rfftfreq(len(ub), d=(ub[1]-ub[0]))
    A=np.abs(np.fft.rfft((dRi-dRi.mean())*win))
    # peaks
    from scipy.signal import find_peaks
    pk,_=find_peaks(A, height=A.max()*0.15, distance=3)
    pk=pk[(F[pk]>3)&(F[pk]<300)]
    pk=pk[np.argsort(A[pk])[::-1]]
    print(f"\n{name}: window [{Blo:.2f},4.0]T  {sel.sum()}pts  dF~{1/(invB.max()-invB.min()):.1f}T")
    print(f"  top peaks (T): "+", ".join(f"{F[k]:.0f}(A{A[k]/A[pk].max():.2f})" for k in pk[:6]))
    return Bs,dR,F,A,pk

fig,ax=plt.subplots(2,2,figsize=(12,8))
for col,(name,R) in enumerate([('sr2 B4-B5',R2),('sr1 T3-T4',R1)]):
    Bs,dR,F,A,pk=analyze(B,R,name,Bfloor)
    ax[0,col].plot(Bs,dR,'.-',ms=2); ax[0,col].set_title(f'{name} dRxx(B) [{Bfloor}-4T]'); ax[0,col].set_xlabel('B(T)'); ax[0,col].grid(alpha=.3)
    ax[1,col].plot(F,A); ax[1,col].axvline(FL,color='r',ls='--',label=f'F_L={FL:.0f}T')
    for k in pk[:5]: ax[1,col].annotate(f'{F[k]:.0f}',(F[k],A[k]))
    ax[1,col].set_xlim(0,250); ax[1,col].set_xlabel('F (T)'); ax[1,col].set_title(f'{name} 1/B FFT'); ax[1,col].legend(); ax[1,col].grid(alpha=.3)
plt.suptitle('QC0426 data/3 hole n=-10e12 SdH FFT')
plt.tight_layout(); plt.savefig('hera_scratch/fft3.png',dpi=110)
print("\nsaved fft3.png")
