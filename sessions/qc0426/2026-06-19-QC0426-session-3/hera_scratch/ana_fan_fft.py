import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

run = open_run("data/4"); md = json.load(open("data/4/metadata.json"))
cols = md["columns"]; ci = {c:i for i,c in enumerate(cols)}
NB = len(md["slow_setpoints"][0]) if isinstance(md["slow_setpoints"][0],list) else len(md["slow_setpoints"])
NF = len(md["fast_setpoints"][0])
A = np.column_stack([run.col(c) for c in cols]).reshape(NB, NF, len(cols))
B = A[:,0,ci["magnet_mag"]]
I = A[:,:,ci["sr0_X"]]/1e6
c_tg,c_bg,n_off = 1.7027e-3,2.2004e-3,-1.581e15
n_des = (c_tg*A[0,:,ci["DC_bias"]] + c_bg*A[0,:,ci["k_2400_volt"]])/1.602176634e-19 + n_off  # m^-2
print(f"fan {NB} B x {NF} n; B {B.min():.2f}-{B.max():.2f} T; n {n_des.min()/1e16:.2f}-{n_des.max()/1e16:.2f} e12")
print("leakage |I_bg|max=%.2e |I_si|max=%.2e A" % (np.abs(A[:,:,ci["k_2400_curr"]]).max(), np.abs(A[:,:,ci["k_2410_curr"]]).max()))

lo, hi = 1.0, 4.0
F_L = luttinger_frequency(np.abs(n_des))   # per-column Luttinger freq

fig, axes = plt.subplots(1, 2, figsize=(15, 5.2), constrained_layout=True)
for ax, ch in zip(axes, ("sr1","sr2")):
    Rg = np.abs(A[:,:,ci[f"{ch}_X"]]/I)              # (NB, NF)
    clipped = Rg.max(axis=0) > 540
    f, spec = sdh_fft(Rg, B, b_range=(lo,hi), detrend=5, window="hann", log=False)  # spec (NF, nf)
    S = spec.copy()
    for j in range(NF):
        S[j] = S[j]/S[j].max() if not clipped[j] and S[j].max()>0 else 0.0
    fmax = 70
    sel = f <= fmax
    im = ax.pcolormesh(n_des/1e16, f[sel], S[:,sel].T, shading="auto", cmap="magma")
    ax.plot(n_des/1e16, F_L, "c--", lw=1.2, label="F_L=(h/4e)n")
    ax.plot(n_des[clipped]/1e16, np.full(clipped.sum(), 2), "rx", ms=4, label="clipped col")
    fig.colorbar(im, ax=ax, label="FFT power (col-norm)")
    ax.set_xlabel("n (1e12 cm^-2)"); ax.set_ylabel("SdH freq F (T)"); ax.set_title(f"{ch}: per-column 1/B FFT [{lo},{hi}]T"); ax.legend(loc="upper left", fontsize=8)
fig.suptitle("Run 4 fan — F(n) per column vs F_L (electron, D=0)")
fig.savefig("hera_scratch/fan_fft_map.png", dpi=115)
print("saved hera_scratch/fan_fft_map.png")

# per-column peak extraction (sr1), unclipped columns
Rg = np.abs(A[:,:,ci["sr1_X"]]/I); clipped = Rg.max(axis=0) > 540
f, spec = sdh_fft(Rg, B, b_range=(lo,hi), detrend=5, window="hann", log=False)
print("\nn[e12]  F_L   sr1 peaks (T, relpow>0.25)  | partition")
for j in range(0, NF, 4):
    if clipped[j]: continue
    P = spec[j]; band=(f>2.5)&(f<1.35*F_L[j]); fb,Pb=f[band],P[band]
    if len(Pb)==0: continue
    pk=[]
    for k in np.argsort(Pb)[::-1]:
        if all(abs(fb[k]-q[0])>2.5 for q in pk): pk.append((fb[k],Pb[k]/Pb.max()))
        if len(pk)>=3: break
    pk=[p for p in pk if p[1]>0.25]
    tones=sorted(t for t,_ in pk)
    s=", ".join(f"{t:.1f}({p:.2f})" for t,p in sorted(pk))
    part = f"sum={sum(tones):.0f} vs F_L={F_L[j]:.0f}" if len(tones)>=2 else ""
    print(f"{n_des[j]/1e16:5.2f}  {F_L[j]:4.0f}   {s:34s} {part}")
