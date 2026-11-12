# LK ladder — amplitude table, global + fixed-Te0 fits, per-branch masses
import csv as _csv
from scipy.optimize import least_squares

_rows = list(_csv.DictReader(open("hera_scratch/lk_table.csv")))
T_l = np.array([float(r["T_mean"]) for r in _rows])
runs_l = [r["run"] for r in _rows]
B_EFF = 2/(1/4.0+1/8.0); C_LK = 14.693/B_EFF
print("runs:", runs_l, "| T:", np.round(T_l, 2), "| B_eff =", round(B_EFF, 2), "T")

def series(ch, br):
    A = np.array([float(r[f"{ch}_{br}"]) for r in _rows])
    N = np.array([float(r[f"{ch}_noise"]) for r in _rows])
    return np.sqrt(np.clip(A**2 - N**2, 0, None))

masses = {}
print("masses vs fixed T_e0 (K)  [T_e0 is unconstrained by the fit: these masses are"
      " too light for the ladder to probe a floor <~8 K — X(8 K) < 0.15]")
for Te0 in (0.0, 8.0):
    Teff = np.sqrt(T_l**2 + Te0**2)
    for ch in ("sr1", "sr2"):
        out = {}
        for br in ("f_s", "f_B", "f_top"):
            A = series(ch, br)
            f = least_squares(lambda p: A - p[0]*(C_LK*p[1]*Teff)/np.sinh(C_LK*p[1]*Teff),
                              [A[-1]*1.2, 0.04], bounds=([0, 0.001], [np.inf, 0.5]))
            J, r_ = f.jac, f.fun
            dm = np.sqrt(np.diag(np.linalg.pinv(J.T@J)*(r_@r_)/max(len(r_)-2, 1)))[1]
            out[br] = (f.x[1], dm, f.x[0])
        if Te0 == 0.0:
            masses[ch] = out
        s = out["f_s"][0] + out["f_B"][0]
        print(f"  Te0={Te0}: {ch}: m_s={out['f_s'][0]:.3f}({out['f_s'][1]:.3f}) "
              f"m_B={out['f_B'][0]:.3f}({out['f_B'][1]:.3f}) m_top={out['f_top'][0]:.3f}({out['f_top'][1]:.3f}) "
              f"| m_s+m_B={s:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
Tf = np.linspace(1, 28, 200)
for ax, ch in zip(axes, ("sr1", "sr2")):
    for br, c in (("f_s", "C0"), ("f_B", "C1"), ("f_top", "C2")):
        m, dm, A0 = masses[ch][br]
        ax.plot(T_l, series(ch, br), "o", color=c, label=f"{br}: m*={m:.3f}({dm:.3f})")
        Xf = C_LK*m*Tf
        ax.plot(Tf, A0*Xf/np.sinh(Xf), "-", color=c, lw=0.9)
    ax.set_xlabel("T measured (K)"); ax.set_title(ch); ax.legend(fontsize=8)
axes[0].set_ylabel("FFT amplitude (leakage-corrected)")
fig.suptitle("LK ladder (runs 10-17): per-branch mass fits, electron n=+6e12, D=0")
fig.tight_layout()
