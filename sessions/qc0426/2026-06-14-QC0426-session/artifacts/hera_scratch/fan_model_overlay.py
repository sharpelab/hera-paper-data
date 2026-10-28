import sys, json, gzip, numpy as np
sys.path.insert(0, "/c/Users/DGG/measurement_env/hera/models/aba_trilayer".replace("/c/","C:/"))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import stack_capacitance, calc_nD
from ll_spectrum import SWMcC
from crossing_model import ml_trajectories, crossing_loci

# --- my fan ---
c_tg = stack_capacitance([(15.6,3)]); c_bg = 1.3136*c_tg; n_off, D_off = -0.225, 0.0
m = json.load(open("data/20/metadata.json")); ci = {c:i for i,c in enumerate(m["columns"])}
d = np.loadtxt(gzip.open("data/20/data.tsv.gz"))
nf = len(m["fast_setpoints"][0]); B = np.array(m["slow_setpoints"][0]); nb = len(B); d = d[:nb*nf]
Ibias = 5e-9
tgc = d[:,ci["DC_bias"]].reshape(nb,nf); bgc = d[:,ci["k_bg_volt"]].reshape(nb,nf)
n_axis = calc_nD(tgc,bgc,c_tg,c_bg,n_off,D_off)[0][0]
R1 = np.abs(d[:,ci["sr1_X"]].reshape(nb,nf))/Ibias
E = np.array([R1[i]/np.maximum(gaussian_filter1d(R1[i],6),1e-9) for i in range(nb)])

# --- model prediction ---
p = SWMcC()
Bg = np.linspace(1.0, 8.0, 36)
traj = ml_trajectories(p, Bg)
print("predicted ML crossing chains (N_M: n@8T 1e12 cm^-2):")
for nm,(nn,bb) in traj.items():
    if len(nn): print(f"  N_M={nm}: n@{bb[-1]:.0f}T = {nn[-1]:+.2f}  (n@{bb[0]:.0f}T={nn[0]:+.2f})")

# --- overlay at a few global density rescales alpha ---
for alpha in [1.0]:
    fig, ax = plt.subplots(figsize=(9,7))
    im = ax.pcolormesh(n_axis, B, E, shading="gouraud", cmap="RdBu_r", vmin=0.6, vmax=1.4)
    for nu in range(2,36,2): ax.plot(0.02418*nu*B, B, "k-", lw=0.25, alpha=0.25)
    cols = plt.cm.viridis(np.linspace(0,1,len(traj)))
    for (nm,(nn,bb)),c in zip(traj.items(),cols):
        ax.plot(alpha*nn, bb, "-", color="lime", lw=2.2, alpha=0.9)
        ax.text(alpha*nn[-1], bb[-1]+0.1, f"N_M={nm}", color="lime", fontsize=8, weight="bold")
    ax.set_xlim(0,4); ax.set_ylim(1,8); ax.set_xlabel("n (1e12 cm^-2)"); ax.set_ylabel("B (T)")
    ax.set_title(f"sr1 Rxx/env + ABA model ML crossing chains (alpha={alpha})  green=predicted chains")
    fig.colorbar(im,ax=ax); fig.tight_layout(); fig.savefig(f"hera_scratch/fan_model_a{alpha}.png", dpi=110)
    print(f"saved fan_model_a{alpha}.png")
