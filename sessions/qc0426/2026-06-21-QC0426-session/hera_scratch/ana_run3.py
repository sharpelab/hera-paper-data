import os, numpy as np, hera.analysis as a
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
MDIR = r"C:\Users\DGG\VTI_local_data\zack\20260621-QC0426"
run = a.open_run(os.path.join(MDIR,"data","3"))
B=run.col("magnet_field"); I=run.col("sr0_X")/(-1e6)
R1=run.col("sr1_X")/I; R2=run.col("sr2_X")/I; Rxy=run.col("sr3_X")/I
o=np.argsort(B); B,R1,R2,Rxy=B[o],R1[o],R2[o],Rxy[o]
lf=(B>0.25)&(B<1.2); sl=np.polyfit(B[lf],Rxy[lf],1)[0]; n_hall=1/(1.602e-19*abs(sl)); FL=float(a.luttinger_frequency(3e16))
print("electron: no-clip sr1max=%.0f ohm; Hall n=%.2fe12 (gate 3.0); F_L=%.0fT; onset=%.2fT"%(np.abs(R1).max(), n_hall/1e16, FL, getattr(a.sdh_onset(R1,B),'onset_b',np.nan)))
def fft(R,lo): f,m=a.sdh_fft(R.reshape(-1,1),B,b_range=(lo,7.9),bg_degree=5); return f,m[0]
def pk(f,m):
    s=f>4;fs,ms=f[s],m[s];p,_=find_peaks(ms,prominence=ms.max()*0.12);p=p[np.argsort(ms[p])[::-1][:5]]
    return sorted([(round(float(fs[i]),1),round(float(ms[i]/ms.max()),2)) for i in p])
for lo in (0.8,1.5): f,m=fft(R1,lo); print(f"  sr1 cut={lo}: {pk(f,m)}")
f1,m1=fft(R1,1.0)
fig,ax=plt.subplots(1,2,figsize=(12,4.4))
ax[0].plot(B,R1,label="sr1");ax[0].plot(B,R2,label="sr2");ax[0].set_xlabel("B[T]");ax[0].set_ylabel("Rxx[ohm]");ax[0].set_title("electron raw (onset~1.5T, low MR)");ax[0].legend()
ax[1].plot(f1,m1/m1[f1>4].max());ax[1].axvline(FL,c='k',ls='--',label="F_L=31");ax[1].axvline(FL/2,c='gray',ls=':',label="F_L/2")
ax[1].set_xlim(0,40);ax[1].set_xlabel("F[T]");ax[1].set_title("electron FFT cut1.0: dominant ~F_L");ax[1].legend(fontsize=8)
fig.suptitle("Run 3 electron SdH n=+3e12 D=0"); fig.tight_layout(); plt.show()
