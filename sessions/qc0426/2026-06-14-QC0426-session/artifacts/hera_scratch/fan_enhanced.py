import json, gzip, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import stack_capacitance, calc_nD

c_tg = stack_capacitance([(15.6,3)]); c_bg = 1.3136*c_tg; n_off, D_off = -0.225, 0.0
m = json.load(open("data/20/metadata.json")); ci = {c:i for i,c in enumerate(m["columns"])}
d = np.loadtxt(gzip.open("data/20/data.tsv.gz"))
nf = len(m["fast_setpoints"][0]); B = np.array(m["slow_setpoints"][0]); nb = len(B)
d = d[:nb*nf]; Ibias = 5e-9
tgc = d[:,ci["DC_bias"]].reshape(nb,nf); bgc = d[:,ci["k_bg_volt"]].reshape(nb,nf)
nval,_ = calc_nD(tgc, bgc, c_tg, c_bg, n_off, D_off); n_axis = nval[0]
R1 = np.abs(d[:,ci["sr1_X"]].reshape(nb,nf))/Ibias
R2 = np.abs(d[:,ci["sr2_X"]].reshape(nb,nf))/Ibias

def enhance(R):
    out = np.zeros_like(R)
    for i in range(nb):
        sm = gaussian_filter1d(R[i], 6)            # smooth envelope
        out[i] = R[i]/np.maximum(sm, 1e-9)          # oscillation relative to envelope
    return out

fig, ax = plt.subplots(1,2, figsize=(15,6))
for a,(R,lab) in zip(ax,[(R1,"sr1 T3-T4"),(R2,"sr2 B4-B5")]):
    E = enhance(R)
    im = a.pcolormesh(n_axis, B, E, shading="gouraud", cmap="RdBu_r", vmin=0.5, vmax=1.5)
    for nu in range(2,40,2):
        a.plot(0.02418*nu*B, B, "k-", lw=0.3, alpha=0.35)
        if nu<=18: a.text(0.02418*nu*8.2, 7.6, str(nu), fontsize=6, color="k")
    a.set_xlim(0.2, 4); a.set_ylim(1.0, 8); a.set_xlabel("n (1e12 cm^-2)"); a.set_ylabel("B (T)")
    a.set_title(f"{lab} Rxx / envelope (oscillations)  black=even-nu rays")
fig.tight_layout(); fig.savefig("hera_scratch/fan_enhanced.png", dpi=120)
print("saved fan_enhanced.png")

# quantitative: at each B row, do detected minima sit on constant-nu rays (straight) -> read slope dn/dB per ray
# track the strongest 3 minima across B>=4T and fit n vs B
from scipy.signal import argrelmin
rows = [i for i in range(nb) if B[i]>=4.0]
allmin = []
for i in rows:
    E = gaussian_filter1d(R1[i]/np.maximum(gaussian_filter1d(R1[i],6),1e-9), 1)
    for j in argrelmin(E, order=2)[0]:
        if n_axis[j]>0.3 and E[j]<0.92:
            allmin.append((B[i], n_axis[j]))
allmin = np.array(allmin)
print(f"\n{len(allmin)} strong Rxx minima (B>=4T). dn/dB of linear ray families => nu = dn/dB / 0.02418:")
# crude: histogram nu = n/(0.02418*B) of all minima
if len(allmin):
    nus = allmin[:,1]/(0.02418*allmin[:,0])
    h,edges = np.histogram(nus, bins=np.arange(0,40,2))
    for k in range(len(h)):
        if h[k]: print(f"  nu {edges[k]:.0f}-{edges[k+1]:.0f}: {'#'*h[k]} ({h[k]})")
