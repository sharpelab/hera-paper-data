import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft
import scipy.constants as cst

r = open_run("data/2")
B = r.col("magnet_field")
i = r.col("sr0_X") / (-1e6)
R1 = r.col("sr1_X") / i
R2 = r.col("sr2_X") / i
print(f"rows {len(B)}, B {B.min():.3f}..{B.max():.3f} T")
print(f"Rxx sr1 {R1.min():.0f}..{R1.max():.0f} ohm ; sr2 {R2.min():.0f}..{R2.max():.0f} ohm")
# overload check: V = R*I vs FS (sr1/2 1e-5=10uV)
Vmax1 = (np.abs(R1)*np.abs(i)).max()*1e6
print(f"max |V| sr1 = {Vmax1:.2f} uV (FS=10uV) -> {'OK' if Vmax1<10 else 'CLIPPED'}")

n = 3.5e16; F_L = cst.h/(4*cst.e)*n
print(f"F_L = {F_L:.1f} T")

# Onset on sr1
try:
    on = sdh_onset(R1, B)
    print(f"onset_b={on.onset_b:.3f} T  clip_high_b={on.clip_high_b:.3f} T  consensus_freq={on.consensus_freq:.1f} T")
    cutoff = on.onset_b
except Exception as e:
    print("onset failed:", e); cutoff = 1.5

fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
ax[0].plot(B, R1, lw=0.7, label="sr1"); ax[0].plot(B, R2, lw=0.7, label="sr2")
ax[0].set_xlabel("B [T]"); ax[0].set_ylabel("Rxx [ohm]"); ax[0].legend(); ax[0].set_title("Rxx(B) PARTIAL")
# bg-subtracted vs 1/B
for ch, R, c in [("sr1", R1, "C0"), ("sr2", R2, "C1")]:
    m = B >= max(cutoff, 1.0)
    coef = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(coef, B[m])
    ax[1].plot(1/B[m], dR, lw=0.7, color=c, label=ch)
ax[1].set_xlabel("1/B [1/T]"); ax[1].set_ylabel("dRxx [ohm]"); ax[1].legend(); ax[1].set_title(f"bg-sub (B>{max(cutoff,1.0):.1f}T)")
# FFT
for ch, R, c in [("sr1", R1, "C0"), ("sr2", R2, "C1")]:
    f, mag = sdh_fft(R, B, b_range=(max(cutoff, 1.0), B.max()), bg_degree=5)
    ax[2].plot(f, mag, color=c, label=ch)
ax[2].axvline(F_L, ls="--", c="k", lw=1, label=f"F_L={F_L:.0f}T")
ax[2].set_xlabel("F [T]"); ax[2].set_ylabel("FFT mag"); ax[2].set_xlim(0, 1.3*F_L)
ax[2].legend(); ax[2].set_title("SdH FFT PARTIAL")
fig.tight_layout(); fig.savefig("hera_scratch/sc1_partial.png", dpi=110)
print("saved hera_scratch/sc1_partial.png")
