import os, numpy as np, hera.analysis as a
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
MDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(MDIR, "hera_scratch")
run = a.open_run(os.path.join(MDIR, "data", "4"))
fg = a.fan_grids(run); B = np.asarray(fg.slow)
rg = a.resistance_grids(fg); R1 = rg.R["sr1"]
ncol = R1.shape[1]
ns_cm = np.linspace(-0.7, -2.5, ncol)

# Representative columns
targets = [-2.5, -2.1, -1.7, -1.3, -0.9]
cols = [int(np.argmin(np.abs(ns_cm - t))) for t in targets]

fig, ax = plt.subplots(1, 2, figsize=(14, 6))
for cutoff, axx, title in [(0.5, ax[0], "cutoff 0.5T"), (1.2, ax[1], "cutoff 1.2T")]:
    for c in cols:
        n = abs(ns_cm[c]); FL = float(a.luttinger_frequency(n*1e16))
        f, mag = a.sdh_fft(R1[:, c:c+1], B, b_range=(cutoff, 7.9), bg_degree=5)
        m = mag[0]; sel = f > 2
        offset = abs(ns_cm[c])  # stack
        axx.plot(f[sel], m[sel]/m[sel].max() + offset, lw=1)
        axx.axvline(FL, ymin=0, ymax=1, color='gray', ls=':', lw=0.5)
        axx.text(36, offset+0.1, f"n=-{n:.1f}, F_L={FL:.0f}T", fontsize=7)
    axx.set_xlim(0, 40); axx.set_xlabel("F (T)"); axx.set_ylabel("FFT (norm, stacked by |n|)"); axx.set_title(title)
fig.suptitle("Run 4 fan — per-column SdH spectra at representative n (sr1)")
fig.tight_layout(); out = os.path.join(SCR, "run4_spectra.png"); fig.savefig(out, dpi=110); print("saved", out)

# Also: peak table per column at cutoff 1.0
from scipy.signal import find_peaks
print("\nn[1e12]  F_L   peaks(F[T], rel)  [cutoff 1.0T, f>5]")
for c in cols:
    n = abs(ns_cm[c]); FL = float(a.luttinger_frequency(n*1e16))
    f, mag = a.sdh_fft(R1[:, c:c+1], B, b_range=(1.0, 7.9), bg_degree=5)
    m = mag[0]; sel = f > 5; ff, mm = f[sel], m[sel]
    pk, _ = find_peaks(mm, prominence=mm.max()*0.15)
    pk = pk[np.argsort(mm[pk])[::-1][:4]]
    peaks = sorted([(round(float(ff[i]), 1), round(float(mm[i]/mm.max()), 2)) for i in pk])
    print(f"  -{n:.2f}   {FL:4.1f}   {peaks}")
