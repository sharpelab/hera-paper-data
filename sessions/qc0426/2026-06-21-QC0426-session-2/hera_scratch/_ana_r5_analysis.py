# Per-column F(n) + Onsager forward-model overlay (ABA ML+BL vs ABC single)
import sys, scipy.constants as cst
sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\trilayer_fs_count")
import fs_count_b0 as fsc

F_Lc = cst.h / (4 * cst.e) * n_col
def fpk(R, cutoff=1.5, fmin=3.0):
    f, mag = sdh_fft(R[oB, :], Bs5, b_range=(cutoff, Bs5.max()), bg_degree=5); mag = np.asarray(mag)
    return np.array([f[f > fmin][np.argmax(mag[j, f > fmin])] for j in range(mag.shape[0])])
F1 = fpk(R1f); F2 = fpk(R2f)

ns = np.linspace(1.5e16, 3.5e16, 16); aba_lo, aba_hi, abc_f = [], [], []
for n in ns:
    _, fs = fsc.aba_fs(n); Fs = sorted(F for F, k in fs)
    aba_lo.append(Fs[0]); aba_hi.append(Fs[-1]); abc_f.append(fsc.abc_fs(n)[4])
aba_lo, aba_hi, abc_f = map(np.array, (aba_lo, aba_hi, abc_f))
m = n_col >= 1.5e16
lams = np.linspace(0.8, 1.2, 41)
lam = lams[np.argmin([np.nanmean((F1[m] - np.interp(l * n_col[m], ns, abc_f))**2) for l in lams])]
print(f"ABA(ML,BL)@2.5e12=({np.interp(2.5e16,ns,aba_lo):.1f},{np.interp(2.5e16,ns,aba_hi):.1f})T ; "
      f"ABC@2.5e12={np.interp(2.5e16,ns,abc_f):.1f}T ; global rescale lambda={lam:.3f}")

plt.figure(figsize=(8, 5.5))
plt.plot(ns/1e16, abc_f, "g-", lw=2, label="ABC single pocket")
plt.plot(ns/1e16, aba_hi, "b-", lw=1.5, label="ABA BL")
plt.plot(ns/1e16, aba_lo, "b--", lw=1.5, label="ABA ML (discriminator)")
plt.plot(n_col/1e16, F_Lc, "k:", lw=0.8, label="F_L")
plt.plot(n_col[m]/1e16, F1[m], "o", color="C3", ms=5, label="sr1 measured")
plt.plot(n_col[m]/1e16, F2[m], "s", color="C1", ms=4, label="sr2 measured")
plt.xlabel("n [10^12 cm^-2]"); plt.ylabel("F [T]"); plt.legend(fontsize=8)
plt.title(f"FS-count: F(n) vs Onsager model (rescale lambda={lam:.2f})")
plt.ylim(0, 40); plt.show()
print("KEY: ABA-BL ~ ABC ~ F_L (coincide); the only discriminator (ABA-ML) sits <~2T,")
print("below this run's resolution (df~1.9T) and in the MR-background band.")
