import os, numpy as np, hera.analysis as a
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
MDIR = r"C:\Users\DGG\VTI_local_data\zack\20260621-QC0426"
run = a.open_run(os.path.join(MDIR, "data", "2"))
B = run.col("magnet_field"); I = run.col("sr0_X")/(-1e6)
R1 = run.col("sr1_X")/I; R2 = run.col("sr2_X")/I; Rxy = run.col("sr3_X")/I
o = np.argsort(B); B,R1,R2,Rxy,I = B[o],R1[o],R2[o],Rxy[o],I[o]
print("no-clip: sr1 max |X|=%.1fuV/100uV FS; Rxx max=%.0f Ω; I=%.2f nA; interrupted=%s"
      % (np.abs(run.col("sr1_X")).max()*1e6, np.abs(R1).max(), np.median(I)*1e9, run.interrupted))
# Hall density (low-field slope) — lever-arm cross-check
lf = (B>0.25)&(B<1.2); sl = np.polyfit(B[lf],Rxy[lf],1)[0]
n_hall = 1/(1.602176634e-19*abs(sl)); FL = float(a.luttinger_frequency(3.0e16))
print("Hall n=%.2fe12 cm^-2 (gate 3.00e12; ratio %.3f);  F_L=%.1f T;  onset=%.2f T"
      % (n_hall/1e16, n_hall/3.0e16, FL, getattr(a.sdh_onset(R1,B),'onset_b',float('nan'))))
def fft(R, lo, deg=5):
    f,m = a.sdh_fft(R.reshape(-1,1), B, b_range=(lo,7.9), bg_degree=deg); return f, m[0]
f1,m1 = fft(R1,0.8); f2,m2 = fft(R2,0.8)
def peaks(f,m):
    s=f>4; fs,ms=f[s],m[s]; p,_=find_peaks(ms,prominence=ms.max()*0.1)
    p=p[np.argsort(ms[p])[::-1][:5]]; return sorted([(round(float(fs[i]),1),round(float(ms[i]/ms.max()),2)) for i in p])
print("sr1 tones (cut0.8):", peaks(f1,m1), " sr2 tones:", peaks(f2,m2))
print("Model @n=3e12 D=0: ABA=[1.5, 29.5] sum31 (2 FS); ABC=[31] (1 FS)")
fig,ax=plt.subplots(1,3,figsize=(16,4.4))
ax[0].plot(B,R1,label="sr1");ax[0].plot(B,R2,label="sr2");ax[0].plot(B,-Rxy,label="-Rxy",alpha=.6)
ax[0].set_xlabel("B [T]");ax[0].set_ylabel("R [Ω]");ax[0].set_title("Raw R(B) — no clip");ax[0].legend()
m=B>0.8; bb=B[m]; dr=R1[m]-np.polyval(np.polyfit(bb,R1[m],5),bb)
ax[1].plot(1/bb,dr);ax[1].set_xlabel("1/B [1/T]");ax[1].set_ylabel("ΔRxx sr1 [Ω]");ax[1].set_title("SdH vs 1/B")
ax[2].plot(f1,m1/m1[f1>4].max(),label="sr1");ax[2].plot(f2,m2/m2[f2>4].max(),label="sr2")
ax[2].axvline(FL,c='k',ls='--',label=f"F_L={FL:.0f}T");ax[2].axvline(FL/2,c='gray',ls=':',label="F_L/2")
ax[2].set_xlim(0,40);ax[2].set_xlabel("F [T]");ax[2].set_ylabel("FFT (norm)");ax[2].set_title("1/B FFT (cut 0.8T)");ax[2].legend(fontsize=8)
fig.suptitle("Run 2 — hole SdH n=-3e12 D=0: two tones ~12 & ~16 T sum~F_L (ABA-leaning)")
fig.tight_layout(); plt.show()
