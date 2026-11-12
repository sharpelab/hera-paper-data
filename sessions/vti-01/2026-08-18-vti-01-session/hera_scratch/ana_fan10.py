# Run 10 — D=0 hole fan: raw, per-column FFT map vs models, branch table
import sys
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/trilayer_fs_count"))
from fs_count_b0 import aba_fs, abc_fs
from scipy.signal import find_peaks

g = run(10)
print(summarize_run(g))
plot_raw(g)

NFAST = 53
B_all = g.col("magnet_field")
i_dr = np.abs(g.col("sr0_X")) / 1e6
nrows = len(B_all) // NFAST
gr = lambda c: c[:nrows * NFAST].reshape(nrows, NFAST)
B = gr(B_all)[:, 0]
ns = np.linspace(-0.70, -1.74, NFAST)

fig, axs = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, ch in zip(axs, ("sr1", "sr3")):
    R = gr(g.col(f"{ch}_X")) / gr(i_dr)
    f, spec = sdh_fft(R, B, b_range=(1.7, 5.0), bg_degree=5)
    S = spec / spec.max(axis=1, keepdims=True)
    ax.pcolormesh(ns, f, S.T, shading="nearest", cmap="magma", vmax=1.0)
    FL = cst.h * np.abs(ns) * 1e16 / (4 * cst.e)
    ax.plot(ns, FL, "c--", lw=1, label="F_L")
    ax.plot(ns, 0.90 * FL, "c:", lw=1, label="0.90 F_L")
    ax.plot(ns, 0.45 * FL, "w:", lw=0.8, label="0.45 F_L (A/2)")
    aba1 = [sorted(F for F, _ in aba_fs(n * 1e16)[1])[0] for n in ns]
    aba2 = [sorted(F for F, _ in aba_fs(n * 1e16)[1])[-1] for n in ns]
    abcF = [abc_fs(n * 1e16)[4] for n in ns]
    ax.plot(ns, aba1, "g-.", lw=1, label="ABA f_ML")
    ax.plot(ns, aba2, "g--", lw=1, label="ABA f_BL")
    ax.plot(ns, abcF, "m--", lw=1, label="ABC F_tot")
    ax.set_title(f"{ch} per-column FFT"); ax.set_xlabel("n (1e12 cm^-2)"); ax.set_ylim(0, 45)
axs[0].set_ylabel("F (T)"); axs[0].legend(fontsize=6, loc="upper left")
plt.show()

# branch A fit: dominant peak per column, F vs |n|
R = gr(g.col("sr1_X")) / gr(i_dr)
f, spec = sdh_fft(R, B, b_range=(1.7, 5.0), bg_degree=5)
FA = []
for j in range(NFAST):
    s = spec[j] / spec[j].max()
    p, _ = find_peaks(s, prominence=0.15)
    cand = [(f[i], s[i]) for i in p if 4 < f[i] < 20]
    if cand:
        FA.append((abs(ns[j]), max(cand, key=lambda t: t[0] * (t[1] > 0.4))[0]))
FA = np.array(FA)
# fit only columns where the high branch is the max-F strong peak
sl = np.polyfit(FA[:, 0], FA[:, 1], 1)
print(f"branch fit (crude, strong peaks 4-20 T): F = {sl[0]:.2f}*|n| {sl[1]:+.2f}  "
      f"(F_L slope 10.36 -> scale {sl[0]/10.36:.2f})")
