"""Direct look at run 5 high-B record."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

run = open_run("data/5")
B = run.col("magnet_field")
I = 20e-9
R1 = run.col_at(run.col_indices("sr1_X")[-1]) / I
R2 = run.col_at(run.col_indices("sr2_X")[-1]) / I
R3 = run.col_at(run.col_indices("sr3_X")[-1]) / I

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
m = B > 1.5
axes[0, 0].plot(B, R1, lw=0.6, label="sr1")
axes[0, 0].plot(B, R2, lw=0.6, label="sr2")
axes[0, 0].plot(B, -R3, lw=0.6, label="-sr3 (Rxy)")
axes[0, 0].legend(); axes[0, 0].set_xlabel("B (T)"); axes[0, 0].set_title("full record")

axes[0, 1].plot(1/B[m], R1[m], lw=0.7)
axes[0, 1].set_xlabel("1/B (1/T)"); axes[0, 1].set_title("sr1, B>1.5 T vs 1/B")

for ax, (R, name), deg in ((axes[1, 0], (R1, "sr1"), 7), (axes[1, 1], (R2, "sr2"), 7)):
    p = np.polyfit(B[m], R[m], deg)
    dR = R[m] - np.polyval(p, B[m])
    ax.plot(1/B[m], dR, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_title(f"{name} - deg{deg} poly(B), B>1.5 T")
    print(f"{name}: dR rms {dR.std():.2f} Ohm over B>1.5 T; R(8T) = {R[m][-1]:.0f} Ohm")
fig.tight_layout(); fig.savefig("hera_scratch/sdh5_look.png", dpi=110)
print("saved")
