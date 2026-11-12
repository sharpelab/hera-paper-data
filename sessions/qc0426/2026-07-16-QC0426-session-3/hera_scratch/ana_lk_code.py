# Runs 11-16: tone amplitudes vs T + joint LK fit (shared T_e0)
from scipy.optimize import differential_evolution, curve_fit

RIDS = [11, 12, 13, 14, 15, 16]
T_l, A11, A55, A66 = [], [], [], []
for rid in RIDS:
    r = run(rid)
    B = r.col_at(1); R = r.col("sr1_X") / 20e-9
    freqs, spec = sdh_fft(R[:, None], B, b_range=(3.2, 8.0), bg_degree=5)
    a = spec[0]
    def amp(F, w):
        m = (freqs > F - w) & (freqs < F + w)
        return a[m].max()
    T_l.append(np.mean(r.col("T_sample")))
    A11.append(amp(11.1, 3)); A55.append(amp(55.3, 4)); A66.append(amp(66.4, 4))
T_l, A11, A55, A66 = map(np.array, (T_l, A11, A55, A66))
B_EFF = 2.0 / (1/3.2 + 1/8.0)

def lk(T, A0, m, Te0):
    x = 14.694 * m * np.sqrt(T**2 + Te0**2) / B_EFF
    return A0 * x / np.sinh(x)

def resid(p):
    Te0, a1, m1, a2, m2 = p
    return (np.sum((np.log(lk(T_l, a1, m1, Te0)) - np.log(A11))**2)
            + np.sum((np.log(lk(T_l, a2, m2, Te0)) - np.log(A55))**2))

sol = differential_evolution(resid, [(0.1, 15), (1, 4), (0.005, 0.06), (1, 4), (0.02, 0.2)], seed=1, tol=1e-10)
Te0, a1, m1, a2, m2 = sol.x
p66, _ = curve_fit(lambda TT, A0, m: lk(TT, A0, m, Te0), T_l, A66, p0=[2.5, m1 + m2], maxfev=20000)
print(f"T_e0 = {Te0:.2f} K | m*(11.1) = {m1:.4f} m_e | m*(55.3) = {m2:.4f} m_e | ratio {m2/m1:.2f}")
print(f"sum tone m* = {p66[1]:.4f} vs m_ML+m_BL = {m1+m2:.4f} | beat exclusion: m(11)<m(55) PASS")

fig, ax = plt.subplots(figsize=(8, 5))
Tf = np.linspace(0.5, 27, 200)
for A, lbl, c, (a0, m) in ((A11, "f_ML 11.1 T", "C0", (a1, m1)),
                            (A55, "f_BL 55.3 T", "C1", (a2, m2)),
                            (A66, "sum 66.4 T", "C2", (p66[0], p66[1]))):
    ax.semilogy(T_l, A, "o", color=c, label=f"{lbl}: m*={m:.3f} m_e")
    ax.semilogy(Tf, lk(Tf, a0, m, Te0), "-", color=c, lw=1)
ax.set_xlabel("T_lattice (K)"); ax.set_ylabel("FFT amplitude (fixed 3.2–8 T window)")
ax.set_title(f"LK mass split, runs 11–16 (T_e0 = {Te0:.1f} K fitted)")
ax.legend()
fig.tight_layout()
