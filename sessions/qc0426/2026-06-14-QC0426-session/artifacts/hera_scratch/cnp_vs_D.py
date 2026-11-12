import json, gzip, numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sharpelab_nb.gates import stack_capacitance, calc_nD

# calibration (phase 1)
c_tg = stack_capacitance([(15.6, 3)]); c_bg = 1.3136 * c_tg
n_off, D_off = -0.225, 0.0

m = json.load(open("data/18/metadata.json")); ci = {c: i for i, c in enumerate(m["columns"])}
d = np.loadtxt(gzip.open("data/18/data.tsv.gz"))
bg = np.array(m["slow_setpoints"]); tg = np.array(m["fast_setpoints"]); nbr, nf = len(bg), len(tg)
Ibias = 5e-9

def cnp_vs_D(ch):
    V = d[:, ci[ch]].reshape(nbr, nf)
    D_arr, R_arr, n_arr = [], [], []
    for i in range(nbr):
        s = gaussian_filter1d(np.abs(V[i]), 1.5); j = int(np.argmax(s))
        if j <= 1 or j >= nf - 2:   # edge-clipped row, skip
            continue
        n, D = calc_nD(tg[j], bg[i], c_tg, c_bg, n_off, D_off)
        D_arr.append(D); R_arr.append(np.abs(V[i, j]) / Ibias); n_arr.append(n)
    return np.array(D_arr), np.array(R_arr), np.array(n_arr)

fig, ax = plt.subplots(figsize=(7, 5))
print("Rxx at CNP vs D (per channel, from file_id 18 ridge):")
for ch, lab in [("sr1_X", "sr1 T3-T4"), ("sr2_X", "sr2 B4-B5")]:
    D, R, n = cnp_vs_D(ch)
    o = np.argsort(D)
    D, R = D[o], R[o]
    print(f"\n{lab}:  CNP n-residual max |n|={np.max(np.abs(n)):.3f} (1e12 cm^-2)")
    print(f"  D[V/nm]: " + "  ".join(f"{x:+.2f}" for x in D))
    print(f"  Rxx[kO]: " + "  ".join(f"{x/1e3:6.1f}" for x in R))
    print(f"  range: Rxx {R.min()/1e3:.2f}-{R.max()/1e3:.1f} kO  growth x{R.max()/R.min():.1f}  "
          f"min@D={D[np.argmin(R)]:+.2f}  max@D={D[np.argmax(R)]:+.2f}")
    ax.semilogy(D, R/1e3, "o-", label=lab, ms=4)
ax.axhline(0.25, ls=":", c="gray", lw=1)  # paper semimetallic ~250 Ohm benchmark (geom-uncorrected)
ax.set_xlabel("D (V/nm)"); ax.set_ylabel("Rxx at CNP (kOhm)"); ax.legend()
ax.set_title("CNP Rxx vs D (file_id 18, B=0) — step 1 discriminator")
fig.tight_layout(); fig.savefig("hera_scratch/cnp_vs_D.png", dpi=110)
print("\nsaved hera_scratch/cnp_vs_D.png")
