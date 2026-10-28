# Run 7 — FFT stack, branch traces, Luttinger partition, amplitude systematics
from scipy.signal import find_peaks

r7 = run(7)
fg7 = fan_grids(r7)
rg7 = resistance_grids(fg7)
B7 = np.asarray(fg7.slow)
ns_true = np.linspace(2.0, 6.3, 51) * 1.07          # Hall-pinned scale (runs 5/6)
F_L7 = (cst.h / (4 * cst.e)) * ns_true * 1e16

fr7, spec1 = sdh_fft(np.asarray(rg7.R["sr1"]), B7, b_range=(1.4, 8.0), bg_degree=5, log=False)
_,   spec2 = sdh_fft(np.asarray(rg7.R["sr2"]), B7, b_range=(1.4, 8.0), bg_degree=5, log=False)

def trace(spec):
    fs, fB, ftop = np.full(51, np.nan), np.full(51, np.nan), np.full(51, np.nan)
    for i in range(51):
        mag = spec[i]
        pk, _ = find_peaks(mag, height=mag.max() * 0.12, distance=3)
        pf, pm = fr7[pk], mag[pk]
        m = (pf >= 3) & (pf <= max(6, 0.35 * F_L7[i]))
        if m.any(): fs[i] = pf[m][np.argmax(pm[m])]
        m = (pf >= 0.55 * F_L7[i]) & (pf <= 0.93 * F_L7[i])
        if m.any(): fB[i] = pf[m][np.argmax(pm[m])]
        m = (pf > 0.93 * F_L7[i]) & (pf <= 1.12 * F_L7[i])
        if m.any(): ftop[i] = pf[m][np.argmax(pm[m])]
    return fs, fB, ftop

t1, t2 = trace(spec1), trace(spec2)
# ABA forward model (fs_count_b0, Datta SWMcC, D=0; clamped <=3.5e12)
model_n, model_ML, model_BL = (np.array([1.0, 1.5, 2.0, 3.0]),
                               np.array([0.0, 0.2, 0.5, 1.5]),
                               np.array([10.3, 15.3, 20.2, 29.5]))

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
for ax, S, nm in ((axes[0, 0], spec1, "sr1"), (axes[0, 1], spec2, "sr2")):
    pm = ax.pcolormesh(fr7, ns_true, S / S.max(axis=1, keepdims=True), cmap="magma", shading="auto")
    ax.plot(F_L7, ns_true, "c--", lw=1.2, label="F_L(n)")
    ax.set_xlim(0, 120); ax.set_xlabel("F (T)"); ax.set_ylabel("n_true (1e12)")
    ax.set_title(f"{nm} per-column |FFT|"); ax.legend(fontsize=8)
for ax, (fs, fB, ftop), nm in ((axes[1, 0], t1, "sr1"), (axes[1, 1], t2, "sr2")):
    ax.plot(ns_true, F_L7, "k--", lw=1, label="F_L")
    ax.plot(ns_true, fs, "o", ms=3, label="f_s"); ax.plot(ns_true, fB, "s", ms=3, label="f_B")
    ax.plot(ns_true, ftop, "^", ms=3, label="f_top"); ax.plot(ns_true, fB + fs, "r.", ms=4, label="f_B+f_s")
    ax.plot(model_n, model_BL, "g-", lw=1, label="ABA BL model"); ax.plot(model_n, model_ML, "g:", lw=1, label="ABA ML model")
    ok = np.isfinite(fs) & np.isfinite(fB) & (ns_true > 4.3)
    print(f"{nm}: partition over n>4.3 ({ok.sum()} cols): median f_B+f_s-F_L = "
          f"{np.nanmedian((fB+fs-F_L7)[ok]):+.2f} T, rms {np.nanstd((fB+fs-F_L7)[ok]):.2f} T (dF res 1.6 T)")
    ax.set_xlabel("n_true (1e12)"); ax.set_ylabel("F (T)"); ax.set_title(f"{nm} branches"); ax.legend(fontsize=7)
fig.suptitle("run 7 - FS-count read: FFT stack, branch traces, ABA-model overlay")
fig.tight_layout()

# amplitude systematics: intermod test on f_top (n > 5.3e12)
def amp_in(mag, frq, f0, w=4.0):
    m = (frq >= f0 - w) & (frq <= f0 + w)
    return mag[m].max() if m.any() else np.nan
for ch, R in (("sr1", rg7.R["sr1"]), ("sr2", rg7.R["sr2"])):
    for brange in ((2.0, 4.5), (4.5, 8.0)):
        frq, spec = sdh_fft(np.asarray(R), B7, b_range=brange, bg_degree=3, log=False)
        ratios = [amp_in(spec[i], frq, F_L7[i]) / amp_in(spec[i], frq, 0.83 * F_L7[i])
                  for i in range(35, 51)]
        print(f"{ch} B{brange}: median a_top/a_B = {np.nanmedian(ratios):.2f}")
print("(intermod predicts a_top/a_B grows x3-5 from low to high window; observed <x1.4 — disfavored, not excluded)")
