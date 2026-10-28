import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

run = open_run("data/2")
B = np.asarray(run.col("magnet_mag"))
I = np.asarray(run.col("sr0_X"))/1e6
R = {ch: np.asarray(run.col(f"{ch}_X"))/I for ch in ("sr1","sr2")}
n_target = -5e16
F_L = float(luttinger_frequency(abs(n_target)))   # (h/4e)|n|
print(f"n=-5e12  F_L=(h/4e)|n| = {F_L:.1f} T")

# clip edge: where |R| pins at the 109 ohm ceiling (2e-6 sat). Use unclipped B only.
clipR = 108.0
unclip = np.abs(R["sr1"]) < clipR
B_clip = B[unclip].max() if unclip.any() else B.max()
print(f"clip ceiling ~109 Ω; last unclipped B = {B_clip:.2f} T")

fig, ax = plt.subplots(2, 2, figsize=(13, 8))
# raw R(B)
for ch,c in (("sr1","C0"),("sr2","C1")):
    ax[0,0].plot(B, np.abs(R[ch]), ".-", ms=2, color=c, label=ch)
ax[0,0].axvline(B_clip, color="r", ls="--", lw=.8, label=f"clip {B_clip:.1f}T")
ax[0,0].set_xlabel("B (T)"); ax[0,0].set_ylabel("|Rxx| (Ω)"); ax[0,0].legend(); ax[0,0].set_title("Run 2 raw Rxx(B), hole n=-5e12")
ax[0,0].grid(alpha=.3)

# background-subtracted dRxx vs 1/B over [onset, B_clip], per channel; FFT
onset = 0.8
for ch,c in (("sr1","C0"),("sr2","C1")):
    m = (B>=onset)&(B<=B_clip)
    Bm, Rm = B[m], np.abs(R[ch])[m]
    p = np.polyfit(Bm, Rm, 5); dR = Rm - np.polyval(p, Bm)
    ax[0,1].plot(Bm, dR, "-", color=c, lw=.8, label=f"{ch} ΔRxx")
    f, P = sdh_fft(np.abs(R[ch])[:,None], B, b_range=(onset, B_clip), detrend=5, window="hann", log=False)
    P = P[0]
    ax[1,0].plot(f, P/P.max(), "-", color=c, lw=1, label=ch)
ax[0,1].set_xlabel("B (T)"); ax[0,1].set_ylabel("ΔRxx (Ω, 5th-poly removed)"); ax[0,1].legend(); ax[0,1].set_title(f"ΔRxx over [{onset},{B_clip:.1f}] T"); ax[0,1].grid(alpha=.3)
ax[1,0].axvline(F_L, color="k", ls="--", lw=.8, label=f"F_L={F_L:.0f}T")
ax[1,0].set_xlim(0, 1.4*F_L); ax[1,0].set_xlabel("SdH frequency (T)"); ax[1,0].set_ylabel("FFT power (norm)"); ax[1,0].legend(); ax[1,0].set_title("1/B FFT vs F_L"); ax[1,0].grid(alpha=.3)

# peak report (sr1)
f1,P1 = sdh_fft(np.abs(R["sr1"])[:,None], B, b_range=(onset,B_clip), detrend=5, window="hann", log=False); P1=P1[0]
band=(f1>3)&(f1<1.4*F_L); fb,Pb=f1[band],P1[band]
order=np.argsort(Pb)[::-1]
print("sr1 top FFT peaks (T, rel-power):")
seen=[]
for k in order[:12]:
    if all(abs(fb[k]-s)>3 for s in seen):
        seen.append(fb[k]); print(f"   {fb[k]:6.1f} T   {Pb[k]/Pb.max():.2f}")
    if len(seen)>=5: break
ax[1,1].axis("off")
ax[1,1].text(0.02,0.95,f"n=-5e12 (hole), D=0\nF_L={F_L:.1f} T\nFFT window [{onset},{B_clip:.1f}] T\n"
             f"Δ(1/B)={1/onset-1/B_clip:.3f} -> δF~{1/(1/onset-1/B_clip):.1f} T\n"
             f"top sr1 tones: "+", ".join(f"{s:.0f}" for s in seen)+" T",
             va="top", fontsize=10, family="monospace")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_hole_run2.png", dpi=110)
print("saved hera_scratch/sdh_hole_run2.png  (window Δ(1/B)=%.3f, δF~%.1f T)"%(1/onset-1/B_clip, 1/(1/onset-1/B_clip)))
