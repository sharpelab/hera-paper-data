"""Global LK fit: A(T) = A0 * X/sinh(X), X = C*m*T_eff/B_eff, T_eff = sqrt(T^2+T_e0^2).
Shared T_e0 across all branch/channel series; per-series A0, m*."""
import numpy as np, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

rows = list(csv.DictReader(open("hera_scratch/lk_table.csv")))
T = np.array([float(r["T_mean"]) for r in rows])
B_EFF = 2 / (1/4.0 + 1/8.0)        # 5.33 T harmonic mean of the FFT window
C = 14.693 / B_EFF                  # X = C * m*(m_e) * T_eff

series = {}
for ch in ("sr1", "sr2"):
    for br in ("f_s", "f_B", "f_top"):
        A = np.array([float(r[f"{ch}_{br}"]) for r in rows])
        N = np.array([float(r[f"{ch}_noise"]) for r in rows])
        A = np.sqrt(np.clip(A**2 - N**2, 0, None))   # leakage-floor correction
        series[f"{ch}_{br}"] = A

keys = list(series)
def model(p):
    Te0 = p[0]
    out = []
    Teff = np.sqrt(T**2 + Te0**2)
    for i, k in enumerate(keys):
        A0, m = p[1 + 2*i], p[2 + 2*i]
        X = C * m * Teff
        out.append(series[k] - A0 * X / np.sinh(X))
    return np.concatenate(out)

p0 = [6.0] + [v for k in keys for v in (series[k][-1] * 1.5, 0.04)]
lo = [0.5] + [v for k in keys for v in (0, 0.001)]
hi = [15.0] + [v for k in keys for v in (np.inf, 0.5)]
fit = least_squares(model, p0, bounds=(lo, hi))
Te0 = fit.x[0]

# rough parameter errors from jacobian
J = fit.jac; res = fit.fun
dof = max(len(res) - len(fit.x), 1)
cov = np.linalg.pinv(J.T @ J) * (res @ res) / dof
perr = np.sqrt(np.diag(cov))

print(f"global T_e0 = {Te0:.2f} +- {perr[0]:.2f} K   (B_eff = {B_EFF:.2f} T)")
masses = {}
for i, k in enumerate(keys):
    m, dm = fit.x[2 + 2*i], perr[2 + 2*i]
    masses[k] = (m, dm)
    print(f"  {k}: m* = {m:.4f} +- {dm:.4f} m_e   (A0 = {fit.x[1+2*i]:.0f})")

for ch in ("sr1", "sr2"):
    ms, mB, mt = masses[f"{ch}_f_s"][0], masses[f"{ch}_f_B"][0], masses[f"{ch}_f_top"][0]
    print(f"{ch}: m_s + m_B = {ms + mB:.4f} vs m_top = {mt:.4f}  "
          f"-> {'BREAKDOWN/INTERMOD-like (m_top ~ sum)' if abs(mt - (ms+mB)) < 0.15*(ms+mB) else ('THIRD BAND (distinct mass)' if mt < 0.85*(ms+mB) else 'inconclusive')}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
Tfine = np.linspace(1, 28, 200)
for ax, ch in zip(axes, ("sr1", "sr2")):
    for br, c in (("f_s", "C0"), ("f_B", "C1"), ("f_top", "C2")):
        k = f"{ch}_{br}"; i = keys.index(k)
        ax.plot(T, series[k], "o", color=c, label=f"{br} (m*={masses[k][0]:.3f})")
        A0, m = fit.x[1 + 2*i], fit.x[2 + 2*i]
        Xf = C * m * np.sqrt(Tfine**2 + Te0**2)
        ax.plot(Tfine, A0 * Xf / np.sinh(Xf), "-", color=c, lw=0.9)
    ax.set_xlabel("T_lattice (K)"); ax.set_title(f"{ch}"); ax.legend(fontsize=8)
axes[0].set_ylabel("FFT amplitude (leakage-corrected)")
fig.suptitle(f"LK ladder runs 10-17: global fit, T_e0 = {Te0:.2f} K")
fig.tight_layout(); fig.savefig("hera_scratch/lk_fit.png", dpi=110)
print("saved hera_scratch/lk_fit.png")
