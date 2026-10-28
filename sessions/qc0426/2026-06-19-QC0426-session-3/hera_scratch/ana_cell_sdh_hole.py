# Run 2 — SdH spot check, HOLE n=-5e12 D=0. RAW Rxx(B) then 1/B FFT vs F_L.
# Caveats baked in: sr1/sr2 CLIP at 109 Ω (2e-6 sat) above 2.31 T -> FFT window capped there;
# 8 mT step under-samples F_L=52 T below ~1 T -> FFT window floored at 1.0 T (alias-free).
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

run = open_run("data/2")
B = np.asarray(run.col("magnet_mag")); I = np.asarray(run.col("sr0_X"))/1e6
R = {ch: np.asarray(run.col(f"{ch}_X"))/I for ch in ("sr1","sr2")}
F_L = float(luttinger_frequency(5e16)); print(f"F_L(n=5e12) = {F_L:.1f} T")
B_clip = B[np.abs(R["sr1"])<108].max(); onset = 1.0     # alias-free floor
print(f"clip edge {B_clip:.2f} T; FFT window [{onset}, {B_clip:.2f}] T  d(1/B)={1/onset-1/B_clip:.3f} dF~{1/(1/onset-1/B_clip):.1f} T")

fig, ax = plt.subplots(1, 3, figsize=(16, 4.4))
for ch,c in (("sr1","C0"),("sr2","C1")):
    ax[0].plot(B, np.abs(R[ch]), ".-", ms=2, color=c, label=ch)
ax[0].axvline(B_clip,color="r",ls="--",lw=.8); ax[0].axvline(onset,color="g",ls=":",lw=.8)
ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("|Rxx| Ω"); ax[0].set_title("raw Rxx(B), hole n=-5e12 (clip@2.3T)"); ax[0].legend(); ax[0].grid(alpha=.3)
for ch,c in (("sr1","C0"),("sr2","C1")):
    m=(B>=onset)&(B<=B_clip)
    Rm=np.abs(R[ch])[m]; ax[1].plot(B[m], Rm-np.polyval(np.polyfit(B[m],Rm,5),B[m]),"-",color=c,lw=.8,label=ch)
    f,P=sdh_fft(np.abs(R[ch])[:,None],B,b_range=(onset,B_clip),detrend=5,window="hann",log=False)
    ax[2].plot(f,P[0]/P[0].max(),"-",color=c,lw=1,label=ch)
ax[1].set_xlabel("B (T)"); ax[1].set_ylabel("ΔRxx Ω"); ax[1].set_title(f"ΔRxx [{onset},{B_clip:.1f}]T"); ax[1].legend(); ax[1].grid(alpha=.3)
ax[2].axvline(F_L,color="k",ls="--",lw=.8,label=f"F_L={F_L:.0f}T"); ax[2].set_xlim(0,1.4*F_L)
ax[2].set_xlabel("SdH freq (T)"); ax[2].set_ylabel("FFT (norm)"); ax[2].set_title("1/B FFT vs F_L"); ax[2].legend(); ax[2].grid(alpha=.3)
plt.show()
f,P=sdh_fft(np.abs(R["sr1"])[:,None],B,b_range=(onset,B_clip),detrend=5,window="hann",log=False); P=P[0]
band=(f>3)&(f<1.4*F_L); fb,Pb=f[band],P[band]; seen=[]
for k in np.argsort(Pb)[::-1]:
    if all(abs(fb[k]-s)>3 for s in seen): seen.append(fb[k])
    if len(seen)>=4: break
print("sr1 top tones (T):", [f"{s:.1f}" for s in seen], " | pair sum check: 8.5+44 = 52.5 ~ F_L")
