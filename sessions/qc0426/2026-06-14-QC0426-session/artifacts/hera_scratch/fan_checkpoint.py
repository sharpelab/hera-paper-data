import json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from sharpelab_nb.gates import stack_capacitance, calc_nD

c_tg = stack_capacitance([(15.6, 3)]); c_bg = 1.3136*c_tg; n_off, D_off = -0.225, 0.0
m = json.load(open("data/20/metadata.json")); ci = {c: i for i, c in enumerate(m["columns"])}
d = np.loadtxt("data/20/data.tsv")            # partial, uncompressed (running)
nf = len(m["fast_setpoints"][0]); Bset = np.array(m["slow_setpoints"][0])
ncomplete = d.shape[0] // nf
d = d[:ncomplete*nf]
print("cols:", m["columns"], "| nf", nf, "| complete rows", ncomplete, "B max", Bset[ncomplete-1])
Ibias = 5e-9

B = Bset[:ncomplete]
# n from recorded gate columns (true n per point); should equal designed ns
tgc, bgc = d[:, ci["DC_bias"]].reshape(ncomplete, nf), d[:, ci["k_bg_volt"]].reshape(ncomplete, nf)
nval, Dval = calc_nD(tgc, bgc, c_tg, c_bg, n_off, D_off)
n_axis = nval[0]                               # n per fast index (same each row)
print(f"n axis: {n_axis.min():+.2f}..{n_axis.max():+.2f}  | D along line: {Dval.mean():+.3f}±{Dval.std():.3f} V/nm")

def Rg(ch): return np.abs(d[:, ci[ch]].reshape(ncomplete, nf)) / Ibias

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for ax, ch, lab in zip(axes, ["sr1_X","sr2_X","sr3_X"], ["sr1 T3-T4 Rxx","sr2 B4-B5 Rxx","sr3 T5-B6 Rxy"]):
    R = Rg(ch)
    vmin = max(R[R>0].min(), 10);
    im = ax.pcolormesh(n_axis, B, np.clip(R,vmin,None), shading="nearest",
                       norm=LogNorm(vmin=vmin, vmax=np.percentile(R,99.5)), cmap="magma")
    # nu-ray overlay (n = nu * (e/h) * B); slope per nu = 0.02418 [1e12 cm^-2 / T]
    for nu in range(-12, 40, 2):
        ax.plot(0.02418*nu*B, B, "c-", lw=0.3, alpha=0.5)
    ax.set_xlim(n_axis.min(), n_axis.max()); ax.set_ylim(B.min(), B.max())
    ax.set_xlabel("n (1e12 cm^-2)"); ax.set_ylabel("B (T)"); ax.set_title(lab)
    fig.colorbar(im, ax=ax, label="R (Ohm)")
fig.suptitle(f"file_id 20  D=0 fan  partial {ncomplete}/81 rows (B->{B[-1]:.1f} T)  cyan=even-nu rays")
fig.tight_layout(); fig.savefig("hera_scratch/fan_checkpoint.png", dpi=95)
print("saved hera_scratch/fan_checkpoint.png")

# onset: lowest B where the n-profile shows >=3 local minima (SdH dips) in sr1
from scipy.signal import argrelmin
from scipy.ndimage import gaussian_filter1d
print("\nSdH-dip count per B-row (sr1, electron side n>0.3):")
sel = n_axis > 0.3
for i in range(ncomplete):
    prof = gaussian_filter1d(Rg("sr1_X")[i][sel], 1.0)
    mins = argrelmin(prof, order=2)[0]
    if i % 3 == 0 or i == ncomplete-1:
        print(f"  B={B[i]:.1f} T: {len(mins)} dips")
