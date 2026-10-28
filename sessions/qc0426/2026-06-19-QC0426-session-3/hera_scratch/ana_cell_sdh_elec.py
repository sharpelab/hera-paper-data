# Run 3 — SdH spot check, ELECTRON n=+5e12 D=0. Clean (no clip), FFT window [1,4] T (alias-free).
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

run = open_run("data/3")
B = np.asarray(run.col("magnet_mag")); I = np.asarray(run.col("sr0_X"))/1e6
R = {ch: np.asarray(run.col(f"{ch}_X"))/I for ch in ("sr1","sr2","sr3")}
F_L = float(luttinger_frequency(5e16)); lo,hi = 1.0, 4.0
print(f"F_L={F_L:.1f} T; no clip (maxR sr1={np.abs(R['sr1']).max():.0f} sr2={np.abs(R['sr2']).max():.0f} Ω)")
def fft(ch,l,h):
    f,P=sdh_fft(np.abs(R[ch])[:,None],B,b_range=(l,h),detrend=5,window="hann",log=False); return f,P[0]

fig,ax=plt.subplots(1,3,figsize=(16,4.4))
m=(B>=lo)&(B<=hi)
for ch,c in (("sr1","C0"),("sr2","C1")):
    Rm=np.abs(R[ch])[m]; ax[0].plot(B[m],Rm-np.polyval(np.polyfit(B[m],Rm,5),B[m]),"-",lw=.7,color=c,label=ch)
ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("ΔRxx Ω"); ax[0].set_title("ΔRxx [1,4]T (beating = 2 tones)"); ax[0].legend(); ax[0].grid(alpha=.3)
for ch,c in (("sr1","C0"),("sr2","C1")):
    f,P=fft(ch,lo,hi); ax[1].plot(f,P/P.max(),"-",color=c,lw=1.2,label=ch)
ax[1].axvline(F_L,color="k",ls="--",lw=.8,label=f"F_L={F_L:.0f}"); ax[1].set_xlim(0,1.4*F_L)
ax[1].set_xlabel("SdH freq (T)"); ax[1].set_ylabel("FFT (norm)"); ax[1].set_title("1/B FFT: ~8T + ~44-52T cluster"); ax[1].legend(); ax[1].grid(alpha=.3)
for (l,h),c in (((1.0,4.0),"C0"),((1.5,4.0),"C3"),((2.0,4.0),"C4")):
    f,P=fft("sr1",l,h); ax[2].plot(f,P/P.max(),"-",lw=1,color=c,label=f"[{l},{h}]T")
ax[2].axvline(F_L,color="k",ls="--",lw=.8); ax[2].set_xlim(0,1.4*F_L)
ax[2].set_xlabel("SdH freq (T)"); ax[2].set_ylabel("FFT (norm)"); ax[2].set_title("sr1 window-stability"); ax[2].legend(); ax[2].grid(alpha=.3)
plt.show()
for ch in ("sr1","sr2"):
    f,P=fft(ch,lo,hi); bd=(f>2.5)&(f<1.4*F_L); fb,Pb=f[bd],P[bd]; seen=[]
    for k in np.argsort(Pb)[::-1]:
        if all(abs(fb[k]-s)>2.5 for s in seen): seen.append(fb[k])
        if len(seen)>=4: break
    print(f"{ch} tones (T):", [f"{s:.1f}" for s in seen])
