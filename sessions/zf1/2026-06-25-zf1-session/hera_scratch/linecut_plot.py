import json, gzip, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import GateCalibration
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0, n_offset=-0.362e11*1e4)

def load(run):
    md = json.load(open(f"{run}/metadata.json")); cols = md["columns"]
    p = f"{run}/data.tsv"; f = gzip.open(p+".gz","rt") if os.path.exists(p+".gz") else open(p)
    a = np.genfromtxt(f, delimiter="\t", invalid_raise=False); f.close()
    a = a[~np.isnan(a).any(axis=1)]; ix = {}; [ix.setdefault(c,j) for j,c in enumerate(cols)]
    n, D = cal.n_D(a[:, ix["k_tg_volt"]], a[:, ix["k_bg_volt"]])
    return dict(n=n/1e4/1e11, D=D/1e9,
                R3=(a[:, ix["sr830_3_X"]]/100)/1e-9,
                R2=(a[:, ix["sr830_2_X"]]/100)/1e-9,
                I=a[:, ix["sr830_1_X"]]/-1e6*1e9)   # nA

runs = {"D=-0.45":"data/5","D=-0.55":"data/6","D=-0.65":"data/7"}
dat = {k: load(v) for k,v in runs.items()}

fig, ax = plt.subplots(1, 3, figsize=(17,5))
for k,d in dat.items():
    o = np.argsort(d["n"])
    ax[0].plot(d["n"][o], d["R3"][o], "-", lw=1, label=k)
    ax[1].plot(d["n"][o], d["R3"][o], "-", lw=1, label=k)
ax[0].set_ylim(-5,300); ax[0].set_title("4T Rxx (30-31) vs n — all cuts"); ax[0].axhline(0,color="gray",lw=.5)
ax[1].set_ylim(-3,60); ax[1].set_xlim(-8,-3); ax[1].set_title("zoom: candidate band"); ax[1].axhline(0,color="gray",lw=.5)
ax[1].axhspan(-3,5,color="gold",alpha=0.15)
for a_ in ax[:2]:
    a_.set_xlabel("n (1e11 cm^-2)"); a_.set_ylabel("Rxx (Ω)"); a_.legend(); a_.grid(alpha=.3)
# cut3 with current monitor
d = dat["D=-0.65"]; o = np.argsort(d["n"])
ax[2].plot(d["n"][o], d["R3"][o], "b-", lw=1, label="4T Rxx (Ω)")
ax[2].axhline(0,color="gray",lw=.5); ax[2].set_ylim(-3,60); ax[2].set_xlim(-8,-3)
ax[2].set_xlabel("n (1e11 cm^-2)"); ax[2].set_ylabel("Rxx (Ω)", color="b")
axb = ax[2].twinx(); axb.plot(d["n"][o], d["I"][o], "r-", lw=0.8, alpha=.6, label="I monitor (nA)")
axb.set_ylabel("I (nA)", color="r"); axb.set_ylim(0.9,1.1)
ax[2].set_title("D=-0.65: Rxx dip + current monitor")
fig.suptitle("zf1 runs 5-7 — constant-D n-linecuts; SC candidate at D=-0.65, n~-5e11 (Rxx->0)")
fig.tight_layout(); fig.savefig("hera_scratch/linecuts.png", dpi=110)

# precise dip characterization for cut 3
d = dat["D=-0.65"]; m = (d["n"] > -6.5) & (d["n"] < -4)
sub_n = d["n"][m]; sub_R = d["R3"][m]; o = np.argsort(sub_n)
jmin = np.argmin(sub_R)
low = sub_R < 5
print(f"D=-0.65 dip: min Rxx={sub_R.min():.2f}Ω at n={sub_n[jmin]:.2f}e11")
print(f"  Rxx<5Ω over n=[{sub_n[low].min():.2f},{sub_n[low].max():.2f}]e11 ({low.sum()} pts)")
print(f"  current monitor over dip: {d['I'][m].min():.3f}-{d['I'][m].max():.3f} nA (expect ~1.0, steady)")
print("saved hera_scratch/linecuts.png")
