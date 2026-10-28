# Electron FFT: stable dominant tone, F_L comparison, secondary-peak search
import scipy.constants as cst
from scipy.signal import find_peaks
F_L = cst.h / (4 * cst.e) * 3.5e16
print(f"F_L = {F_L:.1f} T")
print("FFT dominant peak(>2T) vs extraction (electron — stable, cf. hole wandered):")
for cut in (1.5, 2.0, 3.0, 4.0):
    pks = []
    for deg in (3, 5, 7):
        f, m = sdh_fft(R1[:, None], B, b_range=(cut, B.max()), bg_degree=deg); m = np.asarray(m).squeeze()
        pks.append(f[f > 2][np.argmax(m[f > 2])])
    print(f"  cut {cut:.1f}T  bg(3,5,7): " + ", ".join(f"{p:5.1f}T" for p in pks))

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
for cut, c in [(1.5, "C0"), (2.0, "C1"), (3.0, "C2")]:
    f, m = sdh_fft(R1[:, None], B, b_range=(cut, B.max()), bg_degree=5); m = np.asarray(m).squeeze()
    ax[0].plot(f, m / m[f > 2].max(), lw=1, label=f"sr1 cut {cut}T")
ax[0].axvline(F_L, ls="--", c="k", lw=1.2, label=f"F_L={F_L:.0f}T")
ax[0].set_xlim(0, 60); ax[0].set_xlabel("F [T]"); ax[0].set_ylabel("norm FFT"); ax[0].legend(fontsize=8)
ax[0].set_title("sr1 FFT vs cutoff: stable dominant ~34T")
for ch, R, c in [("sr1", R1, "C0"), ("sr2", R2, "C1")]:
    f, m = sdh_fft(R[:, None], B, b_range=(2.0, B.max()), bg_degree=5); m = np.asarray(m).squeeze(); mn = m / m[f > 2].max()
    ax[1].plot(f, mn, color=c, lw=1.2, label=ch)
    pk, pr = find_peaks(mn[f > 3], height=0.15); fpk = f[f > 3][pk]
    dom = fpk[np.argmax(pr["peak_heights"])]
    print(f"{ch}: dominant {dom:.1f}T ; F_L/dom={F_L/dom:.2f} (1 => single pocket at F_L = ABC)")
ax[1].axvline(F_L, ls="--", c="k", lw=1.2, label=f"F_L={F_L:.0f}T")
ax[1].set_xlim(0, 60); ax[1].set_xlabel("F [T]"); ax[1].set_ylabel("norm FFT"); ax[1].legend(fontsize=8)
ax[1].set_title("FFT sr1 vs sr2 (cut 2T)")
plt.show()
