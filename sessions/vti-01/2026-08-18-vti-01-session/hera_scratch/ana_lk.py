# Runs 12-18 — LK mass ladder: amplitudes vs T and the mass fits
from scipy.optimize import curve_fit

RUNS = list(range(12, 19))
B_EFF = 1 / ((1 / 2.0 + 1 / 5.0) / 2)     # 2.86 T (1/B midpoint of the 2-5 T window)
C_LK = 14.69 / B_EFF

def amp_at(f, s, F0, half=2.0):
    m = (f > F0 - half) & (f < F0 + half)
    return s[m].max() if m.any() else np.nan

rows = []
for rid in RUNS:
    r = run(rid)
    print(summarize_run(r))
    B = r.col("magnet_field")
    i_dr = np.abs(r.col("sr0_X")) / 1e6
    T = np.mean(r.col("T_sample")); Td = np.ptp(r.col("T_sample"))
    o = {"run": rid, "T": T, "drift": Td}
    for ch in ("sr1", "sr3"):
        f, s = sdh_fft((r.col(f"{ch}_X") / i_dr)[:, None], B, b_range=(2.0, 5.0), bg_degree=4)
        o[f"{ch}_A"], o[f"{ch}_A2"] = amp_at(f, s[0], 16.2), amp_at(f, s[0], 8.1)
    rows.append(o)
    print(f"  T={T:.3f} K (intra-sweep drift {Td:.3f} K)")

T_arr = np.array([o["T"] for o in rows])
def lk(T, m, a0):
    X = C_LK * m * T
    return a0 * X / np.sinh(X)

fig, axs = plt.subplots(1, 2, figsize=(11, 4.3))
for ax, key, lbl in ((axs[0], "_A", "branch A (16.2 T)"), (axs[1], "_A2", "A/2 (8.1 T)")):
    for ch, c in (("sr1", "tab:blue"), ("sr3", "tab:green")):
        amps = np.array([o[ch + key] for o in rows]); ok = np.isfinite(amps)
        try:
            p, cov = curve_fit(lk, T_arr[ok], amps[ok], p0=[0.08, amps[ok][0] * 1.2],
                               bounds=([0.001, 0], [1.0, np.inf]))
            err = np.sqrt(np.diag(cov))[0]
            Tf = np.linspace(1, 16, 200)
            ax.plot(Tf, lk(Tf, *p), color=c, lw=1)
            ax.plot(T_arr[ok], amps[ok], "o", color=c, label=f"{ch}: m*={p[0]:.3f}±{err:.3f} mₑ")
            print(f"{lbl} {ch}: m* = {p[0]:.4f} ± {err:.4f} mₑ")
        except Exception as e:
            ax.plot(T_arr[ok], amps[ok], "x", color=c, label=f"{ch}: fit failed")
    ax.set_title(lbl); ax.set_xlabel("T (K)"); ax.legend(fontsize=7); ax.grid(alpha=0.3)
axs[0].set_ylabel("FFT amplitude (2–5 T window)")
plt.show()
print(f"B_eff = {B_EFF:.2f} T | model masses at n = −1.74e12 (hole): "
      f"ABA {{ML 0.010, BL 0.060}}, ABC 0.108 mₑ")
print("NOTE: LK fit is manual/ana-side per recipe — flagged for expert review.")
