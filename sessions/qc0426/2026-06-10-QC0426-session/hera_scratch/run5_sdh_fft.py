"""Run 5 — SdH FFT per n-column (1/B domain, B 2-6 T).

ABA(D=0): ML + BL pockets coexist -> two SdH frequencies per n.
ABC(D=0): single ladder -> one frequency f = n h/(4e) (4-fold deg).
Overlay: f_1ladder(n) = n*h/(4e) = 10.34 * n12  [T]; and 2-pocket split lines.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

eps0, e, h = 8.8541878128e-12, 1.602176634e-19, 6.62607015e-34
c_tg = eps0 * 3 / 15.6e-9
NF = 271

m = json.load(open(r"data/5/metadata.json"))
arr = np.loadtxt(r"data/5/data.tsv.gz")
cols = m["columns"]
nr = arr.shape[0] // NF
g = lambda nm: arr[: nr * NF, cols.index(nm)].reshape(nr, NF)
B = g("mag")[:, 0]
n12 = 2 * c_tg * g("DC_bias")[0] / e * 1e-16
I = g("sr0_X") / (-1e6)
R1 = np.abs(g("sr1_X") / I)

sel = (B >= 2.0) & (B <= 6.0)
Bv = B[sel]
invB = 1.0 / Bv
M = 512
u = np.linspace(invB.min(), invB.max(), M)
du = u[1] - u[0]
freqs = np.fft.rfftfreq(M, du)

spec = np.zeros((NF, len(freqs)))
order = np.argsort(invB)
for j in range(NF):
    y = np.log10(np.maximum(R1[sel, j], 1))
    yi = np.interp(u, invB[order], y[order])
    yi -= np.polyval(np.polyfit(u, yi, 3), u)   # detrend
    yi *= np.hanning(M)
    spec[j] = np.abs(np.fft.rfft(yi))

fig, ax = plt.subplots(figsize=(11, 6))
fm = freqs <= 120
pc = ax.pcolormesh(n12, freqs[fm], spec[:, fm].T,
                   cmap="viridis", shading="nearest",
                   vmax=np.nanpercentile(spec[:, fm], 99.5))
fig.colorbar(pc, ax=ax, label="FFT amplitude")
nn = np.linspace(0, 8, 50)
ax.plot(nn, 10.34 * nn, "w--", lw=1.2, label="single 4-fold ladder f = n h/4e")
ax.plot(nn, 2 * 10.34 * nn, "w:", lw=0.8, label="2nd harmonic")
ax.set_xlabel(r"n (10$^{12}$ cm$^{-2}$)")
ax.set_ylabel("SdH frequency (T)")
ax.set_ylim(0, 120)
ax.set_xlim(0.5, 8)
ax.legend(fontsize=8)
ax.set_title("Run 5 sr1 — SdH FFT per n-column (B 2-6 T)")
fig.tight_layout()
fig.savefig(r"hera_scratch/run5_sdh_fft.png", dpi=120)
print("saved hera_scratch/run5_sdh_fft.png")

# peak table at a few n
print("\npeak frequencies vs n (peaks > 25% of column max, f > 4 T):")
for ncen in (1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5):
    j = np.argmin(np.abs(n12 - ncen))
    s = spec[j]
    fsel = (freqs > 4) & (freqs <= 120)
    ss, ff = s[fsel], freqs[fsel]
    pk = [i for i in range(1, len(ss) - 1)
          if ss[i] > ss[i - 1] and ss[i] > ss[i + 1] and ss[i] > 0.25 * ss.max()]
    print(f"  n={n12[j]:4.2f}: f = {np.round(ff[pk], 1)}  "
          f"(1-ladder pred {10.34 * n12[j]:.1f} T)")
