"""Interim onset look at partial run 5 (B up to ~1.4 T)."""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/5/data.tsv", sep="\t", header=None)
B = df[1].values
R1 = df[9].values / 20e-9
R2 = df[11].values / 20e-9
m = B > 0.35
fig, axes = plt.subplots(2, 2, figsize=(13, 7))
for col, (R, name) in zip(axes.T, ((R1, "sr1"), (R2, "sr2"))):
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    col[0].plot(B[m], R[m], lw=0.7); col[0].set_title(f"{name} raw"); col[0].set_xlabel("B (T)")
    col[1].plot(1/B[m], dR, lw=0.7); col[1].set_title(f"{name} deg-5 poly(B) subtracted vs 1/B")
    col[1].set_xlabel("1/B (1/T)"); col[1].set_ylabel("dR (Ohm)")
    print(f"{name}: dR rms {dR.std():.3f} Ohm; last-quarter rms {dR[-len(dR)//4:].std():.3f} Ohm")
fig.tight_layout(); fig.savefig("hera_scratch/interim_sdh.png", dpi=110)
print("saved")
