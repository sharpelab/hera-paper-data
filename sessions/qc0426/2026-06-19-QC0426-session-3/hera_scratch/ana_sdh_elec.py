import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

run = open_run("data/3")
B = np.asarray(run.col("magnet_mag")); I = np.asarray(run.col("sr0_X"))/1e6
R = {ch: np.asarray(run.col(f"{ch}_X"))/I for ch in ("sr1","sr2","sr3")}
F_L = float(luttinger_frequency(5e16)); print(f"n=+5e12  F_L = {F_L:.1f} T")
print("clip check: sr1 maxR=%.0f sr2 maxR=%.0f sr3 maxR=%.0f Ω (sens ceilings 500/500/1000)"
      % (np.abs(R['sr1']).max(), np.abs(R['sr2']).max(), np.abs(R['sr3']).max()))

def peaks(ch, lo, hi):
    f,P = sdh_fft(np.abs(R[ch])[:,None], B, b_range=(lo,hi), detrend=5, window="hann", log=False)
    return f, P[0]

fig, ax = plt.subplots(2, 2, figsize=(14, 9))
# raw
for ch,c in (("sr1","C0"),("sr2","C1")):
    ax[0,0].plot(B, np.abs(R[ch]), "-", lw=.6, color=c, label=f"{ch} Rxx")
ax[0,0].plot(B, np.abs(R["sr3"]), "-", lw=.6, color="C2", label="sr3 Rxy")
ax[0,0].set_xlabel("B (T)"); ax[0,0].set_ylabel("R (Ω)"); ax[0,0].legend(); ax[0,0].set_title("Run 3 raw, electron n=+5e12 (no clip)"); ax[0,0].grid(alpha=.3)
# dRxx
lo,hi = 1.0, 4.0
for ch,c in (("sr1","C0"),("sr2","C1")):
    m=(B>=lo)&(B<=hi); Rm=np.abs(R[ch])[m]
    ax[0,1].plot(B[m], Rm-np.polyval(np.polyfit(B[m],Rm,5),B[m]), "-", lw=.7, color=c, label=ch)
ax[0,1].set_xlabel("B (T)"); ax[0,1].set_ylabel("ΔRxx (Ω)"); ax[0,1].legend(); ax[0,1].set_title(f"ΔRxx [{lo},{hi}]T"); ax[0,1].grid(alpha=.3)
# FFT both Rxx, full window
for ch,c in (("sr1","C0"),("sr2","C1")):
    f,P = peaks(ch, lo, hi); ax[1,0].plot(f, P/P.max(), "-", color=c, lw=1.2, label=ch)
ax[1,0].axvline(F_L,color="k",ls="--",lw=.8,label=f"F_L={F_L:.0f}T"); ax[1,0].set_xlim(0,1.4*F_L)
ax[1,0].set_xlabel("SdH freq (T)"); ax[1,0].set_ylabel("FFT (norm)"); ax[1,0].set_title(f"1/B FFT [{lo},{hi}]T"); ax[1,0].legend(); ax[1,0].grid(alpha=.3)
# stability sweep on sr1
for (l,h),c in ((( 1.0,4.0),"C0"),((1.5,4.0),"C3"),((2.0,4.0),"C4")):
    f,P = peaks("sr1", l, h); ax[1,1].plot(f, P/P.max(), "-", color=c, lw=1, label=f"[{l},{h}]T")
ax[1,1].axvline(F_L,color="k",ls="--",lw=.8); ax[1,1].set_xlim(0,1.4*F_L)
ax[1,1].set_xlabel("SdH freq (T)"); ax[1,1].set_ylabel("FFT (norm)"); ax[1,1].set_title("sr1 FFT window-stability"); ax[1,1].legend(); ax[1,1].grid(alpha=.3)
fig.suptitle(f"Run 3 SdH FFT — electron n=+5e12, F_L={F_L:.0f}T")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_elec_run3.png", dpi=110)

# peak report per channel, full window
for ch in ("sr1","sr2"):
    f,P = peaks(ch, lo, hi); band=(f>2.5)&(f<1.4*F_L); fb,Pb=f[band],P[band]
    seen=[]
    for k in np.argsort(Pb)[::-1]:
        if all(abs(fb[k]-s[0])>2.5 for s in seen): seen.append((fb[k],Pb[k]/Pb.max()))
        if len(seen)>=5: break
    print(f"{ch} top tones (T,relpow):", [f"{a:.1f}({b:.2f})" for a,b in seen])
print(f"window [{lo},{hi}]T  Δ(1/B)={1/lo-1/hi:.3f}  δF~{1/(1/lo-1/hi):.2f} T")
print("saved hera_scratch/sdh_elec_run3.png")
