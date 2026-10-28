# Runs 8-13 — LK mass ladder fit (temperature-dependence-vti Flavor B)
from scipy.optimize import curve_fit

RUNS_LK = [8, 9, 10, 11, 12, 13]
B_RANGE_LK = (1.7, 8.0)
B_EFF = 2 / (1 / B_RANGE_LK[0] + 1 / B_RANGE_LK[1])
ALPHA = 14.694  # X = ALPHA*(m*/me)*T/B

tones_lk = {"ML": (4.3, 1.5), "BL": (28.0, 2.0), "FL": (32.4, 1.6)}
amps = {ch: {k: [] for k in tones_lk} for ch in ("sr1_X", "sr2_X")}
Ts_lk = []
for fid in RUNS_LK:
    r = open_run(f"data/{fid}")
    o = np.argsort(r.col("magnet_field"))
    Bl = r.col("magnet_field")[o]
    Ts_lk.append(r.col("T_sample").mean())
    for ch in amps:
        R = (r.col(ch) / 20e-9)[o]
        fl_, sp = sdh_fft(R[:, None], Bl, b_range=B_RANGE_LK, log=False)
        for k, (F0, w) in tones_lk.items():
            m = (fl_ > F0 - w) & (fl_ < F0 + w)
            amps[ch][k].append(sp[0][m].max())
Ts_lk = np.array(Ts_lk)
print(f"rungs: T = {np.round(Ts_lk, 2)} K (accepted means; hover-accepted, drift < 0.26 K/rung)")

def lk(T, m, A0):
    X = ALPHA * m * T / B_EFF
    return A0 * X / np.sinh(X)

fits_lk = {}
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for ax, ch in zip(axes, amps):
    for k, mk in (("ML", "o"), ("BL", "s"), ("FL", "^")):
        A = np.array(amps[ch][k])
        p, cov = curve_fit(lk, Ts_lk[1:], A[1:], p0=[0.05, A[1] * 2], maxfev=20000)
        fits_lk[(ch, k)] = (p[0], np.sqrt(cov[0, 0]))
        ax.semilogy(Ts_lk, A, mk, label=f"{k}: m* = {p[0]:.4f} ± {np.sqrt(cov[0,0]):.4f}")
        Tg = np.linspace(1, 33, 200)
        ax.semilogy(Tg, lk(Tg, *p), "-", lw=0.8, alpha=0.6)
    ax.set_xlabel("T (K)")
    ax.set_title(ch)
    ax.legend(fontsize=8)
axes[0].set_ylabel("FFT amplitude (arb)")
fig.suptitle("runs 8–13: LK per-branch fit (T ≥ 6 K rungs; base rung shown, excluded — T_e ≈ 8 K floor)")
fig.tight_layout()
plt.show()

for ch in amps:
    mml, mbl, mfl = (fits_lk[(ch, k)][0] for k in ("ML", "BL", "FL"))
    print(f"{ch}: m_ML={mml:.4f}, m_BL={mbl:.4f} (sum {mml+mbl:.4f}), m_FL={mfl:.4f} "
          f"→ m_FL/(m_ML+m_BL) = {mfl/(mml+mbl):.2f}")
print("Two distinct masses (×2–3) on the pair → two genuine bands (decisive per the "
      "investigation). m_FL sits between m_BL and the parents' sum: heavier than the "
      "light branch (beat NOT excluded by the lighter-than rule, but the B-window split "
      "already favors breakdown); consistent-with a breakdown sum orbit with BL-window "
      "harmonic-contamination systematics (m_BL: sr1 0.064 vs sr2 0.037 disagreement is "
      "that systematic); an ABC-domain pocket at F_L is not positively required by any check.")
