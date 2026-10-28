import json, gzip, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelmin, argrelmax
from sharpelab_nb.gates import stack_capacitance, calc_nD

c_tg = stack_capacitance([(15.6,3)]); c_bg = 1.3136*c_tg; n_off, D_off = -0.225, 0.0
m = json.load(open("data/20/metadata.json")); ci = {c:i for i,c in enumerate(m["columns"])}
d = np.loadtxt(gzip.open("data/20/data.tsv.gz"))
nf = len(m["fast_setpoints"][0]); B = np.array(m["slow_setpoints"][0]); nb = len(B)
d = d[:nb*nf]; Ibias = 5e-9
tgc = d[:,ci["DC_bias"]].reshape(nb,nf); bgc = d[:,ci["k_bg_volt"]].reshape(nb,nf)
nval,_ = calc_nD(tgc, bgc, c_tg, c_bg, n_off, D_off); n_axis = nval[0]
def Rg(ch): return np.abs(d[:,ci[ch]].reshape(nb,nf))/Ibias
def Sg(ch): return (d[:,ci[ch]].reshape(nb,nf))/Ibias       # signed (for Rxy)
R1,R2 = Rg("sr1_X"), Rg("sr2_X"); Rxy = Sg("sr3_X")
print(f"fan {nb}x{nf}, B {B.min()}-{B.max()} T, n {n_axis.min():+.2f}..{n_axis.max():+.2f}")

# ---- fan images ----
fig, ax = plt.subplots(1,3, figsize=(17,5))
for a,(R,lab,signed) in zip(ax,[(R1,"sr1 T3-T4 Rxx",0),(R2,"sr2 B4-B5 Rxx",0),(Rxy,"sr3 T5-B6 Rxy",1)]):
    if signed:
        v=np.percentile(np.abs(R),99); im=a.pcolormesh(n_axis,B,R,shading="nearest",cmap="RdBu_r",vmin=-v,vmax=v)
    else:
        vmin=max(R[R>0].min(),20); im=a.pcolormesh(n_axis,B,np.clip(R,vmin,None),shading="nearest",
                  norm=LogNorm(vmin=vmin,vmax=np.percentile(R,99.5)),cmap="magma")
    for nu in range(-12,40,2): a.plot(0.02418*nu*B,B,"c-",lw=0.25,alpha=0.4)
    a.set_xlim(n_axis.min(),n_axis.max()); a.set_ylim(0,8); a.set_xlabel("n (1e12 cm^-2)"); a.set_ylabel("B (T)"); a.set_title(lab)
    fig.colorbar(im,ax=a)
fig.suptitle("file_id 20  D=0 fan complete (B 0-8 T)  cyan=even-nu rays")
fig.tight_layout(); fig.savefig("hera_scratch/fan_full.png", dpi=95); print("saved fan_full.png")

# ---- high-B line cuts: Rxx minima -> nu, and Rxy plateaus ----
def nu_of(n_1e12, Bf): return n_1e12/(0.02418*Bf)   # nu = n/(e/h*B)
for Bf in [6.0, 7.0, 8.0]:
    i = int(np.argmin(np.abs(B-Bf)))
    prof = gaussian_filter1d(R1[i],1.0); mins = argrelmin(prof,order=2)[0]
    mins = [j for j in mins if n_axis[j]>0.2]   # electron side
    nus = [nu_of(n_axis[j],B[i]) for j in mins]
    print(f"\nB={B[i]:.1f}T sr1 Rxx minima: n=" + " ".join(f"{n_axis[j]:+.2f}" for j in mins))
    print(f"          -> nu=" + " ".join(f"{x:+.1f}" for x in nus))
    # Rxy at those n
    rxyv = [Rxy[i,j]/1e3 for j in mins]
    print(f"   Rxy@mins (kOhm)=" + " ".join(f"{x:+.1f}" for x in rxyv) + f"  [h/e^2/nu: nu=2->12.9, 6->4.30, 10->2.58]")

# ---- channel agreement (triage): correlate sr1 vs sr2 minima positions at high B ----
i8=int(np.argmin(np.abs(B-8)))
m1=set(np.round(n_axis[[j for j in argrelmin(gaussian_filter1d(R1[i8],1),order=2)[0] if n_axis[j]>0.2]],1))
m2=set(np.round(n_axis[[j for j in argrelmin(gaussian_filter1d(R2[i8],1),order=2)[0] if n_axis[j]>0.2]],1))
print(f"\nchannel triage @8T: sr1 minima n={sorted(m1)}  sr2 minima n={sorted(m2)}")
