import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

run = open_run("data/0")
print(summarize_run(run))
print("cols:", run.cols)
print("interrupted:", run.interrupted)

vbg = run.col("k_2400_volt")
# current channel
i = run.col("sr0_X") / (-1e6)   # A, Ithaco gain
# voltage channels (gain 1)
v1 = run.col("sr1_X"); v2 = run.col("sr2_X"); v3 = run.col("sr3_X")
Ibias = np.median(i)
print(f"I_bias median = {Ibias*1e9:.2f} nA  (min {i.min()*1e9:.2f}, max {i.max()*1e9:.2f})")

R1 = v1 / i; R2 = v2 / i; R3 = v3 / i
# gate leakage
for c in ("k_2400_curr", "k_2410_curr"):
    if c in run.cols:
        x = run.col(c)
        print(f"{c}: |max| = {np.abs(x).max():.3e} A")

# peak (CNP) location per channel
for nm, R in [("sr1(T3-T4)", R1), ("sr2(B4-B5)", R2)]:
    k = np.argmax(R)
    print(f"{nm}: peak R = {R[k]:.1f} Ω at BG = {vbg[k]:.3f} V; min R = {R.min():.1f} Ω")

# raw-first plot: raw X, then derived R
fig, ax = plt.subplots(2, 1, figsize=(7, 8), sharex=True)
ax[0].plot(vbg, v1*1e6, label="sr1 X (T3-T4)")
ax[0].plot(vbg, v2*1e6, label="sr2 X (B4-B5)")
ax[0].plot(vbg, v3*1e6, label="sr3 X (Hall)")
ax[0].set_ylabel("lock-in X [µV]"); ax[0].legend(); ax[0].set_title("Gate C raw — run 0, BG sweep @ TG=0,Si=0,B=0")
ax[1].plot(vbg, R1, label="sr1 Rxx")
ax[1].plot(vbg, R2, label="sr2 Rxx")
ax[1].set_xlabel("V_bg [V]"); ax[1].set_ylabel("R [Ω]"); ax[1].legend(); ax[1].set_title("derived R = V / I_bias")
fig.tight_layout(); fig.savefig("hera_scratch/gatec_run0.png", dpi=110)
print("saved hera_scratch/gatec_run0.png")
