import sys, json, gzip, numpy as np
sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\aba_trilayer")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from sharpelab_nb.gates import stack_capacitance, calc_nD
from hera.analysis import fan_grids, resistance_grids, sdh_fft
from ll_spectrum import SWMcC; from crossing_model import ml_trajectories

c_tg = stack_capacitance([(15.6,3)]); c_bg = 1.3136*c_tg; n_off, D_off = -0.225, 0.0
m = json.load(open("data/21/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
d = np.loadtxt(gzip.open("data/21/data.tsv.gz")); nf=len(m["fast_setpoints"][0])
B=np.array(m["slow_setpoints"][0]); nb=len(B); d=d[:nb*nf]; Ib=5e-9
tg=d[:,ci["DC_bias"]].reshape(nb,nf); bg=d[:,ci["k_bg_volt"]].reshape(nb,nf)
n_axis=calc_nD(tg,bg,c_tg,c_bg,n_off,D_off)[0][0]
print(f"data/21: {nb}x{nf}, B {B.min()}-{B.max()} T, n {n_axis.min():.2f}..{n_axis.max():.2f}, Dline {calc_nD(tg,bg,c_tg,c_bg,n_off,D_off)[1].mean():.3f} V/nm")
R1=np.abs(d[:,ci["sr1_X"]].reshape(nb,nf))/Ib
order=np.argsort(n_axis); n_s=n_axis[order]; R1=R1[:,order]
E=np.array([R1[i]/np.maximum(gaussian_filter1d(R1[i],6),1e-9) for i in range(nb)])

fig,ax=plt.subplots(1,2,figsize=(16,6))
ax[0].pcolormesh(n_s,B,E,shading="gouraud",cmap="RdBu_r",vmin=0.7,vmax=1.3)
traj=ml_trajectories(SWMcC(), np.linspace(3,8,26))
for nm,(nn,bb) in traj.items():
    if len(nn) and nn.max()>3: ax[0].plot(nn,bb,"lime",lw=2.2); ax[0].text(nn[-1],bb[-1],f"N_M={nm}",color="g",fontsize=9,weight="bold")
for nu in range(20,90,4): ax[0].plot(0.02418*nu*B,B,"k-",lw=0.25,alpha=0.25)
ax[0].set_xlim(3.5,10); ax[0].set_ylim(3,8); ax[0].set_xlabel("n (1e12 cm^-2)"); ax[0].set_ylabel("B (T)")
ax[0].set_title("data/21 sr1 Rxx/env + ABA chains (green N_M=1,2)  — do curved arcs co-locate?")

fg=fan_grids("data/21"); rg=resistance_grids(fg)
fr,spec=sdh_fft(np.abs(rg.R["sr1"]), fg.slow, b_range=(4.0,8.0))
order2=np.argsort(calc_nD(fg.data and None or tg,bg,c_tg,c_bg,n_off,D_off)[0][0]) if False else order
sp=spec[order]
sel=(n_s>3.6)&(n_s<10)
im=ax[1].pcolormesh(n_s[sel],fr,sp[sel].T,shading="nearest",cmap="viridis"); ax[1].set_ylim(0,140)
h=6.626e-34; e=1.602e-19
ax[1].plot(n_s[sel], n_s[sel]*1e16*h/(4*e),"w--",lw=1,label="single band g=4")
ax[1].set_xlabel("n (1e12 cm^-2)"); ax[1].set_ylabel("SdH freq (T)"); ax[1].legend(); ax[1].set_title("data21 SdH-FFT high-n (B4-8T, clean)")
plt.tight_layout(); fig.savefig("hera_scratch/fan21.png",dpi=100); print("saved fan21.png")
two=sum(1 for j in np.where(sel)[0] if len(find_peaks(sp[j]/ (sp[j].max()+1e-9),height=0.35,distance=15)[0])>=2)
print(f"high-n SdH-FFT: {sel.sum()} columns, {two} with two pockets")
