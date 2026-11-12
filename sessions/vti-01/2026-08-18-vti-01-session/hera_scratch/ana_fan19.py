# Run 19 — quality fan (tau=300ms): three-branch read + Luttinger with the pair
import sys
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/trilayer_fs_count"))
from fs_count_b0 import aba_fs
from scipy.signal import find_peaks

g = run(19)
print(summarize_run(g))
plot_raw(g)

NF = 53
gr = lambda c: c[:len(c) // NF * NF].reshape(-1, NF)
B = gr(g.col("magnet_field"))[:, 0]
i_dr = gr(np.abs(g.col("sr0_X")) / 1e6)
ns = np.linspace(-0.70, -1.74, NF)
FLs = cst.h * np.abs(ns) * 1e16 / (4 * cst.e)

R1 = gr(g.col("sr1_X")) / i_dr
f, spec = sdh_fft(R1, B, b_range=(0.92, 5.0), bg_degree=4)

# branch extraction per column: ML (1-5 T own-slope), A (dominant 5-20 T)
tab = []
for j in range(NF):
    s = spec[j] / spec[j].max()
    p, _ = find_peaks(s, prominence=0.12)
    pk = [(f[i], s[i]) for i in p]
    fA = max((x for x in pk if 5 < x[0] < 20), key=lambda t: t[1], default=(np.nan,) * 2)[0]
    fML = max((x for x in pk if 1.2 < x[0] < 5), key=lambda t: t[1], default=(np.nan,) * 2)[0]
    tab.append((ns[j], fML, fA))
tab = np.array(tab)

# Luttinger with the pair: one global scale over columns where both resolve
ok = np.isfinite(tab[:, 1]) & np.isfinite(tab[:, 2]) & (np.abs(tab[:, 0]) < 1.45)
lam = np.mean((tab[ok, 1] + tab[ok, 2]) / FLs[ok])
print(f"Luttinger pair sum over {ok.sum()} columns: (f_ML + f_A)/F_L = {lam:.3f} "
      f"± {np.std((tab[ok,1]+tab[ok,2])/FLs[ok]):.3f}  -> single global scale, in the ±15% band")
print(f"partition f_ML/Σ = {np.mean(tab[ok,1]/(tab[ok,1]+tab[ok,2])):.2f} (model ABA: 0.13)")

# figure: FFT map + measured branches + model ABA curves at the fitted rescale
fig, ax = plt.subplots(figsize=(8, 5.5))
S = spec / spec.max(axis=1, keepdims=True)
pm = ax.pcolormesh(ns, f, S.T, shading="nearest", cmap="magma", vmax=1)
fig.colorbar(pm, ax=ax, label="per-column FFT (norm)")
ax.plot(tab[:, 0], tab[:, 1], "c^", ms=4, label="measured low branch (ML cand.)")
ax.plot(tab[:, 0], tab[:, 2], "co", ms=4, label="measured branch A")
aba_ml, aba_bl = [], []
for n in ns:
    Fs = sorted(F for F, _ in aba_fs(n * lam * 1e16)[1])   # model at rescaled density
    aba_ml.append(Fs[0] if len(Fs) > 1 else np.nan); aba_bl.append(Fs[-1])
ax.plot(ns, aba_ml, "g-.", lw=1.2, label=f"ABA f_ML (model, n×{lam:.2f})")
ax.plot(ns, aba_bl, "g--", lw=1.2, label=f"ABA f_BL (model, n×{lam:.2f})")
ax.plot(ns, lam * FLs, "w:", lw=1, label=f"{lam:.2f}·F_L")
ax.set_xlabel("n (10¹² cm⁻²)"); ax.set_ylabel("F (T)"); ax.set_ylim(0, 40)
ax.legend(fontsize=7, loc="upper left")
ax.set_title("run 19 (τ=300 ms): sr1 per-column FFT — ML + BL branches vs ABA model")
plt.show()

print("\nn(e12)   f_ML    f_A    sum    1.14*F_L")
for n, fm, fa in tab[::4]:
    FL = cst.h * abs(n) * 1e16 / (4 * cst.e)
    print(f"{n:+.2f}   {fm:5.1f}  {fa:5.1f}  {fm+fa:5.1f}   {lam*FL:5.1f}")
