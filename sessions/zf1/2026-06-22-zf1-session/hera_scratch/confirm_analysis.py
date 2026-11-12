import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, GateCalibration

rid = sys.argv[1] if len(sys.argv)>1 else "4"
run = open_run(f"data/{rid}"); print(summarize_run(run)); print("interrupted:", run.interrupted)
v = np.load("hera_scratch/confirm_vectors.npz"); vtg=v["vtg"]; vbg=v["vbg"]; seg=v["seg"]
cal = GateCalibration.from_thicknesses(23.6e-9,20e-9,0)
N = cal.density(vtg,vbg)/1e15; D = cal.displacement_field(vtg,vbg)/1e9

I  = run.col("sr830_1_X")/(-1e6); v3 = run.col("sr830_3_X")/100.0; P3=run.col("sr830_3_P")
Rxx = np.abs(v3/I)
itg=run.col("k_tg_curr"); ibg=run.col("k_bg_curr")
m=min(len(Rxx),len(seg)); Rxx,N,D,seg,P3=Rxx[:m],N[:m],D[:m],seg[:m],P3[:m]
print(f"rows {len(Rxx)} (expected {len(vtg)}); leakage |Itg|max={np.abs(itg).max():.1e} |Ibg|max={np.abs(ibg).max():.1e}")
print(f"current med={np.median(I)*1e9:.3f} nA")

fig, ax = plt.subplots(1,2,figsize=(13,5))
print("\n--- constant-D linecuts ---")
gmin=(1e9,None)
for D0 in (-0.55,-0.60,-0.65):
    s=np.isclose(D,D0,atol=0.01);
    if s.sum()==0: continue
    o=np.argsort(N[s]); n_s=N[s][o]; R_s=Rxx[s][o]
    k=np.argmin(R_s)
    print(f"  D={D0:+.2f}: Rxx min={R_s.min():.2f} Ω @ n={n_s[k]:+.2f}e11  (phase {P3[s][o][k]:+.1f}°)")
    if R_s.min()<gmin[0]: gmin=(R_s.min(), (n_s[k],D0))
    ax[0].plot(n_s,R_s,marker=".",ms=4,label=f"D={D0:+.2f}")
ax[0].set_xlabel("n (1e11 cm⁻²)"); ax[0].set_ylabel("R_4T (Ω)"); ax[0].axhline(0,color="k",lw=.5)
ax[0].set_title(f"Run {rid}: confirm linecuts (200 µV)"); ax[0].legend(); ax[0].grid(alpha=.3)
# edge segment: Rxx vs D (max-|D| boundary)
se=seg=="edge"
if se.sum():
    o=np.argsort(D[se]);
    ax[1].plot(D[se][o], Rxx[se][o], "o-", ms=4, color="purple")
    ax[1].set_xlabel("D (V/nm)"); ax[1].set_ylabel("R_4T (Ω)")
    ax[1].set_title("edge sweep (BG=+4.198): Rxx vs D"); ax[1].grid(alpha=.3)
    ke=np.argmin(Rxx[se]); print(f"  edge: Rxx min={Rxx[se].min():.2f} Ω @ D={D[se][ke]:+.3f}, n={N[se][ke]:+.2f}e11")
fig.tight_layout(); fig.savefig(f"hera_scratch/confirm_run{rid}.png", dpi=120)
print(f"\nGLOBAL Rxx min = {gmin[0]:.2f} Ω at (n,D)={gmin[1]}")
print(f"  floor check: 200µV sens resolution ~0.07 Ω; Rxx min {'~0 (SC-lean)' if gmin[0]<1 else 'finite (failed-SC/anom-metal watch)'}")
print(f"saved hera_scratch/confirm_run{rid}.png")
