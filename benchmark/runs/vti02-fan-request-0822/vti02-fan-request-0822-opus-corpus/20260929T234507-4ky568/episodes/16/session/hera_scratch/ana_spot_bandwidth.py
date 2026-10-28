"""Run 6 (electron spot check): how far up in F does the spectral content run?
Sets the fan's Nyquist requirement / aliasing risk.  Scratch.
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

r = open_run("data/6")
B = np.asarray(r.col("magnet_field"), float)
R = np.asarray(r.col("sr1_X"), float) / (np.asarray(r.col("sr0_X"), float) / -1e6)
o = np.argsort(B); B, R = B[o], R[o]

fig, ax = plt.subplots(2, 2, figsize=(13, 8))

# (a) raw dR vs 1/B in the high-B region (anharmonicity check)
for k, (blo, bhi) in enumerate([(1.0, 3.0), (3.0, 10.0)]):
    m = (B >= blo) & (B <= bhi)
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[0, k].plot(1 / B[m], R[m] - bg, lw=0.8)
    ax[0, k].set(xlabel="1/B (1/T)", ylabel=r"$\Delta R$ ($\Omega$)",
                 title=f"run 6 bg-sub, B {blo}-{bhi} T")

# (b) wide-band FFT on a uniform 1/B resample, several windows
for k, (blo, bhi) in enumerate([(1.0, 10.0), (4.0, 10.0)]):
    m = (B >= blo) & (B <= bhi)
    bb, rr = B[m], R[m]
    bg = np.polyval(np.polyfit(bb, rr, 5), bb)
    d = rr - bg
    inv = 1 / bb
    # native finest spacing in this window
    ns = 8192
    g = np.linspace(inv.min(), inv.max(), ns)
    di = np.interp(g, inv[::-1], d[::-1])
    w = np.hanning(ns)
    sp = np.abs(np.fft.rfft(di * w, n=4 * ns))
    f = np.fft.rfftfreq(4 * ns, d=g[1] - g[0])
    sp /= sp.max()
    ax[1, k].semilogy(f, sp, lw=0.8)
    for j in range(1, 30):
        ax[1, k].axvline(7.3 * j, color="g", ls=":", lw=0.5)
    ax[1, k].axvline(33.1, color="k", ls="--", lw=1.0, label="$F_L$ 33.1 T")
    ax[1, k].set(xlim=(0, 400), ylim=(1e-4, 1.5), xlabel="F (T)",
                 ylabel="|FFT| norm", title=f"wideband FFT B {blo}-{bhi} T "
                 f"(green: k x 7.3 T); native $\\Delta(1/B)$ max "
                 f"{np.diff(inv[::-1]).max():.2e}")
    ax[1, k].legend(fontsize=7)
    # peak list
    from scipy.signal import find_peaks
    pk, _ = find_peaks(np.log(sp), prominence=0.7)
    keep = [(f[i], sp[i]) for i in pk if f[i] > 3 and sp[i] > 3e-3]
    print(f"\nwindow B {blo}-{bhi} T  peaks (F, rel amp), k=F/7.3:")
    for fr, a in keep[:40]:
        print(f"   {fr:7.1f} T  {a:8.4f}   k={fr/7.3:5.2f}")

plt.tight_layout()
plt.savefig("hera_scratch/spot6_bandwidth.png", dpi=120)
print("\nwrote hera_scratch/spot6_bandwidth.png")
