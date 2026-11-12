import json, gzip, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import stack_capacitance, calc_nD

c_tg = stack_capacitance([(15.6,3)]); c_bg = 1.3136*c_tg; n_off, D_off = -0.225, 0.0
m = json.load(open("data/20/metadata.json")); ci = {c:i for i,c in enumerate(m["columns"])}
d = np.loadtxt(gzip.open("data/20/data.tsv.gz"))
nf = len(m["fast_setpoints"][0]); B = np.array(m["slow_setpoints"][0]); nb=len(B); d=d[:nb*nf]; Ibias=5e-9
tgc=d[:,ci["DC_bias"]].reshape(nb,nf); bgc=d[:,ci["k_bg_volt"]].reshape(nb,nf)
n_axis=calc_nD(tgc,bgc,c_tg,c_bg,n_off,D_off)[0][0]
R1=np.abs(d[:,ci["sr1_X"]].reshape(nb,nf))/Ibias
R2=np.abs(d[:,ci["sr2_X"]].reshape(nb,nf))/Ibias
Rxy=(d[:,ci["sr3_X"]].reshape(nb,nf))/Ibias
Rq=25812.8

fig,axes=plt.subplots(2,1,figsize=(11,9),sharex=True)
for Bf,c in [(7.0,"C0"),(8.0,"C3")]:
    i=int(np.argmin(np.abs(B-Bf)))
    axes[0].plot(n_axis, gaussian_filter1d(R1[i],1)/1e3, c, label=f"sr1 {B[i]:.0f}T")
    axes[0].plot(n_axis, gaussian_filter1d(R2[i],1)/1e3, c, ls="--", alpha=0.6, label=f"sr2 {B[i]:.0f}T")
    axes[1].plot(n_axis, gaussian_filter1d(Rxy[i],1)/1e3, c, label=f"Rxy {B[i]:.0f}T")
# nu markers at 8T: n = nu*0.02418*8
i8=int(np.argmin(np.abs(B-8)))
for nu in range(2,22,2):
    nn=0.02418*nu*8
    if nn<4:
        axes[0].axvline(nn, color="gray", lw=0.4, ls=":")
        axes[0].text(nn,0.05,str(nu),fontsize=7,color="gray")
# Rxy quantized levels h/(nu e^2)=Rq/nu
for nu in [2,6,10,14,18]:
    axes[1].axhline(Rq/nu/1e3, color="gray", lw=0.4, ls=":")
    axes[1].text(3.7, Rq/nu/1e3, f"nu={nu}", fontsize=7, color="gray")
    axes[1].axhline(-Rq/nu/1e3, color="gray", lw=0.4, ls=":")
axes[0].set_ylabel("Rxx (kOhm)"); axes[0].set_yscale("log"); axes[0].legend(fontsize=8); axes[0].set_title("High-B line cuts (gray dotted = integer-nu @8T)")
axes[1].set_ylabel("Rxy (kOhm)"); axes[1].set_xlabel("n (1e12 cm^-2)"); axes[1].legend(fontsize=8); axes[1].set_xlim(-0.5,4)
fig.tight_layout(); fig.savefig("hera_scratch/linecuts.png", dpi=110); print("saved linecuts.png")

# Rxy: is it stepping (plateaus) or smooth/linear? check dRxy/dn flatness near sr1 Rxx minima
prof=gaussian_filter1d(R1[i8],1); from scipy.signal import argrelmin
mins=[j for j in argrelmin(prof,order=2)[0] if n_axis[j]>0.2]
print("@8T  n_min   nu(geom)   Rxy[kOhm]   dRxy/dn[kOhm per 1e12]   Rxy_classical=B/(n e)[kOhm]")
for j in mins:
    nu=n_axis[j]/(0.02418*8)
    dr=(Rxy[i8,min(j+2,nf-1)]-Rxy[i8,max(j-2,0)])/(n_axis[min(j+2,nf-1)]-n_axis[max(j-2,0)])/1e3
    ncl=n_axis[j]*1e16; Rcl=8/(ncl*1.602e-19)/1e3 if ncl>0 else 0
    print(f"     {n_axis[j]:+.2f}   {nu:5.1f}     {Rxy[i8,j]/1e3:+6.2f}     {dr:+7.2f}              {Rcl:+.2f}")
