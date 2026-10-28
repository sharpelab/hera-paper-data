import os, numpy as np, hera.analysis as a
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
MDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(MDIR, "hera_scratch")
run = a.open_run(os.path.join(MDIR, "data", "3"))
B = run.col("magnet_field"); I = run.col("sr0_X")/(-1e6)
R1 = run.col("sr1_X")/I; R2 = run.col("sr2_X")/I; Rxy = run.col("sr3_X")/I
o = np.argsort(B); B,R1,R2,Rxy,I = B[o],R1[o],R2[o],Rxy[o],I[o]
print(f"N={len(B)} B[{B.min():.2f},{B.max():.2f}] I={np.median(I)*1e9:.2f}nA; no-clip sr1max={np.abs(R1).max():.0f}ohm ({np.abs(run.col('sr1_X')).max()*1e6:.0f}/100uV)")
# Hall density (electron: Rxy positive slope)
lf=(B>0.25)&(B<1.2); sl=np.polyfit(B[lf],Rxy[lf],1)[0]
n_hall=1/(1.602176634e-19*abs(sl)); FL=float(a.luttinger_frequency(3.0e16))
print(f"Hall slope={sl:.1f} ohm/T -> n_Hall={n_hall/1e16:.2f}e12 (gate +3.00; ratio {n_hall/3e16:.3f}); F_L={FL:.1f}T; onset={getattr(a.sdh_onset(R1,B),'onset_b',float('nan'))}")
def fft(R,lo,deg=5):
    f,m=a.sdh_fft(R.reshape(-1,1),B,b_range=(lo,7.9),bg_degree=deg); return f,m[0]
def peaks(f,m):
    s=f>4; fs,ms=f[s],m[s]; p,_=find_peaks(ms,prominence=ms.max()*0.1)
    p=p[np.argsort(ms[p])[::-1][:6]]; return sorted([(round(float(fs[i]),1),round(float(ms[i]/ms.max()),2)) for i in p])
print("\n--- electron sr1 FFT peak stability ---")
for lo in (0.4,0.6,0.8,1.0):
    f,m=fft(R1,lo); print(f"  cut={lo}: {peaks(f,m)}")
print("--- sr2 ---")
for lo in (0.6,0.8): f,m=fft(R2,lo); print(f"  cut={lo}: {peaks(f,m)}")
f1,m1=fft(R1,0.8); f2,m2=fft(R2,0.8)
fig,ax=plt.subplots(1,3,figsize=(16,4.4))
ax[0].plot(B,R1,label="sr1");ax[0].plot(B,R2,label="sr2");ax[0].plot(B,Rxy,label="Rxy",alpha=.6)
ax[0].set_xlabel("B[T]");ax[0].set_ylabel("R[ohm]");ax[0].set_title("Electron raw R(B) no clip");ax[0].legend()
m=B>0.8;bb=B[m];dr=R1[m]-np.polyval(np.polyfit(bb,R1[m],5),bb)
ax[1].plot(1/bb,dr);ax[1].set_xlabel("1/B");ax[1].set_ylabel("dRxx sr1");ax[1].set_title("SdH vs 1/B")
ax[2].plot(f1,m1/m1[f1>4].max(),label="sr1");ax[2].plot(f2,m2/m2[f2>4].max(),label="sr2")
ax[2].axvline(FL,c='k',ls='--',label=f"F_L={FL:.0f}");ax[2].axvline(FL/2,c='gray',ls=':',label="F_L/2")
ax[2].set_xlim(0,40);ax[2].set_xlabel("F[T]");ax[2].set_title("electron FFT cut0.8");ax[2].legend(fontsize=8)
fig.suptitle("Run 3 electron SdH n=+3e12 D=0")
fig.tight_layout();out=os.path.join(SCR,"run3_sdh_electron.png");fig.savefig(out,dpi=110);print("saved",out)
