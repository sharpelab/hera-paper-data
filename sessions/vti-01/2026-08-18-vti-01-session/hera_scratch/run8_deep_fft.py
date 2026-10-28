# Run 8 deep FFT read: stability sweep + B-window split (scratch)
import numpy as np
from hera.analysis import open_run, sdh_fft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

r = open_run("data/8")
B = r.col("magnet_field")
i_dr = np.abs(r.col("sr0_X")) / 1e6
R1 = (r.col("sr1_X") / i_dr)[:, None]
FL = 18.6

fig, axs = plt.subplots(1, 3, figsize=(16, 4.4))

# --- (a) stability sweep: bg_degree x low-cutoff ---
for bg in (4, 5, 6):
    for lo in (1.7, 2.2):
        f, s = sdh_fft(R1, B, b_range=(lo, 9.0), bg_degree=bg)
        axs[0].plot(f, s[0] / s[0].max(), lw=0.8, label=f"bg{bg}, B>{lo}")
axs[0].set_title("sr1: stability sweep (bg_degree × cutoff)")

# --- (b) B-window split: low vs high half in 1/B ---
# split point ~ geometric mean of (1.67, 9) in 1/B: 1/B_mid = (1/1.67+1/9)/2 -> B_mid ~ 2.83
for (lo, hi), lbl in (((1.7, 2.85), "low half"), ((2.85, 9.0), "high half")):
    f, s = sdh_fft(R1, B, b_range=(lo, hi), bg_degree=4)
    axs[1].plot(f, s[0] / s[0].max(), lw=0.9, label=f"{lbl} ({lo}-{hi} T)")
axs[1].set_title("sr1: B-window split (breakdown test)")

# --- (c) all channels, canonical window ---
for ch in ("sr1", "sr2", "sr3"):
    Rc = (r.col(f"{ch}_X") / i_dr)[:, None]
    f, s = sdh_fft(Rc, B, b_range=(1.7, 9.0), bg_degree=5)
    axs[2].plot(f, s[0] / s[0].max() + {"sr1": 0, "sr2": 1.1, "sr3": 2.2}[ch], lw=0.9, label=ch)
axs[2].set_title("all channels (offset), B 1.7–9 T")

for ax in axs:
    ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.legend(fontsize=7); ax.grid(alpha=0.3)
    ax.axvline(FL, color="r", ls="--", lw=0.8)
    for v in (7.3, 11.4, 17.7, 25.6):
        ax.axvline(v, color="gray", ls=":", lw=0.5)
fig.tight_layout(); fig.savefig("hera_scratch/run8_fft.png", dpi=110)

# numeric peak table for the canonical + split windows
from scipy.signal import find_peaks
def peaks(f, s, prom=0.05):
    p, pr = find_peaks(s / s.max(), prominence=prom)
    return [(f[i], (s / s.max())[i]) for i in p if f[i] < 60]

f, s = sdh_fft(R1, B, b_range=(1.7, 9.0), bg_degree=5)
print("sr1 canonical (1.7-9, bg5):", [f"{x:.1f}T({a:.2f})" for x, a in peaks(f, s[0])])
for (lo, hi), lbl in (((1.7, 2.85), "low"), ((2.85, 9.0), "high")):
    f, s = sdh_fft(R1, B, b_range=(lo, hi), bg_degree=4)
    print(f"sr1 {lbl} half:", [f"{x:.1f}T({a:.2f})" for x, a in peaks(f, s[0])])
print("saved hera_scratch/run8_fft.png")
